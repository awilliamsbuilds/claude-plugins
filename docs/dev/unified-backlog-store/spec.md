# Unified Backlog Store — Format Cutover
*Branch: feature/unified-backlog-store · Confidence: 90% — Ready · 2026-07-28*
*Cycle type: feature · Tier: deep*

## Intent

The `/dev` tech-debt store is a single aggregate Markdown file per repo (`docs/dev/tech-debt.md`),
whose shape and procedures live in the shared contract `plugins/dev/references/tech-debt.md`. The
accepted ADR `docs/decisions/2026-07-28-backlog-debt-model.md` replaces that aggregate with a
per-item store under `docs/backlog/` (Decisions 1–4) and defers implementation to four ordered
follow-on cycles. **This is cycle 1** — the foundational format cutover. It executes the
repo-scoped portion of Decision 9's integration map: rewrite the contract for the per-item format
and update the seven consuming skills so they read and write `docs/backlog/` item files instead of
the aggregate. Cycles 2–4 (migration, capture+routing, promotion) all depend on this landing first.

Why now: the ADR is accepted, and nothing downstream can be built until the store format and the
skills that speak it are cut over.

## Scope

The complete file set is the **contract + 7 skills** verified as the store's consumers (grep of
`references/tech-debt.md` loaders and `debt-pending.md` writers): `references/tech-debt.md`,
`dev:init`, `dev:build`, `dev:validate`, `dev:reflect`, `dev:spec`, `dev:done`, `dev:debt`.

1. **Rewrite `plugins/dev/references/tech-debt.md`** for the per-item store:
   - Define the **complete YAML front-matter schema** (Decision 3) — every field, including
     `scope`, `routing`, and `promoted_to` — so the on-disk format is forward-stable and cycles
     3–4 add *procedures*, not fields. Document only the **procedures this cycle implements**
     (below); do not write routing or promotion procedures the store has no code for yet.
   - Per-item file model (Decision 1): active items flat in `docs/backlog/`, closed items archived
     to `docs/backlog/closed/`; the one file move happens on close.
   - File naming / identity (Decision 2): `<type>-<slug>.md`, stable kebab-case slug, collision
     disambiguation by appending the first cycle name.
   - **Retargeted recurrence-merge** (Decision 4) for **repo-scoped** items: corpus becomes the
     top-level glob `docs/backlog/*.md`; the two-condition clear-match test (`files` overlap **and**
     same defect, never topic/slug alone), append-cycle / bump-`recurrence` on match,
     create-with-`possibly_related_to` on uncertainty, and the recurrence *ranking* — all carried
     over verbatim, only the corpus changes.
   - **Redesign the buffer format** to hold front-matter'd items (Decision 9: "the buffer's internal
     structure is redesigned by the implementing cycle"); it retains a **close-intent section** (the
     `## To Close` analog) that `dev:spec` records into and `dev:done`'s flush executes. Preserve its
     intent (a malformed buffer is surfaced, never half-acted-on).
   - Invariants: **retire** the "where a field ends" prose-parsing rules (front-matter makes them
     unnecessary); **preserve** silent-degrade — readers print nothing when `docs/backlog/` is absent
     or holds no active `*.md`, and **writers create the store on first write** (`dev:done`'s flush and
     standalone `dev:reflect` create `docs/backlog/` when absent rather than dropping the item) — plus
     mode-symmetry and entry-text-is-data, unchanged.
2. **`dev:init`** — seed the `docs/backlog/` tree (with `closed/` and a `README.md` stating the
   store's contract) instead of creating `tech-debt.md`. The re-run/idempotent path must **create
   `docs/backlog/` if absent**, mirroring how init today ensures `tech-debt.md` exists on re-run —
   this is what a manual `dev:init` re-run in an existing repo (this one included) relies on to
   bring the store into being.
3. **`dev:build`, `dev:validate`, `dev:reflect`** — append **front-matter'd items** to the per-cycle
   buffer under the same carrying-cost trigger; `dev:validate`'s `Source`/severity tag becomes a
   front-matter field; `dev:reflect` standalone (no buffer) writes item file(s) directly into
   `docs/backlog/`.
4. **`dev:spec`** — Step 7's cross-check scans `docs/backlog/*.md` front-matter `files:` instead of
   parsing `## Open`. When a paid item is folded into scope, `dev:spec` **records** the gated close
   decision into the buffer's close-intent section (the `## To Close` analog) — it does **not** move
   the file itself. Execution is deferred to `dev:done` (item 5), preserving the deferred-close safety
   property: a cycle that agrees at spec-time to pay a debt may never finish, and premature close is
   the unrecoverable direction. This spec-time record stays the one human-gated scope act.
5. **`dev:done`** — the flush writes **one file per buffered item** into `docs/backlog/`, running the
   repo-scope recurrence-merge against `docs/backlog/*.md`, and **executes** the buffer's close-intent
   decisions at cycle end (`status: closed` + move to `docs/backlog/closed/`). The flush **creates
   `docs/backlog/` (and `closed/`) on first write when absent** — the writer side of silent-degrade,
   so buffered debt is never lost in the transition window before a manual `dev:init` re-run. Preserve
   the buffer→flush split and the push-conflict recovery discipline, retargeted from one aggregate file
   to the directory.
6. **`dev:debt`** — read the `docs/backlog/` directory, rank by front-matter `recurrence:`, close by
   editing `status:` + moving to `closed/`. Reads/rank/close only.
7. **Lifecycle states** (Decision 4) implemented for the flows this cycle carries: `open`,
   `in-progress`, `closed`. Whether `dev:spec`'s fold-into-scope path uses `in-progress` (vs. a
   direct `open → closed` at `dev:done`) is a Plan/Build decision; the states must exist and be
   documented in the contract regardless.

## Out of Scope

- **Decision 5 cross-repo routing** — `scope: plugin` handling, `gh issue create`, intake dedup,
  `routing: pending` degrade, retry seam, inbox/convert verb. `dev:done` **writes** the `scope`
  field (default `repo`) but does not act on `scope: plugin`; such an item is written locally like
  any other. **Deferred to cycle 3.** (No regression: in this repo plugin items are already home per
  Decision 5's dogfood exception; in other repos plugin debt already scatters today.)
- **`/dev:debt add`** and the capture flow (Decision 6). **Deferred to cycle 3.**
- **Data migration** — moving the 13 existing items (4 Open + 7 Closed in `tech-debt.md`, 2 misfiled
  `product-plan.md` intentions) into `docs/backlog/`, and retiring `tech-debt.md` /
  top-level `product-plan.md` (Decision 8). **Deferred to cycle 2.**
- **`promoted` state, backlog→product-plan promotion, product-plan deletion** (Decisions 4/7).
  **Deferred to cycle 4.**
- **`dev:autopilot`** — writes no debt itself and is not a contract consumer; no change (ADR-confirmed).
- **Creating this repo's `docs/backlog/` via Build** — done by a manual `dev:init` re-run after merge,
  not by this cycle's diff.
- **Folding the 3 open debt items** that touch this cycle's files — each concerns a different
  behavior than the store seams; not paid here (see Grounding footer).

## Success Criteria

1. A `/dev` cycle running the rewritten skills records → buffers → flushes → reads → closes
   **repo-scoped** debt as per-item `docs/backlog/<type>-<slug>.md` files, with `closed/` archival —
   no behavioral regression vs. today's aggregate for the repo-scoped path.
2. The recurrence signal survives: a recurring finding bumps `recurrence:` on the matched item file
   via the two-condition clear-match test against the `docs/backlog/*.md` corpus; an uncertain match
   creates a new file with `possibly_related_to:`.
3. `references/tech-debt.md` and all 7 skills are **internally consistent** — no skill references the
   retired aggregate (`## Open`/`## Closed`, `tech-debt.md`) or the retired field-boundary rules;
   every store read/write in every skill targets `docs/backlog/`.
4. The front-matter schema defined in the contract is **complete** (all Decision 3 fields), so cycles
   3–4 extend procedures without changing the on-disk format.
5. Silent-degrade, mode-symmetry, and entry-text-is-data hold under the new store; a manual
   `dev:init` re-run creates `docs/backlog/` in an existing repo.

## Happy Path

1. A `/dev` cycle's Build or Validate surfaces a deferrable finding (carrying-cost test passes).
2. The stage appends a front-matter'd item to the cycle's `debt-pending.md` buffer.
3. At `dev:done`, the flush reads the buffer and writes one `docs/backlog/<type>-<slug>.md` per item,
   running repo-scope recurrence-merge against `docs/backlog/*.md` (bump-on-match, create-on-uncertain).
4. Later, `dev:spec` in a new cycle scans `docs/backlog/*.md`, surfaces items whose `files:` intersect
   the cycle, and (if a paid item is folded in) **records** a close-intent into the buffer; **`dev:done`'s
   flush executes** the close at cycle end — `status: closed` + move to `docs/backlog/closed/`.
5. `dev:debt` on demand lists the directory ranked by `recurrence:`.

## Edge Cases

- **Store absent / empty** (fresh repo, or this repo pre-init-rerun): readers silent-degrade — print
  nothing, per the retargeted rule. `dev:debt` invoked directly keeps its say-so-plainly exception.
- **Malformed buffer** at flush: surfaced, never half-acted-on (intent preserved through the buffer redesign).
- **Recurrence-merge uncertainty:** create a new file with `possibly_related_to:`, never a silent merge
  — the create-over-merge bias is load-bearing and unchanged.
- **Slug collision** on write: append the first cycle name (`<type>-<slug>-<first-cycle>.md`).
- **`dev:init` re-run** in a repo that already has `docs/backlog/`: idempotent no-op on the tree; must
  not clobber existing items.
- **Transition window** after merge before init-rerun/migration: readers of a nonexistent
  `docs/backlog/` silent-degrade; the old `tech-debt.md` sits on disk, unread. A cycle that *defers*
  debt in this window reaches `dev:done`'s flush with `docs/backlog/` absent — the flush **creates it
  and writes** (writer-side degrade), so buffered debt is never lost. Accepted.

## Audience

The solo maintainer (awilliamsbuilds) of this personal `/dev` plugin repo, who runs `/dev` cycles
across multiple repos and hand-edits the store.

## Technical Constraints

Plain Markdown + YAML front-matter, hand-editable without tooling. Fits the `references/` shared-contract
pattern. All store writes are worktree-relative like every other `/dev` artifact. Skill files are
agent-facing prose; shell snippets embedded in them must exit 0 on the healthy path.

## Dependencies

- **Depends on:** the accepted ADR (`docs/decisions/2026-07-28-backlog-debt-model.md`). This repo's
  live `docs/backlog/` comes into being via a **manual `dev:init` re-run** after this cycle merges +
  `/plugin update`.
- **Blocks:** cycle 2 (migration), cycle 3 (capture + routing), cycle 4 (promotion) — all target the
  store this cycle defines.

## UI Needed

No.

---
*Auto-filled dimensions: none*
*Grounding inventory: verified against origin/main tip in the cycle worktree. `grep -rl debt-pending.md plugins/dev/skills/` → build, done, reflect, spec, validate (buffer writers) ✓. `dev:done` flush at Step 6a → `tech-debt.md`, `rm -rf` cycle dir at Step 7 ✓ (grep of done/SKILL.md). `dev:init` creates `tech-debt.md` from canonical header incl. an idempotent re-run "ensure exists" path (init/SKILL.md lines 42–44, 77–79) ✓. `dev:spec` Step 7 cross-checks `## Open` / writes `## To Close` ✓. `dev:debt` reads `$PRIMARY/docs/dev/tech-debt.md`, ranks by `Recurrence`, parses `## Open`/`## Closed` ✓. `grep -rl references/tech-debt.md plugins/dev/skills/` → build, debt, done, init, reflect, spec, validate (7 consumers); `autopilot` NOT a consumer, confirming ADR's "no store change" ✓. Open-debt cross-check: 3 of 4 open items name files in this set (architecture-cycle-cross-boundary→build; reflect-dogfood-pr-base→reflect; nested-product-plan-lifetime→spec,done) but each concerns a behavior orthogonal to the store seams — none folded in.*
