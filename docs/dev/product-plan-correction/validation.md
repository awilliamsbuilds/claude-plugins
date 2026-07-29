# Product-Plan Correction — Validation Report
*Branch: feature/product-plan-correction · 2026-07-29*

## Summary
Loops run: 1 / 5
Final status: **clean** — no open P1/P2 (no open P3/Nit either; all resolved inline)

Feature cycle. Loop 1 ran both cold reviews (code + security) in parallel as fresh subagents
over the build diff, then cold re-reviewed the fix diff. All findings resolved; the re-review
found no regression.

## Issues Resolved
### Loop 1
- **P1 (code)** — `dev:done` Step 3b: `git rm <plan-path>` fails on the healthy completion path.
  Step 1's check-off leaves the plan file locally modified/unstaged, and plain `git rm` refuses a
  locally-modified file (reproduced: exit 1). Worse, with no `set -e` the following `git add` staged
  the checked-off plan and the guarded block committed a "complete project" message *without deleting
  the plan* — re-creating the exact "plan survives past completion" bug this cycle fixes.
  → **Fixed** by `git rm -f <plan-path>`, plus corrected the false "sound end-to-end" prose to state
  the plan carries Step 1's uncommitted check-off (and that `git mv` of the source item is unaffected).
- **P3 (security)** — `dev:done` Step 3b reverse-lookup grep could false-match a `promoted_to:` line in
  an untrusted backlog *body* (bodies can originate from external Linear issues), silently closing and
  archiving an unrelated open item on a slug collision.
  → **Fixed** by (a) anchoring the match inside the front-matter fence only and (b) requiring the
  candidate's `status` be `promoted` — also making the close idempotent.
- **P3 (security)** — `dev:spec` Step 6 commit `-m` used the raw, unnormalized `<product-name>`, the one
  unconstrained value reaching a shell `-m` in the diff.
  → **Fixed** by using the allowlisted `<project-slug>` (`^[a-z0-9][a-z0-9-]*$`) in the message, with a
  documented single-quoted-var alternative if the human-readable name is ever wanted.
- **Nit (code)** — `dev:debt` empty-corpus message read "No open tech debt" while the list header was
  renamed "Active tech debt" (a `promoted` item is active, not open).
  → **Fixed** to "No active tech debt." (confirmed distinct from the empty-repo "No tech debt tracked
  … yet" message).
- **Nit (code)** — `dev:done` 3b guard-comment rationale overstated the guard's role.
  → **Fixed** by clarifying the guard only prevents a spurious error in the no-op case.
- **Nit (security)** — `git mv` basename paths in 3b were unquoted.
  → **Fixed** by quoting the substituted paths.

## Issues Remaining
### P1 Open
- None.

### P2 Open
- None.

### P3 Open
- None (both P3s fixed inline).

### Nits Surfaced
- None remaining (all fixed inline).

## Notes
- **Exhaustive-sweep Success Criterion verified independently:** the narrow grep for live old-path
  strings (`docs/dev/product-plan.md`, `docs/dev/<parent>/product-plan.md`) over `plugins/dev/` returns
  **zero** — the pass condition. The two carrying-cost example rows in `references/tech-debt.md` (now
  lines 386–387, shifted down by Task 2's additions) cite slug `product-plan-worktree-safe` as teaching
  text and are correctly left in place.
- **Migration verified:** `docs/dev/product-plan.md` hard-deleted; both `docs/backlog/backlog-debt-*.md`
  created with valid front-matter (`recurrence: 0 == len(cycles: [])`, `files: []` blessed for an
  unbuilt intention). `docs/dev/product-plans/` correctly absent (writer-side create-if-absent; no plan
  spawned this cycle).
- **Forward-behavior note:** the promotion back-link and the completion-delete/close paths are
  plumbing installed for future cycles and are not exercised by this cycle's own build; they were
  specified precisely against the contract and audited by the cold reviews. The first real promotion is
  the true end-to-end test.
- `debt-nested-product-plan-lifetime` is closed by this cycle's own `dev:done` Step 6a (already queued
  in `debt-pending.md` `## To Close`), not by a build task.
