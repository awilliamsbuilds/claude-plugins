---
type: debt
scope: plugin
status: open
first_recorded: 2026-08-22
cycles: [challenger-loop-economics]
recurrence: 1
files:
  - plugins/dev/skills/plan/SKILL.md
---

**What's wrong:** `dev:plan` Step 7a's spec-coverage lens asks whether every spec requirement "maps to
at least one task's work." That is satisfied as soon as a task exists for a success criterion, so a
task whose *implementation steps* under-specify what the criterion requires passes the lens. Neither
of the other two lenses catches it either — sequencing and interface-consistency both operate on task
boundaries, not on step content.

**Why deferred:** surfaced at `dev:reflect` after the cycle's PR had merged. Changing a challenger
lens is a contract decision about what the plan challenger is for, not a fix to fold into a cycle that
had already shipped.

**Done looks like:** the spec-coverage lens states the granularity it checks at — either explicitly
narrowed to task existence, with the gap named and accepted, or widened to ask whether a task's
implementation steps actually cover the criterion the task claims.

**What the next cycle pays if this stays open:** on the cycle that recorded it, plan Task 1 step 6
specified relabelling a worked example but never said to update the header counter that summarizes it.
All three plan lenses passed. Build followed the plan faithfully — the code reviewer said so in those
words — and the gap surfaced at Validate as a P2 that could have rendered a five-finding verdict as
all-clear at a user-facing gate. Cost: one validate loop plus the cold dispatch that caught it, for a
defect that was visible in the plan text one stage earlier.
