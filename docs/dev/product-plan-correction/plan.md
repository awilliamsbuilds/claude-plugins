# Product-Plan Correction — Implementation Plan
*Branch: feature/product-plan-correction · 2026-07-28*
*Cycle type: feature · Tier: deep*

This plan implements ADR Decision 7 and the product-plan slice of 8(c): make product-plans
**ephemeral single-project milestone carriers** living at a durable, project-lifetime location,
finish the tech-debt migration's leftover data move, and activate the one-way
`backlog → product-plan` promotion flow. All changes are agent-facing Markdown (`SKILL.md` +
`references/`) plus one-time data operations. No end-user UI.

## Pinned design decisions (Plan's job per spec)

These are settled here so Build never guesses:

- **Durable plan location:** `docs/dev/product-plans/<project-slug>.md` — one directory, outside
  any single cycle's dir. Replaces both old locations (`docs/dev/product-plan.md` top-level and
  `docs/dev/<parent>/product-plan.md` nested). Writer-side create-if-absent for the directory
  (same discipline as the `docs/backlog/` store, contract P7).
- **`<project-slug>` source:** kebab-case slugification of the product/project name (the
  `# [Product Name] — Product Plan` header), constrained to `^[a-z0-9][a-z0-9-]*$` (the repo's
  existing feature-slug allowlist shape). The slug is chosen once, when the plan is first spawned.
- **Child-cycle slug recovery (the load-bearing rule):** the plan path is recorded in
  `state.json.product_plan` as the **full repo-relative path** (`docs/dev/product-plans/<slug>.md`).
  A nested child cycle **inherits** that value: `dev:spec` Step 1 nesting detection already locates
  the active parent's `state.json`; the child copies the parent's `product_plan` into its own state.
  **Inheritance is unconditional on nesting** — it happens whenever nesting detection finds a parent
  with a non-null `product_plan`, *independent of* whether this child cycle itself authored a plan
  (a nested child implementing one milestone item is not product-scale and never triggers Step 2/4,
  yet must still record the path so `dev:done` checks it off). Precedence: if a cycle is *itself*
  product-scale it authors a new plan/slug (path (A)); else if nested under a parent-with-plan it
  inherits (path (B)); else `product_plan` stays `null`.
  `dev:done` then reads `state.json.product_plan` **uniformly** — top-level and nested collapse into
  one path. `parentFeature` no longer drives plan location (its other uses are untouched).
- **Deletion trigger (precision):** `dev:done` deletes the plan **only on project completion** —
  defined as *every* checkbox item in the plan being `[x]` after this cycle's check-off. Never on a
  mid-project child teardown.
- **Source-item close on completion:** the promotion back-link is bidirectional. `dev:done`, on
  completion, reverse-looks-up the source item by grepping `docs/backlog/` for
  `promoted_to: <plan-path>`; if found, it executes the `promoted → closed` move (set `status: closed`,
  `closed:`, `closed_by:`; `git mv` to `docs/backlog/closed/`) **inline**, in the same commit that
  `git rm`s the plan. This is a *designed* lifecycle terminus (promotion's end), distinct from the
  incidental debt closes the contract routes through the buffer — so it legitimately closes here.
- **No new `state.json` key.** The existing `product_plan` key is repurposed (now the full relocated
  path, and now inherited by nested children). No new counter is introduced, so the mode-symmetry
  contract is satisfied by construction. `product_plan` is written by `dev:spec`'s deferred Step 6
  block in both modes identically — `(writes: both)`.

## Files

| File | Action | Purpose |
|------|--------|---------|
| docs/backlog/backlog-debt-backfill.md | Create | Rehome the `debt-backfill` intention as a `type: backlog` item |
| docs/backlog/backlog-debt-linear-promotion.md | Create | Rehome the `debt-linear-promotion` intention as a `type: backlog` item |
| docs/dev/product-plan.md | Delete | Hard-delete the retired stale top-level plan |
| plugins/dev/references/tech-debt.md | Modify | Un-reserve `promoted`/`promoted_to`; document one-way flow + ephemeral lifecycle + durable location |
| plugins/dev/skills/spec/SKILL.md | Modify | Relocate plan writes; define `<project-slug>` + child recovery; promotion back-link (Steps 2/4/6) |
| plugins/dev/skills/done/SKILL.md | Modify | Step 3: read `product_plan` path; add project-completion deletion + source-item close |
| plugins/dev/skills/dev/SKILL.md | Modify | Step 6 continuation: point at the new plan location |
| plugins/dev/skills/debt/SKILL.md | Modify | Surface `promoted` status in the open-items list |

## Tasks

### Task 1: Retire the stale top-level product-plan
What: Rehome the two live backlog intentions into `docs/backlog/` and hard-delete the emptied
`docs/dev/product-plan.md` (its remaining content is three historical `[x]` milestones, dropped by design).
Used by: Nothing programmatic — this is a one-time data operation. Success Criteria verify the files.
Depends on: nothing — first task.
Files: create `docs/backlog/backlog-debt-backfill.md`, `docs/backlog/backlog-debt-linear-promotion.md`; delete `docs/dev/product-plan.md`.
Interfaces:
- Consumes: nothing.
- Produces: nothing later tasks reference — terminal data change. (The two files are data read by `dev:spec` grounding / `dev:done` flush at *runtime*, not by any plan task.)

Implementation steps:
1. Create `docs/backlog/backlog-debt-backfill.md` (worktree-relative, in `$WORKDIR`) with this exact front-matter and body:
   ```markdown
   ---
   type: backlog
   scope: repo
   status: open
   first_recorded: 2026-07-21
   cycles: []
   recurrence: 0
   files: []
   ---

   **What:** Mine existing `docs/decisions/*.md` on init to seed the tech-debt tracker from
   past cycles.
   **Why:** Deferred from tech-debt-tracking — measured yield was ~3 items across 10 cycles with
   2 of them cosmetic, and parsing ten unstructured log formats is far easier once real entries
   exist to define the target shape. Depends on tech-debt-tracking (now shipped).
   **Done looks like:** `dev:init` seeds `docs/backlog/` from prior decision logs.
   ```
2. Create `docs/backlog/backlog-debt-linear-promotion.md` with:
   ```markdown
   ---
   type: backlog
   scope: repo
   status: open
   first_recorded: 2026-07-21
   cycles: []
   recurrence: 0
   files: []
   ---

   **What:** `/dev:debt promote <id>` turns a tracker entry into a Linear issue with link-back.
   **Why:** The Linear seam already exists via `dev:fix`. Deferred from tech-debt-tracking as an
   independent second deliverable. Depends on tech-debt-tracking (now shipped). Note: this is a
   distinct mechanism from this cycle's `backlog → product-plan` promotion.
   **Done looks like:** `/dev:debt promote <id>` creates a Linear issue from a backlog item and
   records the link.
   ```
3. Verify front-matter validity against the contract: `recurrence: 0 == len(cycles: [])`; `files: []`
   is legitimately empty (not-yet-built intention, per contract `files` field rule); slugs keep the
   historical `debt-` names — `type: backlog`, not the slug, classifies them (ADR 8(c)). The
   `backlog-` filename prefix + `debt-` slug can't collide with any active `debt-*.md`.
4. Hard-delete `docs/dev/product-plan.md`: `git -C "$WORKDIR" rm docs/dev/product-plan.md`.
5. Commit: `git -C "$WORKDIR" add docs/backlog/ && git -C "$WORKDIR" commit -m "chore: migrate backlog intentions, retire stale product-plan"`.

### Task 2: Un-reserve promotion in the shared contract
What: In `references/tech-debt.md`, activate `promoted` (status) and `promoted_to` (field), and
document the one-way `backlog → product-plan` promotion flow, the ephemeral product-plan lifecycle,
and the durable `docs/dev/product-plans/<project-slug>.md` location — as the single source of truth.
Used by: `dev:spec` (Task 3) and `dev:done` (Task 4) implement against this contract; `dev:debt`
(Task 5) surfaces the `promoted` status it defines.
Depends on: nothing — independent of Task 1.
Files: modify `plugins/dev/references/tech-debt.md`.
Interfaces:
- Consumes: nothing.
- Produces: the live `promoted` status value; the `promoted_to` field semantics (path of the
  product-plan a backlog item spawned); the documented one-way flow (`open → promoted → closed`,
  never demote); the ephemeral lifecycle (plan deleted on project completion). These are the
  interface Tasks 3 and 4 write and read.
- State keys: none.

Implementation steps:
1. Front-matter schema block (~line 66): change the `status` comment from
   `open | in-progress | closed (promoted is reserved — see P3)` to include `promoted` as a live
   backlog-only value: `open | in-progress | closed | promoted (promoted is backlog-only, see below)`.
2. `promoted_to` field line (~line 75): drop "reserved (Decision 7, cycle 4); no procedure here";
   replace with a live description: `optional — for a backlog item promoted to a product-plan, the
   repo-relative path of the plan it spawned (docs/dev/product-plans/<project-slug>.md). Set by
   dev:spec at promotion; cleared never (one-way).`
3. `status` field description (~line 92): change `open | in-progress | closed (plus the reserved
   promoted, P3)` to name `promoted` as live and backlog-only.
4. `promoted_to` field bullet (~line 109): replace the "Reserved … no procedure this cycle" text
   with the live semantics from step 2, and reference the promotion flow section added in step 6.
5. Lifecycle section (~line 169): replace the "`promoted` is a **reserved** state value … no
   procedure here" paragraph with the live lifecycle. Update the state diagram to include the
   promotion path:
   ```
   open ──► promoted ──► closed        (backlog item promoted to a product-plan, then completed)
     │                     ▲
     └──► in-progress ──────┤
     └──► closed  (paid directly / dropped / obsolete)
   ```
   State description: `open → promoted` when `dev:spec` spawns a product-plan **from** this backlog
   item (sets `promoted_to`); `promoted → closed` when that product-plan's project completes
   (`dev:done` archives the item to `docs/backlog/closed/`). Note `promoted` is **one-way** — a plan
   never demotes back to a backlog item.
6. Add a short **one-way promotion flow + ephemeral product-plan lifecycle** subsection (near the
   lifecycle section) stating, as the single source of truth — no copy in individual skills:
   - A product-plan is an **ephemeral single-project milestone carrier**, living at
     `docs/dev/product-plans/<project-slug>.md`, **deleted on project completion**. It is not a
     standing backlog; the standing store is `docs/backlog/`.
   - Promotion is **one-way**: `dev:spec` spawns a product-plan from a `docs/backlog/` item and sets
     the item `status: promoted` + `promoted_to: <plan-path>`. On project completion `dev:done`
     deletes the plan and moves the source item `promoted → closed`, reverse-looked-up by
     `promoted_to`. A plain product-scale request with no originating backlog item spawns a plan with
     no back-link (nothing to link).
   - A promoted-but-never-completed project leaves its plan in place by design (deleted on
     completion, not on a timer); `/dev:debt` shows the item as `promoted` so it is never silently
     stranded.

### Task 3: Relocate plan writes + promotion back-link in dev:spec
What: Point every product-plan read/write in `dev:spec` at `docs/dev/product-plans/<project-slug>.md`,
define `<project-slug>` and the child-cycle recovery rule, record the full path in
`state.json.product_plan`, and — when the spec originates from a `docs/backlog/` item — set the
promotion back-link on that item at **both** plan-writing paths (Step 2 and Step 4).
Used by: `dev:done` (Task 4) reads `state.json.product_plan` and the slug scheme; the contract
(Task 2) is the promotion definition this implements.
Depends on: Task 2 (the `promoted`/`promoted_to` contract).
Files: modify `plugins/dev/skills/spec/SKILL.md` (Steps 2, 4, 6; state template ~line 192).
Interfaces:
- Consumes: `promoted` status + `promoted_to` field semantics from Task 2.
- Produces:
  - the `<project-slug>` scheme (kebab-case product name, `^[a-z0-9][a-z0-9-]*$`);
  - the durable path `docs/dev/product-plans/<project-slug>.md` (writer-side create-if-absent);
  - `state.json.product_plan` = full repo-relative path to the relocated plan (its **new
    semantics** — Task 4 consumes this exact value to locate the plan);
  - the child-cycle recovery rule (nested child inherits the parent's `product_plan` value).
- State keys: `product_plan` — **existing** key, semantics changed (now the full relocated path,
  now inherited by nested children). Written by the deferred Step 6 block in both modes identically
  → `(writes: both)`. No new key is introduced.

Implementation steps:
1. **Step 2 (Scale Detection), line ~47:** replace the target-path rule. New text: the target is
   always `docs/dev/product-plans/<project-slug>.md`, where `<project-slug>` is the kebab-cased
   product name (constrained `^[a-z0-9][a-z0-9-]*$`). Remove the parent-vs-top-level path fork.
   Keep the deferred-write discipline (content prepared now, written after Step 6).
2. **Step 2 promotion back-link:** add that **if this spec originates from a `docs/backlog/<slug>.md`
   item** (the user named/pointed the spec at a backlog item), carry that source slug; the deferred
   Step 6 write will set the item `status: promoted` + `promoted_to: docs/dev/product-plans/<slug>.md`.
   If there is no originating backlog item, no back-link.
3. **Step 4 (Scope Check), lines ~78–79:** same relocation — target
   `docs/dev/product-plans/<project-slug>.md`, remove the nested/top-level fork. Add the identical
   promotion back-link clause (Step 4 is the "multi-cycle nature emerges through conversation" path;
   the back-link must fire here too, closing the invariant hole where a Step-4-emergent
   product-scale backlog item would otherwise spawn a plan with no back-link).
4. **Path-authoring — Step 6 deferred write block, lines ~226–250 (path (A), when this cycle is
   itself product-scale via Step 2/4):** rewrite. New behavior:
   - Compute `<project-slug>`; path is `$WORKDIR/docs/dev/product-plans/<project-slug>.md`.
   - Create `docs/dev/product-plans/` if absent (writer-side create-if-absent).
   - Append-if-exists at that path; else create from the Step 2 template.
   - Set `state.json.product_plan` to `"docs/dev/product-plans/<project-slug>.md"` (full path).
   - If this spec originated from a backlog item (steps 2/3 above), also write the back-link:
     set `docs/backlog/<source-slug>.md` `status: promoted` + `promoted_to: <plan-path>`, and stage
     it in the same commit. Update the commit's `git add` pathspec to include the plan path, the
     backlog item (when promoted), and `state.json`.
5. **Path-inheritance (path (B)) — add near where Step 6 sets `parentFeature`/`worktreePath`
   (~line 210), OUTSIDE the deferred authoring block of step 4.** This must run even when the child
   is a plain feature cycle that never authored a plan: if Step 1 nesting detection found an active
   parent whose committed `state.json.product_plan` is non-null, set this child's
   `state.json.product_plan` to that same path (inherit — do not compute a new slug). Precedence: a
   cycle that is *itself* product-scale takes path (A) instead; a non-nested feature cycle leaves
   `product_plan` `null`. State the precedence explicitly so Build never runs both.
6. **Step 6 state.json template, line ~192:** leave the `"product_plan": null` default as-is (null =
   non-product-scale, non-inheriting cycle) — only its *set* value changes, documented in steps 4–5.
7. Update the inline comment at ~line 243 (`# <product-plan-path> is …`) to name the single new
   path scheme, not the old fork.
8. Self-check: grep `dev:spec` after editing for any surviving `docs/dev/product-plan.md` or
   `docs/dev/<parent>/product-plan.md` live reference — there must be none.

### Task 4: Ephemeral deletion + source-item close in dev:done
What: Rewrite `dev:done` Step 3 to locate the plan uniformly via `state.json.product_plan`, and add
the project-completion trigger that deletes the plan and closes the promoted source item — while a
mid-project child teardown only checks off its item.
Used by: This is terminal skill behavior — no later task consumes it.
Depends on: Task 3 (the `state.json.product_plan` = full-path contract + slug scheme) and Task 2
(the `promoted`/`promoted_to` fields + the promotion-terminus definition).
Files: modify `plugins/dev/skills/done/SKILL.md` (Step 3, lines ~130–147).
Interfaces:
- Consumes: `state.json.product_plan` (full relocated path) from Task 3; `promoted`/`promoted_to`
  semantics + the promotion-terminus rule from Task 2.
- Produces: nothing later tasks reference.
- State keys: reads `product_plan` (no new key; no write).

Implementation steps:
1. **Locate the plan (line ~132):** replace the parentFeature/top-level fork with a single rule —
   "if `state.json.product_plan` is null, skip this step; otherwise the governing plan is at
   `state.json.product_plan` (always `docs/dev/product-plans/<slug>.md`)." Remove the
   `parentFeature`-based nested-path reconstruction.
2. Update the surrounding prose (line ~134) that explains why the plan is present at the detached
   integration tip: it still rides the creating cycle's PR, but now lives at the durable location and
   is inherited by children via `product_plan`; drop the "top-level branch fires only when
   product_plan non-null which dev:spec sets for top-level product-scale cycles" wording (now every
   product-scale cycle sets it).
3. **Check-off (unchanged core):** read the plan, match this feature's line item, flip `- [ ]` →
   `- [x]`, increment the header's cycles-completed count.
4. **Completion detection (new):** after the check-off, test whether **every** checkbox item across
   all milestones is now `[x]`. That boolean is "project complete".
5. **On project complete (new):**
   a. Reverse-look-up the source backlog item: grep `docs/backlog/*.md` for a front-matter line
      `promoted_to: <plan-path>` (the exact `state.json.product_plan` value). At most one match by
      the one-way invariant.
   b. If a source item is found, execute the `promoted → closed` move inline (P3 mechanics): set its
      front-matter `status: closed`, `closed:` (today's date from `date -u +%Y-%m-%d`),
      `closed_by: <feature>`, and `git mv` it to `docs/backlog/closed/<same-basename>.md`. Note in
      the step this is the *designed* promotion terminus, distinct from incidental debt closes that
      route through the buffer.
   c. `git rm` the plan file (`docs/dev/product-plans/<slug>.md`).
   d. Commit both the plan removal and the source-item close (when present) in **one** commit, then
      `push_integration`. Guard the commit so an empty stage does not error.
6. **On not complete:** commit only the check-off (today's behavior), as before.
7. Trace the git sequence end-to-end: the plan file and the backlog item both exist at the detached
   `$INTEGRATION` tip (Step 2 left `$WORKDIR` there); `git mv` + `git rm` both operate on tracked
   files present at that tip; `push_integration` is defined at Step 2. Confirm the deletion cannot
   fire on a child teardown (guarded by the all-`[x]` test in step 4).

### Task 5: Continuation path, promoted surfacing, exhaustive sweep
What: Update `dev:dev`'s product-plan continuation to the new location, surface `promoted` status in
`dev:debt`'s list, and run the spec-mandated exhaustive grep across the full `plugins/dev/` surface
to catch any live old-path read/write the named sites missed.
Used by: Terminal — no later task consumes it.
Depends on: Task 3 (new path scheme) and Task 2 (the `promoted` status value).
Files: modify `plugins/dev/skills/dev/SKILL.md` (Step 6, ~line 128–130) and
`plugins/dev/skills/debt/SKILL.md` (Step 3, ~line 65–93).
Interfaces:
- Consumes: the `docs/dev/product-plans/<slug>.md` scheme (Task 3); the `promoted` status (Task 2).
- Produces: nothing later tasks reference.
- State keys: none.

Implementation steps:
1. **dev:dev Step 6 (line ~130):** the "When a `docs/dev/product-plan.md` exists" continuation
   trigger no longer matches a fixed path. Rewrite to detect any plan under
   `docs/dev/product-plans/*.md` (a decomposition cycle's plan reaches `main` via its PR). Update the
   surrounding prose (line ~128) that references the old singular path.
2. **dev:debt Step 3 (lines ~71–87):** add a status indicator to each printed item block. For items
   whose front-matter `status` is not `open` (notably `promoted`), print a `Status: <status>` line
   (e.g. `Status: promoted`) so promoted items are visible and distinguished from plain open debt.
   Open items may omit the line or show `Status: open` for consistency — pick one and apply it
   uniformly. Ensure the "No open tech debt" empty-corpus logic (line ~92) still counts a `promoted`
   item as present in the active corpus (it lives outside `closed/`), so a lone promoted item is
   never mis-reported as "no items".
3. **Exhaustive sweep (spec Edge Case — the belt-and-suspenders pass):** run
   `grep -rn "product-plan" plugins/dev/` in `$WORKDIR`. For every hit, classify as **live
   read/write** (rewrite to the new scheme) or **illustrative/historical** (leave). Confirm the only
   remaining `docs/dev/product-plan.md` / `docs/dev/<parent>/product-plan.md` strings are the two
   exempt carrying-cost example rows in `references/tech-debt.md` (~lines 361–362), which cite the
   nested path as debt-qualification *teaching text*, not a live operation. Leave those unless their
   surrounding contract prose was itself rewritten in Task 2.
4. Final verification: `grep -rn "docs/dev/product-plan\.md\|docs/dev/<parent>/product-plan\.md"
   plugins/dev/` returns only the two exempt example rows and no live read/write.

## Edge Cases
| Edge case | Handled in | Approach |
|-----------|-----------|----------|
| Reference sweep targets live reads/writes, not textual mentions | Task 5 | Grep full `plugins/dev/`; rewrite live sites, leave the two exempt tech-debt.md example rows (~361–362) |
| Promoted-but-never-completed project | Task 2 (doc) + Task 5 (surfacing) | Plan stays by design; `/dev:debt` shows the item as `promoted` — never silently stranded |
| Deletion trigger precision (completion ≠ any child teardown) | Task 4 | Delete only when the all-`[x]` completion test passes; child teardown only checks off |
| Migration collision (`backlog-debt-backfill` vs `debt-*`) | Task 1 | `<type>-` prefix + distinct slugs → no disambiguation needed (ADR 8(c)) |
| `state.json` schema stays honest | Task 3 | Existing `product_plan` repurposed to full relocated path + inherited by children; no new key, `(writes: both)` |
| Both modes exercise every automatic write identically | Task 3, Task 4 | All writes are in unconditional (mode-agnostic) skill steps — no autopilot-only or standard-only path |

## Out of Scope
- The Linear-promotion feature (`debt-linear-promotion`) — migrated as an item, not built.
- `debt-backfill` — migrated as an item, not implemented.
- `/dev:debt add` capture verb, inbox/convert verb, cross-repo routing — ADR follow-on 3.
- The tech-debt-entry migration (Decision 8(a)/(b)) — already shipped.
- `debt-reflect-dogfood-pr-base` — unrelated open item.
- **Closing `debt-nested-product-plan-lifetime`** is *not* a Build task — the close-intent already
  sits in `docs/dev/product-plan-correction/debt-pending.md` `## To Close`, and **this cycle's own
  `dev:done` Step 6a** executes it automatically after merge (Success Criterion satisfied by the
  framework, not by a build step).

## Risks and Unknowns
- **Promotion is forward-behavior, unexercised by this cycle's own Build.** Tasks 3's back-link and
  Task 4's completion-delete/close paths cannot be end-to-end tested inside this cycle (no promotion
  occurs here). Mitigation: specify them precisely against the contract (Task 2) and rely on the
  interface-consistency cold review; the first real promotion is the true test. This is inherent to a
  plumbing change that installs future behavior.
- **`<project-slug>` derivation from a free-text product name.** A product name with punctuation or
  non-ASCII could slugify ambiguously. Mitigation: Task 3 constrains the slug to
  `^[a-z0-9][a-z0-9-]*$` (the repo's existing feature-slug allowlist shape); Build applies the same
  kebab-casing rule already used for feature slugs. Investigate reuse of any existing slug helper in
  `dev:spec` during Task 3.
- **Child-inheritance timing.** The recovery rule assumes the parent's `state.json.product_plan` is
  already set when the child's `dev:spec` runs nesting detection. True for the intended flow (parent
  decomposes first, then children spawn). Mitigation: Task 3 reads the parent's *committed*
  `state.json`; a child cut before the parent set `product_plan` inherits `null` and simply skips
  plan updates — safe degradation, matching today's nested-without-plan behavior.
