---
type: debt
scope: repo
status: open
severity: P3
first_recorded: 2026-08-11
cycles: [autopilot-handoff]
recurrence: 1
files:
  - plugins/dev/skills/dev/SKILL.md
  - plugins/dev/skills/autopilot/SKILL.md
---

**What's wrong:** `dev:dev`'s Invocation Reference documents `/dev spec` as "Jump to Spec
(new session)", but the Step 5a handler it routes to is written for *resuming*: its step 1 is
"Read state.json to find the current feature," and its requirements table has rows for
build/validate/pr/done only — no `spec` row and no new-session path. With two or more cycles
in flight, "find the current feature" is ambiguous.

**Why deferred:** The gap predates this cycle. It became load-bearing here because
`dev:autopilot`'s new multi-hit STOP points users at `/dev spec` as the way to start a fresh
cycle while others are in flight — but fixing `dev:dev`'s stage-jump procedure is outside the
autopilot-handoff spec's scope.

**Done looks like:** `dev:dev` Step 5a states a `spec` path explicitly — it creates a new
session rather than reading an existing `state.json`, and says so for the multi-cycle case —
or the Invocation Reference stops advertising `/dev spec` as a new-session route. Either way
`dev:autopilot`'s multi-hit STOP resolves to a procedure that works.
