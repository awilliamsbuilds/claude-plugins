---
type: debt
scope: plugin
status: open
first_recorded: 2026-08-22
cycles: [challenger-loop-economics]
recurrence: 1
files:
  - plugins/dev/skills/validate/SKILL.md
possibly_related_to: debt-same-region-recurrence-no-severity-floor-autopilot
---

**What's wrong:** `dev:validate`'s fix loop is bounded only by `validate.loops_max`. Nothing tests
whether the findings a loop is still producing are worth another cold dispatch. Step 8's
same-region-recurrence rule has a converging-cascade exemption that, when all three signals hold,
explicitly keeps the loop running — which is correct for the case it was built from, but means a loop
whose remaining findings are one-word bookkeeping consequences of its own prior edits keeps spending
full cold dispatches on them. This is structurally the same defect
`debt-spec-challenger-loop-lacks-blocker-kind-exit` named at Spec, one stage later: a count-bounded
loop with no test of what kind of finding earns another round.

**Why deferred:** this cycle's spec scoped the fix to `dev:spec` Step 12a. Its Out of Scope section
draws the line at the spec challenger on recorded grounding, and Validate's loop is a different
mechanism with a different severity vocabulary — folding it in would have been opportunistic rather
than caused by the work.

**Done looks like:** `dev:validate`'s fix loop states what kind of remaining finding earns another
iteration, in the same shape Step 12a now uses — as a consequence of existing definitions rather than
a new exit test — and the converging-cascade exemption is reconciled with it rather than left to
override it.

**What the next cycle pays if this stays open:** measured on the cycle that recorded it, loops 2 and 3
each spent a full cold dispatch to fix one nit that was a consequence of loop 1's own edit; loop 3's
dispatch reviewed a one-word synonym swap in a registry description no skill executes. This file's own
Step 4 step 3c puts a cold dispatch in this repo at 60k-170k tokens. That is roughly two-thirds of a
standard-tier validate budget spent on bookkeeping, on a cycle whose substance was entirely settled in
loop 1 — and it recurs on any prose-heavy cycle, which in this repo is every cycle.
