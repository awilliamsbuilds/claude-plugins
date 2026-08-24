# /dev Process Hardening — Product Plan
*Created: 2026-08-17 · Cycles completed: 4/6*

Five recorded `docs/backlog/` items about `/dev`'s own process, grouped so that the cheap fixes which
make every later cycle cheaper land first. Four of the five were surfaced by `dev:reflect` at the
close of a real cycle, which is why they are process defects rather than feature gaps.

**Ordering principle: compounding first.** Milestones 1–2 reduce what it costs to run a cycle at all
— fewer validate loops, fewer spec rounds, less spec bloat, no re-run of an approved stage. Milestones
3–4 are structural corrections that benefit from those savings, and Milestone 4 is the largest change
in the set.

**Dependency structure — two chains, not one line.** Sequencing is driven by file overlap:

```
  validate-prose-resync ──────► retro-inside-pr ─────────┐
    (validate)                    (done, reflect,        │
                                   validate)             ├──► project-scoped-worktree
  autopilot-resume-stage ─────► challenger-loop-economics┘      │
    (autopilot)                   (spec, autopilot)              ▼
                                                        4a plan-linkage
                                                        (spec, fix, done)
                                                                 │
                                                                 ▼
                                                        4b plan-scoped-worktree
                                                             (12 files)
```

Milestone 1's two cycles share no files and are genuinely parallelizable. Milestones 2 and 3 are
independent of **each other** and may run in either order, or concurrently, once their respective
Milestone 1 predecessor has merged. Everything converges on Milestone 4, which rewrites `WORKDIR`
resolution in twelve files and so must merge last.

## Milestone 1: Cheap pipeline wins
- [x] validate-prose-resync (feature)
- [x] autopilot-resume-stage (feature)

Sources: `debt-validate-fix-prose-desyncs-from-code-in-same-loop`,
`debt-autopilot-handoff-stage-not-explicit`.

Both are small and unblocked, and they touch disjoint files (`validate/SKILL.md` and
`autopilot/SKILL.md`), so they are the only pair in this plan that can run concurrently. Ordered first
because their savings compound across the remaining three cycles: the prose-resync fix would have
saved 2 of 4 validate loops on the cycle that produced it, and this repo is entirely prose, so it
fires almost every cycle.

## Milestone 2: Challenger economics
- [x] challenger-loop-economics (feature)

Source: `debt-spec-challenger-loop-lacks-blocker-kind-exit`, plus one open question folded in.

Blocked by `autopilot-resume-stage` — both edit `autopilot/SKILL.md`. Settles four related decisions
in one spec rather than spreading them across cycles that would each re-edit the same challenger
rules: the blocker-kind exit rule (a round earns another round only while blockers still take the form
*"a builder following this literally ships something broken"*), whether revision rationale belongs in
`spec.md` at all, whether an errored dispatch should advance `loops_run` or leave a stale `blockers`
value, and **whether autopilot should ignore challenger *concerns* entirely** — the last raised at
Reflect and not previously recorded as its own item.

## Milestone 3: Cycle-boundary correctness
- [x] retro-inside-pr (feature)

Source: `backlog-reflect-before-pr-merge-retire-legacy-commands`.

Blocked by `validate-prose-resync` — both edit `validate/SKILL.md`. Moves the retrospective and
decision log inside the cycle's own PR instead of landing them on the integration branch after the
merge, unreviewed. The item names the real tension the cycle must settle rather than rediscover: at
the end of Validate the PR and merge have not happened, so `pr_created`, the merge outcome, and
`dev:done` Step 4a's docs-prose reconciliation are not yet available — most retro dimensions are, and
the cycle must decide explicitly whether the merge-tail ones are deferred or dropped.

## Milestone 4a: Plan linkage
- [ ] plan-linkage (feature)

Sources: `backlog-project-context-lost-between-cycles` (human-visible half),
`debt-plan-item-cycles-never-set-product-plan`.

Split out of the original Milestone 4 on a cold reviewer's right-sizing blocker at that cycle's Spec
gate. Builds the mechanism both halves need — **given a feature name, find the product plan that
governs it** — and ships its two cheap consumers: `dev:spec` Step 6 path (C) setting
`state.json.product_plan` so `dev:done` Step 3 stops depending on the operator remembering, and an
order-mismatch check at `/dev:spec` and `/dev:fix` so naming the wrong item is a deliberate choice
rather than an accident.

Touches no worktree behavior, so it is standard tier and carries none of 4b's coordinated-edit risk.
It satisfies the first source's "Done looks like" in full: at the start of a cycle the human sees
which milestone is current and what is next, without having to remember it across a session boundary.

## Milestone 4b: Plan-scoped worktree
- [ ] plan-scoped-worktree (feature, deep)

Source: `backlog-project-context-lost-between-cycles` (the "one worktree per project" direction).
Blocked by 4a — the worktree cannot be named after the governing plan until a cycle can determine
what its governing plan is.

**The original rationale did not survive grounding and must not be restated.** The source item argues
that a per-cycle worktree means "the plan and the accumulated context persist rather than being torn
down and rebuilt." That premise is false: worktrees are cut from `origin/main` and the plan lives at
`docs/dev/product-plans/`, so a freshly created worktree already contains the plan with every
completed box ticked. Verified during 4a's Spec. Nothing was ever torn down.

**The surviving rationale is narrower and prospective.** A fresh worktree does not inherit ignored
files, so in a repo with a dependency install it needs a full reinstall per cycle. Three of the five
repos running `/dev` carry one (`node_modules` at 186M / 571M / 584M); none of them currently runs a
product plan, so the saving is real but not yet observed. Two smaller benefits do apply today: a
stable directory path across milestones, and the directory name itself as ambient evidence of which
project is in flight.

**Four findings from 4a's cold review belong to this cycle** and are recorded here rather than lost
with the split:

1. **Resolution must not derive the plan slug.** `<plan-slug>` cannot come from
   `state.json.product_plan` — that file is inside the tree being located. Resolve by glob instead:
   `$PRIMARY/.dev-worktrees/*/docs/dev/<feature>/state.json` (first hit wins; more than one hit STOPs
   and names both), then `$PRIMARY/docs/dev/<feature>/state.json` for a legacy in-place cycle. The
   glob makes the directory name irrelevant, so resolution survives `dev:done` Step 3b deleting the
   plan file at project completion — the case a slug-derivation route silently breaks. This is the
   glob `dev` Step 3 and `autopilot` already use for discovery.
2. **Concurrency needs a stated fallback.** `git worktree add` refuses a branch already checked out
   elsewhere, so a shared plan tree holds one cycle at a time. When it is occupied by an unmerged
   branch, `dev:spec` must create a per-cycle worktree instead. Without this, two cycles in one plan
   can no longer run in parallel — and adding it later means reopening all ten resolution blocks.
3. **Plan-tree removal must appear in scope, not only in the criteria.** `dev:done` Step 3b, on the
   all-`[x]` path that deletes the plan file, also removes the plan tree (`worktree remove --force` +
   `prune`) from `$PRIMARY`, after Step 2's detach has freed it.
4. **The plan's second design question needs one line, not reconstruction.** Cycle directories never
   coexist in a shared tree: one cycle occupies it at a time, and Step 7's
   `rm -rf docs/dev/<feature>/` lands on the integration branch before the next milestone branches
   from it.

Also worth weighing before building: seeding a new worktree's ignored dependency directories from the
primary checkout would capture the same saving for **every** cycle, plan-governed or not, without
changing directory identity or losing concurrency. If that turns out to be the better trade, this
milestone may close as declined rather than built.

**The second source is disposed of, not deferred.** `debt-plan-item-cycles-never-set-product-plan` is
adopted by 4a, which is the cheaper of the owners the original entry named.

---

## Notes

**No promotion back-links, deliberately.** The five source items are named per milestone above but are
**not** marked `status: promoted` / `promoted_to:`. Two reasons, both recorded defects:

1. `debt-done-promotion-close-assumes-single-source` — `dev:done` Step 3b's reverse-lookup asserts "at
   most one such match" and does not define behavior for several. `dev-observability` already violates
   that with two sources; promoting five here would make the worst case worse, at a step that runs
   once, at project completion, in the same commit that deletes the plan — unrecoverable.
2. The same item's second half: a source item satisfied by an early milestone stays `promoted` until
   the *whole* plan completes. Four of these five are paid by a single cycle each, so they would read
   `promoted` long after being done — inverting the reason `dev:debt list` surfaces that status.

Instead **each cycle closes its own source item** through the normal `## To Close` buffer at its own
`dev:done` Step 6a — the path that closed `debt-secure-tree-scoping-unsettled` cleanly. Revisit this
if `debt-done-promotion-close-assumes-single-source` is ever paid.

**Excluded on purpose: `backlog-vercel-plugin-injects-into-unrelated-work`.** It has no repo surface
(`files:` is empty by nature) — its remaining work is unregistering a stale marketplace from
`~/.claude/plugins/known_marketplaces.json` and filing an upstream matcher bug. Neither is a `/dev`
cycle. Handled outside this plan on 2026-08-17; see that item's Progress note.

**Second live plan.** `docs/dev/product-plans/dev-observability.md` is at 1/4 with `telemetry-schema`
next. The two plans share no files — that one builds viewer/telemetry surfaces, this one edits stage
skills — so they can proceed independently. `/dev` Step 6 lists both and asks which to continue.
