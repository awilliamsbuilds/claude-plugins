---
type: debt
scope: plugin
status: open
first_recorded: 2026-08-20
cycles: [autopilot-resume-stage]
recurrence: 1
files: [plugins/dev/skills/validate/SKILL.md]
---

**What's wrong:** `dev:validate` Step 4 step 3b requires measuring "any claim about observable
command or tool behavior" before committing the fix that asserts it. It does not say what to do
with a **compound** claim — one sentence carrying two or more independently checkable assertions.
The observed failure mode is measuring the conjunct that is cheapest to check, finding it true, and
treating the whole sentence as measured.

  In this cycle a fix asserted: PR should be treated as satisfied when `artifacts.pr_url` is set,
  "because the re-run stages pushed their commits to the same branch." The first half was measured
  (`pr/SKILL.md:204` sets the key). The second was not, and was false — `pr/SKILL.md:142` is the
  only feature-branch push in the pipeline. The unmeasured half was the load-bearing one, and it
  shipped as a P1 that would have caused silent work loss.

**Why deferred:** The fix is a rule change to a step outside this cycle's spec scope, and this cycle
had already spent two of three validation loops on scope creep originating in the fix loop. Adding
another out-of-scope edit there would have repeated the exact mistake the retrospective names.

**Done looks like:** Step 3b states that a claim with more than one checkable assertion is measured
**per assertion**, and that the expensive or inconvenient conjunct is the one that most needs it —
cheapness of verification correlates with unimportance.

**Cost if not paid:** the rule keeps reading as satisfied when half a claim is checked, so the
failure recurs precisely where it is most expensive: a compound rationale is exactly the shape a
reviewer finds authoritative, and Build or a later loop follows it correctly *because* it reads as
measured.
