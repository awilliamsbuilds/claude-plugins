# challenger-loop-economics — pending debt

## To Close
- debt-spec-challenger-loop-lacks-blocker-kind-exit — this cycle is Milestone 2 of
  `dev-process-hardening`, whose Notes section assigns each source item's close to its own cycle's
  `dev:done` Step 6a buffer rather than to a promotion back-link. All three of its "Done looks like"
  clauses are this cycle's scope.

## To Record

### plan-challenger-errored-dispatch-undefined
````markdown
---
type: debt
scope: plugin
status: open
first_recorded: 2026-08-22
cycles: [challenger-loop-economics]
recurrence: 1
files:
  - plugins/dev/skills/plan/SKILL.md
  - plugins/dev/skills/autopilot/SKILL.md
---

**What's wrong:** `dev:spec` Step 12a now defines what happens when a challenger dispatch returns an
error instead of a verdict — `challenge.loops_run` does not advance, `challenge.blockers` /
`challenge.concerns` are set `null`, one retry per stage, a second error STOPs. `dev:plan` Step 7a has
no counterpart. An errored plan-challenger dispatch therefore leaves the previous round's
`challenge_plan.blockers` / `challenge_plan.concerns` standing, and `challenge_plan.loops_run` advances
as though a verdict returned. `dev:autopilot`'s plan-challenger section states the asymmetry
explicitly ("the errored-dispatch rule does not apply here") — it documents the gap rather than
closing it.

**Why deferred:** this cycle's spec scoped the errored-dispatch rule to the spec challenger
deliberately (§Scope item 3), and the plan challenger's Blocker definition and severity handling are
named in §Out of Scope. Widening the rule mid-cycle would have crossed a scope line the spec drew on
recorded grounding.

**Done looks like:** either `dev:plan` Step 7a carries the errored-dispatch rule as a marked mirror of
`dev:spec` Step 12a (canonical), with `dev:autopilot`'s plan-challenger section updated and its stop
list naming the twice-errored plan dispatch — or Step 7a records an explicit decision that the plan
challenger does not need one, with the reasoning, replacing today's bare assertion.

**What the next cycle pays if this stays open:** an autopilot plan-challenger run whose dispatch
errors reads the previous round's counters as a fresh verdict, so it can exit the loop believing
blockers were resolved when no verdict ever returned — a silent wrong exit, in the mode with no human
present. Nothing records it: `loops_run` advanced, `blockers` holds a real number from an earlier
round, and `run` is `true`, so `dev:reflect` sees an ordinary clean cycle. Diagnosing it after the fact
means reconstructing which round errored from state that no longer distinguishes the cases — which is
exactly the reconstruction the `null` value exists to make unnecessary on the spec side.
````
