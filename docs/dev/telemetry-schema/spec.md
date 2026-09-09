# Telemetry Schema
*Branch: feature/telemetry-schema · Confidence: 90% — Ready · 2026-09-09*
*Cycle type: feature · Tier: standard*

## Intent

`/dev` records a good deal about a cycle as it runs — per-stage timestamps, validate loop counts,
confidence, spec revisions, questions asked — and then **deletes all of it**. `dev:done` Step 7 runs
`rm -rf "$WORKDIR/docs/dev/<feature>/"` and commits the removal, so `state.json` and every metric in
it end with the cycle.

The consequence is that no question spanning more than one cycle can be answered. `dev:reflect`
reads the metrics once, at the end of the cycle that produced them, and reports stage-duration
outliers in prose. After that the data is gone. "Are validate loops trending up?", "do deep cycles
cost three times a standard one?", "did the challenger change how often specs churn?" are all
unanswerable today, and Milestone 3's lifecycle viewer has nothing to render.

This cycle makes a finished cycle's telemetry survive its own teardown.

## Scope

**1. A committed, append-only ledger.** `docs/dev/telemetry/cycles.jsonl` — one JSON object per line,
one line per completed run. `dev:done` appends the cycle's record **before** Step 7's `rm -rf`, so the
data is captured while `state.json` still exists.

**2. Fill the two real stamp gaps.** `dev:pr` gains `pr_start` / `pr_end` (it records only
`pr_created` today), and `dev:done` gains a `done` stamp (it records nothing today).

**3. A lane record for `/dev:fix` runs, derived rather than written.** `/dev:fix merge` appends a
second, smaller record shape after a successful merge. Its start and end are **read from git** — the
first commit on the branch and the merge commit — so the lane writes nothing while it works and its
"no cycle artifacts" premise is untouched.

**One envelope, two depths.** Both record kinds share an outer shape; a cycle record carries
per-stage detail from `state.json`, a lane record carries start, end, PR number, and churn. A viewer
renders both from one file.

## Out of Scope

Each of these was considered and cut, with the reason:

- **Token and cost estimation.** The source item asked for it. An agent cannot measure its own token
  usage from inside a skill, so any figure would be an estimate of an estimate, and it is the most
  expensive part of the original milestone with the weakest payoff. Dropped until something concrete
  needs it.
- **Counting `/dev:debt` invocations.** Also from the source item. `dev:debt` is not part of a cycle,
  so counting its invocations means instrumenting a skill outside the thing being measured.
- **New per-stage instrumentation.** The original milestone assumed the stamps were missing. They are
  not — see Technical Constraints. Only the two gaps in Scope 2 are real.
- **Backfilling past cycles.** The data is already deleted. Merge dates and PR numbers could be
  reconstructed from git, but per-stage detail cannot. The ledger starts empty and grows forward.
- **The viewer itself.** Milestone 3 (`lifecycle-viewer`), which this unblocks.
- **A schema-decision architecture cycle.** The original Milestone 2 scoped `telemetry-schema` as an
  architecture cycle producing ADRs, then `telemetry-instrumentation` as a second cycle. Grounding
  showed most instrumentation already exists and the only blocking gap is persistence, so the two
  items collapse into this one feature cycle. **This cycle updates the plan to say so.**

## Success Criteria

1. After `dev:done` completes, the finished cycle's metrics are readable from
   `docs/dev/telemetry/cycles.jsonl` without reconstructing anything from git history.
2. The record is written **before** Step 7's `rm -rf`, and a failure to write it does not leave the
   cycle half-torn-down.
3. Every stage of a completed standard cycle has both a start and an end stamp in its record —
   including `pr` and `done`, which lack them today.
4. A `/dev:fix merge` appends a lane record whose start and end come from git, with **no state
   written during the lane run itself**.
5. The two record kinds are distinguishable by a field, so a reader never averages a lane run
   together with a cycle by accident.
6. Running `dev:done` twice on the same cycle does not append two records for it.
7. `docs/dev/telemetry/` is created if absent, and its absence never fails a cycle.

## Happy Path

1. A cycle runs normally; every stage stamps its own start and end into `state.json` as it does today.
2. `dev:pr` records `pr_start` and `pr_end` around its own work.
3. `dev:done` merges, checks off the plan, flushes debt — then stamps `done`, reads `state.json`, and
   appends one line to `docs/dev/telemetry/cycles.jsonl`.
4. That append is committed and pushed with the teardown commit, so it reaches the integration branch
   by the same path every other closeout write uses.
5. Step 7's `rm -rf` removes the cycle directory. The metrics are already out.
6. Separately: a `/dev:fix` lane run ends at `/dev:fix merge`, which reads the branch's first commit
   date and the merge commit date from git and appends a lane record.

## Edge Cases

- **The ledger append fails** (disk, a bad `state.json`). The cycle must not be left half-torn-down —
  the append is attempted before `rm -rf`, and a failure reports and stops rather than proceeding to
  destroy the data it failed to save.
- **`dev:done` re-entry.** The tail is documented as idempotent and re-runnable. A second run must not
  append a duplicate record; the write is guarded on the feature already being present in the ledger.
- **Two cycles finish near-simultaneously.** Both append to the same file and the second push
  conflicts. Append-only makes this resolvable by keeping both lines — never by picking a side. Worth
  noting the risk is currently theoretical: every repo shows a single worktree, and the one cycle pair
  this repo's plans called "genuinely parallelizable" never actually overlapped.
- **A lane run whose PR is never merged.** `/dev:fix merge` never runs, so no record is appended.
  Correct: unmerged work is not a completed run.
- **A lane record's start is its first commit**, which is *after* grounding and triage. The figure
  runs short and must not be compared against a cycle's `spec_start` as though the two measured the
  same thing. The record names which basis it used.
- **A legacy in-place cycle** (`worktreePath: null`). `$WORKDIR` is the primary checkout, but the
  ledger path is the same repo-relative location, so no special case is needed — worth confirming at
  Plan rather than assuming.
- **`docs/dev/telemetry/` does not exist** — first run in any repo. Create it writer-side, the same
  discipline `docs/backlog/` already uses.

## Audience

Single operator (awilliamsbuilds) running `/dev` across five personal repos. The ledger is a local
committed artifact, not a service; nothing here may assume a database, a daemon, or network access.

## Technical Constraints

- **The stamps mostly exist already.** Verified this stage: `spec`, `shape`, `plan`, `build`, and
  `validate` each write `<stage>_start` and `<stage>_end`. `pr` writes only `pr_created`. `done`
  writes nothing. The governing plan's claim that "only `spec` has one today" is **false** and is
  corrected by this cycle.
- **`state.json` is deleted at Step 7** — `rm -rf "$WORKDIR/docs/dev/<feature>/"`. This is the whole
  reason the cycle exists, and it fixes the ordering: the ledger write must precede it.
- **`/dev:fix` writes no `state.json` by design.** Its record must therefore be derived, not stored.
  Verified derivable: for PR #94, the branch's first commit (`2026-09-06T04:06Z`) and the merge commit
  (`2026-09-06T17:19Z`) are both readable after the fact, along with commit count and churn.
- **`dev:done`'s closeout commits already push to the integration branch** through its
  `push_integration` helper, so the ledger append has an existing path to `main` and needs no new one.
- **The repo is markdown and stdlib Python only.** No new runtime dependency may be introduced.

## Dependencies

Milestone 2 of `docs/dev/product-plans/dev-observability.md`. Milestone 1 (`backlog-viewer`) is
merged. Milestone 3 (`lifecycle-viewer`) depends on this cycle and cannot start until the ledger
exists and has records in it.

## UI Needed

No. All deliverables are skill markdown plus one data file. The viewer that renders it is Milestone 3.

---
*Auto-filled dimensions: none.*
*Grounding inventory: `grep -rn stage_timestamps plugins/dev/skills/*/SKILL.md` → written by spec,
shape, plan, build, validate (both `_start` and `_end` each), plus `pr_created` in `pr` and nothing in
`done` — disproving the plan's "only `spec` has one today"; `grep -rho 'metrics\.[a-z_.]*'` → 16
distinct keys, no token or cost key anywhere; `grep -rin token|cost|usage` across skills and
references → no existing cost tracking, all hits are unrelated senses of "token"; `dev:done` Step 7
confirmed as `rm -rf "$WORKDIR/docs/dev/<feature>/"` followed by a commit, so `state.json` does not
survive; `fix/SKILL.md` confirmed to write no `state.json` (its own `## Purpose` states it);
`dev:reflect` Step 1 confirmed as the sole reader of `metrics` today; derivability of a lane record
probed live against merged PR #94 → first-commit and merge-commit dates, commit count, and
`+153/-10 across 5 files` all readable post-merge; `git worktree list` across all five `/dev` repos →
one worktree each, so concurrent-cycle contention is currently theoretical.*
