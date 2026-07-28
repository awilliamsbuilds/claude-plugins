# Tech-Debt Migration — Implementation Plan
*Branch: feature/tech-debt-migration · 2026-07-28*

Migrate the 4 Open + 7 Closed entries from the orphaned aggregate `docs/dev/tech-debt.md`
into per-item `docs/backlog/` files (P1 front-matter + verbatim body), then retire the aggregate.
Data files only — no skill or contract edit, and **no new `state.json` key** (this migration
introduces none).

## Source-of-truth line ranges (in `docs/dev/tech-debt.md`)

Bodies are transferred **verbatim** from these ranges. In every case the trailing
`**Files:**` prose line is the **last line** of the entry and is **NOT** copied into the body —
it becomes the front-matter `files:` list (the P1 model retires the prose `**Files:**` field).
The body is exactly the `**What's wrong:**` / `**Why deferred:**` / `**Done looks like:**`
prose above that line.

| Entry | Body source lines | Body ends before |
|---|---|---|
| autopilot-grounding-gate (Open) | 13–22 | `**Files:**` (line 23) |
| nested-product-plan-lifetime (Open) | 28–39 | `**Files:**` (line 40) |
| reflect-dogfood-pr-base (Open) | 45–47 | `**Files:**` (line 48) |
| arch-cross-boundary-transport (Open) | 53–55 | `**Files:**` (line 56) |
| reflect-hardcoded-path (Closed) | 63–75 | `**Files:**` (line 76) |
| spec-product-plan-push-main (Closed) | 81–89 | `**Files:**` (line 90) |
| feature-slug-allowlist (Closed) | 95–106 | `**Files:**` (line 107) |
| gate-path-state-writes (Closed) | 112–150 | `**Files:**` (line 151) |
| validate-fix-loop-verification (Closed) | 156–182 | `**Files:**` (line 183) |
| validate-config-contract-wording (Closed) | 188–190 | `**Files:**` (line 191) |
| validate-stale-loops-max (Closed) | 196–198 | `**Files:**` (line 199) |

## Files

| File | Action | Purpose |
|------|--------|---------|
| docs/backlog/debt-autopilot-grounding-gate.md | Create | Open item 1 |
| docs/backlog/debt-nested-product-plan-lifetime.md | Create | Open item 2 |
| docs/backlog/debt-reflect-dogfood-pr-base.md | Create | Open item 3 |
| docs/backlog/debt-arch-cross-boundary-transport.md | Create | Open item 4 (the post-ADR 4th) |
| docs/backlog/closed/ | Create (dir) | Archive location for closed items — currently missing |
| docs/backlog/closed/debt-reflect-hardcoded-path.md | Create | Closed item 1 |
| docs/backlog/closed/debt-spec-product-plan-push-main.md | Create | Closed item 2 |
| docs/backlog/closed/debt-feature-slug-allowlist.md | Create | Closed item 3 |
| docs/backlog/closed/debt-gate-path-state-writes.md | Create | Closed item 4 (recurrence:2 exception) |
| docs/backlog/closed/debt-validate-fix-loop-verification.md | Create | Closed item 5 |
| docs/backlog/closed/debt-validate-config-contract-wording.md | Create | Closed item 6 |
| docs/backlog/closed/debt-validate-stale-loops-max.md | Create | Closed item 7 |
| docs/dev/tech-debt.md | Delete | Retire the orphaned aggregate (`git rm`) |

## Tasks

### Task 1: Write the 4 Open item files
What: Create one `docs/backlog/debt-<slug>.md` file (`status: open`) per Open source entry.
Used by: `/dev:debt`'s list view (P5 corpus / P8 ranking) once the files exist.
Depends on: nothing — first task.
Files (all Create):
- docs/backlog/debt-autopilot-grounding-gate.md
- docs/backlog/debt-nested-product-plan-lifetime.md
- docs/backlog/debt-reflect-dogfood-pr-base.md
- docs/backlog/debt-arch-cross-boundary-transport.md
Interfaces:
- Consumes: nothing (source data is `docs/dev/tech-debt.md`, already present).
- Produces: 4 active P5-corpus item files (`docs/backlog/debt-*.md`). Task 3 counts and round-trips them.
- State keys: none — this task introduces no new `state.json` key.

Every file's front-matter carries the same three constants: `type: debt`, `scope: repo`,
`status: open`. Per-file front-matter (derive `first_recorded`/`cycles`/`recurrence`/`files`
from each source meta line; all four are `recurrence: 1`):

**docs/backlog/debt-autopilot-grounding-gate.md**
```yaml
---
type: debt
scope: repo
status: open
first_recorded: 2026-07-21
cycles: [spec-grounding-and-clock]
recurrence: 1
files:
  - plugins/dev/skills/autopilot/SKILL.md
---
```
Body: verbatim from source lines 13–22 (What's wrong / Why deferred / Done looks like).

**docs/backlog/debt-nested-product-plan-lifetime.md**
```yaml
---
type: debt
scope: repo
status: open
first_recorded: 2026-07-22
cycles: [tech-debt-tracking]
recurrence: 1
files:
  - plugins/dev/skills/spec/SKILL.md
  - plugins/dev/skills/done/SKILL.md
---
```
Body: verbatim from source lines 28–39.

**docs/backlog/debt-reflect-dogfood-pr-base.md**
```yaml
---
type: debt
scope: repo
status: open
first_recorded: 2026-07-28
cycles: [reflect-repo-discovery]
recurrence: 1
files:
  - plugins/dev/skills/reflect/SKILL.md
---
```
Body: verbatim from source lines 45–47.

**docs/backlog/debt-arch-cross-boundary-transport.md** (the 4th Open entry the ADR table omitted — slug newly assigned)
```yaml
---
type: debt
scope: repo
status: open
first_recorded: 2026-07-28
cycles: [backlog-debt-model]
recurrence: 1
files:
  - plugins/dev/skills/build/SKILL.md
  - plugins/dev/skills/plan/SKILL.md
---
```
Body: verbatim from source lines 53–55.

Implementation steps:
1. For each of the four files, write the front-matter block above, then a blank line, then
   the body prose copied verbatim from the named source line range.
2. Do **not** copy the source's trailing `**Files:**` line into the body — it is already
   captured in the `files:` front-matter list.
3. Preserve all body Markdown exactly (bold labels, inline `code`, punctuation, line wrapping).

### Task 2: Create `closed/` and write the 7 Closed item files
What: Create the `docs/backlog/closed/` directory (currently missing) and one archived
`debt-<slug>.md` file (`status: closed`) per Closed source entry.
Used by: `dev:debt`'s "show closed" view; slug-uniqueness checks (P2 checks `closed/` too).
Depends on: nothing — runs in parallel with Task 1 (no shared file, no ordering).
Files (all Create):
- docs/backlog/closed/ (directory)
- docs/backlog/closed/debt-reflect-hardcoded-path.md
- docs/backlog/closed/debt-spec-product-plan-push-main.md
- docs/backlog/closed/debt-feature-slug-allowlist.md
- docs/backlog/closed/debt-gate-path-state-writes.md
- docs/backlog/closed/debt-validate-fix-loop-verification.md
- docs/backlog/closed/debt-validate-config-contract-wording.md
- docs/backlog/closed/debt-validate-stale-loops-max.md
Interfaces:
- Consumes: nothing (source data is `docs/dev/tech-debt.md`).
- Produces: 7 archived item files under `docs/backlog/closed/`. Task 3 counts and round-trips them.
- State keys: none — this task introduces no new `state.json` key.

Every file carries `type: debt`, `scope: repo`, `status: closed`, plus `closed:` and
`closed_by:` from the Closed meta line. Per the spec (Happy Path step 3), a Closed meta line
carries **no `Cycles:` list**, so `cycles:` takes the single closing cycle — `cycles: [<closed_by>]`.

**docs/backlog/closed/debt-reflect-hardcoded-path.md**
```yaml
---
type: debt
scope: repo
status: closed
first_recorded: 2026-07-22
cycles: [reflect-repo-discovery]
recurrence: 1
files:
  - plugins/dev/skills/reflect/SKILL.md
closed: 2026-07-28
closed_by: reflect-repo-discovery
---
```
Body: verbatim from source lines 63–75.

**docs/backlog/closed/debt-spec-product-plan-push-main.md**
```yaml
---
type: debt
scope: repo
status: closed
first_recorded: 2026-07-22
cycles: [init-rerun-hardening]
recurrence: 1
files:
  - plugins/dev/skills/spec/SKILL.md
closed: 2026-07-23
closed_by: init-rerun-hardening
---
```
Body: verbatim from source lines 81–89.

**docs/backlog/closed/debt-feature-slug-allowlist.md**
```yaml
---
type: debt
scope: repo
status: closed
first_recorded: 2026-07-22
cycles: [done-doc-reconciliation]
recurrence: 1
files:
  - plugins/dev/skills/fix/SKILL.md
  - plugins/dev/skills/spec/SKILL.md
  - plugins/dev/skills/done/SKILL.md
closed: 2026-07-24
closed_by: done-doc-reconciliation
---
```
Body: verbatim from source lines 95–106.

**docs/backlog/closed/debt-gate-path-state-writes.md** — ⚠ recurrence-vs-cycles exception (SC #3/#4). Preserve `recurrence: 2` against a single-cycle `cycles:` list; do **not** normalize to 1. Body carries a Markdown table and inline code — transfer exactly.
```yaml
---
type: debt
scope: repo
status: closed
first_recorded: 2026-07-21
cycles: [state-write-mode-audit]
recurrence: 2
files:
  - plugins/dev/skills/spec/SKILL.md
  - plugins/dev/skills/shape/SKILL.md
  - plugins/dev/skills/plan/SKILL.md
  - plugins/dev/skills/build/SKILL.md
  - plugins/dev/skills/validate/SKILL.md
  - plugins/dev/skills/pr/SKILL.md
  - plugins/dev/skills/done/SKILL.md
  - plugins/dev/skills/autopilot/SKILL.md
  - plugins/dev/skills/reflect/SKILL.md
closed: 2026-07-25
closed_by: state-write-mode-audit
---
```
Body: verbatim from source lines 112–150 (includes the `| Counter | … |` table and the two
`| … |`-row groups — copy the table rows and blank lines exactly).

**docs/backlog/closed/debt-validate-fix-loop-verification.md**
```yaml
---
type: debt
scope: repo
status: closed
first_recorded: 2026-07-22
cycles: [harden-validate]
recurrence: 1
files:
  - plugins/dev/skills/validate/SKILL.md
closed: 2026-07-25
closed_by: harden-validate
---
```
Body: verbatim from source lines 156–182 (contains inline `code` spans with backticks and `&&` — copy exactly).

**docs/backlog/closed/debt-validate-config-contract-wording.md**
```yaml
---
type: debt
scope: repo
status: closed
first_recorded: 2026-07-23
cycles: [harden-validate]
recurrence: 1
files:
  - plugins/dev/skills/validate/SKILL.md
closed: 2026-07-25
closed_by: harden-validate
---
```
Body: verbatim from source lines 188–190.

**docs/backlog/closed/debt-validate-stale-loops-max.md**
```yaml
---
type: debt
scope: repo
status: closed
first_recorded: 2026-07-23
cycles: [harden-validate]
recurrence: 1
files:
  - plugins/dev/skills/validate/SKILL.md
closed: 2026-07-25
closed_by: harden-validate
---
```
Body: verbatim from source lines 196–198.

Implementation steps:
1. Ensure `docs/backlog/closed/` exists (the Write tool creates parent dirs on first file write;
   if writing by other means, `mkdir -p docs/backlog/closed` first).
2. For each of the seven files, write the front-matter block above, blank line, then the body
   prose copied verbatim from the named source line range.
3. Do **not** copy the source's trailing `**Files:**` line into the body — it is captured in `files:`.
4. For `debt-gate-path-state-writes.md`, double-check `recurrence: 2` survives with a length-1
   `cycles:` list — this is the one deliberate `recurrence != len(cycles)` file (SC #3 exception).

### Task 3: Verify counts and faithfulness
What: Confirm the migration is complete and round-trips the source before the aggregate is deleted.
Used by: the gate before Task 4 — deletion of the source is irreversible, so this is the safety check.
Depends on: Task 1 and Task 2 (both must have produced their files).
Files: none created/modified (verification only).
Interfaces:
- Consumes: the 4 `docs/backlog/debt-*.md` (Task 1) and 7 `docs/backlog/closed/debt-*.md` (Task 2) files.
- Produces: nothing — terminal verification for the write phase; gates Task 4.
- State keys: none.

Implementation steps:
1. Count active items: `ls docs/backlog/debt-*.md | wc -l` → **4** (SC #1). The type-prefixed glob
   excludes `README.md` (P5).
2. Count closed items: `ls docs/backlog/closed/debt-*.md | wc -l` → **7** (SC #2).
3. Front-matter conformance (SC #3): every file has `type: debt`, `scope: repo`, `status`,
   `first_recorded`, `cycles`, `recurrence`, `files`; closed files additionally have `closed` and
   `closed_by`; open files have neither. Confirm `recurrence == len(cycles)` on all **except**
   `debt-gate-path-state-writes.md`, which is intentionally `recurrence: 2` / one cycle.
4. Faithfulness (SC #4): spot-check each file's body against its source line range — no dropped
   field, no reworded prose, dates copied from source (not re-stamped from the clock). Confirm the
   `**Files:**` prose line was dropped from every body and its paths appear in `files:`.
5. Reader smoke check (SC #6/#7): run `/dev:debt` (reads the P5 corpus) and confirm it lists the
   4 open items ranked by `recurrence` (all `recurrence: 1`, so ties break by most-recent `cycles:`
   name, P8) — i.e. the previously-invisible items are now visible. Silent-degrade (P7) is unaffected.
6. If any count is off or any spot-check fails, fix the offending file before proceeding — do NOT
   advance to Task 4 until counts are 4/7 and spot-checks pass.

### Task 4: Retire the aggregate and commit
What: `git rm` the now-fully-migrated `docs/dev/tech-debt.md` and commit the migration.
Used by: nothing downstream in this cycle; satisfies SC #5 (aggregate no longer exists).
Depends on: Task 3 (verification must have passed — deletion is irreversible).
Files: docs/dev/tech-debt.md (Delete).
Interfaces:
- Consumes: Task 3's verified-complete confirmation.
- Produces: nothing — terminal task.
- State keys: none.

Implementation steps:
1. `git -C "$WORKDIR" rm docs/dev/tech-debt.md` (removes the orphaned aggregate; SC #5).
2. Stage the 11 new files and the deletion together and commit
   (e.g. `git -C "$WORKDIR" add docs/backlog/ && git -C "$WORKDIR" commit -m "chore: migrate tech-debt.md entries to docs/backlog/ per-item store"`).
   Build's per-task commit rhythm may already have committed the Task 1/2 writes; in that case this
   commit carries only the `git rm`. Either way the end state is: 11 item files present, aggregate gone.

## Edge Cases
| Edge case | Handled in | Approach |
|-----------|-----------|----------|
| ADR table omits the 4th Open entry | Task 1 | Migrate `arch-cross-boundary-transport` like any Open entry; slug newly assigned (ADR never gave it one). |
| Slug collisions | Tasks 1 & 2 | None arise — all 11 titles are distinct → distinct slugs. Fallback if one ever did: P2 rule — append first cycle name, checking active **and** `closed/`. |
| `recurrence: 2` vs single cycle (`gate-path-state-writes`) | Task 2 | Preserve source values verbatim; do not normalize. This is the one file where `recurrence != len(cycles)` (SC #3 exception, SC #4 verbatim-history precedence). |
| Long body with Markdown table / inline code (`gate-path-state-writes`, `validate-fix-loop-verification`) | Task 2 | Transfer body verbatim including table rows, blank lines, and backticked code spans. |
| `closed/` directory missing | Task 2 | Create it on first closed-file write (Write auto-creates parents; else `mkdir -p`). |
| Irreversible source deletion | Tasks 3→4 | Verification (Task 3) gates the `git rm` (Task 4); never delete before counts=4/7 and spot-checks pass. |

## Out of Scope
- `product-plan.md` migration/retirement (Decision 8(c)) — deferred to follow-on cycle 4; still actively used by `dev:spec`/`dev:done`.
- Any `SKILL.md` or `references/tech-debt.md` edit — producing/reading stages already target `docs/backlog/`.
- Recurrence-merge across items — target store is empty; each source entry becomes exactly one file.
- Re-judging any item's `scope` — all migrated items get `scope: repo` (hand-editable later).
- `/dev:debt add` capture verb, cross-repo routing, promotion/deletion behavior — follow-on cycles 3 & 4.
