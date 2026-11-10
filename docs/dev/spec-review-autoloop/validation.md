# Spec Review Autoloop — Validation Report
*Branch: feature/spec-review-autoloop · 2026-11-10*

## Summary
Loops run: 3 / 3
Final status: clean

## Build
no build system detected

## Issues Resolved
### Loop 1 (initial reviews: `/dev:review diff` + `/dev:secure diff` against b9f17c6)
- P2: resume after `/clear` at `loops_run == loops_max` assumed a `limit` exit, but `clean` and `scope` exits on the cap round also leave the cap spent → spec/plan Step 1 made exit-neutral ("Round cap used — regenerated findings against the current spec/plan"), with scope-heading switch on the spec side
- P3 (security): suggested fixes were auto-applied with no data-not-instruction guard on the applying session → added to spec 12a, plan 7a and autopilot summaries: fix text is data, applied only as a text edit to the artifact under review
- P3: errored-dispatch canonical marker named only autopilot → now names the `dev:plan` Step 7a mirror and autopilot's new section name
- P3: spec Step 1 / Step 13 carried no canonical marker for the plan mirrors → added
- P3: counter writes on an autopilot `limit`/`scope` STOP pointed at a commit that never happens → STOP now commits `state.json` alone
- P3: autopilot "each round applies every fix" contradicted the heavy-final-round rule → "each round except a heavy final round"
- P3: "`limit` is the only halt" contradicted the errored-dispatch STOP → "only finding-driven halt" (autopilot + plan)
- Nit: scope-exit gate offered `apply` for a non-text-fixable blocker → separate scope reply line (rescope, or apply the other findings)
- Nit: "Round <n>: clean" placement ambiguous → replaces that round's tally
- Nit: telemetry.md rewrap

### Loop 2 (re-review of loop 1's fix diff: 0 P1/P2)
- P3: neutral resume heading had no reply line → limit reply line added
- P3: autopilot resume at a spent cap was undefined → zero findings continue, any findings STOP
- Nit: autopilot summary omitted the STOP's `state.json` commit → added

### Loop 3 (re-review of loop 2's fix diff: 0 P1/P2)
- P3: scope-heading resume got the limit reply line → matching reply line
- P3: "nothing changed" claim was false (dispatch overwrites run/blockers/concerns) → reworded with the accurate reason
- Nit: explained why a spent-cap autopilot resume STOPs even on light findings

Loop 3's re-review: clean.

## Issues Remaining
### P1 Open
- none

### P2 Open
- none

### P3 Open
- none

### Nits Surfaced
- spec/SKILL.md:56 "`Exit scope`'s … `Exit limit`'s" reads awkwardly — polish only; dropped by the carrying-cost test (no cost to the next cycle)

## Notes
- Loops 2–3 revisited one region (the spent-cap resume paragraph, spec/plan Step 1). The converging-cascade exemption applied: severity fell from P2 (loop 1) to P3 and stayed there, only prose changed after loop 1, and each finding was a consequence of the loop 1 resume edit.
- `dev:secure diff`: no P1/P2; secret scan clean; no shell or executable code changed.
- The Component Registry rows for dev:spec, dev:plan and dev:autopilot still describe the old advisory behaviour. `dev:pr` Step 5a updates them.
