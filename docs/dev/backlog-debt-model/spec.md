# Unified Backlog + Tech-Debt Model (ADR)
*Branch: arch/backlog-debt-model · Confidence: 86% — Ready · 2026-07-28*
*Cycle type: architecture · Tier: deep*

## Intent

`/dev`'s tech-debt tracker (`docs/dev/tech-debt.md`, one aggregate file per repo) has two
limitations we've hit in practice:

1. **Plugin debt leaks into the wrong repo.** The tracker is strictly per-repo. When a `/dev`
   cycle running in *some other* repo surfaces a finding about the `/dev` plugin's own skills,
   that finding is recorded in *that* repo's `tech-debt.md`, not the plugin's. Debt about the
   plugin ends up scattered across every repo the plugin runs in.
2. **There is no backlog.** There's nowhere to say "I want to build X later" without reaching for
   a third-party system (Linear). Deferred *findings* have a home; deferred *intentions* don't.

This cycle designs a single, durable **backlog + tech-debt store** that holds both kinds of item,
routes plugin-scoped items back to the plugin, and lets the user capture "save this to the
backlog" on demand — removing the need for Linear for personal/plugin work.

Because the hard part is the design (storage shape, naming, headers, lifecycle, cross-repo
routing — all with open trade-offs), this is an **architecture cycle**: Build produces a
committed ADR under `docs/decisions/`. Implementation is deferred to follow-on feature cycles that
react to the ADR.

## Scope

Produce an ADR that **decides**, each with rationale, the following. This decision set is the
cycle's definition of done (see Success Criteria).

1. **Storage model** — per-item files vs. aggregate vs. hybrid; the directory layout (e.g. a
   `docs/backlog/` tree), and whether debt and backlog items share one tree or split.
2. **File naming + status-in-filename** — how a filename encodes item type and status, and how it
   changes as an item moves through its lifecycle (the user's leaning is per-item files whose
   names reflect status).
3. **Header schema** — the metadata each item carries: at minimum first-recorded date,
   recurrences, cycle(s) saved/fixed-in, item type (debt | backlog), scope (repo | plugin),
   status, and affected files — plus whatever else the model needs. Parity with today's entry
   header is a floor, not a ceiling.
4. **Item lifecycle** — the status states and their transitions, and what happens to today's
   **recurrence-merge** concept under a per-item model (does it survive, change, or drop).
5. **Cross-repo routing** — how a finding is classified plugin-scoped vs. repo-scoped, and how a
   plugin-scoped item reaches the plugin repo. The ADR owns the mechanism; the spec only requires
   routing be solved.
6. **Capture skill shape** — the "save this to the backlog" flow: how a user invokes it, how it
   sets type and scope, and its relationship to the existing `/dev:debt` skill (extend vs. new).
7. **Product-plan boundary + correction** — articulate and correct the product-plan model: it is
   an *ephemeral* milestone carrier for a *single multi-cycle project*, deleted on completion —
   **not** a backlog and not a debt tracker. Define the one-way **backlog → product-plan
   promotion** flow (a backlog item big enough to span cycles spawns a plan). The corrected model
   is a design decision here; implementing the deletion/promotion behavior is a follow-on cycle.
8. **Migration design** — how existing `tech-debt.md` entries move into the new model (design
   only; execution is a follow-on cycle).
9. **Producing-stage integration** — how the current buffer→flush writes in `dev:build`,
   `dev:validate`, `dev:reflect`, and `dev:spec` (and the flush in `dev:done`, creation in
   `dev:init`) adapt to the new store. Design-level: name the seams and the changes, don't edit
   the skills.

## Out of Scope

- **Any implementation or code.** No skill edits, no contract rewrite, no new skill file. Build
  produces the ADR document only.
- **Migration execution** — moving the actual existing entries. Designed here, run later.
- **Full task-tracker features** — priorities, labels, boards, assignees, status columns beyond
  the minimal lifecycle. This is a debt + "things to build" store, not a Linear clone.
- **The memory system** (`~/.claude/.../memory/`) — untouched; not folded into the backlog.
- **`dev:fix`'s Linear seam** — retiring Linear for personal work is a *goal the design enables*,
  not a code change this cycle. The Linear entry path stays as-is.

## Success Criteria

The ADR is done when, committed under `docs/decisions/`, it resolves all nine decisions in Scope,
and specifically:

- A reader can tell, for any item, **where its file lives, what it's named, and what its header
  contains** — concretely enough that a follow-on cycle could implement without re-deciding.
- The **cross-repo routing** mechanism is specified end to end: how classification happens and how
  a plugin item gets home, including the failure case (plugin repo absent or unwritable).
- The **product-plan boundary** is stated as a correction, with the promotion flow defined.
- Each decision records the **alternatives considered and why the chosen option won** (it's an
  ADR, not a spec restatement) — including an explicit argument for per-item files vs. keeping the
  aggregate, since today's aggregate has real strengths (hand-editability, greppability, the
  recurrence-merge procedure) the new model must not silently lose.
- A **migration path** exists for the current `tech-debt.md` entries.

## Happy Path

1. Build reads this spec + the current tech-debt contract (`plugins/dev/references/tech-debt.md`)
   and today's `tech-debt.md` / `product-plan.md`.
2. Build drafts the ADR, proposing each of the nine decisions with alternatives and rationale.
3. Validate reviews the ADR (architecture-cycle review — coherence, completeness against the
   decision set, no unresolved decisions).
4. The ADR is committed under `docs/decisions/`; follow-on feature cycles implement from it.

## Edge Cases

Design-level failure modes the ADR must address (not runtime edges — there's no code):

- **Plugin repo unreachable** during cross-repo routing (not present locally, not writable) —
  the routing design must degrade safely, not silently drop the item.
- **Misclassification** — a finding that is genuinely repo-scoped tagged as plugin (or vice
  versa); the model should make the classification legible and correctable by hand.
- **Loss of recurrence-merge value** — a per-item model must not throw away the "this keeps
  happening" signal the current aggregate provides.
- **Migration collisions** — existing entries with duplicate/near-duplicate titles under the
  new naming scheme.

## Audience

Adam — solo maintainer of this plugin repo. The store and its skills are dogfooded here and used
across his other repos.

## Technical Constraints

- Plain Markdown, hand-editable without tooling (today's tracker property; the ADR should
  preserve it).
- Must fit the `/dev` plugin's existing conventions: the shared-contract-in-`references/` pattern,
  the buffer→flush write model, `state.json`/mode-symmetry rules, worktree-relative writes.
- Cross-repo routing must reuse the **portable plugin-source discovery** `dev:reflect` already
  established (git-remote / plugin-cache resolution, no hardcoded paths).
- UI Needed: **No** — Markdown files and skills only; Shape is skipped.

## Dependencies

- Builds on the existing tech-debt contract (`plugins/dev/references/tech-debt.md`) and tracker.
- Relates to (does not merge with) `docs/dev/product-plan.md`.
- The deferred product-plan items (`debt-backfill`, `debt-linear-promotion` in the current
  product plan) overlap this design; the ADR should note how they fold into or are superseded by
  the new model.

## UI Needed

No.

---
*Auto-filled dimensions: none*
*Grounding inventory: Verified against real files this stage — (1) "tracker is per-repo, no cross-repo routing" → read `plugins/dev/references/tech-debt.md` § Where things live + `docs/dev/tech-debt.md`, no routing mechanism present; (2) "entry header schema (first-recorded, cycles, recurrence, files)" → confirmed from the contract's Tracker file format; (3) "one aggregate file today, not per-item" → confirmed, single `## Open`/`## Closed` file; (4) "product-plan is not deleted on completion today" → `grep` for `rm .*product-plan` / deletion across all `dev:*` skills returned zero hits; `dev:done` Step 3 checks off items but never deletes the plan; the live `docs/dev/product-plan.md` sits at 3/5 with lingering checked boxes. Open-debt cross-check (Step 7 pass 4): "A nested product plan cannot outlive its parent" (spec/done) intersects this cycle's product-plan-model surface — surfaced at the gate, not folded in, because an architecture/design-only cycle cannot pay implementation debt.*
