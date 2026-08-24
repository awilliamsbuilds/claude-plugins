# Plan Linkage
*Branch: feature/plan-linkage · Confidence: 90% — Ready · 2026-08-23*
*Cycle type: feature · Tier: standard*

## Intent

A multi-milestone project loses track of itself between cycles. The human running it cannot tell,
at the start of a session, which milestone is current and what comes next — so the order drifts.
It has already happened once: Milestone 2 of `dev-fast-path` was delivered as `entry-adapters`,
absorbing the item as written, and nothing noticed.

The root cause is a missing lookup: **given a feature name, `/dev` cannot determine which product
plan governs it.** Two defects follow from that, and both are fixed here.

1. **Nothing checks the order.** `/dev` Step 6 renders the milestone map and `dev:done` Step 8 prints
   the next command — but only if you enter through those commands. Starting work by naming a feature
   (`/dev:spec "<name>"`, `/dev:fix "<name>"`) bypasses both, and that is the common entry. This
   session began that way.
2. **The check-off depends on memory.** A cycle that is a milestone item never sets
   `state.json.product_plan`, so `dev:done` Step 3 skips the check-off (verified:
   `done/SKILL.md:135`) and the plan under-reports its own progress. `autopilot-resume-stage`'s box
   had to be ticked by hand. This cycle hit it live — `product_plan` was set manually at Spec because
   no code path sets it.

This cycle is **Milestone 4a** of `dev-process-hardening`, split out from the original Milestone 4 on
a cold reviewer's right-sizing blocker. The worktree half — keying the cycle worktree on the
governing plan — becomes **Milestone 4b** (`plan-scoped-worktree`) and consumes the lookup this
cycle builds. The split is why the prerequisite chain the original spec described ("defect 2 is a
hard prerequisite for defect 3") is now expressed as cycle ordering rather than as one scope.

## Scope

**1. Resolve the governing plan for a named feature.** A new lookup — scan
`docs/dev/product-plans/*.md` for a milestone item matching the feature name — used by both
deliverables below and, later, by Milestone 4b. This is the mechanism the cycle adds; the rest are
its consumers.

**Two-plan collision is defined behavior, not an open question.** When a name matches items in more
than one plan, the lookup returns **no plan** and prints both matches. The cycle proceeds unlinked
rather than guessing, and the human resolves it. No overlap exists today — `dev-observability` and
`dev-process-hardening` have disjoint item names — but the contract is stated so a builder never has
to invent it.

**2. Set `state.json.product_plan` on plan-item cycles.** `dev:spec` Step 6 gains a path (C): when
the feature being specced matches an item in exactly one product plan, record that plan's path.
`dev:done` Step 3 then checks the box and bumps the cycles-completed count without anyone
remembering to.

Path (C) slots into the existing precedence, which currently has no arm for this case: a cycle that
is itself product-scale takes path (A) and authors its own plan; else a nested cycle under a
plan-bearing parent inherits at path (B); else — new — a cycle whose name matches an item in exactly
one existing plan adopts it at path (C); else `product_plan` stays `null`.

Adopts `debt-plan-item-cycles-never-set-product-plan`, named in the governing plan as this
milestone's second source and required to be disposed of explicitly.

**3. Order-mismatch check at the two entry points.** `dev:spec` and `dev:fix`, when started with a
feature name, compare that name against the governing plan's next unchecked item:

```
Plan dev-process-hardening is 4/5.
Next up is plan-scoped-worktree, not telemetry-schema.
Continue anyway, or switch?
```

**When it fires — the exhaustive rule.** The mismatch fires **only** when the name matches an item in
a live plan and that item is not the plan's next unchecked item. A name matching the next item prints
one confirming line. A name matching **no** item in any plan prints nothing, whether or not a plan is
live — this is the ordinary standalone cycle, and roughly half of recent cycles are standalone. With
no live plan at all, nothing prints.

That last clause is load-bearing: without it every `/dev:fix "drop the redundant prefix"` in a
plan-bearing repo would stop and ask for confirmation, which is the same "trains the reader to skip
it" failure that keeps the passive plan line out of mid-cycle stages.

The check never refuses. It turns an accidental skip into a deliberate one.

## Out of Scope

- **Keying the cycle worktree on the governing plan** — the original Milestone 4, now Milestone 4b
  (`plan-scoped-worktree`), which consumes this cycle's lookup. Split out on a right-sizing blocker:
  it rewrites the `WORKDIR` resolution block in ten skills plus `dev:spec` Step 6 create-or-reuse,
  an occupancy fallback, `dev:done` Step 7's teardown, and plan-tree removal at Step 3b. Four
  findings from this cycle's cold review belong to it and are recorded in the governing plan's 4b
  entry so they are not lost.
- **A `## Current Project` section in CLAUDE.md.** Would cross the session boundary with no action at
  all, but adds a tracked section churning in every cycle's PR diff. The entry-point check covers the
  paths that matter.
- **A passive plan line at mid-cycle stages** (shape, plan, build, validate, pr). Six or seven
  repetitions per cycle is the pattern that trains the reader to skip it.
- **Seeding a new worktree's ignored dependency directories from the primary checkout.** A cheaper
  route to Milestone 4b's saving that would also work for non-plan cycles. Not adopted; worth
  recording separately.
- **Forcing every cycle to belong to a plan.** Roughly half of recent cycles are standalone and
  report no problem.

## Success Criteria

1. A cycle whose feature name matches an item in exactly one product plan reaches `dev:done` with
   `state.json.product_plan` set, and Step 3 checks its box with no manual edit.
2. Starting `/dev:spec` or `/dev:fix` with a name that is an item in a live plan but not that plan's
   next unchecked item prints the mismatch and asks for confirmation.
3. Starting with the plan's next item prints one confirming line.
4. Starting with a name that is in no plan prints nothing — verified with a live plan present and
   with none.
5. A name matching items in two plans leaves `product_plan` null and prints both matches.
6. `dev:done` Step 3's check-off runs on a plan-item cycle without the operator editing the plan file.

## Happy Path

1. `/dev:spec "plan-scoped-worktree"` — the lookup finds the item in `dev-process-hardening`,
   confirms it is the plan's next unchecked item, and prints one confirming line.
2. `dev:spec` Step 6 path (C) sets `state.json.product_plan` from the lookup, not by hand.
3. The cycle runs unchanged through every stage — no worktree behavior differs from today.
4. `dev:done` Step 3 reads `product_plan`, ticks the item, and bumps the cycles-completed count.
5. Step 8 prints the milestone map and the next command, as it does today.

## Edge Cases

- **A name matching items in two plans** — defined in Scope 1: return no plan, print both matches,
  proceed unlinked.
- **A plan item whose name differs from the cycle's feature name.** The lookup matches on the item
  name as written in the plan; a cycle deliberately named differently simply does not link, and
  behaves exactly as a standalone cycle does today.
- **The plan's next unchecked item is ambiguous** — several unchecked items in the same milestone
  (Milestone 1 of this very plan had two). "Next" means the first unchecked item in file order; a
  name matching *any* unchecked item in the plan is not a mismatch, since order within a milestone
  is not binding.
- **`dev:fix` invoked with free text rather than a feature name.** The fast path's argument is often
  a sentence, not a slug. Only an argument that matches a plan item can mismatch; free text matches
  nothing and prints nothing.
- **A plan file present but malformed** (no checkbox items). The lookup returns no plan and prints
  nothing rather than erroring — a broken plan must not block an unrelated cycle.
- **Entry-adapter forms** (`/dev:fix linear ENG-123`, `/dev:fix backlog <item>`). The name being
  checked is the resolved cycle slug, not the raw argument.

## Audience

Single operator (awilliamsbuilds) running `/dev` across five personal repos. The plugin is
repo-agnostic; nothing here may assume this repo's markdown-only shape.

## Technical Constraints

- `dev:done` Step 3 skips the check-off entirely when `product_plan` is null (`done/SKILL.md:135`) —
  this is the defect, and the fix is upstream at `dev:spec`, not here.
- `dev:spec` Step 6's precedence already has paths (A) and (B) and states "never run both"; path (C)
  must extend that rule rather than sit beside it.
- Product plans live at `docs/dev/product-plans/*.md`, one file per project, and several coexist
  (two today). The lookup must scan, not assume one.
- `dev:fix`'s four-way argument parse dispatches on whether the next token *identifies* something;
  the mismatch check runs after that parse resolves a cycle slug.

## Dependencies

Milestone 4a of `docs/dev/product-plans/dev-process-hardening.md`. Milestones 1–3 are merged
(`validate-prose-resync`, `autopilot-resume-stage`, `challenger-loop-economics`, `retro-inside-pr`).
Milestone 4b (`plan-scoped-worktree`) depends on this cycle's lookup and must follow it.

## UI Needed

No. All deliverables are skill markdown and terminal output.

---
*Auto-filled dimensions: none — Happy Path and Edge Cases were derived from the verified grounding
inventory rather than from a direct question, and were reviewed cold before this gate.*
*Grounding inventory: `grep -rl dev-worktrees plugins/` → 15 files, not the 12 the source item
claims (omits `spec`, `init`, `review`) — independently reproduced by the cold reviewer;
`grep -l 'active worktree cycle'` → 10 files carry the shared resolution block; `done/SKILL.md:135`
skips Step 3 on a null `product_plan`; `done` Step 7 runs `worktree remove --force` + `prune`;
`fix/SKILL.md:167-173` check 3 keys on `worktreePath: null` and exempts `.dev-worktrees/` by name;
`init/SKILL.md:227` declares `worktree_root` dead while `docs/dev/config.json:10` still carries it;
`dev/SKILL.md:114` and `autopilot/SKILL.md:41` both use `.dev-worktrees/*/docs/dev/*/state.json`;
read `dev` Step 6, `done` Step 8, `spec` Step 6 paths (A)/(B); probed `git worktree add` with an
already-checked-out branch → `fatal: already used by worktree`; `ls` of a freshly-cut worktree's
`docs/dev/product-plans/` → both plans present with all completed boxes ticked, disproving the
source item's "torn down and rebuilt" premise; `git status --porcelain --ignored` in a live worktree
→ empty; `git ls-files` by extension → 150 md / 8 json / 2 py / 1 html; `~/Development` sweep → 5
repos with `docs/dev/`, 3 with a lockfile, `node_modules` 186M/571M/584M, none with a
`product-plans/` directory; git log dates → `validate-prose-resync` merged 08-18 before
`autopilot-resume-stage` initialized 08-19, so the plan's "parallelizable" pair never overlapped.*
