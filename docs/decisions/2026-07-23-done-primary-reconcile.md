# done-primary-reconcile — Decision Log
*2026-07-23 · Branch: feature/done-primary-reconcile · PR #41*

## What was built
`dev:done` now reconciles the user's primary checkout after a worktree-cycle merge, catching its local `main` up to `origin/main` when it can be done safely — so the primary `main` folder reflects the just-merged work without a manual `git pull`.

## Key decisions
- Placement over flagging → The reconciliation block sits at the very end of Step 7's "Otherwise remove the worktree" section, which the legacy in-place path never reaches. Being worktree-cycle-only is enforced by *placement*, not a `worktreePath` check — a prose note warns future edits against hoisting it above the legacy return.
- Top-level only, keyed on `INTEGRATION == main` → Nested cycles (`parentFeature` set, `INTEGRATION` = a parent branch checked out in the parent's own worktree) get a reminder only; auto-reconcile targets the primary checkout's `main`.
- `--ff-only` / `fetch main:main` as the only mutations → Both are self-guarding: `merge --ff-only` advances only a strict fast-forward and aborts harmlessly otherwise; `fetch origin main:main` refuses a non-fast-forward and refuses to touch `main` if it's checked out in another worktree. No path mutates a dirty tree, forces a ref, or creates a merge commit.
- No extra network fetch for the on-`main` case → `push_integration`'s prior pushes already advanced the shared `refs/remotes/origin/main` (remote-tracking refs live in the common git dir, visible from `$PRIMARY`), so the fast-forward reads an already-current `origin/main`. A redundant fetch is deliberately avoided, with a comment to stop maintainers re-adding one.
- Never STOPs the stage → Every path resolves to a `RECONCILE_MSG` token and continues; a failure to reconcile is reported as a reminder, not an error (so `dev:autopilot` needs no change).
- `fetch` exit code as the single authority (spec Open Question) → For the overlapping "different branch AND diverged" case, the exit code of `fetch origin main:main` alone decides the outcome, so the Step 8 report can never claim "ref advanced" when nothing moved.

## Validation notes
- 1 loop run (tier: standard). Two parallel fresh general-purpose subagents (code + security review) saw only the diff, Success Criteria, and task list.
- P3 (both reviewers): stale SHA in the `refadvanced` report — `origin_main` snapshotted before the fetch. → Fixed: the token now reads the ref's actual post-fetch tip.
- Nit (code review): inconsistent output suppression — `merge --ff-only` printed its summary. → Fixed: added `-q`.
- A code-review P3 proposing a `*)` default arm on the Step 8 `case` was investigated and rejected as a false positive: on the legacy path `RECONCILE_MSG` is unset and must print nothing; a default reminder would nag every legacy cycle. An anti-regression comment was added instead.
- Accepted as-is: duplicated `uptodate`/`reminder` ladder across the on/off-`main` branches — local, no carrying cost; dropped, not recorded as debt.

## Artifacts (archived)
Spec and plan committed at: 752fdfcff1138d2601a94ab9db95cc79a3a9505a on branch feature/done-primary-reconcile
