# Unified Backlog Store — Format Cutover — Decision Log
*2026-07-28 · Branch: feature/unified-backlog-store · PR #52*

## What was built
Cycle 1 of the backlog/debt-model ADR: the `/dev` tech-debt store was cut over from a single aggregate `docs/dev/tech-debt.md` file to a per-item store under `docs/backlog/`, with the shared contract and all seven consuming skills rewritten to speak the new format.

## Key decisions
- **Rewrite the contract in place, keeping the filename `tech-debt.md`** → the seven `references/tech-debt.md` links stay valid, so Tasks 2–8 touch no reference paths and can run independently after Task 1.
- **Define the complete front-matter schema up front (all 13 Decision 3 fields, including the reserved `scope`/`routing`/`promoted_to`)** → the on-disk format is forward-stable, so cycles 3–4 add *procedures*, not fields; the store never has to be re-migrated for a schema change.
- **Document fields in full but only the procedures this cycle implements** → no routing or promotion behavior is written for code that doesn't exist yet; reserved fields carry a one-line "handled by a follow-on cycle" note.
- **Per-item file model with a single close-move** (Decision 1) → active items flat in `docs/backlog/`, closed items archived to `docs/backlog/closed/`; the only file move happens on close, keeping the terminal state visible in the tree.
- **Type-prefixed corpus glob `docs/backlog/*.md`** cited by every reader → the recurrence-merge corpus can't be diluted by `README.md` or other non-item files; the two-condition clear-match test (files overlap **and** same defect) carries over verbatim, only the corpus changes.
- **`dev:spec` records a gated close-intent; `dev:done`'s flush executes it** → preserves the deferred-close safety property (a cycle may agree at spec-time to pay a debt and never finish; premature close is the unrecoverable direction).
- **Writer-side silent-degrade** → `dev:done`'s flush and standalone `dev:reflect` create `docs/backlog/` on first write when absent, so buffered debt is never lost in the transition window before a manual `dev:init` re-run.

## Validation notes
- 1 loop run (tier: deep). Two cold reviews (code + security) ran in parallel over the Build diff as fresh subagents; a cold re-review of the fix diff found no regression.
- **P2** — buffer template used a 3-backtick per-item fence where the rule three lines below mandates 4 (the exact early-close-prone fence the rule exists to prevent). Fixed: bumped the template to a 4-backtick fence matching `dev:done`.
- **P3** — `dev:spec` still cited the retired `tech-debt.md` as a write precedent (a literal Success-Criterion-3 gap). Fixed: replaced both citations with still-valid cycle artifacts.
- **P3** — slug-collision check ignored the `closed/` archive, so a slug matching a closed item could produce two identical basenames. Fixed: made the contract's P2 rule span active + `closed/`, updated both skill steps.
- **Nit** — slug charset (`[a-z0-9-]`, no path separators / `..`) was prose convention, not a stated invariant, though slugs derive from external finding text and compose an on-disk path. Fixed: added an explicit charset/strip-or-reject sentence to P2.
- No open P1/P2/P3/Nit issues carried forward.

## Artifacts (archived)
Spec, plan, and validation committed at: 49c802ef607289b7e7a69ca15c4ffb9ac36be1ee on branch feature/unified-backlog-store

## Retrospective
*Reviewed by dev:reflect · 2026-07-28*

**Spec:** Confidence (90/Ready) matched actual clarity — 0 revisions. The spec cold-review caught 1 blocker + 1 concern upstream, both applied, none dismissed; the spec then held with no post-gate churn.
**Shape:** Skipped — ADR-implementation cycle, no UI.
**Plan:** Accurate; one minor mid-build step added to Task 7. The self-contained contract kept `files_read_in_build` at 1. Plan cold-review logged 1 concern, carried as acknowledged.
**Validate:** 1/5 loops, clean. A P2 (buffer-template backtick fence), two P3s (stale `tech-debt.md` citation in `dev:spec`; slug-collision check ignoring `closed/`), and a Nit (slug charset) all resolved in loop 1; cold re-review found no regression.
**Flow:** Tier `deep` was right — shared contract + 7 skills with load-bearing safety properties. No unnecessary stages.
**Token efficiency:** No outliers. The multi-hour Build span was wall-clock elapsed with real-time gaps, not a spend signal; `visual_screens_shown=0` correct for a no-UI cycle.
**Suggestions:** Low-value only — a Build-time grep of Success Criteria phrased as "no skill references X" could have caught the stale `tech-debt.md` citation before Validate, but Validate already catches it reliably.
**Deferred to tech debt:** none
