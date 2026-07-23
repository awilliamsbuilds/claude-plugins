# done-primary-reconcile
*Branch: feature/done-primary-reconcile · Confidence: 90% — Ready · 2026-07-23*
*Cycle type: feature · Tier: standard*

## Intent

A worktree-cycle `dev:done` runs entirely in the cycle's own worktree: it merges the PR and
pushes every post-merge commit (decision log, Component Registry, tech-debt flush, cleanup) to
`origin/main` via `git -C "$WORKDIR" push origin "HEAD:$INTEGRATION"`, ending detached at the
merged `origin/$INTEGRATION` tip (`done/SKILL.md:103`). It deliberately never touches the user's
**primary checkout** — because the primary usually has `main` checked out and git forbids the
same branch in two worktrees, the whole worktree design exists to avoid checking `main` out a
second time.

The side effect: the primary checkout's local `main` and working tree are left **stale**. After
the cycle completes, `origin/main` has advanced by every `done` commit but the primary's `main`
has not, so the user must `git pull` by hand before their main folder reflects the work they just
merged. This is the friction this cycle removes: `done` should reconcile the primary checkout
itself, whenever it can do so without risk.

The **legacy in-place cycle** (`worktreePath` null) does not have this problem — there `WORKDIR`
*is* the primary tree, and `done` already runs `checkout $INTEGRATION` + `pull --ff-only`
(`done/SKILL.md:110-113`), so the primary is reconciled as part of the merge. The fix is therefore
**worktree-cycle-only** and must be a no-op for the legacy path.

## Scope

Add a **final reconciliation step** to `dev:done`, in the worktree-cycle teardown, that catches
the primary checkout's `main` up to `origin/main` when safe:

1. **Placement:** after the worktree is removed at the end of Step 7 (the `worktree remove` /
   `prune` block, `done/SKILL.md:342-347`), reconcile the primary checkout. It runs only on the
   worktree-cycle path — the legacy branch (`worktreePath` null) returns before this block and is
   untouched.
2. **Top-level only:** applies when `INTEGRATION == main` (top-level cycle, `parentFeature` null).
   The reconciliation target is the primary checkout's local `main`.
3. **Safe-case behavior, decided by the primary checkout's state:**
   - Primary is **on `main` and clean** → `git -C "$PRIMARY" merge --ff-only origin/main`.
     `--ff-only` advances a strictly-behind branch and updates the working tree with no merge
     commit; it aborts harmlessly if anything is not a clean fast-forward.
   - Primary is **on a different branch** (a concurrent session working elsewhere) →
     `git -C "$PRIMARY" fetch origin main:main` — advances the local `main` ref without a
     checkout (allowed precisely because `main` is not the checked-out branch).
   - Primary is **dirty** (uncommitted changes), or local `main` has **diverged** from
     `origin/main` (local commits not on origin, so no fast-forward is possible) → **do not mutate
     the primary tree.** Print a reminder line telling the user to `git pull` when ready.
4. **Report the outcome** in the Step 8 display: state whether the primary was fast-forwarded
   (and to what), its ref advanced, or left for a manual pull with the reminder.

## Out of Scope

- **Nested cycles** (`parentFeature` set, so `INTEGRATION` is a parent feature branch, checked
  out in the parent's own worktree rather than the primary tree). These print the reminder only;
  no auto-reconcile. Uncommon today, and the reminder yields a correct (manual) outcome.
- **The legacy in-place path** — already reconciles via its existing `pull --ff-only`; left
  untouched.
- Changing how any stage pushes to `$INTEGRATION`, or any change to the worktree model itself.
- Reconciling anything other than the integration branch (e.g. the user's other local branches).
- A `git pull` reminder for cycles that were already up to date (nothing to reconcile → no
  reminder needed).

## Success Criteria

- After a **top-level worktree cycle** where the primary is on a **clean `main`**: the primary's
  `main` matches `origin/main` with **no manual pull** — verifiable by `git -C "$PRIMARY" rev-parse main`
  equalling `origin/main` immediately after `done` exits.
- Primary **on another branch**: its local `main` ref is advanced to `origin/main`; the checked-out
  branch and working tree are untouched.
- Primary **dirty** or `main` **diverged**: the primary working tree is byte-for-byte unchanged,
  and the Step 8 display carries the `git pull` reminder.
- **Legacy in-place cycle:** behavior is identical to today — the reconciliation block does not run
  (the legacy branch returns before it).
- **Nested cycle:** the primary tree is not auto-reconciled; the reminder is shown.
- Never a merge commit, never a forced update, never a mutation of a dirty primary tree.

## Happy Path

1. User runs `/dev:done` for a top-level feature; the worktree cycle merges the PR and pushes all
   post-merge commits to `origin/main`.
2. Step 7 removes the cycle worktree.
3. The new reconciliation step inspects the primary checkout: it is on `main` and clean.
4. `git -C "$PRIMARY" merge --ff-only origin/main` fast-forwards it.
5. Step 8 reports: primary checkout fast-forwarded to `<sha>` — no manual pull needed.

## Edge Cases

- **Primary on a non-integration branch:** advance the `main` ref via `git fetch origin main:main`;
  do not disturb the checked-out branch or its working tree.
- **Primary dirty (uncommitted tracked changes on `main`):** skip the fast-forward entirely; print
  the reminder. `--ff-only` would refuse a conflicting update anyway, but the check is explicit so a
  non-conflicting dirty tree is still never silently advanced.
- **`main` diverged from `origin/main`** (local commits not pushed): no fast-forward is possible;
  skip and print the reminder rather than attempting a merge.
- **Primary already up to date** (`main` already equals `origin/main` — e.g. a no-op cycle, or the
  user pulled manually mid-cycle): reconciliation is a no-op; print no reminder.
- **Primary checkout in detached HEAD:** treated as "not on `main`" → advance the `main` ref via
  `fetch origin main:main` if it exists; never check anything out.
- **Legacy in-place cycle** (`worktreePath` null): the reconciliation block is never reached — the
  legacy path already caught the primary up.
- **Nested cycle** (`INTEGRATION` = parent branch): reminder only; the parent branch's worktree is
  not the primary tree and is out of scope.

## Audience

Developers using and maintaining the `/dev` plugin — a portable workflow installed across arbitrary
repos. No repo-, person-, or environment-specific assumptions may leak into the fix. (From CLAUDE.md:
personal Claude Code plugin repo, agent-facing.)

## Technical Constraints

- **Never mutate a dirty primary working tree.** The primary checkout is the user's space; a
  reconciliation that touched uncommitted work would be worse than the staleness it fixes.
- **`--ff-only` only** — no merge commits, no forced updates. A non-fast-forward is a signal to
  stop and defer to the user, not to reconcile harder.
- **Portability:** must hold whether or not `main` has branch protection, and regardless of what
  branch the primary tree happens to be on (a concurrent cycle may have moved it).
- **Boundary awareness:** this adds a second working-tree mutation of the primary checkout (the
  first being `worktree remove`). It is gated behind the clean-and-fast-forwardable checks so it
  never surprises the user.
- **Prose, not code:** `done/SKILL.md` is a Markdown skill with embedded shell; "verify" means
  tracing the procedure and confirming embedded snippets exit 0 on their healthy path, not running
  a test suite.

## Dependencies

- None external. A self-contained edit to `plugins/dev/skills/done/SKILL.md`.
- Relies on the existing `PRIMARY` / `WORKDIR` / `INTEGRATION` definitions already computed at the
  top of `dev:done`.

## UI Needed

No. Shape stage is skipped; Plan follows Spec directly.

---
*Auto-filled dimensions: none*
*Grounding inventory: `grep -n 'push origin\|HEAD:\$INTEGRATION\|checkout --detach\|pull --ff-only' plugins/dev/skills/done/SKILL.md` → worktree cycle ends detached at `origin/$INTEGRATION` (`:103`), legacy cycle reconciles via `checkout $INTEGRATION`+`pull --ff-only` (`:110-113`), push_integration pushes `HEAD:$INTEGRATION` from `$WORKDIR` (`:124`). `grep -n 'git -C "\$PRIMARY"'` → primary-tree touches are only `branch -D` (`:87`, a ref) and `worktree remove`/`prune` (`:345-346`); no existing fast-forward of the primary's main (confirmed: staleness is real, reconciliation is net-new). `grep -n 'worktreePath.*null\|legacy in-place'` → legacy branch (`:106`) reconciles the primary in-place, returns before Step 7's worktree-removal block (`:332-334`), so the new step is worktree-cycle-only by placement. Step 8 (`:352-366`) has no stale-main reminder today → the fallback reminder is new text. `$INTEGRATION` defined as `main` when `parentFeature` null, else parent branch — confirms top-level-only scope keys on `parentFeature`/`INTEGRATION == main`.*
