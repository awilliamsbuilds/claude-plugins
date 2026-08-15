---
type: backlog
scope: repo
status: closed
promoted_to: docs/dev/product-plans/dev-observability.md
first_recorded: 2026-08-12
cycles: [manual]
recurrence: 1
files:
  - plugins/dev/skills/debt/SKILL.md
closed: 2026-08-15
closed_by: backlog-viewer
---

**What:** Ship a lightweight app with `/dev` that renders a repo's `docs/backlog/` store — active
corpus and `closed/` archive — as a browsable view.
**Why:** `/dev:debt list` is scannable but strictly linear: one block per item, one sentence of
body, ranked only by recurrence. Comparing items, filtering by type/scope/files, or seeing closed
items next to open ones each means re-invoking the skill with a different verb. A viewer makes the
store legible at a glance, which is what you actually want when deciding what to fold into an
upcoming cycle. May share a shell with the stage-lifecycle app
(`backlog-stage-lifecycle-telemetry-app`) rather than being a second standalone thing.
**Done looks like:** `/dev` ships a lightweight app that renders `docs/backlog/` (active plus
closed) as a browsable, filterable view.
