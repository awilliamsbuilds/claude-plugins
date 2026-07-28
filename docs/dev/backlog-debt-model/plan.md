# Unified Backlog + Tech-Debt Model (ADR) — Implementation Plan
*Branch: arch/backlog-debt-model · 2026-07-28*

This is an **architecture cycle**. Build produces **one ADR document** — not code, not skill
edits — that resolves all nine Scope decisions with alternatives and rationale. Every task below
authors a section of that single file. There is **no code and therefore no new `state.json`
key** in this cycle, so no task carries a `State keys:` declaration (the interface-consistency
lens's write-mode check is N/A by construction).

The doc is written during the cycle at `docs/dev/backlog-debt-model/backlog-debt-model.md` and is
moved to `docs/decisions/YYYY-MM-DD-backlog-debt-model.md` by `dev:done`.

## Files

| File | Action | Purpose |
|------|--------|---------|
| docs/dev/backlog-debt-model/backlog-debt-model.md | Create | The ADR — nine decisions, alternatives, rationale, consequences |

Every task below creates or appends to this **one** file. No other file is touched — skill edits,
contract rewrites, migration execution, and the new capture skill are all follow-on cycles
(spec Out of Scope).

## Build sequence

The nine decisions form a DAG rooted at the storage model. Core decisions (2→3→4→5) must settle
before the dependent designs (6, 7, 8, 9) can reference a concrete store. Migration (Task 10)
and Consequences (Task 11) come last because they depend on every prior decision.

```
Task 1 (scaffold + Context)
        │
        ▼
Task 2 (D1 Storage model)  ◀── root of the DAG; everything downstream reads it
        │
        ├──► Task 3 (D2 Naming/identity)
        ├──► Task 4 (D3 Header schema)
        │            │
        │            ▼
        │       Task 5 (D4 Lifecycle) ─────┐
        │            │                     │
        │            ▼                     ▼
        ├──► Task 6 (D5 Cross-repo routing)
        ├──► Task 7 (D7 Product-plan boundary)
        │            │
        │            ▼
        ├──► Task 8 (D6 Capture skill)   ◀── also reads Task 5, Task 6
        ├──► Task 9 (D9 Producing-stage integration) ◀── reads Task 4, Task 5
        │
        ▼
Task 10 (D8 Migration)  ◀── reads Tasks 2,3,4,5,7 (target shape must be final)
        │
        ▼
Task 11 (Consequences + cross-consistency pass)  ◀── reads all
```

**Parallel-safe once the core is written:** Tasks 6, 7, 9 have no dependency on each other and
may be drafted in any order after Tasks 2/4. Task 8 (capture) additionally reads Tasks 5 and 6, so
it follows both. All sections live in one file, so "parallel" here means order-independent, not
concurrent writes.

## Tasks

### Task 1: Scaffold the ADR and write the Context section
What: Create the ADR file with its status header and the Context section that frames the problem and grounding.
Used by: Every later task appends to this file; Validate reviews it; `dev:done` moves it to `docs/decisions/`.
Depends on: nothing — first task.
Files: Create docs/dev/backlog-debt-model/backlog-debt-model.md
Interfaces:
- Consumes: nothing.
- Produces: the ADR file at a known path with an `# Unified Backlog + Tech-Debt Model` H1, a `*Status: accepted · Date: YYYY-MM-DD*` line, and a `## Context` section. Later tasks append `## Decision N …` sections to this file.
- State keys: none — architecture cycle, no code.

Implementation steps:
1. Run `date -u +%Y-%m-%d` and use that output for the `Date:` in the status line (never inferred — the tech-debt contract's clock rule applies to any dated artifact).
2. Write the H1 title and status line per Build's ADR format (`*Status: accepted · Date: …*`).
3. Write `## Context`: the two concrete limitations from the spec Intent — (a) plugin debt leaks into the wrong repo because the tracker is strictly per-repo; (b) there is no purpose-built backlog, so deferred *intentions* are misfiled into `product-plan.md` (`debt-backfill`, `debt-linear-promotion`). State why this is an architecture cycle (the design carries the open trade-offs; implementation is deferred to follow-on cycles).
4. Ground the Context in the real files Build has read: `plugins/dev/references/tech-debt.md` (the contract), `docs/dev/tech-debt.md` (three live Open entries), and `docs/dev/product-plan.md` (the 3/5 multi-project plan). Name them so a reader can verify.
5. Commit: `git -C "$WORKDIR" add docs/dev/backlog-debt-model/backlog-debt-model.md && git -C "$WORKDIR" commit -m "arch: scaffold ADR + context for backlog-debt-model"`.

### Task 2: Decision 1 — Storage model
What: Decide per-item vs aggregate vs hybrid storage, the directory layout, and whether debt and backlog share one tree or split.
Used by: Every downstream decision (3–9) reads the storage model; migration (Task 10) targets it.
Depends on: Task 1 (file + Context exist).
Files: Append `## Decision 1 — Storage model` to the ADR.
Interfaces:
- Consumes: the ADR file from Task 1.
- Produces: **the settled storage model** — one of {per-item files, single aggregate, hybrid}; **the directory layout** (e.g. a `docs/backlog/` tree with concrete paths); and **the debt/backlog tree topology** (shared vs split). Downstream tasks reference these three by the names fixed here.
- State keys: none.

Implementation steps:
1. Present the alternatives: per-item files, keep-the-aggregate, and hybrid. For each, state what it costs and what it buys.
2. **Explicitly argue per-item-vs-aggregate** (Success Criteria requires this): the current aggregate's real strengths the new model must not silently lose are named in the contract — hand-editability, greppability, and the recurrence-merge procedure. The rationale must confront each, not wave at them.
3. Decide and record the directory layout with concrete paths (whatever the model, give a reader real paths, not a placeholder).
4. Decide whether debt and backlog items share one tree or split into two, with rationale.
5. Honor Technical Constraints: plain Markdown, hand-editable, fits the `references/` shared-contract pattern, worktree-relative writes.
6. Commit: `git -C "$WORKDIR" add … && git -C "$WORKDIR" commit -m "arch: decide storage model"`.

### Task 3: Decision 2 — File naming / identity
What: Decide how an item is named and identified, and — if Decision 1 chose per-item or hybrid — how the filename encodes type and status and changes across the lifecycle.
Used by: Header schema (Task 4) and migration (Task 10) reference the identity scheme; capture (Task 8) sets the name on creation.
Depends on: Task 2 (storage model determines whether a filename scheme even applies).
Files: Append `## Decision 2 — File naming / identity` to the ADR.
Interfaces:
- Consumes: the settled storage model + directory layout (Task 2).
- Produces: **the item identity scheme** — how an item is named/identified, and (if per-item/hybrid) **the filename convention** encoding type and status, and how a name changes as the item moves through its lifecycle. The user's stated leaning is per-item files whose names reflect status; the ADR decides whether to adopt it.
- State keys: none.

Implementation steps:
1. If Decision 1 chose aggregate-only, state that a filename scheme is N/A and record how items are identified *within* the file instead (e.g. unique titles, as the current tracker requires). If per-item/hybrid, proceed.
2. Decide the filename convention: how type (debt | backlog) and status appear in the name.
3. Decide what happens to the filename as status changes (rename on transition vs. status-in-header only). Weigh greppability and hand-editability against churn — a rename-per-transition scheme changes the path on every lifecycle move.
4. Record alternatives considered and why the chosen scheme won.
5. Commit.

### Task 4: Decision 3 — Header schema
What: Decide the metadata each item carries, at parity-or-better with today's tracker header.
Used by: Lifecycle (Task 5) reads the status field; routing (Task 6) reads the scope field; capture (Task 8) writes the header; migration (Task 10) maps old headers onto it; producing-stage integration (Task 9) writes into it.
Depends on: Task 2 (storage model shapes where the header lives).
Files: Append `## Decision 3 — Header schema` to the ADR.
Interfaces:
- Consumes: the settled storage model (Task 2).
- Produces: **the header field set** — at minimum first-recorded date, recurrences, cycle(s) saved/fixed-in, item type (debt | backlog), scope (repo | plugin), status, and affected files — plus any field the model needs. The `status` and `scope` fields are named here and consumed by Tasks 5 and 6 respectively.
- State keys: none.

Implementation steps:
1. Take today's entry header as the **floor** (the contract's Open/Closed meta lines: `First recorded`, `Cycles`, `Recurrence`, `Files`) — enumerate every field it carries so nothing is silently dropped.
2. Add the new fields the unified model needs: item **type** (debt | backlog) and **scope** (repo | plugin), plus a **status** field (feeds Task 5).
3. Decide the concrete syntax (meta line vs. front-matter vs. bold-label fields) consistent with Decision 1's storage model and the hand-editable constraint.
4. Note that `scope` is the field Task 6's routing keys on, and `status` is the field Task 5's lifecycle drives — name them so those tasks bind cleanly.
5. Record alternatives (e.g. YAML front-matter vs. the current bold-label prose) and why the choice won.
6. Commit.

### Task 5: Decision 4 — Item lifecycle
What: Decide the status states and their transitions, and what happens to the recurrence-merge concept under the new model.
Used by: Capture (Task 8) creates items in the initial state; producing-stage integration (Task 9) drives transitions; migration (Task 10) maps existing Open/Closed onto the new states.
Depends on: Task 2 (storage model), Task 4 (the `status` field the lifecycle drives).
Files: Append `## Decision 4 — Item lifecycle` to the ADR.
Interfaces:
- Consumes: the storage model (Task 2) and the `status` field (Task 4).
- Produces: **the status state set and transition rules**, and **the decided fate of recurrence-merge** (survives as-is / changes / drops) with rationale.
- State keys: none.

Implementation steps:
1. Enumerate the status states (at minimum today's open/closed, plus whatever backlog items need — e.g. an in-progress or promoted state) and the legal transitions between them.
2. **Resolve the recurrence-merge question head-on** (spec Decision 4 + Edge Case "Loss of recurrence-merge value"): under a per-item model, does the "this keeps happening" signal survive, change form, or drop? If per-item files fragment the aggregate that recurrence-merge scanned, say concretely how the signal is preserved (e.g. a recurrence count in the header + a merge-on-capture step) or explicitly accept its loss with justification.
3. Tie transitions to the `status` field syntax from Task 4 and, if per-item with status-in-filename (Task 3), to the rename behavior.
4. Record alternatives and rationale.
5. Commit.

### Task 6: Decision 5 — Cross-repo routing
What: Decide how a finding is classified plugin-scoped vs repo-scoped and how a plugin-scoped item reaches the plugin repo, including the failure case.
Used by: Capture (Task 8) sets scope at creation and invokes routing; the Consequences section (Task 11) notes the follow-on that implements it.
Depends on: Task 2 (where items live), Task 4 (the `scope` field).
Files: Append `## Decision 5 — Cross-repo routing` to the ADR.
Interfaces:
- Consumes: the storage model (Task 2) and the `scope` field (Task 4).
- Produces: **the routing mechanism, specified end to end** — how classification happens, how a plugin item gets home, and the degradation behavior when the plugin repo is absent or unwritable.
- State keys: none.

Implementation steps:
1. Decide how classification happens (plugin-scoped vs repo-scoped) and make it **legible and hand-correctable** (Edge Case "Misclassification").
2. Design the delivery mechanism for a plugin-scoped item reaching the plugin repo. **Reuse `dev:reflect`'s portable plugin-source discovery** (git-remote / plugin-cache resolution, no hardcoded paths) per Technical Constraints — do not invent a second discovery path.
3. **Design around the known discovery flaw, not past it:** the open tracker entry *"dev:reflect dogfood shortcut can open a PR against a fork's upstream"* means the `origin`-slug == marketplace-slug heuristic misfires on a fork. The routing design must account for this (e.g. confirm the target repo before writing, or an explicit target) rather than assume discovery is clean — the spec Technical Constraints call this out explicitly.
4. Specify the **failure case end to end** (Success Criteria + Edge Case "Plugin repo unreachable"): plugin repo not present locally or not writable → the item must degrade safely (recorded locally, surfaced) and **never be silently dropped**, mirroring the contract's silent-degrade discipline.
5. Record alternatives and rationale.
6. Commit.

### Task 7: Decision 7 — Product-plan boundary + correction
What: Articulate and correct the product-plan model, and define the one-way backlog → product-plan promotion flow.
Used by: Migration (Task 10) moves the misfiled product-plan items per this boundary; Consequences (Task 11) names the follow-on that implements deletion/promotion.
Depends on: Task 2 (the backlog concept must exist to define promotion into a plan).
Files: Append `## Decision 7 — Product-plan boundary + correction` to the ADR.
Interfaces:
- Consumes: the storage model / backlog concept (Task 2).
- Produces: **the corrected product-plan model** stated as a *correction* (ephemeral, single-project, deleted on completion — not a backlog, not a debt tracker), **the backlog → product-plan promotion flow**, and **an explicit decision on the existing multi-project top-level plan** (migrate its milestones / archive / wipe).
- State keys: none.

Implementation steps:
1. State the corrected model: product-plan is an *ephemeral milestone carrier for a single multi-cycle project, deleted on completion.*
2. Frame it explicitly as a **correction, not a description** (spec Decision 7): today's top-level `product-plan.md` survives cycles, is never deleted, and the live one spans three unrelated projects at 3/5. Say plainly that the corrected model changes current top-level behavior.
3. Decide what happens to the existing multi-project plan: migrate its milestones into the new backlog, archive it, or wipe it — pick one, with rationale. (Its two unfinished items, `debt-backfill` and `debt-linear-promotion`, are backlog intentions — note that Task 10 handles their physical migration.)
4. Define the one-way **backlog → product-plan promotion** flow: a backlog item big enough to span cycles spawns a plan.
5. Relate the corrected model to the open tracker entry *"A nested product plan cannot outlive its parent"* (spec Decision 7): note how the corrected model bears on it and that the implementing cycle is the natural place to close it. Do **not** close it here (design-only cycle).
6. Record alternatives and rationale.
7. Commit.

### Task 8: Decision 6 — Capture skill shape
What: Decide the "save this to the backlog" flow — invocation, how it sets type and scope, and its relationship to the existing `/dev:debt` skill.
Used by: Consequences (Task 11) names the follow-on cycle that builds it.
Depends on: Task 2 (storage), Task 4 (header fields it writes), Task 5 (initial lifecycle state), Task 6 (it sets scope, which routing consumes).
Files: Append `## Decision 6 — Capture skill shape` to the ADR.
Interfaces:
- Consumes: the storage model (Task 2), the header schema (Task 4), the lifecycle states (Task 5), and the scope/routing design (Task 6).
- Produces: **the capture-flow design** — how a user invokes it, how it sets item type (debt | backlog) and scope (repo | plugin), and the **extend-`/dev:debt`-vs-new-skill decision** with rationale.
- State keys: none.

Implementation steps:
1. Decide invocation: how the user says "save this to the backlog" (a `/dev:debt` subcommand, a new `/dev:backlog` skill, or an argument form).
2. Decide how the flow sets **type** (debt | backlog) and **scope** (repo | plugin) — default + override, tying to the header fields (Task 4) and the routing classification (Task 6).
3. **Decide extend vs new** relative to `/dev:debt` (spec Decision 6): `/dev:debt` today owns all reads and manual lifecycle changes — argue whether capture extends it or is a new skill, and why.
4. Keep this **design-only**: describe the skill's shape; do not write a SKILL.md (Out of Scope).
5. Record alternatives and rationale.
6. Commit.

### Task 9: Decision 9 — Producing-stage integration
What: Name the seams and changes by which the current buffer→flush writes adapt to the new store — design-level, no skill edits.
Used by: Consequences (Task 11) rolls these into the follow-on implementation cycle(s).
Depends on: Task 2 (storage), Task 4 (header), Task 5 (lifecycle).
Files: Append `## Decision 9 — Producing-stage integration` to the ADR.
Interfaces:
- Consumes: the storage model (Task 2), header schema (Task 4), and lifecycle (Task 5).
- Produces: **the integration map** — for each producing seam, what changes: the buffer→flush writes in `dev:build`, `dev:validate`, `dev:reflect`, `dev:spec`; the flush in `dev:done`; and the creation in `dev:init`.
- State keys: none.

Implementation steps:
1. Enumerate the current seams from the contract: producing stages append to the per-cycle buffer (`debt-pending.md`); `dev:done` Step 6a flushes it into the tracker; `dev:init` creates the tracker; `dev:reflect` standalone appends directly.
2. For each seam, state at design level how it adapts to the new store (does the buffer survive? does flush target per-item files? does `dev:init` seed a `docs/backlog/` tree?). **Name the seam and the change; do not edit the skill** (Out of Scope).
3. **Own the cross-skill ripple as design** (high-cost failure-mode scan — "Cross-skill behavior ripple"): because the store change touches multiple skills, this section is where the ADR enumerates *every* skill the follow-on implementation must change, so the ripple is recorded in one place rather than discovered piecemeal during a later Build.
4. Preserve the contract's invariants where they still apply (silent-degrade rule, mode-symmetry / both-modes-traceability, worktree-relative writes) — note any that the new model changes.
5. Record alternatives and rationale.
6. Commit.

### Task 10: Decision 8 — Migration design
What: Design how existing deferred items move into the new model — both `tech-debt.md` entries and the backlog-shaped items misfiled in `product-plan.md`.
Used by: Consequences (Task 11) names the migration-execution follow-on cycle.
Depends on: Task 2, Task 3, Task 4, Task 5 (the target shape must be final), and Task 7 (product-plan items' destination).
Files: Append `## Decision 8 — Migration design` to the ADR.
Interfaces:
- Consumes: the full target model — storage (Task 2), naming (Task 3), header (Task 4), lifecycle (Task 5) — and the product-plan correction (Task 7).
- Produces: **a concrete migration path** for (a) the current `tech-debt.md` Open/Closed entries and (b) the misfiled `product-plan.md` items (`debt-backfill`, `debt-linear-promotion`), including the collision-handling rule.
- State keys: none.

Implementation steps:
1. Map today's tracker entries (3 Open, several Closed — enumerated from the real `docs/dev/tech-debt.md`) onto the new storage model, naming scheme, and header fields. Show the mapping concretely enough that a follow-on cycle could execute it without re-deciding (Success Criteria).
2. Map the misfiled `product-plan.md` items (`debt-backfill`, `debt-linear-promotion`) into the new backlog per Task 7's boundary.
3. **Handle migration collisions** (Edge Case "Migration collisions"): existing entries with duplicate/near-duplicate titles under the new naming scheme — reuse the contract's disambiguation instinct (append the first cycle name) or define an equivalent rule.
4. Keep it **design-only**: execution is a follow-on cycle (Out of Scope). State that explicitly.
5. Record alternatives and rationale.
6. Commit.

### Task 11: Consequences + cross-consistency pass
What: Write the ADR's Consequences section and do a final read-through confirming every decision references the others consistently.
Used by: Validate reviews the finished ADR; `dev:done` moves it to `docs/decisions/`.
Depends on: all prior tasks.
Files: Append `## Consequences` to the ADR; edit earlier sections only to fix cross-reference drift found in the pass.
Interfaces:
- Consumes: every prior decision.
- Produces: **the Consequences section** (what the model enables, what it forecloses, and the follow-on cycles it requires — implementation, migration execution, capture skill, product-plan deletion/promotion, closing the two related open tracker entries), and a **cross-consistent ADR** where a field named in one decision matches its use in another.
- State keys: none.

Implementation steps:
1. Write `## Consequences`: what the unified model enables, what it forecloses, and — concretely — the **follow-on cycles** it requires (store implementation + producing-stage edits, migration execution, capture skill, product-plan deletion/promotion). Note the two open tracker entries the follow-ons naturally close (*"A nested product plan cannot outlive its parent"*, *"dev:reflect dogfood shortcut can open a PR against a fork's upstream"*).
2. **Cross-consistency pass:** re-read all nine decisions and confirm field names line up — the `status` field (Task 4) as used by lifecycle (Task 5); the `scope` field (Task 4) as used by routing (Task 6); the storage paths (Task 2) as referenced everywhere. Fix any drift inline (this is the one task allowed to edit earlier sections).
3. Confirm every one of the nine Scope decisions has a `## Decision N` section and that each records alternatives + why-the-choice-won (ADR discipline, Success Criteria).
4. Commit: `git -C "$WORKDIR" add … && git -C "$WORKDIR" commit -m "arch: consequences + cross-consistency pass"`.

## Edge Cases
| Edge case | Handled in | Approach |
|-----------|-----------|----------|
| Plugin repo unreachable (absent / unwritable) during routing | Task 6 | Routing degrades safely — item recorded locally + surfaced, never silently dropped |
| Misclassification (repo-scoped tagged plugin or vice versa) | Task 6 | Classification made legible and hand-correctable in the header's `scope` field |
| Loss of recurrence-merge value under per-item model | Task 5 | Lifecycle decision resolves whether the "keeps happening" signal survives, changes form, or is explicitly accepted as lost |
| Migration collisions (duplicate/near-duplicate titles) | Task 10 | Disambiguation rule (reuse the contract's append-first-cycle-name instinct or equivalent) |
| Known discovery flaw (fork `origin`-slug misfire) leaking into routing | Task 6 | ADR designs around the flaw (confirm target repo / explicit target) rather than assuming clean discovery |

## Out of Scope
- Any implementation or code — no skill edits, no contract rewrite, no new SKILL.md. Build writes the ADR only.
- Migration execution — designed in Task 10, run by a follow-on cycle.
- Full task-tracker features (priorities, labels, boards, assignees, status columns beyond the minimal lifecycle).
- The memory system (`~/.claude/.../memory/`) — untouched.
- `dev:fix`'s Linear seam — the design enables retiring Linear for personal work but changes no code this cycle.
- Closing the two related open tracker entries — noted in Consequences as follow-on work, not paid here.

## Risks and Unknowns
- **Storage model is the load-bearing decision (Task 2).** Every downstream section reads it; if it's re-decided late, Tasks 3–10 need revision. Mitigation: Task 2 argues per-item-vs-aggregate fully and early, and the Task 11 cross-consistency pass is the backstop if a later section exposes a gap in it.
- **Recurrence-merge under per-item storage (Task 5)** is the sharpest open trade-off — the aggregate's recurrence signal is a real strength a per-item split could fragment. Mitigation: Task 5 must resolve it explicitly (preserve / change / accept-loss), never leave it implied.
- **Routing inherits a known-flawed discovery heuristic (Task 6).** The fork `origin`-slug misfire is a live open debt entry, not hypothetical. Mitigation: Task 6 designs around it explicitly per the spec's Technical Constraints, rather than assuming discovery is clean.
- **Cross-skill ripple is design-only this cycle but must be complete (Task 9).** If the ADR under-names the producing-stage seams, the follow-on Build discovers them piecemeal. Mitigation: Task 9 owns enumerating every affected skill in one place.
