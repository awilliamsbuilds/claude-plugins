# Tech-Debt Migration — tech-debt.md → docs/backlog/
*Branch: feature/tech-debt-migration · Confidence: 95% — Ready · 2026-07-28*
*Cycle type: feature · Tier: standard*

## Intent

The unified backlog + tech-debt store (`docs/backlog/`, per-item Markdown files) has landed:
the store tree and its `README.md` exist, `references/tech-debt.md` is fully rewritten for the
per-item model, and every producing/reading skill (`dev:init`, `dev:build`, `dev:validate`,
`dev:reflect`, `dev:spec`, `dev:done`, `dev:debt`) already targets `docs/backlog/` — verified:
`grep -rn 'docs/dev/tech-debt' plugins/dev/skills/` returns zero hits (the `references/tech-debt.md`
contract shares the basename but is a different file). But the **actual deferred items still live
only in the old aggregate** `docs/dev/tech-debt.md`. The new store is empty; the data has not moved.

This cycle executes **Decision 8(a) + 8(b)** of the backlog-debt-model ADR: carry every existing
`docs/dev/tech-debt.md` entry into per-item `docs/backlog/` files, then delete the aggregate. It is
the "Migration execution" follow-on (cycle 2) narrowed to the tech-debt aggregate only — the
`product-plan.md` half of Decision 8 is deliberately deferred (see Out of Scope).

Now, because the aggregate is orphaned: nothing writes to it anymore, so every day it persists it
is a stale second home for data that the tooling can no longer see. `/dev:debt` reads the empty
`docs/backlog/`, not `tech-debt.md`, so today the 4 open debt items are effectively invisible to
the workflow that is supposed to surface them.

## Scope

- Migrate all **4 Open** entries from `docs/dev/tech-debt.md` into active items at
  `docs/backlog/debt-<slug>.md`, each `status: open`.
- Migrate all **7 Closed** entries into `docs/backlog/closed/debt-<slug>.md`, each `status: closed`.
- Each migrated file uses the contract's P1 YAML front-matter followed by the body prose,
  transferred **verbatim** from the source entry.
- Delete (`git rm`) `docs/dev/tech-debt.md` once every entry is migrated — the aggregate is retired.
- Verify counts and faithfulness before retiring: 4 active + 7 closed files exist and round-trip
  the source data.

## Out of Scope

- **`product-plan.md` migration and retirement (Decision 8(c) + its retirement).** The two
  unfinished items (`debt-backfill`, `debt-linear-promotion`) and deleting the file are deferred to
  follow-on cycle 4. Rationale: unlike `tech-debt.md`, `product-plan.md` is **still actively used** —
  `dev:spec` writes to it and `dev:done` checks items off it — so retiring it now would break those
  paths until the promotion/deletion behavior (follow-on 4) corrects them. `tech-debt.md` has no such
  entanglement.
- **Any skill edits.** The producing/reading stages already target `docs/backlog/` (follow-on 1).
  This cycle touches data files only, never a `SKILL.md` or the contract.
- **Cross-repo routing, the `/dev:debt add` capture verb, promotion/deletion behavior** — follow-on
  cycles 3 and 4; untouched here.
- **Re-judging any item's `scope`.** Per Decision 8(a), all migrated items get `scope: repo` even
  though several concern the plugin's own skills. Migration does not silently reclassify; `scope` is
  a hand-editable line to correct later.
- **Recurrence-merge across items.** The target store is empty, so no two migrated items can merge;
  each source entry becomes exactly one file. Slugs are distinct by construction (see Edge Cases).

## Success Criteria

1. `docs/backlog/` contains exactly **4** active `debt-*.md` files, one per Open source entry.
2. `docs/backlog/closed/` contains exactly **7** `debt-*.md` files, one per Closed source entry.
3. Every file's front-matter conforms to contract **P1**: required `type: debt`, `scope: repo`,
   `status`, `first_recorded`, `cycles`, `recurrence`, `files`; `closed`/`closed_by` present on
   closed items only. The invariant `recurrence == len(cycles)` holds on every file **except the
   migrated `gate-path-state-writes` item, which faithfully preserves the source's pre-existing
   `recurrence: 2` / single-cycle discrepancy** (Edge Cases; SC #4 — verbatim history is preserved
   over invariant repair).
4. Every source entry's meta line and body prose are reproduced faithfully — no dropped field, no
   reworded body, dates preserved from the source (not re-stamped from the clock; these are
   historical records, not new writes).
5. `docs/dev/tech-debt.md` no longer exists.
6. `/dev:debt` (reading `docs/backlog/`) now lists the 4 open items ranked by `recurrence` — i.e.
   the previously-invisible items are visible to the workflow again.
7. Silent-degrade still holds: with items now present, readers show them; the empty-store behavior
   is unchanged for `closed/`-only queries.

## Happy Path

1. Read `docs/dev/tech-debt.md` (source of truth for the entries).
2. For each of the 4 `## Open` entries: write `docs/backlog/debt-<slug>.md` — P1 front-matter
   derived from the meta line (`First recorded` → `first_recorded`, `Cycles` → `cycles`,
   `Recurrence` → `recurrence`, `**Files:**` → `files`), `type: debt`, `scope: repo`,
   `status: open`; body prose (`**What's wrong:**` / `**Why deferred:**` / `**Done looks like:**`)
   copied verbatim.
3. For each of the 7 `## Closed` entries: write `docs/backlog/closed/debt-<slug>.md` the same way,
   plus `status: closed`, `closed:` and `closed_by:` from the Closed meta line
   (`*Closed YYYY-MM-DD by cycle <name> · …*`). The Closed meta line carries **no `Cycles:` list**,
   so `cycles:` takes the single closing cycle (`by cycle <name>` → `cycles: [<name>]` → same as
   `closed_by`); `recurrence:` still comes from the meta line verbatim and may exceed `len(cycles)`
   for the one pre-existing discrepancy (SC #3 exception).
4. Verify: `ls docs/backlog/debt-*.md` = 4, `ls docs/backlog/closed/debt-*.md` = 7; spot-check
   front-matter round-trips each source entry.
5. `git rm docs/dev/tech-debt.md`.
6. Commit; `/dev:debt` now surfaces the migrated open items.

## Edge Cases

- **The 4th Open entry the ADR's table omits.** Decision 8(a)'s table lists only 3 Open entries; the
  live file has a 4th — *"Architecture-cycle design doesn't pressure-test cross-boundary delivery
  mechanisms"* (`first_recorded: 2026-07-28`, `cycles: [backlog-debt-model]`, files `build`/`plan`) —
  deferred by this ADR's own retrospective *after* Decision 8 was captured. It migrates like any
  other Open entry; it just needs a slug the ADR never assigned (proposed slug
  `arch-cross-boundary-transport`, i.e. filename `debt-arch-cross-boundary-transport.md`).
- **Slug collisions.** All 11 entries have distinct titles → distinct slugs, so no collision arises.
  Were one to, the contract's P2 rule applies: append the first cycle name
  (`debt-<slug>-<first-cycle>.md`), checking both active and `closed/` before deeming a slug free.
- **`recurrence` values.** All entries are `recurrence: 1` except the closed *"Sweep for gate-path
  state writes…"* which is `recurrence: 2` with `cycles: [state-write-mode-audit]` — a
  pre-existing `recurrence != len(cycles)` discrepancy in the *source*. Per P1, `cycles` is
  authoritative; migration copies the source values verbatim (recording history faithfully) and does
  not "fix" the count, since re-deriving it would rewrite the historical record. (Flag for the gate:
  confirm we transcribe `recurrence: 2` as-is rather than normalizing to 1.)
- **Multi-line `**Files:**` and long bodies.** Some entries (e.g. the gate-path sweep) have a table
  and 9 file paths; the body transfers verbatim including any embedded Markdown, and `files:` becomes
  a YAML list of all listed paths.

## Audience
The solo maintainer of the `/dev` plugin (this repo). No external consumers.

## Technical Constraints
- Plain Markdown + YAML front-matter, hand-editable, conforming to `references/tech-debt.md` **P1**.
- All writes are worktree-relative (`$WORKDIR/docs/backlog/…`), like every `/dev` artifact.
- Dates are **preserved from the source entries**, not read from the clock — the clock rule (P1)
  governs *new* stamps; a migration reproduces historical `first_recorded`/`closed` values.
- No skill or contract file is edited.

## Dependencies
- Follow-on cycle 1 (store implementation + producing-stage edits + contract rewrite) — **landed and
  verified** (store tree + README present; contract rewritten; zero skill references to
  `tech-debt.md`). This migration is unblocked.

## UI Needed
No. This is a data migration — no interface. (Shape stage is skipped.)

---

### Migration Map (reference — the concrete target for Plan/Build)

**Open → `docs/backlog/debt-<slug>.md` (`status: open`, `scope: repo`, `type: debt`):**

| Source Open entry | slug | first_recorded | cycles | rec | files |
|---|---|---|---|---|---|
| Autopilot doesn't cross-note the spec grounding gate | `autopilot-grounding-gate` | 2026-07-21 | spec-grounding-and-clock | 1 | autopilot |
| A nested product plan cannot outlive its parent | `nested-product-plan-lifetime` | 2026-07-22 | tech-debt-tracking | 1 | spec, done |
| dev:reflect dogfood shortcut can open a PR against a fork's upstream | `reflect-dogfood-pr-base` | 2026-07-28 | reflect-repo-discovery | 1 | reflect |
| Architecture-cycle design doesn't pressure-test cross-boundary delivery mechanisms | `arch-cross-boundary-transport` | 2026-07-28 | backlog-debt-model | 1 | build, plan |

**Closed → `docs/backlog/closed/debt-<slug>.md` (`status: closed`, + `closed`/`closed_by`):**

| Source Closed entry | slug | first_recorded | closed | closed_by | rec |
|---|---|---|---|---|---|
| Hardcoded repo path in dev:reflect | `reflect-hardcoded-path` | 2026-07-22 | 2026-07-28 | reflect-repo-discovery | 1 |
| dev:spec's product-plan procedure pushes straight to origin/main | `spec-product-plan-push-main` | 2026-07-22 | 2026-07-23 | init-rerun-hardening | 1 |
| The feature slug reaches git commit -m with no character allowlist | `feature-slug-allowlist` | 2026-07-22 | 2026-07-24 | done-doc-reconciliation | 1 |
| Sweep for gate-path state writes that are dead in autopilot | `gate-path-state-writes` | 2026-07-21 | 2026-07-25 | state-write-mode-audit | 2 |
| Validate's fix loop never verifies the fixes it writes | `validate-fix-loop-verification` | 2026-07-22 | 2026-07-25 | harden-validate | 1 |
| validate's config-contract gate says "every reader" but the convention is "every reader of that key" | `validate-config-contract-wording` | 2026-07-23 | 2026-07-25 | harden-validate | 1 |
| validate inherits a stale loops_max that doesn't match the tier | `validate-stale-loops-max` | 2026-07-23 | 2026-07-25 | harden-validate | 1 |

For each closed item `cycles: [<closed_by>]` (the closing cycle is the only cycle name a closed meta
line carries). Full `files:` lists and body prose come verbatim from the source entries; the slug
column above is proposed and confirmable at Build.

---
*Auto-filled dimensions: none*
*Grounding inventory: `ls docs/backlog/` → store tree + README.md only (empty corpus); `cat docs/backlog/README.md` → per-item contract stub; `sed -n '1,150p' plugins/dev/references/tech-debt.md` → contract fully rewritten for per-item store (P1 front-matter schema, P2 naming, buffer-survives); `grep -rn 'tech-debt\.md' plugins/dev/skills/` → **zero hits** (no skill writes the aggregate → safe to retire); `cat docs/dev/tech-debt.md` → **4 Open + 7 Closed** entries (ADR Decision 8 table listed 3 Open; live file has a 4th, added post-ADR); `cat docs/dev/product-plan.md` → still referenced by dev:spec/dev:done (→ retirement deferred, Out of Scope).*
