# dev:migrate-tracker — Legacy Tracker Migration
*Branch: feature/legacy-tracker-migration · Confidence: 92% — Ready · 2026-08-01*
*Cycle type: feature · Tier: standard*

## Intent

Three repos still carry the pre-`docs/backlog/` tech-debt tracker — the single aggregate
`docs/dev/tech-debt.md` with `## Open` / `## Closed` sections — because the migration that ran here
(`tech-debt-migration`, 2026-07-28) was a one-repo, hand-mapped execution of ADR
`2026-07-28-backlog-debt-model.md` Decision 8. It migrated *this* repo's ten entries and retired
*this* repo's tracker. Nothing generalized it.

Verified: no `/dev` skill mentions the legacy tracker at all. The only thing in the plugin called a
"migration" is `dev:init` Scenario D's **config-schema** merge, which is a different mechanism on a
different file. So a repo on the old model has no path forward except hand-transcription — and the
old format's parsing rules were *retired* from the contract when it moved to front-matter
(`references/tech-debt.md:417`), so even a careful hand-migration is now working without a spec of
its own source format.

This ships that path as a skill: `/dev:migrate-tracker`, run once per repo.

The routing half is what makes it more than a file split. In a foreign repo, an item about the
`/dev` plugin's own skills is exactly the scatter ADR Decision 5 exists to end — it belongs in the
plugin repo, and §P9 already knows how to send it there. Migration is the moment that debt is finally
in a position to go home.

## Scope

One new skill: `plugins/dev/skills/migrate-tracker/SKILL.md`, invoked `/dev:migrate-tracker`.

- **Guard first — no-op when there is nothing to migrate.** Absent `docs/dev/tech-debt.md` ⇒ the skill
  says nothing and exits (P7 silent-degrade). This is what makes the skill safe to keep after the three
  repos are done, and makes re-running it in a migrated repo a no-op rather than an error.
- **Delegate store setup to `dev:init`.** `dev:init` Scenario D already creates `docs/backlog/` +
  `closed/` idempotently on *both* its branches, and self-describes as "the only automatic path by which
  a repo initialized before the store shipped ever gets `docs/backlog/`" (`init/SKILL.md:49-52`). This
  skill calls it and holds no second copy of the tree-creation logic.
- **Carry the old format's parsing rules.** This skill is the last consumer of that knowledge, so it
  states the source format itself rather than citing a contract that no longer describes it. The rules
  are recovered, not invented — see the grounding inventory for the exact SHAs.
- **Parse both sections.** Each `### <title>` under `## Open` → one `docs/backlog/debt-<slug>.md`,
  `status: open`. Each under `## Closed` → `docs/backlog/closed/debt-<slug>.md`, `status: closed`, with
  `closed:` / `closed_by:` lifted from the Closed meta line.
- **`type: debt` for every item, no classification pass.** The legacy tracker held only debt by
  construction — it *was* a debt tracker. Backlog intentions in the old model were misfiled into
  `product-plan.md`, and none of the three target repos has one.
- **Classify `scope` per open item, confirm once, then route.** The skill proposes `repo | plugin` for
  each open item with its reason, prints them as one table, and takes a single confirmation (with the
  option to flip items by number) before anything leaves the repo. Confirmed `plugin`-scope items are
  delivered per §P9; `repo`-scope items are written locally.
- **Merge, don't assume an empty store.** Each migrated item runs the existing **P6 recurrence-merge**
  against the active P5 corpus, exactly as `dev:done`'s flush does.
- **Verify, then retire.** Count entries parsed vs. items written vs. items routed; only on a clean
  reconciliation delete `docs/dev/tech-debt.md`.
- **Never commit, never stage.** Same rule and same reason as `dev:init` and `dev:debt`: this runs
  outside a cycle, usually on `main`.

## Out of Scope

- **Seeding the store from decision logs** — that is `backlog-debt-backfill` (`docs/backlog/`, open),
  a *different* feature: different source (`docs/decisions/*.md`), different trigger (`dev:init`),
  different yield profile. Named here because "backfill the backlog" and "migrate the tracker" are
  easy to read as one thing. This cycle does not touch it and does not close it.
- **Product-plan migration** — the old model misfiled backlog intentions into `docs/dev/product-plan.md`.
  Confirmed with the user: none of the three target repos has one. If a fourth repo ever does, that is
  its own cycle.
- **`type` classification** — everything migrates `type: debt` (see Scope). No heuristic, no gate.
- **Changing `dev:init`, `dev:debt`, `dev:done`, or `references/tech-debt.md`.** This skill *calls*
  `dev:init` and *cites* §P9/P6/P2/P7; it modifies none of them. They are read during Build for
  alignment and must end the cycle byte-identical.
- **Reimplementing routing.** §P9's six sub-procedures (`target-resolution`, `dogfood`, `intake-dedup`,
  `delivery`, `degrade`, `retry-seam`) are cited, never copied — the single-source-of-truth discipline
  the contract applies to itself, and the same call `dev:debt add` Step 7 §5 already makes.
- **Migrating repos automatically / in bulk.** The skill is run by hand, once per repo. No multi-repo
  driver, no discovery of which repos need it.
- **Retiring this skill.** Whether it is deleted once the three repos are done is a later decision the
  no-op guard makes cheap. Not this cycle.

## Success Criteria

1. Run in a repo with no `docs/dev/tech-debt.md`: **no output at all**, no files created, exit clean.
2. Run in a repo with one: every `## Open` entry becomes exactly one
   `docs/backlog/debt-<slug>.md` with `type: debt`, `status: open`, and `first_recorded` / `cycles` /
   `recurrence` / `files` derived from the entry's meta line and `**Files:**` field; every `## Closed`
   entry becomes `docs/backlog/closed/debt-<slug>.md` with `status: closed` plus `closed` / `closed_by`
   from its Closed meta line.
3. Body prose (`**What's wrong:** / **Why deferred:** / **Done looks like:**`) transfers **verbatim** —
   the migration lifts text, never rewrites it.
4. The scope table is displayed and confirmed **before** any `gh issue create` fires. No item is routed
   that the user did not see classified.
5. **No closed item is ever routed**, whatever its scope.
6. An item whose slug collides with an existing file in the active corpus **or** in `closed/` is
   disambiguated per P2 (`debt-<slug>-<first-cycle>.md`) — uniqueness spans the whole tree.
7. An item that clear-matches an existing store item (P6: `files:` overlap **and** same defect) merges
   into it — `cycles:` appended, `recurrence:` bumped, body detail appended, never replaced — rather
   than creating a duplicate file.
8. `docs/dev/tech-debt.md` is deleted **only** after parsed-count == written-count + routed-count.
   On any mismatch the tracker survives and the discrepancy is reported.
9. Nothing is `git add`ed and nothing is committed; the closing report says the store is modified but
   uncommitted.
10. Re-running the skill in a repo it already migrated hits criterion 1 (the tracker is gone) and is
    therefore a silent no-op.
11. `references/tech-debt.md`, `dev:init`, `dev:debt`, and `dev:done` are unmodified by this cycle.

## Happy Path

1. User runs `/dev:migrate-tracker` in a repo still on the legacy model.
2. Skill finds `docs/dev/tech-debt.md` and reads it.
3. Skill invokes `dev:init` to ensure `docs/backlog/` + `closed/` exist.
4. Skill parses the aggregate into N open + M closed entries using the old-format rules it carries.
5. Skill proposes `scope` for each of the N open entries and prints the classification table with a
   one-line reason per item.
6. User confirms, or names numbers to flip.
7. Skill writes every item (P6-merging against the existing corpus, P2-disambiguating collisions),
   then routes the confirmed `plugin`-scope open items via §P9.
8. Skill reconciles counts, deletes `docs/dev/tech-debt.md`, and prints a report: items written by
   scope, items routed with their issue numbers, anything degraded to `routing: pending`, anything
   flagged.

## Edge Cases

- **Tracker present but empty** (headers only, no `###` entries) — nothing to migrate. Report it and
  delete the tracker; an empty aggregate carries no information the store needs.
- **Mixed state: old tracker *and* a populated `docs/backlog/`.** Expected, not exotic — `dev:done`'s
  flush creates the store the first time any cycle defers something, so any target repo that ran a cycle
  since the store shipped is already here. Handled by P6 merge (Success Criterion 7), not by refusing.
- **Slug collision** against the active corpus or `closed/` → P2 disambiguation (Success Criterion 6).
- **Entry missing `**Files:**`** — required by the old format and by the P1 schema, but a hand-edited
  tracker may lack it. Write the item with `files: []`, flag it in the report as needing a hand fix,
  and **count it as migrated**. Never drop it: an item lost in migration is unrecoverable once the
  tracker is deleted, while an item with an empty `files:` is merely invisible to `dev:spec`'s
  cross-check until someone fills it in.
- **Entry the parser cannot read at all** (drifted or hand-mangled shape) — do **not** guess and do
  **not** skip silently. Report it verbatim, leave it unmigrated, and let the count reconciliation fail
  so the tracker is **not** deleted. The user hand-fixes and re-runs.
- **`gh` unauthenticated, offline, or the target slug unresolvable** — P9.degrade: the item is written
  locally with `scope: plugin` + `routing: pending` and surfaced in the report. `/dev:debt list` and the
  next `dev:done` flush in that repo both already re-attempt delivery (P9.retry-seam), so a partial
  migration self-heals without this skill needing a retry path of its own.
- **User declines the classification table entirely** — write nothing, route nothing, leave the tracker
  in place. The migration is abandoned cleanly rather than half-applied.
- **Run inside the plugin repo itself** — P9.dogfood: a `plugin`-scope item is already home and is
  written to the local `docs/backlog/` as an ordinary file. No issue, no routing. (Moot for the three
  target repos, but the skill must not open issues against the repo it is standing in.)
- **Repo has a tracker but no `docs/dev/config.json`** — `dev:init` handles it as a fresh init
  (Scenario A/B/C rather than D); the store still gets created and migration proceeds.

## Audience

Solo maintainer of `awilliamsbuilds/claude-plugins`, running the skill by hand in three of their own
repos, all with `dev` installed from the same marketplace. The skill is written to be safe for anyone
who forked the plugin and is in the same position, which is why routing goes through §P9's explicit
target resolution rather than assuming this repo.

## Technical Constraints

- **Skill-instruction editing only** — the deliverable is one `SKILL.md`. No code.
- **`gh` for all GitHub operations**, carrying its own auth; routing works from a foreign repo with no
  local plugin checkout (ADR Decision 5).
- **Single source of truth** — §P9, P6, P2, P7 live in `references/tech-debt.md` and are cited. The
  *old* format's rules are the one thing this skill states itself, because no live document describes
  them any more.
- **Derive `PRIMARY` absolute.** `dev:debt` Step 1's `PRIMARY=$(dirname "$(git rev-parse
  --git-common-dir)")` is relative when run from the primary checkout — the open debt item
  `primary-path-relative-in-dev-headers`. This skill runs standalone from the primary checkout, which is
  precisely the failing case, so it derives `PRIMARY` absolute at its single computation site rather
  than inheriting the bug into a new file.
- **Never `cd`** — the skill locates the store from `$PRIMARY` and uses `git -C`, per the same
  convention every `/dev` skill follows.

## Dependencies

- **§P9 routing** — shipped in `debt-capture-routing` (PR #56), in live use by `/dev:debt add`.
- **`dev:init` Scenario D** — shipped in `init-rerun-hardening`; provides the store backfill this skill
  delegates to.
- **The old format's rules and a real example** — recoverable from git history (see grounding
  inventory). Build needs both; neither exists in the working tree.
- **`gh` CLI, authenticated** — present.

## UI Needed

No. A CLI skill with a text classification table; no visual surface. Shape is skipped.

## Notes carried to Plan

- **The residual risk this spec cannot close: format drift in the three target repos.** Every parsing
  rule here was recovered from *this* repo's history, and this repo's tracker was written entirely by
  `dev:done`. A hand-edited entry in another repo may not match. The design absorbs this rather than
  eliminating it — the unparseable-entry edge case fails the count reconciliation and preserves the
  tracker — but Plan should treat "parse defensively, fail loudly, never delete on doubt" as the
  ordering principle for the parse-and-verify tasks, not an afterthought. If a sample of one target
  repo's tracker becomes available before Build, it is worth reading.
- **Where the classification heuristic's judgment sits.** `files:` paths that don't resolve in the
  current repo (especially under `plugins/dev/skills/`) are the strong signal; body text naming `dev:*`
  skills is the weaker one. Plan should decide whether the skill states a rule or states a rule plus
  examples — the table's per-item "why" column is what makes a wrong guess cheap to catch, so the
  heuristic does not need to be perfect, only legible.

---
*Auto-filled dimensions: none — every dimension was answered from the user's request, the two
pre-cycle answers (no misfiled product-plan; three repos, one marketplace), the routing decision at
Step 8, the comprehension check at Step 9, or the grounding sweeps below.*

*Grounding inventory (all run this stage against the real files):
`grep -n "docs/backlog" plugins/dev/skills/init/SKILL.md` → Scenario D backfills the store on **both**
branches (`:42` keep-branch, `:77` update-branch) and states at `:49-52` that it is the only automatic
path for a pre-store repo — basis for delegating setup rather than reimplementing it;
`grep -o "P9\.[a-z-]*" plugins/dev/references/tech-debt.md | sort -u` → the six citable sub-procedures
(`degrade`, `delivery`, `dogfood`, `intake-dedup`, `retry-seam`, `target-resolution`);
`grep -rln "references/tech-debt.md" plugins/dev/skills/` → seven consumers (init, build, validate,
reflect, done, debt, spec) — the set this skill joins as an eighth;
read `plugins/dev/skills/debt/SKILL.md:198-278` → `/dev:debt add` already implements the exact routing
decision tree (dogfood→local; off-repo→`P9.target-resolution` + echo/confirm + `P9.intake-dedup` +
`P9.delivery`; failure→`P9.degrade` to `routing: pending`), and does **not** commit (`:187`, `:266`,
with the never-commit-to-`main` reason stated) — the precedent this skill mirrors for both;
read `plugins/dev/skills/debt/SKILL.md:36-57` → the standalone store-location pattern (`PRIMARY` from
`git rev-parse --git-common-dir`, no `cd`), and the one documented exception to silent-degrade (a
directly-asked question deserves an answer);
`grep -rni "tech-debt\.md\|legacy tracker\|migrat" plugins/dev/skills/` → **zero** hits describing a
legacy-tracker migration; the only "migration" in the plugin is `dev:init`'s config-schema merge
(`init/SKILL.md:53-80`) — confirming this capability does not exist in any form today;
`git show ab054df:plugins/dev/references/tech-debt.md` → the retired **§ Where a field ends** rules
(line-initial field labels as the only boundaries; mid-line bold-colon spans and blank lines are *not*
boundaries; first-sentence-is-summary with the backtick-period exception) — the source-format spec Build
must carry, confirmed **absent** from the live contract, which retains only the one-line retirement note
at `:417`;
`git show 7ebe89a^:docs/dev/tech-debt.md` → a real 10-entry example (3 Open, 7 Closed) with the Open meta
line `*First recorded: … · Cycles: … · Recurrence: N*` and the Closed meta line `*Closed YYYY-MM-DD by
cycle <name> · First recorded: … · Recurrence: N*` — Build's parser fixture;
Step 7 pass-4 cross-check → read `files:` front-matter of all 9 active `docs/backlog/` items; **zero**
intersect this cycle's surface (the new `SKILL.md` does not exist yet), so nothing was folded in. Read
`backlog-debt-backfill.md` in full to confirm it is a **distinct** feature (decision-log mining at
`dev:init`) rather than this one — recorded in Out of Scope so the two are not later conflated.*
