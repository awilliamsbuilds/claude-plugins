# Project-Scoped Worktree
*Branch: feature/project-scoped-worktree · Confidence: 90% — Ready · 2026-08-23*
*Cycle type: feature · Tier: deep*

## Intent

A multi-milestone project loses track of itself between cycles. The human running it cannot tell,
at the start of a session, which milestone is current and what comes next — so the order drifts.
It has already happened once: Milestone 2 of `dev-fast-path` was delivered as `entry-adapters`,
absorbing the item as written, and nothing noticed.

Three separate defects produce that outcome, and this cycle fixes all three because they share one
missing mechanism: **given a feature name, `/dev` cannot determine which product plan governs it.**

1. **Nothing checks the order.** `/dev` Step 6 renders the milestone map, and `dev:done` Step 8
   prints the next command — but only if you go through those commands. Starting work by naming a
   feature (`/dev:spec "<name>"`, `/dev:fix "<name>"`) bypasses both, and that is the common entry.
2. **The check-off depends on memory.** A cycle that is a milestone item never sets
   `state.json.product_plan`, so `dev:done` Step 3 skips the check-off entirely and the plan
   under-reports its own progress. `autopilot-resume-stage`'s box had to be ticked by hand. This
   cycle hit it live — `product_plan` was set manually at Spec because no code path sets it.
3. **Cycle infrastructure is rebuilt per milestone.** Each cycle creates and destroys its own
   worktree. In this repo that is 150 markdown files and costs nothing, but `/dev` runs in five
   repos and three carry a dependency install (`node_modules` at 186M / 571M / 584M) that a fresh
   worktree does not inherit, because `git worktree add` does not copy ignored files.

Defect 2 is a hard prerequisite for defect 3: a worktree cannot be named after the governing plan
until the cycle knows what its governing plan is. Defect 1 consumes the same lookup. That shared
dependency is why these ship together rather than as three cycles.

## Scope

**1. Resolve the governing plan for a named feature.** A new lookup — scan
`docs/dev/product-plans/*.md` for a milestone item matching the feature name — used by all three
deliverables below. This is the mechanism the cycle actually adds; the rest are its consumers.

**2. Set `state.json.product_plan` on plan-item cycles.** `dev:spec` Step 6 gains a path (C):
when the feature being specced matches an item in an existing product plan, record that plan's path.
`dev:done` Step 3 then checks the box and bumps the cycles-completed count without anyone
remembering to. Adopts `debt-plan-item-cycles-never-set-product-plan`, named as this milestone's
second source.

**3. Key the cycle worktree on the governing plan.** A plan-governed cycle runs in
`.dev-worktrees/<plan-slug>/`, which persists across the project's milestones instead of being
rebuilt per cycle. A cycle with no governing plan keeps today's `.dev-worktrees/<feature>/` and
today's teardown, unchanged.

The `WORKDIR` resolution block in the ten skills that carry it gains a candidate ordering rather
than a single hardcoded path:

```
1. $PRIMARY/.dev-worktrees/<plan-slug>/   → plan-scoped worktree
2. $PRIMARY/.dev-worktrees/<feature>/     → per-cycle worktree (today's shape)
3. $PRIMARY/                              → legacy in-place cycle (worktreePath null)
```

Each candidate is tested for `docs/dev/<feature>/state.json`, as today — so the ordering
disambiguates itself and no candidate can false-match another cycle's tree.

**4. Automatic fallback preserves concurrency.** `git worktree add` refuses a branch already checked
out elsewhere, so a shared plan tree can hold only one cycle at a time. When the plan tree is
occupied by an unmerged branch, `dev:spec` creates a per-cycle worktree instead and the cycle
resolves at candidate 2. No flag, no decision asked of the user, and two cycles in one plan can
still run in parallel.

This is in scope specifically to avoid a second rewrite: collapsing resolution to a single
hardcoded path would mean reopening all ten blocks later to add the escape hatch.

**5. Order-mismatch check at the two entry points.** `dev:spec` and `dev:fix`, when started with a
feature name while a product plan is live, compare that name against the plan's next unchecked item
and speak up on a mismatch:

```
Plan dev-process-hardening is 4/5.
Next up is project-scoped-worktree, not telemetry-schema.
Continue anyway, or switch?
```

A match prints one confirming line. No plan, or a feature in no plan while no plan is live, prints
nothing. This turns an accidental skip into a deliberate one — it never refuses.

## Out of Scope

- **A `## Current Project` section in CLAUDE.md.** Considered and declined: it would cross the
  session boundary with no action at all, but adds a tracked section churning in every cycle's PR
  diff. The announcement covers the entry paths that matter.
- **A passive plan line at mid-cycle stages** (shape, plan, build, validate, pr). Six or seven
  repetitions per cycle is the pattern that trains the reader to skip it.
- **Seeding a new worktree's ignored dependency directories from the primary checkout.** Raised as
  a cheaper route to the same saving that would work for non-plan cycles too. Not adopted here;
  worth recording separately.
- **Forcing every cycle to belong to a plan.** Roughly half of recent cycles are standalone and
  report no problem.
- **Changing behavior for legacy in-place cycles** (`worktreePath` null). Candidate 3 is unchanged.
- **Retiring the dead `worktree_root` config key.** `dev:init` line 227 declares it dead and no
  longer emits it, but this repo's `config.json` still carries it. Unrelated to this change.

## Success Criteria

1. A cycle whose feature name matches an item in a product plan reaches `dev:done` with
   `state.json.product_plan` set, and Step 3 checks its box with no manual edit.
2. Starting `/dev:spec` or `/dev:fix` with a feature name that is not the live plan's next item
   prints the mismatch and asks for confirmation. Starting with the next item prints one confirming
   line. With no live plan, both print nothing.
3. A second cycle in the same plan, started while the first is unmerged, gets its own worktree and
   both cycles run to PR without either failing to resolve `WORKDIR`.
4. A standalone cycle's worktree path, creation, and teardown are byte-identical to today.
5. `grep -rn 'dev-worktrees' plugins/` shows no site still assuming the directory name equals the
   feature name, except where that is candidate 2's deliberate meaning.
6. A plan-scoped worktree survives its cycles' `dev:done` runs and is removed when the plan
   completes.

## Happy Path

1. `/dev:spec "project-scoped-worktree"` — the lookup finds the item in `dev-process-hardening`,
   confirms it is the plan's next item, and prints one line.
2. `state.json.product_plan` is set from the lookup, not by hand.
3. The worktree resolves to `.dev-worktrees/dev-process-hardening/`, creating it if absent and
   reusing it if the previous milestone left it behind.
4. Stages run; every skill resolves `WORKDIR` through candidate 1.
5. `dev:done` merges, checks off Milestone 4, removes `docs/dev/<feature>/`, and leaves the plan
   tree in place on the integration branch.
6. The next milestone starts in the same directory with no `worktree add` and no dependency
   reinstall.

## Edge Cases

Derived from the grounding inventory rather than asked, and worth confirming at the gate:

- **A feature name appearing in two product plans.** No overlap exists today (both live plans have
  disjoint item names), but the lookup needs a defined answer rather than first-match-wins.
- **The plan tree is dirty or mid-rebase** when the next milestone starts. `dev:done` Step 7 already
  guards teardown against a rebase in progress; reuse needs the equivalent guard.
- **A cycle resumed after its plan tree was removed** — resolution falls through to candidate 2,
  finds nothing, and must stop rather than silently starting fresh, matching `dev:autopilot`'s
  existing rule for a validated feature with no cycle.
- **The plan completes mid-session.** `dev:done` Step 3b deletes the plan file; the tree it names
  must still be removable.
- **`dev:fix` running inside a plan tree.** Its check 3 refuses only on a legacy in-place cycle and
  explicitly exempts `.dev-worktrees/`; a plan tree must stay exempt.
- **A feature in no plan while a plan is live.** Prints nothing — this is a standalone cycle, not a
  mismatch.

## Audience

Single operator (awilliamsbuilds) running `/dev` across five personal repos. The plugin is
repo-agnostic; the change must not assume this repo's markdown-only shape.

## Technical Constraints

- `git worktree add` refuses a branch already checked out in another worktree (verified:
  `fatal: 'feature/...' is already used by worktree at ...`). This is what forces criterion 3's
  fallback.
- Worktrees do not inherit ignored files, so a fresh tree in a dependency-carrying repo needs a
  full install. This is the entire cost case for deliverable 3.
- Fifteen files reference `.dev-worktrees`; ten carry the identical numbered resolution block.
- The discovery globs in `dev` Step 3 and `autopilot` are already `.dev-worktrees/*/…` and tolerate
  any directory name; only the resolution block hardcodes `<feature>`.

## Dependencies

Milestone 4 of `docs/dev/product-plans/dev-process-hardening.md`, blocked by Milestones 1–3 — all
merged (`validate-prose-resync`, `autopilot-resume-stage`, `challenger-loop-economics`,
`retro-inside-pr`).

## UI Needed

No. All deliverables are skill markdown and terminal output.

---
*Auto-filled dimensions: none — Happy Path and Edge Cases were derived from the verified grounding
inventory rather than from a direct question, and are flagged in-section for confirmation.*
*Grounding inventory: `grep -rl dev-worktrees plugins/` → 15 files, not the 12 the source item
claims (omits `spec`, `init`, `review`); `grep -l 'active worktree cycle'` → 10 files carry the
shared resolution block; read `spec` Step 6 (creation, rationale "so concurrent sessions never
contend"), `done` Step 3 (`product_plan` null ⇒ skip check-off) and Step 7 (`rm -rf` + `worktree
remove --force`), `dev` Step 6, `done` Step 8, `fix` check 3, `init` line 227 (`worktree_root`
dead); probed `git worktree add` with an already-checked-out branch → `fatal: already used by
worktree`; `ls .dev-worktrees/project-scoped-worktree/docs/dev/product-plans/` → both plans present
with all four completed boxes ticked in a tree created minutes earlier, disproving the source item's
"torn down and rebuilt" premise; `git status --porcelain --ignored` in a live worktree → empty;
`git ls-files` by extension → 150 md / 8 json / 2 py / 1 html, no build output; `~/Development`
sweep → 5 repos with `docs/dev/`, 3 with a lockfile, `node_modules` 186M/571M/584M, none with a
`product-plans/` directory; git log dates → `validate-prose-resync` merged 08-18 before
`autopilot-resume-stage` initialized 08-19, so the plan's "parallelizable" pair never actually
overlapped.*
