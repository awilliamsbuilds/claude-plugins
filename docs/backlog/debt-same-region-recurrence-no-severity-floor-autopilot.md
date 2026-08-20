---
type: debt
scope: plugin
status: open
first_recorded: 2026-08-20
cycles: [autopilot-resume-stage]
recurrence: 1
files: [plugins/dev/skills/validate/SKILL.md]
possibly_related_to: backlog-converging-cascade-third-signal-unaudited
---

**What's wrong:** `dev:validate` Step 4 step 8's **same-region recurrence** rule ends its autopilot
arm with "attempt no further fixes in that region and buffer its remaining findings for Step 5a,
then continue." It carries **no severity floor**. Step 5a's buffer is the carrying-cost store for
P3s and Nits, so a P1 or P2 routed there leaves the loop with a known correctness blocker recorded
as deferred work rather than as an open blocker — and the run proceeds to `dev:pr` and merges.

  Reached live in this cycle: the circling region's second-round finding was a **P1**. The stage
  avoided buffering it only by deleting the region outright, which the rule neither requires nor
  suggests.

**Why deferred:** Out of this cycle's spec scope, and the safe path was available without a rule
change. Choosing the rule change instead would have been the same in-loop scope creep that produced
the P1 in the first place.

**Done looks like:** the autopilot arm distinguishes severities — a P3/Nit in the circling region
buffers and continues as today, while an open **P1/P2** there stops the run and surfaces it,
matching what the rest of Step 4 already does with an unresolved P1/P2 at the loop cap.

**Cost if not paid:** an autopilot run that circles one region with a P1 open buffers it and merges.
The blocker survives as a backlog item nobody reads as a blocker, which is strictly worse than the
loop-cap STOP the same severity would have triggered one branch away.
