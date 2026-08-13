---
type: backlog
scope: repo
status: open
first_recorded: 2026-08-12
cycles: [manual]
recurrence: 1
files: []
---

**What:** A lightweight app in `/dev` showing the lifecycle and details of each stage of a cycle —
time in stage, how often `/dev:debt` gets invoked, estimated token usage, and similar per-stage
metrics.
**Why:** None of this is recorded today. `state.json` carries the current stage but no timestamps
per transition, no stage counts its own invocations, and nothing tracks cost. So the instrumentation
is the larger half of this item and the app is the smaller one — the stages have to emit the data
before anything can display it. Worth scoping the two halves separately. May share a shell with the
backlog viewer (`backlog-backlog-viewer-app`).
**Done looks like:** `/dev` records per-stage lifecycle data as a cycle runs, and an app displays it
per cycle.
