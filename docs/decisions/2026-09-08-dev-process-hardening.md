# /dev Process Hardening — Project Decision Log
*2026-09-08 · Project closed · 5 of 6 milestones built, 1 declined*

Project-level log for `docs/dev/product-plans/dev-process-hardening.md`, written at closeout because
the plan file is deleted on completion and nothing else records the project as a whole. The five
per-cycle logs hold the detail; this holds the arc and the one decision that has no cycle behind it.

## What the project was

Five recorded `docs/backlog/` items about `/dev`'s own process, sequenced so the fixes that make
every later cycle cheaper landed first. Four of the five were surfaced by `dev:reflect` at the close
of a real cycle — process defects found by running the process, not feature gaps.

## What was built

| Milestone | Cycle | Log |
|---|---|---|
| 1 | `validate-prose-resync` | `2026-08-19-validate-prose-resync.md` |
| 1 | `autopilot-resume-stage` | `2026-08-20-autopilot-resume-stage.md` |
| 2 | `challenger-loop-economics` | `2026-08-22-challenger-loop-economics.md` |
| 3 | `retro-inside-pr` | `2026-08-23-retro-inside-pr.md` |
| 4a | `plan-linkage` | `2026-08-23-plan-linkage.md` |

A sixth change shipped outside the plan, after 4a and because of it: `plan-order-near-miss` (PR #94)
added the near-miss suggestion to the plan-order check's silent arm, closing the rename hole 4a left
open. It ran as a `/dev:fix` lane rather than a milestone.

## Milestone 4b — declined, not abandoned

`plan-scoped-worktree` was to key the cycle worktree on the governing plan rather than on the
feature. It is **declined**, and the reasoning is the point of this log.

**Its original rationale was already dead.** The source item argued a per-cycle worktree means "the
plan and the accumulated context persist rather than being torn down and rebuilt." That premise was
disproven during 4a's Spec: worktrees are cut from `origin/main` and the plan lives at
`docs/dev/product-plans/`, so a freshly created worktree already contains the plan with every
completed box ticked. Nothing was ever torn down. The plan file was amended at the time to say so.

**The surviving rationale was a dependency-install saving, and it does not survive measurement
either.** Measured on this machine, 2026-09-05:

```
cp -c -R node_modules (584 MB, 31,976 files)  →  5.1 seconds, 9 MB of real disk
```

`cp -c` on APFS is copy-on-write; the 9 MB is directory metadata. Seeding a fresh worktree's ignored
dependency directories from the primary checkout therefore captures the same saving for **every**
cycle — plan-governed or not — without changing directory identity and without losing concurrency.

**And the milestone's target case is empty.** 4b's benefit requires a repo that both runs a product
plan and carries a dependency install. Across the five repos running `/dev`:

- `claude-plugins` — runs both product plans, **no** dependencies (150 md / 8 json / 2 py / 1 html)
- `cash-flow-forecast`, `tempo-native`, `wishlist` — 186M / 571M / 584M of `node_modules`, **no**
  product plan
- `canopy-ios` — no lockfile at all

The one repo where 4b would change anything is the one where it saves nothing.

**Against that:** the change rewrites `WORKDIR` resolution in ten files that carry the shared
resolution block, plus `dev:spec` Step 6's create-or-reuse, an occupancy fallback, `dev:done` Step 7's
teardown, and plan-tree removal at Step 3b — the largest coordinated edit in the plan. `git worktree
add` also refuses a branch checked out elsewhere, so a shared plan tree holds one cycle at a time and
concurrency needs its own stated fallback to recover.

Two smaller benefits are real and are being given up: a stable directory path across a project's
milestones, and the directory name as ambient evidence of which project is in flight. 4a's
entry-point check covers the second at lower cost.

**Carried forward:** dependency seeding is recorded as `backlog-seed-worktree-dependency-dirs`. The
four cold-review findings the plan held for 4b (glob-based resolution, the concurrency fallback,
plan-tree removal at Step 3b, and the shared-tree occupancy note) are recorded there too — they are
the design work 4b had already done, and they apply to any future revival.

## What the project changed about how /dev runs

- **Validate got cheaper.** Prose re-sync inside the fix loop; the cycle that surfaced it would have
  saved 2 of its 4 loops.
- **Autopilot resumes honestly.** `completed[]` is the authority, `handoff_at` records where a gated
  cycle was taken over, and no row stage is exempt from re-execution.
- **The challenger stops inflating.** Blocker is a two-member class; concerns are countable, foldable,
  and never loop-extending; an errored dispatch does not advance the loop.
- **The retrospective lands inside the PR** it describes, rather than on the integration branch after
  the merge, unreviewed.
- **A cycle links itself to its plan.** `dev:spec` Step 6 path (C) sets `product_plan`, so `dev:done`
  ticks the box without anyone remembering, and both entry points check milestone order.

## Two gaps this closeout exposed

Both were worked around by hand here and are worth fixing if another multi-milestone project runs.

1. **There is no declined state for a milestone.** Checkboxes are `[ ]` or `[x]`, and completion
   detection is "every checkbox is `[x]`". 4b was marked `[x]` with an inline `— declined` annotation
   so the plan could reach completion at all; read literally, that checkbox says "built."
2. **There is no path to close a plan outside a cycle.** `dev:done` Step 3b deletes the plan only at
   a completing cycle's Done. Declining the last milestone is not a cycle, so this closeout — the
   check-off, the deletion, the source-item close — was done by hand.

Recorded as `backlog-plan-milestone-declined-state`.

## Disposition of the six source items

Five closed through their own cycle's `dev:done` Step 6a, as the plan's `## Notes` designed —
deliberately avoiding `promoted`/`promoted_to` back-links, because
`debt-done-promotion-close-assumes-single-source` does not define behavior for several sources and
`dev-observability` already violates that assumption with two.

`backlog-project-context-lost-between-cycles` is closed here. 4a satisfied its human-visible half in
full — at the start of a cycle the operator sees which milestone is current and what is next, without
having to remember it across a session boundary — and its "one worktree per project" direction is
declined above rather than deferred.
