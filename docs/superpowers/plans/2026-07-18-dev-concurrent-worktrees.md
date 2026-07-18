# /dev Concurrent-Session Worktree Isolation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every `/dev` cycle run inside its own git worktree so concurrent Claude Code sessions in one repo never contend for the shared working tree.

**Architecture:** Each cycle gets a worktree at `.dev-worktrees/<feature>/` (gitignored, created in `dev:spec`, torn down in `dev:done`). Every stage resolves a `WORKDIR` from disk discovery — never from the shell's cwd or current branch — and routes all git/file operations through it. Raw `git worktree` is the only mechanism; there is no shared-tree fallback and no dependency on any harness worktree tool.

**Tech Stack:** Markdown skill-instruction files under `plugins/dev/skills/`. No code, no test runner — verification is `grep` consistency checks plus a real dogfood worktree exercise.

## Global Constraints

- Worktrees live at `<primary>/.dev-worktrees/<feature>/`, gitignored. Config key `worktree_root` default `.dev-worktrees`.
- `worktreePath` in state.json is stored **repo-relative** (`.dev-worktrees/<feature>`).
- **cwd-independence:** no stage reads the shell's current directory. `PRIMARY=$(dirname "$(git rev-parse --git-common-dir)")`.
- **No shared-tree fallback:** if `git worktree add` fails, the stage STOPs — it never runs `git checkout -b` in the primary tree.
- **Backward compatible:** a cycle whose state.json has `worktreePath: null` runs in-place (`WORKDIR = PRIMARY`), exactly as today.
- Branch names unchanged: `feature/…`, `fix/…` (Micro / dev:fix), `arch/…` (architecture).
- These are user-instruction Markdown files — preserve each skill's existing structure, headings, and voice; make the minimal targeted edit.

### The canonical WORKDIR block (Interface — defined here, reused verbatim by Tasks 4–10)

Every stage skill (`build`, `plan`, `shape`, `validate`, `pr`, `done`) gets this block inserted immediately after its opening **Announce** line, and `dev:dev` uses the same resolution in its scan/resume. Insert it verbatim:

```markdown
## Resolve the working directory (do this first)

This stage never relies on the shell's current directory or current branch. Compute the
primary checkout, then locate this cycle's directory:

    PRIMARY=$(dirname "$(git rev-parse --git-common-dir)")

Find the cycle directory — first hit wins — by testing for `docs/dev/<feature>/state.json` under:
1. `$PRIMARY/.dev-worktrees/<feature>/`   → active worktree cycle
2. `$PRIMARY/`                            → legacy in-place cycle (worktreePath null)

Set `WORKDIR` to whichever matched. For the rest of this stage: run every git command as
`git -C "$WORKDIR" …`, and read/write all artifacts under `$WORKDIR/docs/dev/<feature>/…`.
Never `cd`, never assume the current branch.
```

---

## Task 1: `dev:init` — gitignore + `worktree_root` config (and apply to this repo)

**Files:**
- Modify: `plugins/dev/skills/init/SKILL.md` (Create Directories ~L106–114; Write config.json ~L152–166; Commit ~L168–173)
- Modify (this repo): `.gitignore` (create if absent), `docs/dev/config.json`

**Interfaces:**
- Consumes: nothing.
- Produces: the `worktree_root` config key (default `.dev-worktrees`) and the `.dev-worktrees/` gitignore line that all later tasks assume exist.

- [ ] **Step 1: Add gitignore step to init's "Create Directories" section**

In `plugins/dev/skills/init/SKILL.md`, after the `touch docs/decisions/.gitkeep` line inside the Create Directories code block (L113), append:

```bash
# Ensure /dev worktrees are ignored (create .gitignore if absent; append only if missing)
grep -qxF '.dev-worktrees/' .gitignore 2>/dev/null || echo '.dev-worktrees/' >> .gitignore
```

- [ ] **Step 2: Add `worktree_root` to the config.json template**

Replace the config.json block (L155–163) so it reads:

```json
{
  "autopilot": {
    "spec_max_questions": 10,
    "spec_min_confidence": 85
  },
  "worktree_root": ".dev-worktrees",
  "changelog": "<detected-path-or-null>",
  "changelog_versioned": "<true-or-false>"
}
```

- [ ] **Step 3: Add `.gitignore` to init's Commit step**

Change the Commit block (L170–172) to stage the gitignore too:

```bash
git add docs/dev/.gitkeep docs/decisions/.gitkeep docs/dev/config.json CLAUDE.md .gitignore
git commit -m "Initialize /dev workflow"
```

- [ ] **Step 4: Apply the same config to THIS repo**

This repo (`claude-plugins`) is already /dev-initialized, so apply the change directly:
- Add `.dev-worktrees/` to `.gitignore` (create the file if it doesn't exist; append only if the line is missing).
- Add `"worktree_root": ".dev-worktrees",` to `docs/dev/config.json` (after the `autopilot` block).

- [ ] **Step 5: Verify**

```bash
grep -n 'worktree_root' plugins/dev/skills/init/SKILL.md docs/dev/config.json
grep -qxF '.dev-worktrees/' .gitignore && echo "gitignore OK"
```
Expected: `worktree_root` present in both the skill template and this repo's config; `gitignore OK` prints.

- [ ] **Step 6: Commit**

```bash
git add plugins/dev/skills/init/SKILL.md docs/dev/config.json .gitignore
git commit -m "dev:init — provision .dev-worktrees gitignore + worktree_root config"
```

---

## Task 2: `dev:spec` — create the worktree unconditionally (Step 6 rewrite)

**Files:**
- Modify: `plugins/dev/skills/spec/SKILL.md` (Step 6 "Create Feature Branch", L115–191)

**Interfaces:**
- Consumes: `worktree_root` (Task 1); `<feature-name>`; nesting info (`parentFeature`, parent's `state.json.branch`).
- Produces: a worktree at `.dev-worktrees/<feature-name>/` with `<branch>` checked out, and `state.json.worktreePath = ".dev-worktrees/<feature-name>"`. All later stages depend on this path.

- [ ] **Step 1: Replace the Worktree-offer + plain-checkout block**

Replace the whole block from L119 ("**Worktree offer:** …") through L131 ("(Skip this plain `git checkout -b` …)") with:

```markdown
**Create the cycle worktree (always).** Every cycle runs in its own git worktree so
concurrent sessions in this repo never contend for the shared working tree. Compute the
primary checkout and create the worktree there:

    PRIMARY=$(dirname "$(git rev-parse --git-common-dir)")
    git -C "$PRIMARY" fetch origin
    git -C "$PRIMARY" worktree add "$PRIMARY/.dev-worktrees/<feature-name>" -b <branch>

`<branch>` is `feature/<feature-name>` (Standard/Deep), `fix/<feature-name>` (Micro), or
`arch/<feature-name>` (architecture). Top-level cycles branch from `origin/main` (the
`worktree add -b` above; `origin/main` is current because of the fetch). For a **nested**
cycle (Step 1's Nesting Detection found a parent), point the new branch at the parent's
HEAD instead — immediately after the worktree is created:

    git -C "$PRIMARY/.dev-worktrees/<feature-name>" reset --hard <parent-branch>

(read `<parent-branch>` from the parent's `state.json.branch`).

Set `WORKDIR="$PRIMARY/.dev-worktrees/<feature-name>"`. All artifacts and git commands for
the rest of this cycle run under `$WORKDIR` (`git -C "$WORKDIR" …`). The user's primary
checkout and shell location are never switched.

If `git worktree add` fails (path exists, disk, etc.), STOP and report the error — never
fall back to `git checkout -b` in the primary tree.
```

- [ ] **Step 2: Set `worktreePath` in the state.json init note**

Change L191 ("Set `worktreePath` to the worktree's path if the Worktree Offer above created one (or `null` if working in-place).") to:

```markdown
Set `worktreePath` to `".dev-worktrees/<feature-name>"` (the worktree created above — always set for new cycles).
```

- [ ] **Step 3: Route the state.json commit through WORKDIR**

Change the commit block (L194–197) to:

```bash
git -C "$WORKDIR" add docs/dev/<feature-name>/state.json
git -C "$WORKDIR" commit -m "spec: initialize /dev session for <feature-name>"
```

Also add a one-line note that all subsequent spec commits (spec.md etc.) use `git -C "$WORKDIR"`.

- [ ] **Step 4: Verify**

```bash
grep -n 'worktree add' plugins/dev/skills/spec/SKILL.md
grep -n 'EnterWorktree' plugins/dev/skills/spec/SKILL.md   # expect: no matches
grep -n 'git checkout -b' plugins/dev/skills/spec/SKILL.md  # expect: no matches
```
Expected: `worktree add` present; `EnterWorktree` and `git checkout -b` gone from spec.

- [ ] **Step 5: Commit**

```bash
git add plugins/dev/skills/spec/SKILL.md
git commit -m "dev:spec — create per-cycle worktree unconditionally (raw git, no shared-tree fallback)"
```

---

## Task 3: `dev:fix` — worktree instead of `git checkout -b`

**Files:**
- Modify: `plugins/dev/skills/fix/SKILL.md` (Step 3 "Set Branch Name", ~L74–83)

**Interfaces:**
- Consumes: Task 2's worktree-creation pattern; the fix branch name `fix/ENG-123-<short-title>`.
- Produces: same as spec — a worktree + `worktreePath`, so the cycle continues into the normal spec flow already isolated.

- [ ] **Step 1: Replace the plain checkout**

Replace the code block at L83 (`git checkout -b fix/ENG-123-<short-title>`) with:

```bash
PRIMARY=$(dirname "$(git rev-parse --git-common-dir)")
git -C "$PRIMARY" fetch origin
git -C "$PRIMARY" worktree add "$PRIMARY/.dev-worktrees/ENG-123-<short-title>" -b fix/ENG-123-<short-title>
# WORKDIR="$PRIMARY/.dev-worktrees/ENG-123-<short-title>" for the rest of the cycle
```

Add a sentence: "This mirrors `dev:spec` Step 6 — the cycle is isolated in its own worktree from the start; `worktreePath` is recorded when spec initializes state.json. No shared-tree fallback."

- [ ] **Step 2: Verify**

```bash
grep -n 'worktree add' plugins/dev/skills/fix/SKILL.md
grep -n 'git checkout -b' plugins/dev/skills/fix/SKILL.md   # expect: no matches
```

- [ ] **Step 3: Commit**

```bash
git add plugins/dev/skills/fix/SKILL.md
git commit -m "dev:fix — isolate fix cycles in a worktree (mirror dev:spec)"
```

---

## Task 4: `dev:build` — WORKDIR resolution + `git -C`

**Files:**
- Modify: `plugins/dev/skills/build/SKILL.md`

**Interfaces:**
- Consumes: `worktreePath` from state.json (Task 2); the canonical WORKDIR block (Global Constraints).
- Produces: nothing new — build commits now land in `$WORKDIR`.

- [ ] **Step 1: Insert the canonical WORKDIR block** immediately after the skill's Announce/Purpose opening (before "Step 1"/artifact gate). Paste the block verbatim from Global Constraints.

- [ ] **Step 2: Route every git command through `$WORKDIR`.** Replace each bare git invocation with the `-C "$WORKDIR"` form. Locate them:

```bash
grep -n 'git ' plugins/dev/skills/build/SKILL.md
```
Edit these known spots (feature path): the per-task commit (`git add … / git commit -m "[task N]…"`), the arch-doc commit (L84–85), the plan-update commit (L105), and the build-complete commit (L124–125). Each becomes `git -C "$WORKDIR" add …` / `git -C "$WORKDIR" commit …`. The `git diff`/recent-commits debugging reference (L59) becomes `git -C "$WORKDIR" diff`.

- [ ] **Step 3: Verify**

```bash
grep -nE '^\s*git (add|commit|diff)' plugins/dev/skills/build/SKILL.md   # expect: none WITHOUT -C
grep -c 'git -C "\$WORKDIR"' plugins/dev/skills/build/SKILL.md            # expect: > 0
```
Expected: no bare `git add/commit/diff` remain; `git -C "$WORKDIR"` occurrences present.

- [ ] **Step 4: Commit**

```bash
git add plugins/dev/skills/build/SKILL.md
git commit -m "dev:build — resolve WORKDIR, route git through the cycle worktree"
```

---

## Task 5: `dev:plan` + `dev:shape` — WORKDIR resolution + `git -C`

**Files:**
- Modify: `plugins/dev/skills/plan/SKILL.md`
- Modify: `plugins/dev/skills/shape/SKILL.md`

**Interfaces:**
- Consumes: `worktreePath`; canonical WORKDIR block.
- Produces: nothing new.

- [ ] **Step 1: Insert the canonical WORKDIR block** after the Announce line in each of `plan/SKILL.md` and `shape/SKILL.md`.

- [ ] **Step 2: Route git through `$WORKDIR`** in both files:

```bash
grep -n 'git ' plugins/dev/skills/plan/SKILL.md plugins/dev/skills/shape/SKILL.md
```
Replace each bare `git add/commit` (the artifact-commit steps that write `plan.md` / `design.md` and update state.json) with `git -C "$WORKDIR" …`.

- [ ] **Step 3: Verify**

```bash
grep -nE '^\s*git (add|commit)' plugins/dev/skills/plan/SKILL.md plugins/dev/skills/shape/SKILL.md  # expect: none bare
```

- [ ] **Step 4: Commit**

```bash
git add plugins/dev/skills/plan/SKILL.md plugins/dev/skills/shape/SKILL.md
git commit -m "dev:plan, dev:shape — resolve WORKDIR, route git through the cycle worktree"
```

---

## Task 6: `dev:validate` — WORKDIR + diff range through the worktree

**Files:**
- Modify: `plugins/dev/skills/validate/SKILL.md` (diff L43; fix-commit L110; state commit L178–179)

**Interfaces:**
- Consumes: `worktreePath`; canonical WORKDIR block.
- Produces: nothing new.

- [ ] **Step 1: Insert the canonical WORKDIR block** after the Announce line.

- [ ] **Step 2: Route the diff and commits through `$WORKDIR`.** The diff line (L43) becomes `git -C "$WORKDIR" diff BASE_SHA..HEAD_SHA`; the loop-fix commit (L110) and the final state/validation commit (L178–179) become `git -C "$WORKDIR" add …` / `git -C "$WORKDIR" commit …`. The subagents still receive **only the diff text + spec + plan as data** — that instruction is unchanged; only how the driver computes the diff changes.

- [ ] **Step 3: Verify**

```bash
grep -nE '^\s*git (add|commit|diff)' plugins/dev/skills/validate/SKILL.md   # expect: none bare
```

- [ ] **Step 4: Commit**

```bash
git add plugins/dev/skills/validate/SKILL.md
git commit -m "dev:validate — resolve WORKDIR, compute diff and commits in the cycle worktree"
```

---

## Task 7: `dev:pr` — WORKDIR + explicit-`--head` gh

**Files:**
- Modify: `plugins/dev/skills/pr/SKILL.md` (changelog commit Step 3; push + `gh pr create` Step 4; state commit Step 5)

**Interfaces:**
- Consumes: `worktreePath`; canonical WORKDIR block; `state.json.branch`, target branch resolution.
- Produces: `pr_url` / `pr_number` in state.json (unchanged); a PR opened with the correct head.

- [ ] **Step 1: Insert the canonical WORKDIR block** after the Announce line.

- [ ] **Step 2: Route the changelog + state commits and the branch push through `$WORKDIR`:**
`git -C "$WORKDIR" add <changelog>` / `commit`; `git -C "$WORKDIR" push -u origin <branch-name>`.

- [ ] **Step 3: Make `gh pr create` cwd-independent.** Replace the `gh pr create` invocation so it runs inside the worktree and pins the head explicitly:

```bash
( cd "$WORKDIR" && gh pr create \
    --title "<feature-name>: [one-sentence summary from spec Intent]" \
    --body "[PR description from Step 2]" \
    --base "<target-branch>" \
    --head "<branch-name>" )
```

Add a one-line rationale: "`gh` has no `-C` flag; running it inside `$WORKDIR` with an explicit `--head` avoids the wrong-head bug where `gh` infers the head from whatever branch the shared tree happens to be on."

- [ ] **Step 4: Route the nested parent-branch push (if present)** through `git -C "$WORKDIR" push origin <parent-branch>`.

- [ ] **Step 5: Verify**

```bash
grep -n 'gh pr create' plugins/dev/skills/pr/SKILL.md
grep -n -- '--head' plugins/dev/skills/pr/SKILL.md          # expect: present
grep -nE '^\s*git (add|commit|push)' plugins/dev/skills/pr/SKILL.md   # expect: none bare
```

- [ ] **Step 6: Commit**

```bash
git add plugins/dev/skills/pr/SKILL.md
git commit -m "dev:pr — WORKDIR routing + explicit --head gh pr create"
```

---

## Task 8: `dev:done` — single-worktree merge/main-commit/teardown lifecycle

**Files:**
- Modify: `plugins/dev/skills/done/SKILL.md` (Merge Step 2; Product Plan Step 3; Registry Step 4; Decision Log Step 5; Reflect Step 6; Clean Up Step 7)

**Interfaces:**
- Consumes: `worktreePath`; `state.json.branch`, `parentFeature`, `product_plan`, PR number.
- Produces: merged PR, `main`/parent-branch commits, removed worktree.

- [ ] **Step 1: Insert the canonical WORKDIR block** after the Announce line. Define `INTEGRATION` = `main` if `parentFeature` is null, else the parent feature's branch (`docs/dev/<parentFeature>/state.json.branch`).

- [ ] **Step 2: Rewrite Merge (Step 2) as flip-then-merge:**

```bash
git -C "$WORKDIR" fetch origin
git -C "$WORKDIR" checkout "$INTEGRATION"          # move the worktree off the feature branch
gh_merge() { ( cd "$WORKDIR" && gh pr merge <pr-number> --merge --delete-branch --head "<branch-name>" ); }
gh_merge
git -C "$WORKDIR" pull --ff-only origin "$INTEGRATION"   # now includes the merge
```

Keep the existing "if it can't be auto-merged, STOP" guard, but check it before the flip (query `gh pr view <n> --json mergeable,mergeStateStatus`); only flip + merge when clean.

- [ ] **Step 3: Route every post-merge commit (Steps 3–5, 7) through `$WORKDIR` on `$INTEGRATION`, with rebase-on-reject.** Define one push helper and use it for each push:

```bash
push_integration() {
  git -C "$WORKDIR" push origin "$INTEGRATION" || {
    git -C "$WORKDIR" pull --rebase origin "$INTEGRATION" && git -C "$WORKDIR" push origin "$INTEGRATION"
  }
}
```
Product-plan commit (Step 3), Component Registry commit (Step 4), decision-log commit (Step 5), and cleanup commit (Step 7) each become `git -C "$WORKDIR" add …` / `git -C "$WORKDIR" commit …` / `push_integration`. The decision log and its pre-merge-SHA note still reference `state.json` values as today.

- [ ] **Step 4: dev:reflect (Step 6) writes to `$WORKDIR`.** Pass `$WORKDIR/docs/decisions/<file>.md` as the decision-log path so its appended `## Retrospective` and commit land in the worktree on `$INTEGRATION`, pushed via `push_integration`.

- [ ] **Step 5: Rewrite Clean Up (Step 7) teardown.** After the cleanup commit is pushed, remove the worktree — `done` now owns teardown:

```bash
git -C "$WORKDIR" ... # (cleanup commit already done above)
# then, from the primary checkout, remove the worktree:
PRIMARY=$(dirname "$(git -C "$WORKDIR" rev-parse --git-common-dir)")
git -C "$PRIMARY" worktree remove --force "$WORKDIR"
git -C "$PRIMARY" worktree prune
```

Replace the old L125–129 block (the `git branch -d` + "defer to ExitWorktree" note): the remote+local feature branch was already deleted by `--delete-branch` in Step 2, and the worktree is removed here. Delete the `worktreePath`-conditional branch-deletion paragraph and the `ExitWorktree` deferral entirely. Add: "For a **legacy in-place cycle** (`worktreePath` null), there is no worktree to remove — skip the removal and, as before, delete the local branch with `git -C \"$PRIMARY\" branch -d <branch>`."

- [ ] **Step 6: Verify**

```bash
grep -n 'worktree remove' plugins/dev/skills/done/SKILL.md      # expect: present
grep -n 'ExitWorktree' plugins/dev/skills/done/SKILL.md          # expect: no matches
grep -n -- '--head' plugins/dev/skills/done/SKILL.md             # expect: present on gh pr merge
grep -nE '^\s*git (add|commit|push|checkout|pull|fetch)' plugins/dev/skills/done/SKILL.md  # expect: none bare
```

- [ ] **Step 7: Commit**

```bash
git add plugins/dev/skills/done/SKILL.md
git commit -m "dev:done — single-worktree merge/main-commit/teardown lifecycle"
```

---

## Task 9: `dev:dev` — discovery scan + resume/restart/abandon through worktrees

**Files:**
- Modify: `plugins/dev/skills/dev/SKILL.md` (Step 3 scan L39; Restart/Abandon L62–63; artifact-path resume table L151)

**Interfaces:**
- Consumes: `.dev-worktrees/*` layout; `worktreePath`.
- Produces: correct in-progress detection and WORKDIR for resumed stages.

- [ ] **Step 1: Broaden the in-progress scan (L39).** Replace "Scan for `docs/dev/*/state.json` files in the current project." with:

```markdown
Compute `PRIMARY=$(dirname "$(git rev-parse --git-common-dir)")`, then scan for state.json in
both locations: `$PRIMARY/.dev-worktrees/*/docs/dev/*/state.json` (active worktree cycles) and
`$PRIMARY/docs/dev/*/state.json` (legacy in-place cycles). Deduplicate by feature name.
```

- [ ] **Step 2: Resume computes WORKDIR.** In the Resume choice (L61), add: "Resume resolves `WORKDIR` via the canonical block (worktree first, else primary) before proceeding to the stage — the user is never asked to `cd`."

- [ ] **Step 3: Restart/Abandon remove the worktree.** Update L62–63 so both also tear down the worktree when `worktreePath` is set:

```markdown
- **Restart:** delete the cycle's state.json and `docs/dev/<feature>/`, then if `worktreePath` is
  set, `git -C "$PRIMARY" worktree remove --force "$PRIMARY/<worktreePath>"` and `worktree prune`;
  start over from spec.
- **Abandon:** same worktree removal; the feature branch was checked out only in that worktree, so
  removing it frees the branch — then `git -C "$PRIMARY" branch -D <branch>`; exit.
```

- [ ] **Step 4: Verify**

```bash
grep -n '.dev-worktrees' plugins/dev/skills/dev/SKILL.md          # expect: present in scan
grep -n 'worktree remove' plugins/dev/skills/dev/SKILL.md         # expect: present in restart/abandon
```

- [ ] **Step 5: Commit**

```bash
git add plugins/dev/skills/dev/SKILL.md
git commit -m "dev:dev — discover worktree cycles, tear down on restart/abandon"
```

---

## Task 10: `dev:autopilot` — drop the moot worktree-offer note

**Files:**
- Modify: `plugins/dev/skills/autopilot/SKILL.md` (Step 2 worktree-offer note, ~L52)

**Interfaces:**
- Consumes: nothing.
- Produces: nothing — cleanup only.

- [ ] **Step 1: Replace the auto-accept note.** Change the L52 line ("**Worktree offer: auto-accept.** …") to:

```markdown
**Worktrees are automatic.** Every cycle is isolated in its own worktree by `dev:spec` Step 6 —
there is no offer to accept. Autopilot inherits this with no special handling; any git it runs uses
`git -C "$WORKDIR"` per the canonical WORKDIR resolution.
```

- [ ] **Step 2: Verify**

```bash
grep -n 'auto-accept' plugins/dev/skills/autopilot/SKILL.md   # expect: no matches
grep -n 'Worktrees are automatic' plugins/dev/skills/autopilot/SKILL.md  # expect: present
```

- [ ] **Step 3: Commit**

```bash
git add plugins/dev/skills/autopilot/SKILL.md
git commit -m "dev:autopilot — worktrees are automatic; drop the offer note"
```

---

## Task 11: Dogfood verification + cross-skill consistency sweep

**Files:** none modified (verification only; fix inline if a check fails).

**Interfaces:**
- Consumes: all prior tasks.
- Produces: evidence the invariants hold.

- [ ] **Step 1: Real worktree isolation exercise.** From this repo root, run the exact commands `dev:spec` now prescribes and confirm the invariants:

```bash
PRIMARY=$(dirname "$(git rev-parse --git-common-dir)")
git -C "$PRIMARY" worktree add "$PRIMARY/.dev-worktrees/_probe" -b _probe origin/main
# Invariant A: gitignore keeps primary status clean
git -C "$PRIMARY" status --porcelain | grep -q '.dev-worktrees' && echo "FAIL: worktree not ignored" || echo "OK: ignored"
# Invariant B: git-common-dir discovery works FROM INSIDE the worktree
( cd "$PRIMARY/.dev-worktrees/_probe" && test "$(dirname "$(git rev-parse --git-common-dir)")" = "$PRIMARY" && echo "OK: PRIMARY derives from inside worktree" )
# Invariant C: nested worktree inside repo does not confuse the primary tree
git -C "$PRIMARY" worktree list
```
Expected: `OK: ignored`, `OK: PRIMARY derives…`, and `worktree list` shows both.

- [ ] **Step 2: Tear down the probe.**

```bash
git -C "$PRIMARY" worktree remove --force "$PRIMARY/.dev-worktrees/_probe"
git -C "$PRIMARY" worktree prune
git -C "$PRIMARY" branch -D _probe
```
Expected: clean; `git worktree list` shows only real worktrees.

- [ ] **Step 3: Consistency sweep across all edited skills.**

```bash
# No stage should still fall back to a shared-tree checkout or depend on the harness tool:
grep -rn 'EnterWorktree\|ExitWorktree' plugins/dev/skills/        # expect: no matches
grep -rn 'git checkout -b' plugins/dev/skills/                    # expect: no matches
# Every stage that commits should do so via -C "$WORKDIR" (spot-check no bare add/commit remain):
grep -rnE '^\s*git (add|commit) ' plugins/dev/skills/             # expect: no matches
# WORKDIR convention present in each stage:
for f in build plan shape validate pr done; do
  grep -q 'Resolve the working directory' plugins/dev/skills/$f/SKILL.md && echo "$f OK" || echo "$f MISSING WORKDIR block"
done
```
Expected: no `EnterWorktree`/`ExitWorktree`, no `git checkout -b`, no bare `git add/commit`; all six stages print `OK`.

- [ ] **Step 4: Fix any failures inline**, re-run the failing check, then commit if anything changed:

```bash
git add -A plugins/dev/skills/
git commit -m "dev — consistency sweep for worktree isolation" || echo "nothing to fix"
```

---

## Self-Review (completed by plan author)

- **Spec coverage:** §1 layout→Task 1; §2 WORKDIR/cwd-independence→canonical block + Tasks 4–10; §3 discovery→Task 9; §4 spec worktree→Task 2; §5 build/shape/plan/validate→Tasks 4–6; §6 gh→Task 7; §7 done lifecycle→Task 8; §8 autopilot/fix→Tasks 3,10; §9 init→Task 1; edge cases (nested→Tasks 2/8; in-repo gitignore→Tasks 1/11; concurrent-done race→Task 8 rebase helper; resume-from-elsewhere→Task 9/canonical block; add-fails→Task 2; legacy null→every task's fallback) all covered; verification plan→Task 11.
- **Placeholder scan:** none — every edit shows exact old/new text or an exact grep-located target with the replacement form.
- **Type/name consistency:** `PRIMARY`, `WORKDIR`, `INTEGRATION`, `worktreePath`, `worktree_root`, `.dev-worktrees` used identically across all tasks; the canonical WORKDIR block is defined once and reused verbatim.

---

## Post-implementation corrections (final whole-branch review)

The opus whole-branch review caught three **plan-level** defects that grep-only task
verification missed (all fixed in commit `640fe5d`, empirically dogfooded):

1. **Task 8 Step 2 — `gh pr merge --head` is invalid.** `--head` exists on `gh pr create`,
   not `gh pr merge` (errors `unknown flag`). Removed; the positional `<pr-number>`
   identifies the PR.
2. **Task 8 Step 2 — flipping the worktree with `git checkout <integration>` collides.**
   `<integration>` (`main`) is normally checked out in the primary tree, and git forbids the
   same branch in two worktrees, so the checkout fails on the common path. Fixed: worktree
   cycles use `git checkout --detach` (free the feature branch) then
   `git checkout --detach origin/<integration>` (position at the merged tip), and push via
   `git push origin HEAD:<integration>`. Legacy in-place cycles keep the plain branch
   checkout (no second worktree to collide with). Verified: `checkout --detach origin/main`
   succeeds while `main` is live in the primary; `push HEAD:main` refspec targets `main`.
3. **Tasks 2 & 3 — `git worktree add -b <branch>` had no start-point.** It defaults to the
   primary's current HEAD, so a top-level cycle started while the primary is on another
   branch inherits the wrong base. Fixed: append `origin/main`. Verified the new branch
   bases on `origin/main` regardless of the primary tree's branch.

Also handled: the mergeability guard now tolerates GitHub's async `UNKNOWN` result.

**Known minor limitations (accepted, not blocking):** `worktree_root` config is written by
`dev:init` but unused (stages hardcode `.dev-worktrees`, which equals the default);
`dev:reflect` invoked standalone *after* `dev:done` has torn down the cycle can't resolve a
WORKDIR (the artifacts are gone) — the `done`-invoked path is fine. The **product-plan
pre-worktree commit** (`spec` L62-63, committed to `main`/parent from the primary tree
before the cycle worktree exists) remains a deferred design question for product-scale
cycles — it needs the same detached-HEAD-or-ephemeral treatment as `dev:done`.
