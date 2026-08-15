---
type: debt
scope: repo
status: open
first_recorded: 2026-08-15
cycles: [backlog-viewer, entry-adapters]
recurrence: 2
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

**Recurrence — `entry-adapters` (2026-08-15): the challenger counters have the same blindness, by a
different mechanism.** `challenge.*` and `challenge_plan.*` overwrite `run`/`blockers`/`concerns` on
every dispatch, so they report only the **last** verdict. This cycle's plan challenger ran 4 loops and
found **13 blockers cumulatively** (4 → 3 → 3 → 3 → 0), two of which would have shipped broken
behavior; because the final dispatch was clean, `state.json` ends with `challenge_plan.blockers: 0`.
The cycle reads as though the plan challenger found nothing. Only `applied: 30` survives as evidence,
and it does not separate blocker fixes from concern fixes. `dev:reflect`'s own guidance treats
`challenge.blockers` as one axis of its diagnostic table, so the table is being read against a value
that is structurally incapable of showing the loop's work. Whatever the metrics contract decides for
revision counts should cover cumulative-vs-last-write semantics for these counters too.
