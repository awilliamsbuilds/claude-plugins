# Tech Debt Tracking
*Branch: feature/tech-debt-tracking · Confidence: 92% — Ready · 2026-07-22*
*Cycle type: feature · Tier: deep*

## Intent

The `/dev` workflow discovers real technical debt on nearly every cycle and then destroys
most of it at Done.

Three stages produce deferred items today, and the two richest are written into files that
`dev:done` Step 7 deletes:

| Producer | Writes to | Survives Done? |
|---|---|---|
| `dev:validate` Step 5 | `validation.md` → "P3 Open" / "Nits Surfaced" | **No** — cycle dir is `rm -rf`'d. Partially rescued by the decision log's "[List any P3/Nits accepted as-is]" line |
| `dev:build` Step 3 | `plan.md` → `## Deferred Improvements` | **No** — plan.md is deleted and nothing in Done reads it first. Lost outright |
| `dev:reflect` Step 6 | "record the suggestion as deferred in the decision log" | Survives, but the Retrospective template has no Deferred field — the destination is unspecified |

Nothing aggregates any of it. No `dev:*` skill has ever read across cycles: a sweep for
reads of `docs/decisions/*` returns only `dev:reflect` opening its own single cycle's log.
There is no view of debt in any repo, and `dev:init` creates `docs/dev/` and
`docs/decisions/` but no place for debt to land.

The goal is one durable, per-repo home for **discovered** debt, with a filter that keeps it
signal rather than a P3 landfill — working in any repo where `/dev` is initialized, not just
this one.

## Scope

1. **`docs/dev/tech-debt.md`** — a standing, repo-level file created by `dev:init`. Lives
   beside `product-plan.md` at `docs/dev/`, one level above the per-cycle directory that Done
   deletes, so it survives cycles by construction.

2. **A carrying-cost write rule** applied by `dev:validate`, `dev:build`, and `dev:reflect`
   when they defer something. The test is carrying cost, not severity:

   > Will this cost us again — does it make future work harder, is it known-wrong behavior
   > that will bite, or is it a pattern rather than an instance?

   Yes → record. A one-off local cleanup, a cosmetic issue, or anything fixed-once-and-
   forgotten → drop it; it already died in Validate's fix loop.

   Severity is explicitly the wrong axis. A Nit exposing a systemic convention gap is debt; a
   P3 that is a local one-liner is not.

3. **Conservative recurrence-merge.** On write, a new item is matched against existing
   entries. A clear match of the same underlying problem increments a recurrence count and
   appends the cycle name. When uncertain, create a new entry carrying a
   `possibly related to:` cross-reference — never merge on topic similarity alone. Duplicates
   are visible and cheap to merge by hand; a wrong merge silently destroys an entry.

4. **Flush at Done.** Items are buffered in the cycle directory during the cycle and written
   to `docs/dev/tech-debt.md` by `dev:done` **before** Step 7's `rm -rf`. Done also closes
   any entry this cycle paid, naming the paying cycle.

5. **Two ways to reach it:**
   - **Proactively at Spec.** `dev:spec` Step 7 already sweeps the codebase to build its
     grounding inventory. Where open debt intersects that inventory, surface it — the one
     moment the debt is actionable, because the cycle is about to be in those files anyway.
   - **On demand.** A new `dev:debt` skill: list open entries ranked by recurrence, show
     closed entries, close an entry. All read and lifecycle logic lives here; the producing
     stages only ever append.

6. **Migrate this repo's holding pen.** Convert the two hand-written entries in
   `docs/dev/tech-debt.md` into the new format and delete the file's holding-pen preamble. It
   self-describes as temporary and instructs migration when a tracker ships.

7. **Record, as the first auto-captured entries**, three defects found by this cycle's own
   grounding sweep (recorded, not fixed):
   - `plugins/dev/skills/reflect/SKILL.md:166` hardcodes `~/Development/claude-plugins` and
     the `local-plugins` marketplace name — the only repo-specific string in the plugin, and a
     direct violation of the portability constraint this cycle is built around.
   - `dev:spec` Step 4's product-plan procedure mandates a direct push to `origin/main`,
     which conflicts with a "never commit directly to `main`" convention.
   - A **nested** product plan lives at `docs/dev/<parent>/product-plan.md`, inside the
     parent's cycle directory — so `dev:done` Step 7 deletes it when the parent completes. A
     nested plan cannot outlive its parent. This is the same disease this cycle treats.

## Out of Scope

- **Backfill from decision-log history** — mining `docs/decisions/*.md` on init to seed the
  tracker. Measured yield is ~3 deferred items across 10 cycles, 2 of them cosmetic, against
  ten unstructured log formats to parse. Deferred to its own cycle (`debt-backfill` in
  `docs/dev/product-plan.md`), where it is also strictly easier: once real entries exist,
  the target shape is known.
- **Linear promotion** — `/dev:debt promote <id>` creating a Linear issue. An independent
  second deliverable; deferred to `debt-linear-promotion` in the product plan.
- **Fixing the three defects in Scope item 7.** They are recorded as tracker entries, not
  repaired here. Fixing them is a later cycle's work, ideally one already in those files —
  which is the behavior this feature exists to enable.
- **Archiving completed product-plan milestones**, and the unbounded accumulation that
  follows from `dev:spec`'s append-only rule. Adjacent, separate.
- **Changing Validate's fix loop.** It must keep fixing P3s and Nits inline. The tracker
  receives only what genuinely survives that loop.

## Success Criteria

1. A deferred item recorded during a cycle is present in `docs/dev/tech-debt.md` after that
   cycle's `dev:done` completes, including Step 7's `rm -rf` of the cycle directory. This is
   the behavior that fails today.
2. Zero repo-specific strings in the tracker machinery — no paths, org names, or marketplace
   names. Verified by sweeping the diff for presence, not by assuming absence.
3. The write rule produces identical behavior in standard and autopilot mode. No tracker
   state write may live on a gate path. (See Edge Cases — this is a defect shape with three
   prior instances in this plugin.)
4. **Regression test against real history:** of the three items actually deferred across this
   repo's ten completed cycles, the two cosmetic ones — the "locality only" Scoring-Template
   nit and the `TMP`-path naming nit — must **not** qualify under the carrying-cost test. The
   nested-product-plan-visibility P3 must qualify.
5. `dev:debt` lists open entries ranked by recurrence, shows closed entries, and closes an
   entry by marking it paid with the paying cycle's name.
6. In a repo with no `docs/dev/tech-debt.md`, every touchpoint degrades silently — Spec
   surfacing prints nothing at all, rather than an empty list or an error.
7. `dev:init` in a fresh repo produces a tracker file that is ready to receive its first
   entry.
8. The two migrated entries survive with their what / why-deferred / done-looks-like content
   intact.

## Happy Path

1. `dev:validate` finishes a cycle with an unresolved P3 that its fix loop consciously chose
   not to fix.
2. It applies the carrying-cost test. The item will make future work harder, so it is
   buffered into the cycle directory with what is wrong, why it was deferred rather than
   fixed, and what "done" looks like.
3. `dev:done` flushes the buffer to `docs/dev/tech-debt.md` before deleting the cycle
   directory. A clear match against an existing entry increments its recurrence and appends
   this cycle's name; otherwise a new entry is created.
4. Cycles later, a different feature's `dev:spec` Step 7 grounding sweep touches those files.
   Spec surfaces: *"2 open debt items touch this cycle"*, ranked by recurrence, and asks
   whether to fold either into scope.
5. The user folds one in. That cycle builds and merges it, and its `dev:done` moves the entry
   to Closed, naming the cycle that paid it.

## Edge Cases

- **Concurrent cycles flushing at Done.** `/dev` runs cycles in separate worktrees, so two
  can complete near-simultaneously and both append to the same file. Writes are append-only
  at the end of the Open section, and Done's existing `push_integration` helper already
  fetch/rebase/retries on a non-fast-forward push. No new machinery.
- **Mode asymmetry.** This plugin has three recorded instances of the same defect: a
  `state.json` write specified only on a standard-mode gate path, silently never executed in
  autopilot, with a downstream reader that has no mode qualification. The carrying-cost test
  and the merge decision must therefore be self-applied by the writing stage, never gated on
  user confirmation, and no counter may be written only on a gate path.
- **Repos initialized before this ships.** No `tech-debt.md` exists and `dev:init` will not
  re-run. Spec surfacing must no-op silently; the first write creates the file.
- **Empty tracker.** Prints nothing during Spec grounding. `dev:debt` invoked directly on an
  empty or absent tracker says so plainly rather than erroring.
- **Spec-time matching is approximate.** At Spec there is no plan and no definitive file
  list, only the grounding inventory. Matching is best-effort against that inventory; a
  missed match costs nothing, and the on-demand `dev:debt` path remains available.
- **An entry whose "done looks like" is already satisfied.** A later cycle may fix a debt
  item incidentally without folding it in. Closing is not automatic in that case; the entry
  remains open until closed via `dev:debt`. Acceptable — a stale-open entry is recoverable,
  a wrongly-closed one is not.

## Audience

Solo developer using `/dev` across multiple repos. The tracker is read by a human deciding
what to fold into an upcoming cycle, and written by `dev:*` skills without supervision.

## Technical Constraints

- All changes are prose in `SKILL.md` files. Skills are auto-discovered — `plugins/dev/.claude-plugin/plugin.json` carries no skill list — so adding `dev:debt` needs no manifest edit. But `dev:start` Step 4 hardcodes both an FYI skill list and a fallback description list; both need the new entry.
- The tracker file must be plain Markdown, readable and hand-editable without tooling.
- No new config keys unless required. If `docs/dev/config.json` gains a key, every skill that reads config.json must have it added to that skill's Step 1 read list — `dev:validate`'s config-contract check enforces this.
- Changes take effect only after merge to `main` plus `/plugin update`.

## Dependencies

None blocking. `debt-backfill` and `debt-linear-promotion` in `docs/dev/product-plan.md` both
depend on this cycle.

## UI Needed

No. All surfaces are terminal output from skills.

---
*Auto-filled dimensions: none*
*Grounding inventory: read in full — `reflect/SKILL.md` (Step 6 line 156 defers to decision log, no template slot in Step 3's format), `validate/SKILL.md` (Step 4 fixes P3/attempts Nits inline; Step 5 writes Issues Remaining to validation.md), `done/SKILL.md` (Step 5 decision-log template's P3/Nit line; Step 7 `rm -rf "$WORKDIR/docs/dev/<feature>/"`; `push_integration` fetch/rebase/retry), `init/SKILL.md` (creates `docs/dev/` + `docs/decisions/`, no debt file), `build/SKILL.md` (Step 3 `## Deferred Improvements` → plan.md), `start/SKILL.md` (Step 4 hardcoded FYI + fallback lists), `spec/SKILL.md` (Steps 2/4 product-plan push to origin/main; nested path under `docs/dev/<parent>/`). Sweeps run this stage: `grep -rniE "tech[- ]debt|deferred|backlog"` across all 13 dev SKILL.md → only 4 hits, all listed in Intent; `grep -rn "docs/decisions"` → no cross-cycle reader exists; `grep -rniE "claude-plugins|awilliamsbuilds|adam|/Users/|local-plugins"` across the plugin → single hit, `reflect/SKILL.md:166` (negative-space check for the portability criterion); `cat plugins/dev/.claude-plugin/plugin.json` → no skills array, auto-discovery confirmed. Volume measured, not assumed: counted P1/P2 vs P3/Nit mentions across all 10 `docs/decisions/*.md` — ~22 P3/Nit mentions, only 3 left open (~0.3 deferred items per cycle), matching the 2-entry hand-written file.*
