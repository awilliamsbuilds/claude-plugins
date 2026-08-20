---
type: debt
scope: repo
status: closed
first_recorded: 2026-08-17
cycles: [extract-review-skills]
recurrence: 1
files:
  - plugins/dev/skills/autopilot/SKILL.md
closed: 2026-08-20
closed_by: autopilot-resume-stage
---

**What's wrong:** `/dev:autopilot docs/dev/<feature>/spec.md` gives autopilot a *feature*, not a
*stage*. Step 1 says to read `stage` from the resolved `state.json`, but nothing in the invocation
form says which stage the user means, and the argument is an artifact path that names Spec's output —
so the run can re-open the stage that produced it.

Observed in this cycle: invoked as `/dev:autopilot docs/dev/extract-review-skills/spec.md` on a cycle
whose `state.json` already read `stage: "plan"` and whose spec was approved and committed, the run
began by reviewing and editing the spec again. The user had to add "the next step is plan, do not run
a review of the spec again" in free text to get the intended behavior. That instruction is not part of
the documented interface.

**Why deferred:** The cost is paid per handoff, and it is not small: a re-opened Spec stage on an
approved spec spends a full challenger loop, mutates a committed artifact, and — because the challenger
loop's edits land as commits — leaves the spec measurably larger without any stage having asked for it.
In this cycle the spec grew 200 → 546 lines across those loops. It also silently defeats the artifact
gate's purpose: the argument form exists to resume a *named* cycle, and resuming it at the wrong stage
is the same class of error as resuming the wrong cycle.

Deferred rather than fixed inline because the fix is an interface change with more than one defensible
shape, and picking one is the user's call: an explicit stage token (`/dev:autopilot plan
docs/dev/<feature>/spec.md`, the user's proposal), or a strict rule that the artifact-path form
*always* resumes at `state.json.stage` and never re-enters a stage already in `completed[]`. The two
differ in whether the user can override the state file.

**Done looks like:** the invocation names the stage to resume at, or the skill refuses to re-enter any
stage already present in `completed[]` — so a handoff cannot re-run an approved stage, and no free-text
instruction is needed to get the documented behavior.
