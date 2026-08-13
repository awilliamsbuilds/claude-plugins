# /dev Observability — Product Plan
*Created: 2026-08-13 · Cycles completed: 0/4*

Promoted from two backlog items — `backlog-backlog-viewer-app` and
`backlog-stage-lifecycle-telemetry-app` — which both noted they may share a shell rather than
ship as two standalone things. This plan is that shared shell plus its two consumers.

## Milestone 1: Backlog viewer
- [ ] backlog-viewer (feature)

Establishes the app shell and its first consumer together, rather than building the shell
speculatively ahead of a live consumer. Renders `docs/backlog/` — active corpus plus `closed/`
archive — as a browsable, filterable view. Ordered first because its data already exists, so it
carries no instrumentation dependency.

## Milestone 2: Stage telemetry instrumentation
- [ ] telemetry-schema (architecture)
- [ ] telemetry-instrumentation (feature)

The schema is its own architecture cycle: the metrics contract is consumed by ~10 stage skills
plus a viewer, and token/cost estimation has no obvious answer to settle mid-build. Instrumentation
then wires the writes into each stage skill per that contract.

Narrower than the source item assumed — `metrics.stage_timestamps` already exists and is written
by spec/shape/plan/build/validate/pr, and `dev:reflect` already reads it. The real gaps are
per-stage `_start` (only `spec` has one today), a `done` stamp, invocation counts, and cost data.

## Milestone 3: Lifecycle viewer
- [ ] lifecycle-viewer (feature)

Reuses Milestone 1's shell to render per-cycle stage telemetry. Depends on Milestone 2.
