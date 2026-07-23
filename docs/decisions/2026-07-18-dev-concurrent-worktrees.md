# /dev Concurrent-Session Worktree Isolation — Architecture Record

*2026-07-18 · Shipped · Built with superpowers subagent-driven-development (outside the /dev workflow, since /dev could not yet run worktree cycles)*

> This is the design record for the worktree model that now underpins every `/dev` cycle.
> It was implemented before `/dev` could isolate its own cycles, so it has no standard
> `dev:done` decision log — this file is that record. A few implementation details evolved
> during build (notably `dev:done`'s branch deletion, which ships as explicit `git` plumbing
> rather than `gh pr merge --delete-branch`); where this doc and the skills differ, the skill
> files under `plugins/dev/skills/` are the source of truth.

## Problem

The `/dev` workflow assumes it owns the repository's single shared working tree and
its checked-out branch. Every stage runs bare `git`/`gh` commands that rely on "the
current branch is this cycle's feature branch" and "the current directory is the repo
root on that branch."

That assumption breaks the moment a second Claude Code session operates in the same
repo. `git checkout` is a repo-global mutable resource: when session B switches the
working tree to its own branch, session A's in-flight `/dev` cycle silently loses its
footing. Concretely, in the `name-evaluation-rubric` cycle:

- `gh pr create` grabbed the wrong head branch (whatever the tree happened to be on).
- `dev:done`'s post-merge commits to `main` (Component Registry, decision log,
  retrospective, product-plan, working-dir cleanup) had nowhere to run, because the
  primary tree was on an unrelated branch.

Both were worked around by hand with throwaway `git worktree`s. This design makes that
isolation the built-in model instead of a manual rescue.

## Goals

- Two or more `/dev` cycles can run concurrently in the same repo with **zero** working-
  tree contention.
- The user's primary checkout and shell location are **never** switched, checked out, or
  committed to by the workflow.
- The workflow is **cwd-independent**: `/clear` between stages requires no repositioning
  and no `cd`.
- Backward compatible: cycles already in flight (no worktree) keep working unchanged.

## Non-Goals

- No change to the stage sequence, tiers, approval gates, or artifact formats.
- No dependency on any harness-specific worktree tool (`EnterWorktree`/`ExitWorktree`).
- Not solving cross-*repo* concurrency or multi-machine coordination — single repo,
  multiple local sessions only.

## Design Overview

Every `/dev` cycle runs entirely inside its own git worktree, created at `dev:spec` and
torn down at `dev:done`. Worktrees are created with raw `git worktree` (git is always
present), so there is no reliance on an optional harness tool and — critically — **no
fall-back to the shared working tree**, which is the failure mode being removed.

Two invariants make concurrency safe:

1. **WORKDIR routing** — every stage resolves one working directory from state and
   routes all file and git operations through it, never through the ambient tree.
2. **cwd-independence** — no stage reads the shell's current directory; each stage
   re-derives everything it needs from the feature slug plus on-disk discovery.

## Detailed Design

### 1. Layout and config

- Worktrees live at `<primary>/.dev-worktrees/<feature>/`, gitignored.
- `docs/dev/config.json` gains `"worktree_root": ".dev-worktrees"` (default; configurable).
- `dev:init` creates/appends `.dev-worktrees/` to `.gitignore` and writes the config key.
- Placing worktrees *inside* the primary repo folder (rather than a sibling) is
  deliberate: it makes an in-flight cycle discoverable from the primary checkout
  regardless of what branch the primary tree is on. A nested worktree carries its own
  `.git` file, so git does not recurse into it, and the `.gitignore` entry keeps the
  primary tree's `git status` clean.

### 2. The WORKDIR convention (every stage)

At stage entry, each stage computes:

```
PRIMARY  = dirname(git rev-parse --git-common-dir)     # primary checkout, from any cwd
WORKDIR  = state.worktreePath ? "$PRIMARY/<worktreePath>" : "$PRIMARY"
```

- `git rev-parse --git-common-dir` resolves to `<primary>/.git` from *anywhere* — the
  primary checkout or inside any worktree — because all worktrees share one common git
  dir. `dirname` of it is the primary checkout root.
- All git commands become `git -C "$WORKDIR" …`.
- All artifact reads/writes use absolute paths under `$WORKDIR/docs/dev/<feature>/…`.
- `worktreePath` is stored **repo-relative** (e.g. `.dev-worktrees/<feature>`) so it is
  portable across machines and clones.

**cwd-independence (invariant):** No stage relies on the shell's current directory. The
user is never asked to `cd`, and `/clear` between stages requires no repositioning — the
only thing a resumed stage needs is the feature slug in its resume command, which every
stage's exit display already prints.

**Backward compatibility:** cycles started before this change have `worktreePath: null`,
so `WORKDIR = PRIMARY` and they operate in-place exactly as today. No mid-flight cycle
breaks; only newly-started cycles get worktrees.

### 3. Discovery / resume (`dev:dev` and each stage's artifact gate)

Given `<feature>` (always supplied on resume), resolve state.json in order:

1. `$PRIMARY/.dev-worktrees/<feature>/docs/dev/<feature>/state.json` — active worktree cycle.
2. `$PRIMARY/docs/dev/<feature>/state.json` — legacy in-place cycle.

The first that exists wins and fixes `WORKDIR` for the rest of the stage. Discovery works
from any cwd because `$PRIMARY` is derived, not assumed.

### 4. `dev:spec` — create the worktree (Step 6 rewrite)

Replaces the current "offer a worktree only for product-plan cycles" opt-in with
unconditional creation:

```
git -C "$PRIMARY" worktree add "$PRIMARY/.dev-worktrees/<feature>" -b <branch>
# top-level: <branch> is created from origin/main (fetch first)
# nested:    then  git -C "$WORKDIR" reset --hard <parent-branch>
```

- Records `worktreePath: ".dev-worktrees/<feature>"` in state.json.
- The old shared-tree `git checkout -b` path and the consent prompt are removed.
- If `git worktree add` fails (e.g. path exists, disk), the stage **STOPs** with a clear
  message — it never falls back to `git checkout -b` in the shared tree.
- Branch naming is unchanged: `feature/…`, `fix/…` (Micro), `arch/…` (architecture).

### 5. `dev:build`, `dev:shape`, `dev:plan`, `dev:validate`

Mechanical: resolve `WORKDIR` at entry (Section 2), route every `git` call through
`git -C "$WORKDIR"`, and read/write artifacts under `$WORKDIR/…`. `dev:validate`'s diff
range (`git diff BASE..HEAD`) runs with `-C "$WORKDIR"`. No behavioral change beyond
where the commands execute.

### 6. `dev:pr` — gh correctness

- Git steps run with `git -C "$WORKDIR"`.
- `gh pr create` and `gh pr merge` **always pass explicit `--head <branch>` and
  `--base <target>`** — never relying on the ambient current branch (the source of the
  wrong-head bug). `gh` has no `-C` flag, so it is run inside the worktree via a subshell
  — `( cd "$WORKDIR" && gh … )` — and/or pinned with `--repo <owner/name>`; with an
  explicit `--head` the result is correct regardless of cwd anyway.
- Any changelog commit rides the feature branch via `git -C "$WORKDIR"`.
- Target branch resolution (main vs. parent branch for nested) is unchanged.

### 7. `dev:done` — merge, main-commits, teardown (single worktree lifecycle)

Rather than spawn a second ephemeral worktree for the post-merge `main` commits, `done`
**reuses the cycle worktree, positioning it at the integration tip via a detached HEAD**
after merge. `<integration>` = `main` (top-level) or the parent feature's branch (nested).

A detached HEAD (not `git checkout <integration>`) is essential: `<integration>` is
normally `main`, which is checked out in the primary tree, and git forbids the same branch
in two worktrees — a plain checkout would fail (`fatal: 'main' is already used by worktree`).
Detaching sidesteps the collision and still lets the feature branch be deleted.

**Worktree cycle (normal):**
1. `git -C "$WORKDIR" fetch origin && git -C "$WORKDIR" checkout --detach` — frees the
   feature branch (detached, no branch-collision).
2. `( cd "$WORKDIR" && gh pr merge <n> --merge )` — merges only. Branch deletion is done
   separately by explicit `git` plumbing after confirming the PR merged, rather than via
   `gh pr merge --delete-branch` (which reads the current branch and fails on a detached
   HEAD). *(This is the detail that evolved from the original draft; see the skills.)*
3. `git -C "$WORKDIR" fetch origin && git -C "$WORKDIR" checkout --detach origin/<integration>`
   — detached at the merged integration tip.
4. Component Registry (Step 4), decision log (Step 5), retrospective (Step 6),
   product-plan (Step 3), and working-dir cleanup (Step 7) all commit in `$WORKDIR` and
   push via one helper using an explicit refspec: `git push origin HEAD:<integration>`,
   with **rebase-on-reject** (`fetch` + `rebase origin/<integration>` + re-push) to tolerate
   a concurrent `done` racing on `main`. The `HEAD:<integration>` refspec works with a
   detached HEAD and never requires checking the branch out.
5. `git -C "$PRIMARY" worktree remove --force "$WORKDIR" && git -C "$PRIMARY" worktree prune`
   — teardown is owned by `done`. The old "defer to `ExitWorktree`" model is dropped.

**Legacy in-place cycle** (`worktreePath` null, `WORKDIR` = primary tree): no second
worktree exists, so a plain `git checkout <integration>` + `pull --ff-only` is safe; the
same `HEAD:<integration>` push helper applies. The mergeability guard also tolerates
GitHub's async `UNKNOWN` result (re-query rather than STOP).

### 8. `dev:autopilot` and `dev:fix`

- `autopilot`: the "auto-accept the worktree offer" note becomes moot (there is no offer);
  worktree creation is simply part of `dev:spec` now. Any `git` it runs uses `-C "$WORKDIR"`.
- `fix`: its `git checkout -b fix/ENG-123-…` is replaced by the same
  `git worktree add … -b …` used in `dev:spec` Step 4, and it records `worktreePath`.

### 9. `dev:init`

- Ensure `.gitignore` contains `.dev-worktrees/` (create the file if absent, append the
  line if missing — never duplicate).
- Write `"worktree_root": ".dev-worktrees"` into `config.json`.
- Skills read `worktree_root` with a `.dev-worktrees` default when the key is absent, so
  repos initialized before this change keep working.

## Edge Cases

| Case | Handling |
|------|----------|
| Nested (sub-milestone) cycle | Integration branch = parent branch; worktree branches off parent HEAD via `reset --hard <parent-branch>` after `worktree add`. |
| Worktree path inside the repo | Gitignored so `git status` stays clean; nested worktree's own `.git` file stops recursion. Verified during build with a real `git worktree add .dev-worktrees/x`. |
| Two `done`s pushing to `main` at once | Per-feature worktree paths never collide; `main` pushes serialize at the remote; rebase-on-reject retries. |
| Resume after `/clear` with shell in a different worktree/subdir | `PRIMARY` is derived from `git rev-parse --git-common-dir`, so discovery still finds `.dev-worktrees/<feature>`. |
| `git worktree add` fails | Stage STOPs with a clear error; no silent shared-tree fallback. |
| Legacy in-flight cycle (`worktreePath: null`) | `WORKDIR = PRIMARY`; behaves exactly as today. |
| User's primary tree on an unrelated branch during any stage | Irrelevant — no stage touches the primary tree or its branch. This is the concurrency case the design fixes. |

## Verification Plan

Because these are Markdown skill instructions, verification is behavioral, exercised on
this repo itself (dogfooding):

1. **Isolation:** start a `/dev` cycle; confirm a worktree appears at `.dev-worktrees/<feature>`,
   the primary tree's branch and cwd are unchanged, and `git status` in the primary tree
   is clean (gitignore working).
2. **cwd-independence:** `/clear` mid-cycle, resume a later stage from the primary root
   without `cd`; confirm it resolves the worktree and proceeds.
3. **Concurrency:** run two cycles' stages interleaved; confirm neither disturbs the other
   and both `done`s land their `main` commits (second one rebases).
4. **done teardown:** confirm PR merges with explicit `--head`, `main` commits land, and
   the worktree is removed + pruned at the end.
5. **Backward compat:** a `worktreePath: null` state.json runs a stage in-place unchanged.

## Files Touched

Skill instructions (all under `plugins/dev/skills/`): `spec`, `build`, `validate`, `pr`,
`done`, `shape`, `plan`, `dev`, `autopilot`, `fix`, `init`.

Repo config for this repository: `.gitignore` (+ `.dev-worktrees/`), `docs/dev/config.json`
(+ `worktree_root`).

## Resolved Decisions

- **Posture:** isolate every cycle (worktree-always), not detect-and-adapt or guard-and-refuse.
- **Mechanism:** raw `git worktree`, no harness-tool dependency, no shared-tree fallback.
- **Location:** gitignored `.dev-worktrees/<feature>/` inside the repo (aids discovery).
- **Main commits:** reuse the cycle worktree at a **detached HEAD** on the integration tip
  (not a `git checkout` of the branch, which collides with the primary tree's `main`), and
  push via a `HEAD:<integration>` refspec. Not a separate ephemeral worktree.
- **Teardown:** owned by `dev:done`, automatic.
