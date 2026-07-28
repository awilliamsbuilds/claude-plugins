# Tech-Debt Migration — Decision Log
*2026-07-28 · Branch: feature/tech-debt-migration · PR #54*

## What was built
Carried all 11 deferred tech-debt entries (4 Open + 7 Closed) out of the orphaned aggregate `docs/dev/tech-debt.md` into per-item Markdown files under the `docs/backlog/` store, then retired the aggregate — executing Decision 8(a)+8(b) of the backlog-debt-model ADR.

## Key decisions
- **Migrate data only; touch no skill or contract.** → The producing/reading stages already targeted `docs/backlog/` (verified: zero skill references to the aggregate); the only thing left was moving the data, so the cycle deliberately stayed out of every `SKILL.md` and `references/tech-debt.md`.
- **Transfer verbatim, preserve source dates.** → These are historical records, not new writes, so `first_recorded`/`closed` dates were copied from the source entries rather than re-stamped from the clock, and body prose was reproduced unchanged.
- **Preserve the `recurrence: 2` / single-cycle discrepancy on `gate-path-state-writes`.** → The source carried a pre-existing `recurrence != len(cycles)` mismatch; re-deriving the count would rewrite history, so verbatim faithfulness was chosen over invariant repair (SC #3 exception, SC #4 precedence).
- **Drop the prose `**Files:**` line into front-matter `files:`.** → The P1 per-item model retires the prose field; each entry's file paths became the YAML `files:` list, no paths lost.
- **Defer `product-plan.md` migration (Decision 8(c)) to a later cycle.** → Unlike the orphaned `tech-debt.md`, `product-plan.md` is still actively written by `dev:spec` and read by `dev:done`; retiring it now would break those paths until the promotion/deletion behavior lands.
- **Migrate the 4th Open entry the ADR table omitted** (`arch-cross-boundary-transport`). → It was deferred by the ADR's own retrospective after Decision 8 was captured; it migrates like any Open entry, with a slug newly assigned since the ADR never gave it one.

## Validation notes
- 1 loop run (tier: standard); final status clean.
- Two cold reviews (code + security) ran in parallel as fresh subagents against the build diff, each denied session history. Both returned no findings at any severity.
- No P1/P2 issues found; no P3/Nits surfaced. No fixes required, so the fix-diff cold re-review did not apply.
- Independently confirmed: verbatim faithfulness of all 11 bodies (including the Markdown table and inline-code spans), counts (4 active + 7 closed), the `recurrence: 2` exception, dropped `**Files:**` lines preserved in `files:`, and safe source deletion.

## Artifacts (archived)
Spec and plan committed at: 41501984a6609419969c1950a06483e585dde882 on branch feature/tech-debt-migration
