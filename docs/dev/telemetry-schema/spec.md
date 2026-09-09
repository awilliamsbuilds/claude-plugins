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

**1. A committed, append-only ledger.** `docs/telemetry/runs.jsonl` — one JSON object per line, one
line per completed run. `dev:done` appends the cycle's record **before** Step 7's `rm -rf`, so the
data is captured while `state.json` still exists.

Two things about that path are deliberate. It sits at `docs/telemetry/`, **not** `docs/dev/telemetry/`:
the latter is a sibling of `docs/dev/<feature>/`, so a future cycle whose slug happened to be
`telemetry` would have Step 7's `rm -rf` delete the ledger — the one artifact whose entire purpose is
surviving that command. And it is named `runs`, not `cycles`, because it holds both cycle records and
lane records (Scope 3); "cycle" would name the file after only half its contents, which is precisely
the conflation Success Criterion 5 exists to prevent.

**2. Fill the two real stamp gaps.** `dev:pr` gains `pr_start` / `pr_end` (it records only
`pr_created` today). `dev:done` gains `done_start` / `done_end` — **a pair, like the other five
stages**, captured the same way they capture theirs: `done_start` as the stage's first action,
`done_end` immediately before the ledger append.

`done_start` / `done_end` are written **into the ledger record directly, not into `state.json`.**
`dev:done` writes no `metrics.*` today, and `state.json` is deleted seconds later by the same stage —
so routing them through it would add a writer to a file already being torn down, for no reader.

**3. A lane record for `/dev:fix` runs, derived rather than written.** `/dev:fix merge` appends a
second, smaller record shape after a successful merge. Its values are **read from git**, so the lane
writes nothing while it works and its "no cycle artifacts" premise is untouched.

**The derivation is merge-commit-relative**, and the capture point is inside the merge fence, after
the merge and while the merge SHA is in hand. It cannot be branch-relative: the fence deletes the
remote and local branch and moves the checkout to the default branch, so a branch name is unusable
by the time a record could be written. Given the merge SHA:

```
start   git log --format=%cI <sha>^1..<sha>^2 | tail -1
end     git log -1 --format=%cI <sha>
count   git rev-list --count <sha>^1..<sha>^2
churn   git diff --shortstat <sha>^1 <sha>^2
```

**A merge with no second parent is recorded with a null start**, not skipped. The `ALREADY_MERGED=1`
path exists for a PR merged outside the lane, which may have been squashed — a squash leaves no
`^2`, so `count` and `churn` are unavailable and `start` cannot be derived. The run still happened
and its end is known, so the record is written with those fields null and a reason field naming why.
Skipping it would silently under-count lane work, which is the failure this scope item exists to
prevent.

**One envelope, two depths.** Both record kinds share an outer shape; a cycle record carries
per-stage detail from `state.json`, a lane record carries start, end, PR number, and churn. A viewer
renders both from one file. **The field list is Plan's first task** — this cycle skips Shape
(`UI Needed: No`), so Plan is the only stage that designs it, and Milestone 3 reads whatever it
settles.

**4. Update the governing plan.** Milestone 2 of `docs/dev/product-plans/dev-observability.md`
currently lists two items — `telemetry-schema (architecture)` and `telemetry-instrumentation
(feature)` — and asserts that per-stage `_start` exists on `spec` alone. This cycle collapses those
two items into one, corrects that claim, and adjusts the header count accordingly. Without this edit
`telemetry-instrumentation` strands: `dev:done` Step 3 checks off only the item matching
`state.json.feature`, so the second line would sit unchecked with no cycle ever coming for it.

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
  items collapse into this one feature cycle — the plan edit that records this is Scope 4.

## Success Criteria

1. After `dev:done` completes, the finished cycle's metrics are readable from
   `docs/telemetry/runs.jsonl` without reconstructing anything from git history.
2. The record is written **before** Step 7's `rm -rf`, and a failure to write it does not leave the
   cycle half-torn-down.
3. **Every stage the cycle actually ran** has both a start and an end stamp in its record — including
   `pr` and `done`, which lack them today. A stage listed in `state.json.skipped[]` is absent from the
   record rather than present with nulls.
4. A `/dev:fix merge` appends a lane record whose values are derived from the merge commit, with **no
   state written during the lane run itself**. A squash merge with no second parent still produces a
   record, with the underivable fields null and a reason given.
5. The two record kinds are distinguishable by a field, so a reader never averages a lane run
   together with a cycle by accident.
6. **Neither writer double-appends on re-entry.** Running `dev:done` twice on the same cycle appends
   one record; re-running `/dev:fix merge` after a partial failure appends one lane record.
7. `docs/telemetry/` is created if absent, and its absence never fails a cycle.
8. Milestone 2 of `dev-observability.md` reads as one item, its `_start` claim is corrected, and the
   header count matches — verifiable by reading the plan after this cycle's PR merges.

## Happy Path

1. A cycle runs normally; every stage stamps its own start and end into `state.json` as it does today.
2. `dev:pr` records `pr_start` and `pr_end` around its own work.
3. `dev:done` stamps `done_start` as its first action, then merges, checks off the plan, and flushes
   debt.
4. Before Step 7, `dev:done` stamps `done_end`, reads `state.json`, appends one line to
   `docs/telemetry/runs.jsonl`, and commits it under **its own pathspec** —
   `-- docs/telemetry/` — pushed by the same `push_integration` helper the stage already uses. Step
   7's teardown commit and its `docs/dev/<feature>/` pathspec are untouched.
5. Step 7's `rm -rf` removes the cycle directory. The metrics are already out.
6. Separately: a `/dev:fix` lane run ends at `/dev:fix merge`, which — inside the merge fence, holding
   the merge SHA — derives start, end, commit count, and churn from that commit and appends a lane
   record.

## Edge Cases

- **The ledger append fails** (disk, a bad `state.json`). The cycle must not be left half-torn-down —
  the append is attempted before `rm -rf`, and a failure reports and stops rather than proceeding to
  destroy the data it failed to save.
- **`dev:done` re-entry.** Guard the cycle append on `feature` already being present in the ledger, so
  a second run appends nothing.
- **`/dev:fix merge` re-entry.** That tail **is** documented idempotent and safe to re-run
  (`fix/SKILL.md` Step 7), and its `ALREADY_MERGED=1` path exists precisely so a partial failure can
  be resumed — it re-runs cleanup and reaches the closeout again. Guard the lane append on
  `pr_number` already being present.
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
- **`docs/telemetry/` does not exist** — first run in any repo. Create it writer-side, the same
  discipline `docs/backlog/` already uses.

## Audience

Single operator (awilliamsbuilds) running `/dev` across five personal repos. The ledger is a local
committed artifact, not a service; nothing here may assume a database, a daemon, or network access.

## Technical Constraints

- **The stamps mostly exist already.** Verified this stage: `spec`, `shape`, `plan`, `build`, and
  `validate` each write `<stage>_start` and `<stage>_end`. `pr` writes only `pr_created`. `done`
  writes nothing. The governing plan's claim that "only `spec` has one today" is **false** and is
  corrected by Scope 4.
- **`state.json` is deleted at Step 7** — `rm -rf "$WORKDIR/docs/dev/<feature>/"`. This is the whole
  reason the cycle exists, and it fixes the ordering: the ledger write must precede it.
- **Step 7's commit is pathspec-scoped and must stay that way.** Both its `git add -A
  docs/dev/<feature>/` and its `commit -- docs/dev/<feature>/` exclude anything outside the cycle
  directory, and `dev:done` states that scoping is load-bearing — it stops unrelated staged work being
  swept into a "clean up working directory" commit. The ledger therefore needs its own commit, not a
  widened pathspec.
- **`/dev:fix` writes no `state.json` by design.** Its record must therefore be derived, not stored.
  Verified derivable: for PR #94, the merge commit's parents yield first-commit date
  `2026-09-06T04:06Z`, merge date `2026-09-06T17:19Z`, 5 commits, and `+153/-10 across 5 files`.
- **`/dev:fix merge` deletes both branches and moves the checkout** before its closeout hook runs; the
  hook's own comments state that neither `BRANCH` nor `ITEM` can be re-derived past that point. Any
  derivation must therefore be merge-SHA-relative, per Scope 3.
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
`done` — disproving the plan's "only `spec` has one today"; `grep -rho 'metrics\.[a-z_.]*'` → 15
distinct keys plus a bare `metrics.` prefix, no token or cost key anywhere; `grep -rin token|cost|usage`
across skills and references → no existing cost tracking, all hits unrelated senses of "token";
`dev:done` Step 7 confirmed as `rm -rf "$WORKDIR/docs/dev/<feature>/"` followed by an `add -A` and a
`commit` **both pathspec-scoped to that directory**, so `state.json` does not survive and the ledger
cannot ride that commit; `fix/SKILL.md:16` confirmed the lane writes no `state.json`, restated at 911,
1268 and 1281; `dev:reflect` Step 1 is the sole **consumer** of `metrics` — `dev:done` Step 1 and
`dev:pr` Step 5d read `state.json` wholesale but interpret nothing; derivability of a lane record
probed live against merged PR #94 → merge `3b75a6e`, first branch commit `78dfbf0`, 5 commits,
`+153/-10 across 5 files`, all readable post-merge from the merge commit's parents; `git worktree list`
across all five `/dev` repos → one worktree each, so concurrent-cycle contention is currently
theoretical.*
