# /dev Process Hardening — Product Plan
*Created: 2026-08-17 · Cycles completed: 0/5*

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
  autopilot-resume-stage ─────► challenger-loop-economics┘      (12 files)
    (autopilot)                   (spec, autopilot)
```

Milestone 1's two cycles share no files and are genuinely parallelizable. Milestones 2 and 3 are
independent of **each other** and may run in either order, or concurrently, once their respective
Milestone 1 predecessor has merged. Everything converges on Milestone 4, which rewrites `WORKDIR`
resolution in twelve files and so must merge last.

## Milestone 1: Cheap pipeline wins
- [ ] validate-prose-resync (feature)
- [ ] autopilot-resume-stage (feature)

Sources: `debt-validate-fix-prose-desyncs-from-code-in-same-loop`,
`debt-autopilot-handoff-stage-not-explicit`.

Both are small and unblocked, and they touch disjoint files (`validate/SKILL.md` and
`autopilot/SKILL.md`), so they are the only pair in this plan that can run concurrently. Ordered first
because their savings compound across the remaining three cycles: the prose-resync fix would have
saved 2 of 4 validate loops on the cycle that produced it, and this repo is entirely prose, so it
fires almost every cycle.

## Milestone 2: Challenger economics
- [ ] challenger-loop-economics (feature)

Source: `debt-spec-challenger-loop-lacks-blocker-kind-exit`, plus one open question folded in.

Blocked by `autopilot-resume-stage` — both edit `autopilot/SKILL.md`. Settles four related decisions
in one spec rather than spreading them across cycles that would each re-edit the same challenger
rules: the blocker-kind exit rule (a round earns another round only while blockers still take the form
*"a builder following this literally ships something broken"*), whether revision rationale belongs in
`spec.md` at all, whether an errored dispatch should advance `loops_run` or leave a stale `blockers`
value, and **whether autopilot should ignore challenger *concerns* entirely** — the last raised at
Reflect and not previously recorded as its own item.

## Milestone 3: Cycle-boundary correctness
- [ ] retro-inside-pr (feature)

Source: `backlog-reflect-before-pr-merge-retire-legacy-commands`.

Blocked by `validate-prose-resync` — both edit `validate/SKILL.md`. Moves the retrospective and
decision log inside the cycle's own PR instead of landing them on the integration branch after the
merge, unreviewed. The item names the real tension the cycle must settle rather than rediscover: at
the end of Validate the PR and merge have not happened, so `pr_created`, the merge outcome, and
`dev:done` Step 4a's docs-prose reconciliation are not yet available — most retro dimensions are, and
the cycle must decide explicitly whether the merge-tail ones are deferred or dropped.

## Milestone 4: Persistent project context
- [ ] project-scoped-worktree (feature, deep)

Source: `backlog-project-context-lost-between-cycles`.

Blocked by everything above — it changes the identity of the cycle directory from `<feature>` to a
plan slug, so **12 files** that hardcode `.dev-worktrees/<feature>/` or `.dev-worktrees/*/` all move
(`build`, `debt`, `dev`, `autopilot`, `done`, `fix`, `reflect`, `pr`, `plan`, `secure`, `shape`,
`validate`). Two design questions belong in its spec rather than in flight: what happens when cycles
sharing one worktree need different branches checked out, and whether several cycles'
`docs/dev/<feature>/` directories coexist in the shared tree.

Worth stating plainly: **this milestone fixes the problem that made this plan necessary.** The item
records the user losing track of which milestone is current and unintentionally skipping order — which
this plan is itself exposed to until Milestone 4 lands.

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
