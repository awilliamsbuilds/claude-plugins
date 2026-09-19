# /dev Observability — Product Plan
*Created: 2026-08-13 · Cycles completed: 1/3*

Promoted from two backlog items — `backlog-backlog-viewer-app` and
`backlog-stage-lifecycle-telemetry-app` — which both noted they may share a shell rather than
ship as two standalone things. This plan is that shared shell plus its two consumers.

## Milestone 1: Backlog viewer
- [x] backlog-viewer (feature)

Establishes the app shell and its first consumer together, rather than building the shell
speculatively ahead of a live consumer. Renders `docs/backlog/` — active corpus plus `closed/`
archive — as a browsable, filterable view. Ordered first because its data already exists, so it
carries no instrumentation dependency.

## Milestone 2: Stage telemetry instrumentation
- [ ] telemetry-schema (feature)

Narrower than the source item assumed, and narrower again than this plan first recorded.
`metrics.stage_timestamps` already carries **both** `_start` and `_end` for `spec`, `shape`, `plan`,
`build` and `validate` — grounding disproved the earlier claim here that only `spec` had one. The
real gaps are `pr` (which records only `pr_created`), `done` (which records nothing), and the
blocking one: all of it is deleted by `dev:done` Step 7 before anything outside the cycle can read
it. So the work is a committed append-only ledger plus the two missing stamp pairs.

One feature cycle, not the architecture-then-instrumentation pair originally planned. The contract
turned out to be one file format with two writers, not a decision needing ADRs. Token and cost
estimation is dropped — an agent cannot measure its own token usage from inside a skill — as is
counting `/dev:debt` invocations, which would mean instrumenting a skill outside the thing being
measured.

## Milestone 3: Lifecycle viewer
- [ ] lifecycle-viewer (feature)

Reuses Milestone 1's shell to render per-cycle stage telemetry. Depends on Milestone 2.
