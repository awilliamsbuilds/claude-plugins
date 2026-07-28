# Unified Backlog Store — Format Cutover — Validation Report
*Branch: feature/unified-backlog-store · 2026-07-28*

## Summary
Loops run: 1 / 5
Final status: clean

Feature cycle. Two cold reviews (code + security) ran in parallel over the Build diff
(`d710550..1209a77`) as fresh subagents seeing only the diff, spec Success Criteria, and plan task
list. One loop resolved every P1/P2/P3/Nit inline; a cold re-review of the fix diff
(`1209a77..b788711`) found no regression. No open issues carry forward.

## Issues Resolved
### Loop 1
- **P2** — Contract P4 buffer template showed a **3-backtick** per-item fence while the rule three
  lines below mandates a **4-backtick** outer fence, and `dev:done`'s own example already uses the
  correct depth. An implementer copying the template verbatim would emit the exact early-close-prone
  fence the rule exists to prevent (a body quoting a ```` ``` ```` code fence closes the item early,
  mis-parsing the flush). → Fixed: bumped the template's doc-wrapper to 5 backticks and the per-item
  fence to 4, matching `dev:done` (`references/tech-debt.md` P4 template).
- **P3** — `dev:spec` still cited the retired `tech-debt.md` as a write precedent at two lines
  (SKILL.md:47, :231) — a literal Success-Criterion-3 gap, and an inaccurate analogy (backlog items
  are now pushed to `$INTEGRATION` by `dev:done`, not carried on the spec's PR). → Fixed: replaced
  both with still-valid cycle artifacts (`spec.md`/`plan.md`).
- **P3** — Slug-collision check ignored the `closed/` archive. The contract's P2 states slugs are
  "unique within the tree" (which includes `closed/`), but `dev:done`'s flush and `dev:reflect`
  standalone disambiguated only against the active directory, so a slug matching a closed item would
  produce two identical basenames and an ambiguous `possibly_related_to:` pointer. → Fixed: made the
  contract P2 rule explicit that the check spans active + `closed/`, and updated both skill steps.
- **Nit** — Slug charset (`[a-z0-9-]`, no path separators / `..`) was prose convention, not a stated
  invariant, even though slugs are derived from externally-sourced finding text and compose an on-disk
  path. → Fixed: added an explicit charset/strip-or-reject sentence to the contract's P2 (closes a
  defense-in-depth gap cycles 2–3 will lean on).

## Issues Remaining
### P1 Open
- None

### P2 Open
- None

### P3 Open
- None

### Nits Surfaced
- None

## Notes
- **Reviews confirmed the change is strong on its own terms:** schema completeness (SC4 — all 13
  Decision 3 fields + the `recurrence == len(cycles)` invariant), the type-prefixed corpus glob
  (P5) cited by every reader so `README.md` can't dilute the merge corpus, full plan coverage
  (Tasks 1–8 including the Build-added Task 7 step 9), and the entry-text-is-data / 4-backtick-fence
  prompt-injection guards intact and strengthened.
- **Security surface is genuinely low.** No embedded shell interpolates a slug, filename, or item
  body; all filesystem mutations use fixed `docs/backlog/` pathspecs; the close-move requires the
  slug to resolve to exactly one existing corpus file. The one hardening (slug charset) was applied.
- Shell exit-code rule holds across the init seed block and the `dev:done` flush commit guard
  (`[ -d docs/backlog ]` guard, `diff --cached --quiet || { commit && push } || { STOP }`).
