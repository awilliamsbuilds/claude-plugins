# Validate Prose Re-sync — Decision Log
*2026-08-19 · Branch: feature/validate-prose-resync · PR #87*
*Handed off to autopilot at Spec*

## What was built

A re-sync rule in `dev:validate` Step 4's fix loop — when a fix edits a fenced code block, the prose
inside the smallest enclosing heading is re-read and reconciled in the same loop commit — plus the
three supporting changes that make it hold and keep it from misfiring.

## Key decisions

**The rule is stated as a relation, not a word list** → counts and ordinals are what went stale in the
observed cases, but a number-hunting rule would miss every non-numeric staleness. "Does this English
still describe the block" subsumes the numeric case; the numbers appear as illustration only.

**The boundary is the smallest enclosing heading, measured rather than assumed** → on the observed
failure the edited fence sat at `review/SKILL.md:152-172` and both stale sentences (`:174`, `:192`)
fell inside the same `###` opening at `:146`. That subsection is ~1,062 tokens of a ~5,825-token file,
so a whole-file re-read costs 5.5× for no additional catch on the available evidence. The original
spec draft had *ruled out* a bounded rule on an unmeasured claim that the stale prose sat far from the
fence; measuring inverted the recommendation.

**Its position is pinned at 3c, not left to the builder** → step 4 carries a circuit breaker that
disables further P3 fixes for the rest of a cycle once one is blamed for a regression. A re-sync rule
folded into step 4 would inherit that breaker and switch itself off in exactly the situation where
prose is going stale fastest. At 3c it runs beside the P1/P2 fixes that trigger it.

**It does not extend to other files** → step 3a already propagates a fix to declared canonical/mirror
counterparts. Cross-file is covered; the uncovered case was intra-file, and that is all this adds.

**Enforcement rides the existing checklist rather than a new artifact** → "re-read the subsection"
leaves no trace, and unenforceable steps get skipped. Step 8's cold re-reviewer already reads every
fix diff and is the party that caught both misses on the observed cycle, so it gained one question.
No new dispatch, no new `state.json` key, no new `validation.md` section.

**`dev:fix` is deliberately not edited** → its cap is pinned to 1, so the multi-loop cascade is
structurally unreachable there. It restates no checklist of its own, so the new question is inherited
by reference rather than omitted. Whether its single round should carry the re-read anyway is
recorded as deferred, not settled.

**The same-region recurrence rule learns to tell converging from circling** → a prose-resync cascade
trips that rule mechanically while being the opposite of circling. On the observed cycle the rule
fired from loop 3 onward and was overridden by documented human judgment. A rule that needs a written
override to behave correctly is itself a defect, so it gained a three-signal exemption — and both
branches were addressed, because the autopilot half is the one with no human present to catch a
misfire.

## Validation notes

- **2 loops run** (tier: standard, cap 3). Both reviewers ran cold; both loops were cold re-reviewed
  on their own fix diffs before the loop could exit.
- **P1 (loop 1)** — step 4's composition clause located the re-sync edit *inside* step 4, placing it
  under the circuit breaker and contradicting step 3c's own reason for existing. Resolved by making
  the clause classificatory rather than locational: a re-sync edit is defect-class but is never a
  step-4 P3.
- **P2 (loop 1)** — the mirror note claimed `dev:fix` "deliberately omits" the new question.
  `dev:fix` restates no checklist at all, so nothing could be omitted. Resolved by stating the
  inheritance accurately.
- **P2 (loop 2)** — loop 1's own fix grounded that claim on a quote whose subject was a different
  checklist, and added fresh cross-file line citations against an open item tracking exactly that
  form. Re-grounded on `dev:fix`'s `### Review` mirror declaration, cited by section name.
- **P3s resolved** — the `5.5×` ratio named its numerator as denominator; step 3c's trigger did not
  reach fixes made at step 4 or step 5, which run after it; "the first round" was ambiguous between
  the cycle's first loop and the region's first round; a buffer slug carried a doubled type prefix.
- **Nits accepted as-is** — two dropped under the carrying-cost test (a wording-precision point on
  correct prose; a line-citation observation already covered by an open item). One recorded:
  `converging-cascade-third-signal-unaudited`.
- **Security review** — no P1/P2/P3. Secret scan clean on all three checks; no shell snippet added
  anywhere in the diff; no new subagent dispatch and no existing dispatch widened.
- **Manual verification** (declared TDD deviation — Markdown prose, no test runner): regression guard
  89/89 (2 pre-existing skips); scope check confirmed `validate/SKILL.md` as the only file under
  `plugins/`; walkthrough of the amended Step 4 against the observed failure.
- **Build:** no build system detected (B5) — not recorded as a pass.

**SC7 — the cycle as its own test — was met and not vacuously.** Loop 1's Nit fix wrote the citation
`validate/SKILL.md:425`; re-measuring before commit showed the line had already moved to 431 under
this cycle's own insertion. The desync failure in miniature, caught by re-reading rather than by a
later reviewer — and the reason the final text cites by section name instead of by line.

## Artifacts (archived)

Spec, plan, and validation committed at: 271a61a on branch feature/validate-prose-resync
