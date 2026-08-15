---
name: fix
description: "The fast path — a grounded change from request to open PR in one unattended run, with no cycle artifacts. Use when the user wants something done rather than specified: fix this, change this, rename that, drop the redundant prefix, update the frontmatter, make this consistent, just do this, small change, quick fix, one-line fix, tweak, open a PR for this. Also handles the merge tail: /dev:fix merge merges that PR and cleans up. Escalates to /dev when the request carries 2+ unresolved decisions. For a full seven-stage cycle with approval gates use /dev; for a Linear issue use /dev:linear."
---

# dev:fix — The Fast Path

**Announce:** "I'm using dev:fix to run this as a fast-path change."

## Purpose

`/dev`'s seven stages are correctly weighted for a real feature and absurdly heavy for a one-line
fix. This lane is the other weight: read the actual files, decide whether the request is safe to
carry alone, make the change, verify it, open a PR — then stop.

It produces **no cycle artifacts**. No worktree, no `spec.md`, no `state.json`, no `validation.md`,
no decision log. That is the feature, not an omission. Rigor here comes from grounding before
acting, running the suite, verifying what the suite cannot reach, capturing what was deferred, and
reporting honestly — the same standard carried by judgment instead of by paperwork.

**Two invocations, and the second is deliberate:**

- `/dev:fix "<what you want done>"` — the lane. Runs unattended to an open PR, then stops.
- `/dev:fix merge` — the tail. Merges that PR and cleans up.

Nothing irreversible happens without the second invocation. The PR is the checkpoint.

## Resolve the working directory (do this first)

This lane operates on the **primary checkout** — it never creates a worktree. Compute it without
relying on the shell's current directory, so the lane runs correctly from anywhere in the repo:

```bash
GIT_COMMON=$(git rev-parse --git-common-dir) || { echo "Not a git repository."; exit 1; }
PRIMARY=$(cd "$(dirname "$GIT_COMMON")" && pwd)
if [ -z "$PRIMARY" ]; then echo "Could not resolve the primary checkout."; exit 1; fi
```

The first two lines are the derivation every `dev` stage header uses (`build/SKILL.md:26-27`). The
third is the non-empty guard **none of those 13 shell sites carries** — the gap
`docs/backlog/debt-primary-cd-failure-unchecked.md` records. This site carries it, so adding the
lane does not grow that item's count to 14. Do not "simplify" the guard away to match the others.

For the rest of this lane: run every git command as `git -C "$PRIMARY" …`. Never `cd`.

## Resolve the default branch

Never assume `main`:

```bash
DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null) \
  || DEFAULT_BRANCH=""
if [ -z "$DEFAULT_BRANCH" ]; then
  DEFAULT_BRANCH=$(git -C "$PRIMARY" symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||')
fi
if [ -z "$DEFAULT_BRANCH" ]; then echo "Could not determine the default branch."; exit 1; fi
```

`dev:done` hardcodes `main` (`done/SKILL.md:26`). The lane deliberately does not copy that — it runs
across several repos, and not all of them use `main`.

## Step 1: Parse the argument

**The argument is the bare token `merge` and nothing else → tail mode** (Step 7).

Any longer argument — **including one whose first word is `merge`** — is a free-text lane request.
`/dev:fix merge the two config loaders` is a request to merge two config loaders, not a request to
merge a PR. Merging is the one irreversible step in this skill, so the token that triggers it is
exact rather than prefix-matched.

No argument at all → ask what the user wants done. Do not guess.

## Step 2: Preflight

**The first three checks run in both modes**, before anything is created, in this order.

1. **`gh` available and authenticated** — `gh auth status`. On failure STOP with the reason. Checked
   first because it is the cheapest and neither mode can finish without it.
2. **Clean working tree** — `git -C "$PRIMARY" status --porcelain`. If anything is modified, STOP and
   name the files. Never stash, never branch over uncommitted work.
3. **No legacy in-place `/dev` cycle occupying the primary checkout** — scan
   `$PRIMARY/docs/dev/*/state.json` for a cycle whose `worktreePath` is `null` and whose `stage` is
   not `"done"`. If one exists, STOP and name that feature.

   Check 2 does **not** catch this: a legacy cycle commits its artifacts as it goes, so it leaves the
   tree clean while still occupying the primary checkout on its own feature branch. A modern cycle
   lives in `.dev-worktrees/` and does not contend — it must not trigger this refusal.

**The fourth check is lane mode only:**

4. **The current branch has no open PR** —
   `gh pr list --head "$(git -C "$PRIMARY" branch --show-current)" --state open`. If one exists,
   STOP and report it, offering the two exits: `/dev:fix merge`, or switch branches manually.

   This is the lane's own leftover state. The lane stops at PR and leaves `$PRIMARY` on that feature
   branch, so a second *lane* invocation would otherwise branch off `$DEFAULT_BRANCH` and strand the
   first PR — which the tail, defined as operating on the current branch, could then no longer reach.

   **In tail mode this same condition is the expected precondition, not a refusal.** Skip check 4
   entirely and go to Step 7. Running it in both modes would make `/dev:fix merge` always STOP while
   offering `/dev:fix merge` as the exit — an infinite loop.

## Step 3: Ground

Read the actual files. Verify every as-is claim the request makes against what is really there.

**No edit may come from a remembered mental model of the code.** If the request says "the frontmatter
has a redundant prefix," open the frontmatter. If it names a set ("all the dev skills"), enumerate
that set by sweep, not by recall — a set named from memory is the most common way a mechanical
change misses a file.

Record what was read and what each file confirmed or contradicted. This becomes the "What I
verified" section of the PR body.

**Nothing to change.** If grounding shows the request is already satisfied, say so plainly, create no
branch, and open no PR. An empty PR is worse than no PR.

## Step 4: Triage

Before changing anything, count the decisions this lane would be making **for** the user — points
where a reasonable person could choose differently.

| Decisions | Behavior |
|---|---|
| 0 | Proceed, **regardless of size**. A mechanical 14-file rename qualifies. |
| 1 | Ask it inline, then proceed. One question is cheaper than a whole cycle. |
| 2+ | **Stop.** List the decisions, print the `/dev` command, and offer to proceed if the user answers them here. |

**Size is deliberately not the trigger.** A 14-file frontmatter rename where the convention is
already established is trivially safe. A one-file change with two defensible answers is not.

**Counting rule.** A decision is countable only if **all three** hold:

- (a) the request text does not determine it,
- (b) no existing repo convention determines it, and
- (c) reversing it later would require editing files this change touches.

A choice already settled by an established convention counts as **zero** — that is what lets a large
mechanical change proceed. When genuinely unsure whether something is countable, **count it**: the
cost of a false escalation is one `/dev` command; the cost of a false proceed is a decision made on
the user's behalf that they never saw.

**What distinguishes the 1 row from the 2+ row.** Both can end in proceeding, so the observable
difference matters:

- **1 decision** — ask inline and proceed in the same turn. Do not print the `/dev` command.
- **2+ decisions** — **always print the `/dev` command** before asking, and never begin changing
  files in the same turn as the question.

That printed command is the marker that the escalation actually happened.

Worked examples:

- *"drop the redundant plugin prefix from the dev skill names"* — 14 files, mechanical, and the bare-
  prefix convention is already established elsewhere in the repo. **0 decisions. Proceed.**
- *"add caching to the config loader"* — which cache, and invalidated when? Neither is determined by
  the request or by convention, and both would require re-editing the loader to reverse.
  **2 decisions. Stop.**

## Step 5: Branch

**Resolve the final name before creating anything.**

Name the branch `fix/<kebab-summary>`, where `<kebab-summary>` describes the change in 2–4 words. The
allowlist applies to `<kebab-summary>` **alone**, not to the full branch name — a prefixed `fix/…`
can never match the anchored `^[a-z0-9][a-z0-9-]*$` because the `/` would be collapsed. Normalize by
`dev:spec` Step 6's construction (`spec/SKILL.md:135`): lowercase, collapse every run of characters
outside `[a-z0-9]` to a single `-`, strip leading and trailing `-`. If the result is empty, ask for a
name rather than proceeding.

**Collision check — both, before creating the branch:**

```bash
git -C "$PRIMARY" rev-parse --verify "fix/<kebab-summary>" >/dev/null 2>&1          # local
git -C "$PRIMARY" ls-remote --exit-code --heads origin "fix/<kebab-summary>" >/dev/null 2>&1  # remote
```

On either hit, disambiguate with a `-2`, `-3` suffix. Never reuse an existing branch, and never
force-push over one.

Then create it from the freshly fetched default branch:

```bash
git -C "$PRIMARY" fetch origin
git -C "$PRIMARY" checkout -b "fix/<kebab-summary>" "origin/$DEFAULT_BRANCH"
```

## Step 6: Change, Verify, PR

### Change

Make the minimal edit that does the job. Commit it with a conventional-commit message.

**Mid-flight discovery.** If implementation reveals a real fork that grounding missed — a decision
that would have been countable at Step 4 — **stop and escalate at that point** rather than deciding
to keep momentum. The Step 4 count is a prediction, and a prediction that turns out wrong is a reason
to stop, not a commitment to honor.

On that stop: **commit the partial work to the feature branch** and report the branch name and what
is on it. Open no PR. Do not leave the tree dirty (Step 2's check would then refuse the follow-up
invocation with a confusing "modified files" message) and do not revert (that discards real work over
a question).

### Verify

Run the repo's test suite if one exists. **Detect it rather than assuming** — `package.json` scripts,
`pytest`, a `Makefile` target, a `test_*.py` convention, `cargo test`, `go test ./...`.

Then verify by whatever means the change actually requires, **including means the suite cannot
reach**: reading rendered output, walking a procedure manually against real files, checking a page in
a browser. Record each result verbatim for the PR body.

**No suite in the repo?** Say so explicitly in the PR body rather than implying tests passed. An
absent suite **raises** the bar on other verification; it does not lower the bar overall.

### The rigor floor

The lane may never skip these, and the PR body says which applied:

- Grounded before acting — no edit from a remembered mental model of the code.
- Ran the project's test suite when one exists.
- Never claimed unverified success; if something could not be verified, said so.
- Captured anything deferred to `docs/backlog/` rather than dropping it.
- Reported what it decided on the user's behalf.

### Deferred-work capture

Anything noticed and not done goes to `docs/backlog/` per `../../references/tech-debt.md`. The lane
is a **consumer** of that schema and must not fork it.

- Per §P7's writer-side rule, create `docs/backlog/` (and `closed/`) when absent, then write. Degrade
  silently rather than erroring if the store cannot be written.
- The lane runs across several repos, so a `scope: plugin` item captured **off** the plugin repo
  routes per **§P9** — follow that section rather than restating it, including its degrade-to-local
  branch (`routing: pending`) so a failed route buffers instead of dropping.

### PR

```bash
git -C "$PRIMARY" push -u origin "fix/<kebab-summary>"
( cd "$PRIMARY" && gh pr create \
    --title "<one-sentence summary>" \
    --body "<body below>" \
    --base "$DEFAULT_BRANCH" \
    --head "fix/<kebab-summary>" )
```

The `-C "$PRIMARY"` on the push is required, not optional — the lane may be invoked from anywhere in
the repo, including from inside a `.dev-worktrees/<feature>` tree. `gh` has no `-C` flag, so it runs
inside `$PRIMARY` with an explicit `--head`; without that it infers the head from whatever branch the
tree happens to be on.

**PR body — four required sections:**

```markdown
## What changed
[the edit, concretely]

## Why
[the request, and what grounding confirmed]

## What was verified
[suite result verbatim, or "no test suite in this repo"; plus whatever else was checked
 and how — and anything that could NOT be verified, stated plainly]

## Decisions made for you
[the 1-decision question and its answer, or "none"]
```

**This mirrors `dev:pr` Step 4 (`pr/SKILL.md:115-140`), which is canonical.** It is duplicated
because the lane produces no `validation.md` and so cannot enter that stage — every `/dev` stage
gates on the prior stage's artifact, and a lane that writes no artifacts cannot enter the chain
anywhere. A change to either side should be reflected at the other. `dev:pr` Step 4 carries the
matching pointer back to here.

### Stop

Report the PR URL and end the turn. **The PR is the checkpoint — the lane never merges.**

## Step 7: The merge tail (`/dev:fix merge`)

### Resolve the PR

The target is the open PR for the branch currently checked out in `$PRIMARY`. If that branch has no
open PR, or if more than one resolves, **stop and report** rather than guessing.

### Check mergeability

```bash
gh pr view <pr-number> --json mergeable,mergeStateStatus
```

GitHub computes mergeability asynchronously, so immediately after PR creation the result can be
`UNKNOWN`/`null` — if so, wait a few seconds and re-query. **Only STOP on a definite conflicting or
blocked state, never on `UNKNOWN`.** Never force, and never delete a branch whose PR did not merge.

### Merge, then clean up

```bash
( cd "$PRIMARY" && gh pr merge <pr-number> --merge )
git -C "$PRIMARY" checkout "$DEFAULT_BRANCH"
git -C "$PRIMARY" pull --ff-only origin "$DEFAULT_BRANCH"
delete_feature_branch || exit 1
```

Ordering matters: the local branch cannot be deleted while it is checked out, so the checkout comes
first.

Branch deletion goes through one guarded helper that **refuses to delete anything unless the PR
actually merged** — so a `gh pr merge` that failed (branch protection, a check that flipped, stale
mergeability, a transient API error) can never delete an unmerged branch:

```bash
delete_feature_branch() {
  if [ "$(gh pr view <pr-number> --json state -q .state)" != "MERGED" ]; then
    echo "STOP: PR is not MERGED — leaving the feature branch intact. Resolve, then re-run /dev:fix merge."
    return 1
  fi
  git -C "$PRIMARY" push origin --delete <branch> 2>/dev/null || {
    git -C "$PRIMARY" ls-remote --exit-code --heads origin <branch> >/dev/null 2>&1 \
      && echo "WARNING: remote branch '<branch>' still exists but could not be deleted (protected or insufficient token scope) — delete it manually." \
      || true
  }
  git -C "$PRIMARY" branch -D <branch> 2>/dev/null || true
}
```

**Why not `gh pr merge --delete-branch`?** `gh`'s `--delete-branch` runs its cleanup after the
server-side merge and reads the current branch to do it, which makes it fragile in exactly the states
this lane can be in. `gh pr merge --merge` on its own never reads the current branch; deleting both
branches with explicit git plumbing is deterministic regardless of what `HEAD` points at. Do not
re-add `--delete-branch`.

### Report

State all four end states plainly: PR merged, remote branch gone, local branch gone, primary checkout
on `$DEFAULT_BRANCH` at the merged tip with a clean tree.

**This mirrors `dev:done` Step 2 (`done/SKILL.md:56-131`), which is canonical.** It is duplicated
because the lane writes no `state.json` and so cannot enter that stage. A change to either side
should be reflected at the other. `dev:done` Step 2 and Step 7 carry the matching pointers back to
here. Two branches of the canonical are **deliberately absent**: its detached-HEAD worktree path (the
lane never creates a worktree, so it has only the in-place shape) and its `push_integration` helper
(the lane makes no post-merge commits, so it never pushes to the integration branch).

## Invocation

- `/dev:fix "<what you want done>"` — the lane: ground, triage, branch, change, verify, PR, stop
- `/dev:fix merge` — the tail: merge that PR, delete both branches, fast-forward, report

For a full seven-stage cycle with approval gates, use `/dev`. For a Linear issue, use `/dev:linear`.
