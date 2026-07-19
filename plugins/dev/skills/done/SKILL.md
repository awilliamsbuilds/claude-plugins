---
name: dev:done
description: "Stage 7 of the /dev workflow. Merges the PR, generates a decision log, invokes dev:reflect, and cleans up the feature branch and working directory. Requires PR URL in state.json."
---

# dev:done — Completion Stage

**Announce:** "I'm using dev:done to merge, document, and close out the cycle."

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

Define `INTEGRATION` — the branch this cycle's post-merge commits land on: `main` if
`state.json.parentFeature` is null; otherwise the parent feature's branch, read from
`docs/dev/<parentFeature>/state.json.branch`.

## Purpose

Close the feature cycle: merge the PR, create a permanent decision log, run the retrospective, and clean up.

## Step 1: Artifact Gate

May be invoked with one or more arguments — a feature slug, a PR URL, or an artifact-path (`validation.md` path) — to derive `<feature>` without requiring it already be known from conversation context. Check in this order, using the first that resolves:
1. A bare slug matching `^[a-z0-9][a-z0-9-]*$` with no `..` segments, where `docs/dev/<slug>/state.json` exists — use it directly as `<feature>`.
2. A GitHub PR URL (`.../pull/<number>`) — parse the PR number, then scan `docs/dev/*/state.json` for one whose `artifacts.pr_number` matches; that directory's name is `<feature>`.
3. An artifact-path matching `docs/dev/<feature>/<artifact>.md`, with `<feature>` matching the same slug pattern and no `..` segments.

If no argument is given, or none of the given arguments resolve, fall back to today's behavior — require `<feature>` already known from conversation context.

Read `docs/dev/<feature>/state.json`. Confirm `artifacts.pr_url` is not null.

If PR URL is missing: STOP — "Done requires an open PR. Run /dev:pr first."

Read once at stage start:
- `docs/dev/<feature>/state.json` — full state including cycle_type, tier, all metrics
- `docs/dev/<feature>/spec.md`
- `docs/dev/<feature>/design.md` (if exists)
- `docs/dev/<feature>/plan.md` (if exists)
- `docs/dev/<feature>/validation.md`

Note the pre-merge commit SHA (used in decision log for artifact archiving).

## Step 2: Merge PR

First, check mergeability without touching the worktree's checkout:

```bash
gh pr view <pr-number> --json mergeable,mergeStateStatus
```

If the PR can't be auto-merged (conflicts or required reviews pending): STOP and display:

```
PR can't be merged automatically. Reason: [conflict / pending reviews].
Resolve in GitHub, then run /dev:done again.
```

GitHub computes mergeability asynchronously, so immediately after PR creation the result can be `UNKNOWN`/`null` — if so, wait a few seconds and re-query; only STOP on a definite conflicting or blocked state, not on `UNKNOWN`.

Only when that check is clean, free the feature branch and position on the integration tip.

Branch deletion is centralized in one guarded helper. It **refuses to delete anything unless the PR actually merged** — so a `gh pr merge` that fails (branch protection, a required check that flipped, stale mergeability, a transient API error) can never delete an unmerged branch. It then removes the remote and local feature branch idempotently (both safe to re-run):

```bash
delete_feature_branch() {
  if [ "$(gh pr view <pr-number> --json state -q .state)" != "MERGED" ]; then
    echo "STOP: PR is not MERGED — leaving the feature branch intact. Resolve, then re-run /dev:done."
    return 1
  fi
  git -C "$WORKDIR" push origin --delete <branch> 2>/dev/null || {     # remote — tolerate already-gone, surface real failures
    git -C "$WORKDIR" ls-remote --exit-code --heads origin <branch> >/dev/null 2>&1 \
      && echo "WARNING: remote branch '<branch>' still exists but could not be deleted (protected or insufficient token scope) — delete it manually." \
      || true                                                          #   ref is gone → nothing to do
  }
  git -C "$PRIMARY" branch -D <branch> 2>/dev/null || true             # local  — freed by the detach; idempotent
}
```

A non-zero return is a **hard STOP** for the stage — do not proceed to Steps 3+ with an unmerged PR. `branch -D` (force) is correct here *because* the helper has already confirmed the PR merged; the branch tip is in `$INTEGRATION`, and `-d`'s merge check would otherwise run against `$PRIMARY`'s possibly-unrelated HEAD and spuriously refuse.

The merge steps differ by cycle type:

**Worktree cycle** (`worktreePath` set — the normal case). Use a detached HEAD so the feature branch can be deleted and commits can be made toward `$INTEGRATION` WITHOUT checking out `$INTEGRATION` (which is usually checked out in the primary tree — git forbids the same branch in two worktrees):

```bash
git -C "$WORKDIR" fetch origin
git -C "$WORKDIR" checkout --detach                       # frees the feature branch; no branch-collision
( cd "$WORKDIR" && gh pr merge <pr-number> --merge )      # merge only — NOT --delete-branch (see note below)
delete_feature_branch || exit 1                           # verifies MERGED, then deletes remote + local; STOP on non-zero
git -C "$WORKDIR" fetch origin
git -C "$WORKDIR" checkout --detach "origin/$INTEGRATION"  # detached at the merged integration tip
```

**Legacy in-place cycle** (`worktreePath` null, `WORKDIR` = the primary tree). There is no second worktree, so a normal branch checkout is safe:

```bash
git -C "$WORKDIR" fetch origin
git -C "$WORKDIR" checkout "$INTEGRATION"
( cd "$WORKDIR" && gh pr merge <pr-number> --merge )      # merge only — NOT --delete-branch (see note below)
delete_feature_branch || exit 1                           # verifies MERGED, then deletes remote + local; STOP on non-zero
git -C "$WORKDIR" pull --ff-only origin "$INTEGRATION"
```

This merges with a merge commit; `delete_feature_branch` then removes the remote and local feature branch — but only after confirming the PR merged.

**Why not `gh pr merge --delete-branch`?** `gh`'s `--delete-branch` runs its branch cleanup *after* the server-side merge and reads the *current* branch to do it. On the worktree cycle's detached HEAD that read fails ("could not determine current branch"), and `gh` aborts **before** deleting the remote branch — leaking both the remote and local branch even though the merge itself succeeded. `gh pr merge --merge` on its own never reads the current branch, so the merge is detached-HEAD-safe; deleting both branches with explicit `git` plumbing is deterministic regardless of what HEAD points at. Do not re-add `--delete-branch`.

All post-merge commits in this stage (Steps 3–5, 7) are made in `$WORKDIR` and pushed to `$INTEGRATION` through one helper, defined once and reused for every push. It pushes via an explicit `HEAD:$INTEGRATION` refspec, which works whether `HEAD` is detached (worktree cycle) or on the branch (legacy):

```bash
push_integration() {
  git -C "$WORKDIR" push origin "HEAD:$INTEGRATION" || {
    git -C "$WORKDIR" fetch origin && git -C "$WORKDIR" rebase "origin/$INTEGRATION" && git -C "$WORKDIR" push origin "HEAD:$INTEGRATION"
  }
}
```

## Step 3: Update Product Plan (if product-scale, top-level or nested)

Determine the governing product plan: if `state.json.parentFeature` is set, it's `docs/dev/<parentFeature>/product-plan.md` (nested); otherwise, if `state.json.product_plan` is not null, it's the top-level `docs/dev/product-plan.md`. If neither applies, skip this step.

For the governing product plan found:
- Read it
- Find this feature's line item (match by feature name)
- Change `- [ ]` to `- [x]`
- Update the header: increment cycles completed count
- Commit (to `$INTEGRATION` — `main` for a top-level plan, the parent feature's own branch for a nested plan, matching wherever that file already lives):

```bash
git -C "$WORKDIR" add <file>
git -C "$WORKDIR" commit -m "chore: mark <feature> complete in product plan"
push_integration
```

## Step 4: Update Component Registry (feature cycles only)

If `cycle_type == "feature"` and the feature added or modified components:
- Read `CLAUDE.md`
- Update the `## Component Registry` table: add new components, update modified ones
- Set "Last updated" date to today
- Commit to `$INTEGRATION`:

```bash
git -C "$WORKDIR" add CLAUDE.md
git -C "$WORKDIR" commit -m "chore: update Component Registry — <feature>"
push_integration
```

For architecture cycles: skip this step.

## Step 5: Generate Decision Log

Write to `$WORKDIR/docs/decisions/YYYY-MM-DD-<feature>.md` (committed to `$INTEGRATION`):

```markdown
# [Feature Name] — Decision Log
*YYYY-MM-DD · Branch: feature/<name> · PR #N*

## What was built
[One sentence from spec Intent.]

## Key decisions
[From spec.md and plan.md — major choices made. Each as: Decision → reason]

## Design choices
[From design.md — UX decisions and copy choices. Each as: UX decision → rationale]
[Omit section if Shape was skipped.]

## Validation notes
- [N] loops run (tier: [micro/standard/deep])
- [List P1/P2s found and how they were resolved]
- [List any P3/Nits accepted as-is]

## Artifacts (archived)
Spec, design, and plan committed at: <pre-merge-sha> on branch feature/<name>
```

```bash
git -C "$WORKDIR" add docs/decisions/YYYY-MM-DD-<feature>.md
git -C "$WORKDIR" commit -m "docs: add decision log for <feature>"
push_integration
```

## Step 6: Run dev:reflect

Invoke `dev:reflect` with the full state context. dev:reflect appends its output as `## Retrospective` to the decision log at `$WORKDIR/docs/decisions/<file>.md`, committing and pushing (via `push_integration`) from `$WORKDIR` on `$INTEGRATION`.

Pass to dev:reflect:
- The full state.json (all metrics)
- The decision log path (`$WORKDIR/docs/decisions/YYYY-MM-DD-<feature>.md`)
- The spec, plan, and validation artifact paths

## Step 7: Clean Up

Delete the feature's working directory (all committed artifacts travel with the branch which is now merged):

```bash
rm -rf "$WORKDIR/docs/dev/<feature>/"
git -C "$WORKDIR" add -A docs/dev/<feature>/
git -C "$WORKDIR" commit -m "chore: clean up /dev working directory for <feature>"
push_integration
```

Then remove the worktree — `done` owns teardown, so this happens now rather than being
deferred. Run from the primary checkout, not `$WORKDIR` (you can't remove a worktree from
inside itself):

```bash
git -C "$PRIMARY" worktree remove --force "$WORKDIR"
git -C "$PRIMARY" worktree prune
```

For a **legacy in-place cycle** (`worktreePath` null), there is no worktree to remove — skip
the removal.

(Both the remote and local feature branch were already deleted in Step 2 by
`delete_feature_branch`, after it confirmed the PR merged.)

## Step 8: Display

```
✓ <feature> cycle complete

  PR #N merged and branch deleted
  Decision log: docs/decisions/YYYY-MM-DD-<feature>.md
  Retrospective appended (see decision log)
```

If a governing product plan exists (top-level or nested, per Step 3), replace the generic "start next cycle?" prompt with the exact-command precision the other stages' exit protocols use:

```
Product plan: 3/8 cycles complete.

Milestone 1: ✓ auth-setup  ✓ data-model  → user-registration
Milestone 2: dashboard  settings

Completed: <this feature's item>. Remaining: <next item>, <item after>, ...

Safe to /clear now — start the next item with: /dev:spec "<next item's name>"
[If this was a nested cycle (parentFeature was set): note that the parent feature (<parentFeature>) itself still needs its own /dev:done once all its sub-milestones are merged.]
```
