# init-rerun-hardening
*Branch: feature/init-rerun-hardening · Confidence: 90% — Ready · 2026-07-23*
*Cycle type: feature · Tier: deep*

## Intent

`dev:init`'s config contract is incoherent in both directions, and its rerun path is unsafe:

- Skills **read** config keys that init **never writes** — `dev:shape` (`shape/SKILL.md:64`, `:200`) and `dev:reflect` (`:73`) read a *component policy* that init's config template (`init/SKILL.md:190-201`) doesn't emit. init asks for it (Question 2) but discards the answer.
- init **asks** setup questions whose answers reach **no consumer**: Question 1 (design personality) has zero downstream readers; Question 3 (audience) is read by `spec/SKILL.md:25` from **CLAUDE.md**, not config, and init writes no audience section to CLAUDE.md. Both answers are discarded.
- init **writes** a key **nobody reads**: `worktree_root` — every skill hardcodes `.dev-worktrees`.
- The rerun "update" path (`init/SKILL.md:53`) **rewrites config from a fixed template**, clobbering any tuned `spec_max_questions`/`spec_min_confidence`, and there is **no schema version or migration**, so a drifted config (this repo's own `config.json` predates the `changelog` keys) is never repaired. `tech-debt.md` backfill is hand-special-cased precisely because no general migration exists.
- init **commits directly to the current branch** (usually `main`) at `init/SKILL.md:207-210`, an unreviewed write to a possibly-protected default branch. The same shape appears in `dev:spec`'s product-plan procedure (a tracked debt entry).

Fix the contract so it is coherent by construction, make rerun a safe migration, and stop writing to `main` outside the branch/PR flow.

## Scope

1. **Config contract coherence (findings A/B/C/D).**
   - Persist the surviving setup answer — **component policy** — into `config.json` under a stable key (e.g. `component_policy`), so `dev:shape` and `dev:reflect` read a key init actually writes.
   - **Both** halves of the missing-key contract: (a) every `dev:*` skill that reads a config key documents a fallback default for that key's absence, and (b) init's rerun migration backfills missing keys with those same defaults. A config in any state (fresh, drifted, hand-edited) yields correct behavior whether or not migration has run.

2. **Prune orphans (finding B).**
   - Remove init's Question 1 (design personality) and Question 3 (audience) — asked but consumed by nothing.
   - Stop writing `worktree_root` (dead key).
   - init retains exactly **one** setup question: component policy.
   - Update every "3 setup questions" reference to match the new count: init frontmatter (`:3`), the "Three Setup Questions" section (`:89`), Scenario C's "infer answers to the 3 setup questions" (`:34`), the exit display, and any other occurrence a sweep finds.

3. **Schema versioning + safe migration (finding E).**
   - Stamp a `schema_version` on `config.json`.
   - init's rerun "update" path becomes a **migration**: backfill missing keys with defaults, **preserve** existing (possibly tuned) values, and record the version. It must not clobber tuned values, and must repair a drifted config.
   - This generalizes and replaces the hand-special-cased `tech-debt.md` backfill (the "keep" path) as the mechanism by which older repos gain new artifacts.

4. **No writes to `main` outside branch/PR (finding F + folded debt entry).**
   - init **stages** the scaffolding it creates and **does not auto-commit** — it reports that the staged files need committing (and pushing, for later cycle worktrees cut from `origin/main` to see them). This matches the existing "keep" path's untracked-file pattern.
   - **`dev:spec` product-plan lifecycle is restructured** (folds in tracked entry *"dev:spec's product-plan procedure pushes straight to origin/main"*): the product plan is written **into the cycle worktree** and reaches `main` through the **cycle's own PR**, exactly like `tech-debt.md`. The ephemeral-detached-worktree push procedure (Step 2 item 6) is removed; Step 4's decomposition write becomes a plain `$WORKDIR` file write; Step 2 reorders so the plan is written *after* the cycle worktree exists (Step 6). `dev:done`'s check-off and `dev/SKILL.md` Step 6's continuation read are verified to still work under the PR-propagation model.

## Out of Scope

- The other six open tech-debt entries (gate-path state writes, feature-slug allowlist, nested product plan, hardcoded reflect path, validate fix-loop verification, autopilot cross-note). Only *"dev:spec's product-plan procedure pushes straight to origin/main"* is folded in.
- The planned `debt-backfill` and `debt-linear-promotion` cycles.
- Redesigning init's stack detection, changelog detection, or the wording of the surviving question beyond what pruning requires.
- Any change to the /dev workflow stages themselves.
- Archiving an abandoned product plan to `docs/decisions/` (a possible mitigation for the fresh-decomposition abandonment window — noted, not built).
- The nested-product-plan-lifetime entry, though it is adjacent to the restructured procedures and should be *looked at* (not fixed) during Build.

## Success Criteria

- **Contract closes both ways** (grep-verifiable): every config key any `dev:*` skill reads is either written by init **or** has a documented consumer-side default; and no key init writes is unread. `component_policy` is written by init and read by `dev:shape`/`dev:reflect`.
- **Tuned values survive rerun:** re-running init on a config with a customized `spec_max_questions` leaves that value unchanged.
- **Drifted config is repaired:** re-running init on this repo's current `config.json` (missing `changelog`, `component_policy`, `schema_version`) backfills those keys with defaults **without altering** existing values, and stamps `schema_version`.
- **One question, no orphans:** init asks exactly one setup question; grep finds no surviving "3 setup questions" phrasing and no write of `worktree_root`.
- **No unreviewed `main` writes:** init makes no commit (it stages and reports); `dev:spec` contains no direct push to `origin/$INTEGRATION` for the product plan — the plan lands via the cycle PR.
- **Product-plan propagation intact:** a decomposed product plan created in cycle-1's worktree is checked off by cycle-1's `done`, merges via cycle-1's PR, and is visible to cycle-2 (cut from `origin/main`) — verified by tracing the procedures, since there is no test harness for prose.

## Happy Path

1. Developer runs `/dev` (or `/dev:init`) in a repo already initialized on an older `/dev` version.
2. init detects `config.json` exists, reads its `schema_version` (absent → treat as legacy).
3. init runs migration: backfills `component_policy`, `changelog`/`changelog_versioned`, `schema_version` with defaults; preserves the existing tuned `spec_max_questions`; drops nothing the user set.
4. init **stages** the updated `config.json` (and any newly created `tech-debt.md`) and reports: "migrated config to schema vN; staged — review and commit when ready."
5. On the next feature cycle, `dev:shape` reads `component_policy` from config and finds it present; if some other repo's config lacks it, shape falls back to the documented default rather than reading undefined.

## Edge Cases

- **Missing key at read time:** consumer uses its documented default (belt); migration backfills it (suspenders). Neither depends on the other having run.
- **Unknown / future `schema_version`:** migration must not downgrade or corrupt a config whose version is newer than the running init knows — leave it untouched and report, rather than clobbering.
- **Tuned-value preservation:** migration merges keys, never overwrites present values with template defaults.
- **Staged-not-pushed visibility:** init's staged scaffolding isn't on `origin/main`, so a cycle worktree cut from `origin/main` won't see `config.json`/`tech-debt.md` until the user commits **and pushes**. init's report must say so. (This is already true of today's commit-to-local-main.)
- **Fresh-decomposition abandonment:** a product plan created in cycle-1's worktree is lost if cycle-1 is abandoned before its PR merges. Accepted as rare; mitigation (archive to `docs/decisions/`) is out of scope.
- **Concurrent fan-out:** a parallel cycle-2 started before cycle-1 (the plan creator) merges won't see the plan. Known limitation; the plan-creating cycle should merge first.
- **`worktree_root` in an existing config:** migration leaves a pre-existing `worktree_root` harmlessly in place (or strips it) — it must not error on encountering a key the new template no longer emits.

## Audience

Developers using and maintaining the `/dev` plugin — a portable workflow installed across arbitrary repos, so no repo-, person-, or environment-specific assumptions may leak into the fix. (From CLAUDE.md: personal Claude Code plugin repo, agent-facing.)

## Technical Constraints

- **Portability:** the plugin runs in any repo; migration and defaults must hold for a repo with branch protection on `main` and for one without.
- **Backward compatibility:** existing configs (including this repo's drifted one) must migrate cleanly; no flag-day break.
- **Config-contract review gate:** `validate/SKILL.md:71` already requires that a new config key be added to every reader's Step 1 read list — this cycle adds `component_policy` and `schema_version`, so that check applies to this cycle's own diff.
- **Prose, not code:** these are Markdown skill files with embedded shell; "verify the fix" means tracing procedures and checking that embedded snippets exit 0 on their healthy path, not running a test suite.

## Dependencies

- None external. Self-contained edits to `dev:*` skill files and the config template.
- Relies on the existing `tech-debt.md` lifecycle as the precedent pattern the product plan is being aligned to.

## UI Needed

No. Shape stage is skipped; Plan follows Spec directly.

---
*Auto-filled dimensions: none*
*Grounding inventory: `grep -rn "config\.json"` across `plugins/dev/skills/*.md` → readers are spec (autopilot keys), autopilot (spec_max_questions), shape (component policy), pr (changelog/changelog_versioned), plus existence-only checks in dev/start/autopilot; init template (`:190-201`) writes autopilot.{spec_max_questions,spec_min_confidence}, worktree_root, changelog, changelog_versioned. `grep -rn "design personality|visual style|personality"` → only init:93-94, zero consumers (Q1 orphan confirmed). `grep -rn "worktree_root"` → only init:197, zero readers (dead key confirmed). `grep audience` → spec:25 reads from CLAUDE.md, init CLAUDE.md template (`:154-186`) writes no audience section (Q3 orphan confirmed). Live `docs/dev/config.json` inspected: has autopilot.{...} + worktree_root, missing changelog/changelog_versioned/component_policy/schema_version (drift confirmed). init commit at `:207-210` (direct-to-branch confirmed). `dev:spec` Step 2 item 6 / Step 4 push-to-origin/$INTEGRATION procedure read (exemption target confirmed); `tech-debt.md` lands via cycle PR (precedent confirmed). Open tech-debt.md cross-checked: file-level intersections with entries for state-writes/slug-allowlist/nested-plan on shape/spec/validate/done exist but in unrelated regions — none folded except the origin/main product-plan entry, which is folded (debt-pending.md `## To Close`).*
