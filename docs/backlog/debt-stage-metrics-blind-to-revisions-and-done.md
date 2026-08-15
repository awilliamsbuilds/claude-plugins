---
type: debt
scope: repo
status: open
first_recorded: 2026-08-15
cycles: [backlog-viewer]
recurrence: 1
files:
  - plugins/dev/skills/reflect/SKILL.md
  - plugins/dev/skills/done/SKILL.md
---

**What's wrong:** `metrics` carries `spec_revisions` but no Shape or Plan analogue, and no `done`
timestamp. `dev:reflect` treats `spec_revisions` as its strongest single signal, so churn after
Shape's or Plan's first draft is invisible to the retrospective — this cycle's two post-draft Shape
corrections (severity's role, facet ordering) were recoverable only by reading git log, and the
missing `done` stamp makes the final stage the one stage whose duration cannot be computed from
`stage_timestamps` at all.

**Why deferred:** Surfaced at the `dev:reflect` gate on backlog-viewer, where the fix belongs to a
metrics contract that Milestone 2 of `dev-observability` is chartered to design rather than to a
one-off counter added here. That milestone's plan names per-stage `_start`, a done stamp,
invocation counts and cost data as the gaps; the revision counters are the item it does not yet
name.

**Done looks like:** The `telemetry-schema` cycle's contract either covers per-stage revision
counts and a `done` timestamp, or records a deliberate decision to exclude them — and
`dev:reflect`'s reading guidance matches whichever it chose.
