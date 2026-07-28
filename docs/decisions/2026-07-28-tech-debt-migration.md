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

## Retrospective
*Reviewed by dev:reflect · 2026-07-28*

**Spec:** Confidence (95/Ready) matched actual clarity — `spec_revisions: 0`, and the spec cold review's 4 findings (2 blockers, 2 concerns) were all applied, none dismissed, so the challenger's net was signal, not noise.

**Shape:** Skipped — correct for a data-only migration with no interface.

**Plan:** Accurate, no mid-build updates; `files_read_in_build: 2` confirms the plan's verbatim line-range map made Build near-lookup-free. The plan challenger's one concern needed no change.

**Validate:** 1/3 loops, clean on the first pass — both cold reviews returned zero findings at any severity.

**Flow:** Tier (standard) was right — the verbatim-faithfulness requirement and the `recurrence: 2` exception warranted the full net. **Cross-cycle defect surfaced by the maintainer:** `state.json` stage-advancement is committed only at each stage's approval gate, while the stage artifact and the challenger's in-place state write commit earlier — so an interrupted gate (`/clear`, session end, or any discard of working-tree changes) leaves committed state lagging the artifacts and commits that prove the stage was reached, forcing manual "state repair." Recurs across cycles; not specific to this one. Plan's resume-mid-approval check (`plan/SKILL.md:49`) covers only the single-stage-lag case; Build/Validate trust committed state on entry.

**Token efficiency:** No outliers — low build reads, zero visual screens, balanced stage durations.

**Suggestions:** Harden state-advancement durability across the `/dev` stage handoffs — either commit `completed[]`/`stage` atomically with the stage artifact, or add a state-reconciliation step at each stage's entry that repairs committed state lagging the on-disk artifacts+commits. Cross-cutting (spec/plan/build/validate); warrants its own cycle. Recorded to tech debt rather than hand-patched.

**Deferred to tech debt:** `state-advancement-commit-durability`
