# Challenger Loop Economics — Validation Report
*Branch: feature/challenger-loop-economics · 2026-08-22*

## Summary
Loops run: 3 / 3
Final status: clean

No P1 was raised at any point. Both Step 2 reviewers ran cold against `2b4636c...HEAD` and were
issued together; both returned. All P2s and both defect-class P3s were fixed in loop 1, and each
loop's own fix diff was cold re-reviewed before the loop could exit.

## Build
no build system detected

Detection ran in `$WORKDIR` in B1–B5 order: no `package.json`, no `Makefile`, no `Cargo.toml`, no
`go.mod`. This is O3 — recorded as "no build system detected," **not** as a pass. Consistent with the
spec's Technical Constraints, which state the surface is prose-only with no test runner and that
verification is by reading the changed prose against the success criteria.

## Issues Resolved

### Loop 1
- P2: `spec/SKILL.md` — the reworked `Verdict format` example flipped the scope entry to a Blocker and
  updated `Scope ⛔1`, but left the header reading `Clarity ⛔1` while a new `⚠️ Concern (clarity)`
  entry sat below it. The header line was defined only by example, so a verdict of 0 blockers and 5
  concerns could render as four `✅`s above five real findings. → fixed: the header rule is now stated
  in prose (tallies every finding per lens; `✅` only where a lens found nothing), and the example
  reads `Clarity ⛔1 ⚠️1`.
- P2: `autopilot/SKILL.md` — the errored-dispatch restatement dropped the canonical's "once per stage,
  not once per round" qualifier, in the one file where the distinction has consequences. A deep-tier
  run reading it per-round would grant 5 retries instead of 1. → fixed: qualifier restored, with one
  sentence on why the scoping only bites in the looping mode.
- P3 (defect-class, dangling reference): the errored-dispatch paragraph landed as a sibling of the
  spec-challenger paragraph while `spec/SKILL.md` and `CLAUDE.md` both cite it as living in "the
  spec-challenger section." → fixed: retitled `**Spec challenger — an errored dispatch is not an
  iteration.**`, which makes both citations accurate and removes the reading that it governs both
  loops.
- P3 (defect-class, security review): the new errored-dispatch rule overlapped the pre-existing
  **Fallback** rule with no stated precedence — "the harness refuses" satisfied both descriptions, and
  the fallback branch would write `run: true` over a review that never returned. → fixed: precedence
  stated in the canonical only. The Fallback covers a harness with no subagent facility at all (a
  verdict is produced; the review happened, degraded); this rule covers a dispatch attempted and
  failed. The discriminator is whether a verdict came back. The trigger wording was also changed from
  "the harness refuses" to "a dispatch is refused" to remove the collision at its source.
- Nit: `autopilot/SKILL.md` plan-challenger paragraph switched to bare `applied` / `applied_concerns`
  mid-clause. → fixed: fully namespace-qualified.
- Nit: the `**Mode behaviour — autopilot: teeth.**` paragraphs in `spec` and `plan` still named only
  `applied` while their autopilot counterparts named both. → fixed in both.

### Loop 2
- Nit: `autopilot/SKILL.md` used "half" in two senses one clause apart. → fixed ("part").
- Nit: `CLAUDE.md`'s `dev:spec` row quoted the literal `` `Verdict format:` `` (with colon) after loop
  1 changed that text to `Verdict format.` → fixed.

### Loop 3
- Nit: the same word-sense collision survived in `CLAUDE.md`'s `dev:autopilot` row — the fix had been
  applied to the skill file but not to the registry row summarizing it. → fixed. The re-review noted
  the swap also converges the row onto the skill file's own vocabulary.

## Issues Remaining

### P1 Open
- none

### P2 Open
- none

### P3 Open
- none

### Nits Surfaced
- `dev:plan` Step 7a has no errored-dispatch rule, so an errored plan-challenger dispatch leaves the
  previous round's counters standing and advances `loops_run` as though a verdict returned. Raised by
  the security reviewer as an observation rather than a regression — behavior is unchanged from before
  this cycle, and the spec scoped the rule to the spec challenger deliberately. **Recorded** to the
  carrying-cost buffer as `plan-challenger-errored-dispatch-undefined` (Step 5a), because it states a
  concrete cost: an autopilot plan run can exit its loop believing blockers were resolved when no
  verdict ever returned, and nothing in `state.json` distinguishes that from a clean cycle.

## Notes

**Loop economics of this cycle's own validation.** Worth recording, since the cycle is about exactly
this. Loop 1 carried all the substance: 2 P2s, 2 defect-class P3s, 2 nits. Loops 2 and 3 were single
nits each, both consequences of loop 1's own edits rather than new findings — the converging-cascade
shape, with severity strictly below the first round in the region and no code changing after it. Loop
3 in particular re-reviewed a one-word synonym swap in a registry description no skill executes. That
is the loop running its budget on bookkeeping, which is the pattern this cycle's Blocker tightening
exists to stop one stage earlier at Spec. It is recorded here rather than acted on: `dev:validate`'s
own loop economics are a separate question from `dev:spec` Step 12a's, and the spec did not scope
them.

**A deviation from plan Task 9 step 2, made in the fix loop.** The plan said to place the
errored-dispatch bookkeeping "in the same paragraph" as the spec-challenger rule. Loop 1's P3 fix
instead kept it as an adjacent paragraph and gave it a `**Spec challenger — …**` lead. Folding roughly
200 words into an already-long paragraph would have hurt readability, and the retitle satisfies what
the citations actually require: that the text read as part of the spec-challenger section. Recorded
because it is a knowing departure from an approved plan, not an oversight.

**Buffer format correction.** `debt-pending.md` arrived from Spec carrying a `## Deferred` heading.
`dev:done` Step 6a's flush reads `## To Record` (contract P4), so an item appended under `## Deferred`
would have been written and then silently never flushed. The heading was normalized to `## To Record`
before this stage's item was appended. The section was empty, so nothing was lost. No skill writes
`## Deferred` — grep across `plugins/dev/` finds it nowhere — so this was a one-off malformed buffer
instance rather than a skill defect, which is why it is a note here and not a backlog item.

**On the two reviewer routes.** Both Step 2 reviewers received the tree and both artifact paths
explicitly, so the code reviewer's spec-comparison and plan-coverage bullets ran rather than reporting
`not run`. Plan coverage was confirmed task by task across all 12 tasks. The config-contract bullet
passed vacuously and said so: no key was added to `docs/dev/config.json`, and `applied_concerns` is a
`state.json` key, which carries no read-list contract.
