# Product-Plan Correction
*Branch: feature/product-plan-correction · Confidence: 90% — Ready · 2026-07-28*
*Cycle type: feature · Tier: deep*

## Intent

`/dev`'s product-plan has drifted into a role it was never meant to hold. The top-level
`docs/dev/product-plan.md` is a de-facto **persistent multi-project backlog** — it survives every
cycle (nothing deletes it) and currently spans three unrelated projects at "Cycles completed: 3/5",
with two backlog *intentions* misfiled inside it. The [backlog-debt-model ADR][adr] (Decision 7)
corrects this: a product-plan is an **ephemeral milestone carrier for a single multi-cycle project,
deleted on completion** — not a standing backlog. The standing store is now `docs/backlog/` (built
by the tech-debt-migration cycle).

This cycle implements that correction and finishes the migration the tech-debt cycle deliberately
left behind: it rehomes the two misfiled intentions, retires the stale plan file, makes product-plans
ephemeral in `dev:done`, adds the one-way `backlog → product-plan` promotion flow, and pins a durable
plan location that survives child-cycle teardown — closing the open `debt-nested-product-plan-lifetime`
entry in the process. It implements ADR Decisions **7** and the product-plan slice of **8(c)**; the
tech-debt-entry slice of Decision 8 already shipped.

[adr]: ../../decisions/2026-07-28-backlog-debt-model.md

## Scope

Four coupled deliverables — the argument bundles them and the ADR ties them together (deletion is
promotion's terminus; migration is the concrete proof of the corrected model):

1. **Migrate the two misfiled backlog intentions.** Move `debt-backfill` and `debt-linear-promotion`
   out of `docs/dev/product-plan.md` into `docs/backlog/` as `type: backlog` files
   (`backlog-debt-backfill.md`, `backlog-debt-linear-promotion.md`), following ADR Decision 8(c):
   - front-matter `type: backlog`, `scope: repo`, `status: open`, `first_recorded: 2026-07-21`
     (the plan's Created date — best available provenance), `cycles: []`, `recurrence: 0`, `files: []`
     (an intention has no defect site yet; `files` is required by schema but legitimately empty here).
   - the descriptive prose (including each item's "Depends on tech-debt-tracking" note and deferral
     rationale) transfers into the body under `What:` / `Why:`.
   - the slugs keep their historical `debt-` names even though `type: backlog` — the `type` field,
     not the slug, classifies them (ADR Decision 8(c)).
   - the three **completed** milestones (`voice-extractor`, `depersonalize-writing`,
     `tech-debt-tracking`, all `[x]`) are historical and already recorded in the cycle history and
     decision logs; they are **not** carried into the backlog (a backlog holds open intentions, not a
     changelog).

2. **Retire `docs/dev/product-plan.md`.** Once its two live items are rehomed, the file holds only the
   three historical `[x]` milestones — nothing that must survive — so it is **hard-deleted**, not
   archived. The top-level product-plan is no longer a durable multi-project list; that role is the
   backlog's.

3. **Ephemeral deletion in `dev:done`.** `dev:done` deletes a project's product-plan when the
   **project** completes — not on each child cycle's `dev:done` teardown. This is the "deleted on
   completion" behavior the corrected model requires.

4. **One-way `backlog → product-plan` promotion.** Emergent in `dev:spec` **Step 2** (Scale Detection),
   which already owns the "this is product-scale → map into cycles → write a product-plan" machinery.
   When a backlog item is picked up and specced and turns out to span cycles, promotion is that
   existing path **plus a back-link to the source item**: spawn the product-plan, set the source
   backlog item `status: promoted` and `promoted_to: <plan path>`. The flow is **one-way** — a plan
   never demotes back to a backlog item. On project completion the item moves `promoted → closed`
   (and is archived to `docs/backlog/closed/`). This activates the `promoted` status value and the
   `promoted_to` field that `references/tech-debt.md` currently marks **reserved**.

**Durable plan location (pinned).** Product-plans move to a dedicated
**`docs/dev/product-plans/<project-slug>.md`** directory — outside any single cycle's dir, so a plan
survives child-cycle `dev:done` teardown and is deleted only on project completion. This replaces the
two current locations (`docs/dev/product-plan.md` top-level, `docs/dev/<parent>/product-plan.md`
nested — the latter being the one that dies with its parent cycle). Pinning this location **closes
`debt-nested-product-plan-lifetime`**. Plan refines the exact write/delete mechanics.

**Skills changed:** `dev:spec` (Steps 2/4/6 — promotion back-link + new plan location), `dev:done`
(Step 3 check-off relocation + new project-completion deletion trigger), `dev:debt` (surface
`promoted` status), `references/tech-debt.md` (un-reserve `promoted`/`promoted_to`; document the
one-way promotion flow and ephemeral lifecycle), plus `dev:dev` if it references the plan path. Data
migration + file retirement are one-time operations Build executes.

## Out of Scope

- **The Linear-promotion feature.** `debt-linear-promotion` is a backlog *item* being migrated here,
  not built — it describes a future `/dev:debt promote <id>` that turns an entry into a Linear issue,
  which is a different mechanism from this cycle's `backlog → product-plan` promotion.
- **`debt-backfill`** — migrated as an item, not implemented.
- **The `/dev:debt add` capture verb, the inbox/convert verb, and cross-repo issue routing** — ADR
  follow-on 3, a separate cycle.
- **The tech-debt-entry migration** (Decision 8(a)/(b)) — already shipped by tech-debt-migration.
- **`debt-reflect-dogfood-pr-base`** — unrelated open item on a different surface.

## Success Criteria

- `docs/backlog/backlog-debt-backfill.md` and `docs/backlog/backlog-debt-linear-promotion.md` exist,
  `type: backlog`, `status: open`, with the intentions' prose preserved.
- `docs/dev/product-plan.md` no longer exists; no `/dev` skill references that path.
- No live data lost: the two intentions are rehomed; the three completed milestones are intentionally
  dropped (verifiable against the decision logs / cycle history).
- Every product-plan read/write in the skills targets `docs/dev/product-plans/<project-slug>.md`;
  no reference to the old singular/nested paths remains.
- `dev:done` deletes a project's product-plan on project completion and never on a mid-project child
  cycle's teardown.
- `dev:spec` Step 2, on speccing an oversized backlog item, spawns a product-plan and sets the source
  item `status: promoted` + `promoted_to`; `references/tech-debt.md` documents `promoted`/`promoted_to`
  as live (no longer "reserved").
- A promoted product-plan survives its child cycles' `dev:done` runs and is deleted only when the
  project completes — `debt-nested-product-plan-lifetime` is closed (moved to `docs/backlog/closed/`).
- Both modes (standard + autopilot) exercise every automatic write identically (mode-symmetry
  invariant from `references/tech-debt.md`).

## Happy Path

1. **Migration:** Build moves the two intentions into `docs/backlog/` as `type: backlog` files and
   hard-deletes `docs/dev/product-plan.md`.
2. **Relocation:** Build updates `dev:spec`, `dev:done`, `dev:dev`, and the contract so every
   product-plan path is `docs/dev/product-plans/<project-slug>.md`.
3. **Promotion (forward behavior):** a later `/dev:spec <backlog item>` detects product-scale in
   Step 2 → spawns `docs/dev/product-plans/<slug>.md`, sets the source item `status: promoted` +
   `promoted_to`.
4. **Completion (forward behavior):** the project's final child cycle's `dev:done` deletes the
   product-plan and moves the source backlog item `promoted → closed`.
5. **Close-out:** this cycle's `dev:done` closes `debt-nested-product-plan-lifetime` per the pending
   buffer.

## Edge Cases

- **Reference sweep must be exhaustive.** Every existing `docs/dev/product-plan.md` and
  `docs/dev/<parent>/product-plan.md` mention in the skills must move to the new scheme, or a stage
  writes/reads a path that no longer exists. A missed reference is a silent breakage — Build must grep
  the full `plugins/dev/` surface, not just the skills named in Scope.
- **Promoted-but-never-completed project.** A promoted item whose project never finishes leaves its
  plan in place by design (ephemeral means *deleted on completion*, not on a timer); `/dev:debt` shows
  it as `promoted` so it's visible, never silently stranded.
- **Deletion trigger precision.** "Project completion" ≠ "any child cycle's `dev:done`". The trigger
  must delete the plan only when the last milestone is checked off, not on every child teardown —
  otherwise the plan dies mid-project, re-creating the exact bug being fixed.
- **Migration collision.** The `<type>-` prefix means `backlog-debt-backfill.md` can't collide with any
  `debt-*.md`; the two slugs are distinct, so no disambiguation is needed (ADR Decision 8(c)).
- **`state.json` schema.** `dev:spec` sets `product_plan` for top-level product-scale cycles today;
  the corrected model must keep `state.json` honest about which project-plan governs a cycle and how
  `dev:done` locates it for deletion (any new key carries its `(writes: …)` tag at its single write
  site, per the contract).

## Audience

The `/dev` workflow maintainer (Adam) and the agent executing `/dev` cycles. Deliverables are
agent-facing `SKILL.md`/reference Markdown plus the `docs/backlog/` and `docs/dev/` data — no
end-user UI.

## Technical Constraints

- Plain, hand-editable Markdown; front-matter for structured item fields (matches the `docs/backlog/`
  store the tech-debt cycle established).
- All artifact writes are worktree-relative like every other `/dev` artifact.
- **Mode symmetry** and **entry-text-is-data** invariants from `references/tech-debt.md` are preserved
  unchanged.
- Changes to the shared contract `references/tech-debt.md` must stay the single source of truth (no
  second copy of the lifecycle rules in individual skills).

## Dependencies

- **Landed:** ADR follow-on 1 (the `docs/backlog/` store) and the tech-debt slice of follow-on 2 — both
  verified present. This cycle builds directly on that store.
- **Blocks:** nothing gating; it completes the product-plan slice of the ADR's follow-on roadmap.

## UI Needed

No.

---
*Auto-filled dimensions: none*
*Grounding inventory: verified against the current repo (post tech-debt-migration), not the ADR's Jul-28 snapshot — `cat docs/dev/product-plan.md` → exists, "Cycles completed: 3/5", 3 unrelated projects, 2 unfinished items `debt-backfill`/`debt-linear-promotion` under Milestone 3; `ls docs/backlog/` → store live, NO `backlog-*.md` (two items unmigrated), `tech-debt.md` retired; `grep 'rm .*product-plan' plugins/dev/skills/` → zero hits (no deletion exists); `grep 'product-plan|promot' references/tech-debt.md` → `promoted`/`promoted_to` explicitly "reserved — Decision 7, cycle 4", status enum `open|in-progress|closed`; `grep product-plan plugins/dev/skills/` → dev:spec, dev:done, dev:dev + contract; `dev:done` Step 3 only checks boxes + increments count; `debt-nested-product-plan-lifetime.md` → open, files: spec+done, "Done looks like" = durable plan location. Debt cross-check: 1 match folded in (debt-nested-product-plan-lifetime).*
