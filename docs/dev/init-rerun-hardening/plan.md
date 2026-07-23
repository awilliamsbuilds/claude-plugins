# init-rerun-hardening — Implementation Plan
*Branch: feature/init-rerun-hardening · 2026-07-23*

Prose/markdown cycle: every file is a `dev:*` SKILL.md whose edits are instructions + embedded
shell. "Implement" means edit the prose; "verify" means trace the procedure and confirm embedded
snippets exit 0 on their healthy path. No test harness.

## Config schema (the contract this cycle establishes)

The canonical `config.json` after this cycle:

```json
{
  "schema_version": 1,
  "autopilot": { "spec_max_questions": 10, "spec_min_confidence": 85 },
  "component_policy": "existing-only" | "can-propose",
  "changelog": "<path-or-null>",
  "changelog_versioned": true | false
}
```

- `worktree_root` is **removed** from new configs (dead key). Migration **leaves** a pre-existing
  `worktree_root` in place — it does not strip it.
- **Consumer-side defaults** (used when a key is absent at read time, independent of migration):
  - `spec_max_questions` → `10`
  - `spec_min_confidence` → `85`
  - `component_policy` → `"can-propose"` (permissive default: propose new components when justified)
  - `changelog` → absent/null ⇒ skip changelog step (already handled)
  - `changelog_versioned` → absent ⇒ `false` (already handled; make explicit)
  - `schema_version` → absent ⇒ treat config as legacy (version `0`)
- `SCHEMA_VERSION = 1` is the version this cycle's init stamps.

## Files

| File | Action | Purpose |
|------|--------|---------|
| plugins/dev/skills/init/SKILL.md | Modify | Prune to one setup question; new config template (`component_policy` + `schema_version`, drop `worktree_root`); rerun becomes a safe migration; leave scaffolding **unstaged** (no `git add`, no commit); exit display |
| plugins/dev/skills/shape/SKILL.md | Modify | Read `component_policy` key from config with documented default |
| plugins/dev/skills/reflect/SKILL.md | Modify | Source component policy from config's `component_policy` (with default) rather than an unwritten key |
| plugins/dev/skills/spec/SKILL.md | Modify | Document config-read defaults (Step 1); restructure product-plan lifecycle — remove ephemeral-worktree push, defer write into `$WORKDIR`, set `product_plan` |
| plugins/dev/skills/pr/SKILL.md | Modify | Make `changelog_versioned` absent ⇒ `false` explicit (close consumer-default half of contract) |
| plugins/dev/skills/done/SKILL.md | Modify | Note check-off reads the plan from the PR-merged integration tip (visibility timing); no logic change |
| plugins/dev/skills/dev/SKILL.md | Modify | Note product-plan continuation is visible post-merge under PR-propagation; no logic change |
| plugins/dev/skills/autopilot/SKILL.md | Verify | Confirm `spec_max_questions` default-10 note already present; no change expected |

## Tasks

### Task 1: init — prune to a single setup question
What: Remove init's orphan questions (design personality, audience); keep component policy as the sole setup question, and fix all in-file "3 setup questions" wording.
Used by: The developer running `/dev:init`; downstream skills that read the surviving answer (`component_policy`, wired in Task 2).
Depends on: nothing — first task.
Files: plugins/dev/skills/init/SKILL.md
Interfaces:
- Consumes: nothing.
- Produces: init asks exactly **one** setup question (component policy: A) existing-only / B) can-propose). Section renamed from "Three Setup Questions" to a single-question heading.

Implementation steps:
1. Frontmatter (`:3`): change "asks 3 setup questions" to "asks 1 setup question" (leave the rest of the description intact).
2. Scenario C (`:34`): "Infer answers to the 3 setup questions" → "Infer the answer to the setup question".
3. Section heading (`:89` "### Three Setup Questions") → "### Setup Question"; drop the "one at a time" plural framing to singular.
4. Delete **Question 1 — Design personality** (`:93-96`) and **Question 3 — Primary audience** (`:103-104`) entirely.
5. Keep **Question 2 — Component policy** (`:98-101`); renumber it to "Question" (or "Question 1"), and make its A/B answers map to the stored values `existing-only` / `can-propose` (the value strings Task 2 persists).
6. Scan the rest of init for any other "3 setup"/"three question" phrasing (exit display, prose) and fix. (Cross-file occurrences are Task 8.)

### Task 2: init — new config.json template (component_policy + schema_version, drop worktree_root)
What: Rewrite init's `Write config.json` template so it emits the surviving answer under `component_policy`, stamps `schema_version`, and no longer emits the dead `worktree_root` key.
Used by: `dev:shape`/`dev:reflect` (read `component_policy`), init's own migration (Task 4 reads `schema_version`).
Depends on: Task 1 (the surviving question supplies `component_policy`'s value).
Files: plugins/dev/skills/init/SKILL.md (`Write config.json`, `:188-203`)
Interfaces:
- Consumes: the component-policy answer from Task 1 (`existing-only` | `can-propose`).
- Produces: the canonical config shape shown in **Config schema** above. `SCHEMA_VERSION = 1` named as a constant in the prose. Key defaults enumerated so Task 4 (migration) and Task 5 (consumers) reference one source.

Implementation steps:
1. Replace the JSON template (`:191-201`) with the **Config schema** block above: add `"schema_version": 1` (first key), add `"component_policy"` set from the Task 1 answer, **remove** the `"worktree_root"` line. Keep `autopilot.{spec_max_questions,spec_min_confidence}`, `changelog`, `changelog_versioned`.
2. Update the surrounding prose (`:202-203`) so it explains: `component_policy` from the setup answer; `schema_version` is the literal current version (`1`); `changelog`/`changelog_versioned` from detection.
3. State `SCHEMA_VERSION = 1` explicitly in the prose as the value init writes and migration stamps — Task 4 refers to it.

### Task 3: init — leave scaffolding unstaged (no commit) + exit display
What: Replace init's `Commit` section (which runs `git add` + `git commit`) with a leave-unstaged-and-report behavior on every init path, and update the exit display to say the files need committing/pushing.
Used by: The developer, who now reviews and commits init's output themselves; matches the existing "keep" path (`:42-48`) which already forbids `git add`.
Depends on: Task 2 (the set of files init writes is now settled — no worktree_root change to the file list, but config content changed).
Files: plugins/dev/skills/init/SKILL.md (`Commit` `:205-210`; `Exit Display` `:212-227`)
Interfaces:
- Consumes: the file set init creates/modifies (dirs, `.gitkeep`s, `config.json`, `tech-debt.md`, `CLAUDE.md`, `.gitignore`).
- Produces: init makes **no `git add` and no commit** on any path. Exit line reports the files are unstaged and must be reviewed, committed, and **pushed** (so a later cycle worktree cut from `origin/main` can see `config.json`/`tech-debt.md`).

Implementation steps:
1. Delete the `### Commit` fenced block (`:207-210`) with its `git add`/`git commit`. Replace with prose: "Do **not** `git add` and do **not** commit. Leave every created/modified file unstaged in the working tree." Mirror the rationale already in the "keep" path (`:44-48`): a file the user didn't ask for must not silently ride their next unrelated commit to `main`.
2. Update the Exit Display (`:214-224`) to add a closing line: files are unstaged — "review, commit, and push when ready. Until pushed, a cycle worktree cut from `origin/main` won't see `config.json`/`tech-debt.md`." (This is the **Uncommitted-not-pushed** edge case; it was already true of today's commit-to-local-main behavior.)
3. Keep the `Omit the Created: docs/dev/tech-debt.md line…` guidance (`:226-227`) intact.

### Task 4: init — rerun "update" path becomes a safe migration
What: Replace Scenario D's "update = re-run Phase 2 which commits" with a merge-migration: backfill missing keys with defaults, preserve existing (possibly tuned) values, stamp `schema_version`, leave a pre-existing `worktree_root` untouched, refuse to touch a future/unknown `schema_version`, and leave everything unstaged.
Used by: A developer re-running `/dev:init` on an older/drifted repo (this repo's own `config.json`).
Depends on: Task 2 (the key set + defaults + `SCHEMA_VERSION`), Task 3 (unstaged/no-commit behavior the migration inherits).
Files: plugins/dev/skills/init/SKILL.md (Scenario D `:39-55`)
Interfaces:
- Consumes: `SCHEMA_VERSION = 1` and per-key defaults from Task 2; the no-commit rule from Task 3.
- Produces: a migration procedure that is idempotent and non-destructive; tuned `spec_max_questions` survives; drifted config gains `component_policy`/`changelog`/`schema_version` without altering set values.

Implementation steps:
1. Rewrite Scenario D (`:39-55`). Keep "Read and display current config" and the "Update or keep?" prompt. Keep the existing **keep** branch (`:42-52`) as-is (it already leaves `tech-debt.md` unstaged) — it remains correct.
2. Replace the **update** branch (`:53-55`) with a **migration** procedure:
   - Read + JSON-parse the existing `config.json`. Read its `schema_version` (absent ⇒ legacy `0`).
   - **Future-version guard:** if `schema_version` > `SCHEMA_VERSION` (`1`), do **not** modify or downgrade it — leave the file untouched and report "config schema vN is newer than this init knows (v1); left unchanged." (Edge: Unknown/future `schema_version`.)
   - Otherwise **merge**: for each key in the current schema (see **Config schema**), if absent add it with its default (`component_policy`→`can-propose` only when no answer is available; if init just asked the surviving question, use that answer); if present, **preserve the existing value** — never overwrite a present value with a template default. (Edge: Tuned-value preservation.)
   - Leave any key the new template no longer emits (e.g. a pre-existing `worktree_root`) **in place**; do not error on encountering it. (Edge: `worktree_root` in an existing config.)
   - Stamp `schema_version = SCHEMA_VERSION`.
   - Also ensure `tech-debt.md` exists (create from the canonical header if absent, as the keep path does).
   - **Leave the updated `config.json` (and any newly created `tech-debt.md`) unstaged** — no `git add`, no commit — and report: "migrated config to schema v1; left unstaged — review, commit, and push when ready." (Ties to Task 3; this is the general migration that replaces the hand-special-cased `tech-debt.md` backfill.)
3. Note in the prose that this migration is the general mechanism by which older repos gain new artifacts (generalizing the former `tech-debt.md`-only backfill).

### Task 5: Consumer-side documented defaults (close the contract's "belt" half)
What: At every `dev:*` config read site, document the fallback default used when the key is absent, so a config in any state yields correct behavior even before migration runs.
Used by: `dev:shape`, `dev:reflect`, `dev:spec`, `dev:pr` at their config reads.
Depends on: Task 2 (canonical key names + default values).
Files: plugins/dev/skills/shape/SKILL.md (`:64`), plugins/dev/skills/reflect/SKILL.md (`:71-73`), plugins/dev/skills/spec/SKILL.md (`:24`), plugins/dev/skills/pr/SKILL.md (`:80`, `:97`)
Interfaces:
- Consumes: key names + defaults from Task 2's **Config schema**.
- Produces: each reader names its key and its documented default inline. Satisfies the grep-verifiable success criterion "every config key any `dev:*` skill reads is either written by init **or** has a documented consumer-side default."

Implementation steps:
1. **shape `:64`:** change "Read `docs/dev/config.json` → component policy (existing only vs. can propose new)" to read the **`component_policy`** key explicitly, "default `can-propose` if the key is absent." Ensure the value maps to the same "existing only / can propose new" wording used at `:70` and `:200`.
2. **reflect `:71-73`:** the retrospective question "Were any components proposed that didn't fit component policy?" — add a parenthetical that the policy is `config.json`'s **`component_policy`** (default `can-propose`), so reflect reads a key init actually writes rather than an undefined concept.
3. **spec `:24`:** the Step 1 read line for `config.json` — append the defaults: "`spec_max_questions` default `10`, `spec_min_confidence` default `85` when the key or file is absent."
4. **pr `:80` / `:97`:** `:80` already skips when `changelog` is absent/null (keep). At `:97` make explicit: "`changelog_versioned` absent ⇒ treat as `false`." (Closes the last consumer default.)
5. (autopilot `:45` already documents `spec_max_questions` default `10` — verified in Task 8's sweep, no edit expected.)

### Task 6: spec — restructure the product-plan lifecycle onto the cycle PR
What: Stop pushing the product plan to `origin/$INTEGRATION` via an ephemeral detached worktree; instead write it as a plain file in the cycle's own `$WORKDIR` after Step 6 creates the worktree, so it reaches the integration branch through the cycle's own PR (the `tech-debt.md` precedent). Set `state.json.product_plan` so `done`'s top-level check-off fires.
Used by: `dev:done` Step 3 (check-off) and `dev` Step 6 (continuation) read the resulting plan; verified in Task 7.
Depends on: nothing (independent of the init/config tasks) — first task of the product-plan strand.
Files: plugins/dev/skills/spec/SKILL.md (Step 2 product-scale `:47-77`; Step 4 decomposition `:94-99`; Step 6 `:150-231`)
Interfaces:
- Consumes: `$WORKDIR` created in Step 6; the product-plan template already in Step 2 (`:48-58`).
- Produces: no `git add`/`commit`/`push` to `origin/$INTEGRATION` for the product plan anywhere in spec. A `product_plan`-write block after Step 6 that (a) writes/appends the prepared plan into `$WORKDIR/docs/dev/[<parent>/]product-plan.md`, (b) sets `state.json.product_plan` to the top-level path (top-level cycles only; nested rely on `parentFeature`), (c) commits it to the cycle branch with `git -C "$WORKDIR"`.

Implementation steps:
1. **Step 2 item 5 (`:47`):** keep "determine target path + prepare content", but change "item 6 writes it into the ephemeral worktree" to "the write is deferred until after Step 6 creates the cycle worktree (see the product-plan write below)".
2. **Step 2 item 6 (`:60-77`):** delete the entire ephemeral-detached-worktree procedure (the `PRIMARY`/`TMP`/`worktree add --detach`/`push origin HEAD:$INTEGRATION`/`worktree remove` block and its rationale). Item 6 becomes: "Pick the first feature to build (was item 7) and proceed as a normal feature-scale spec (was item 8)." Renumber items 7/8 accordingly.
3. **Step 2 item 5 append note (`:59`):** reword "the ephemeral worktree in item 6 starts from `origin/$INTEGRATION`, so any existing plan is already present to append to" → "the cycle worktree (Step 6) is created from `origin/main` (or the parent's HEAD for a nested cycle), so any existing product plan is already present in `$WORKDIR` to append to."
4. **Step 4 decomposition (`:98-99`):** replace "Land it before proceeding, using Step 2 item 6's product-plan push procedure…" with "prepare the decomposition content now; it is written into `$WORKDIR` after Step 6 (same deferred write as Step 2)." Reword `:99` "durable artifact on `origin/$INTEGRATION`" → "durable artifact in the cycle's worktree, reaching the integration branch via the cycle's PR."
5. **Add the deferred write at the end of Step 6** (after the initial `state.json` commit, `:225-231`): a labeled block — "If Step 2 (product-scale) or Step 4 (decomposition) prepared a product plan, write it now into `$WORKDIR`:"
   - Top-level: `$WORKDIR/docs/dev/product-plan.md`; set `state.json.product_plan` to `"docs/dev/product-plan.md"`.
   - Nested: `$WORKDIR/docs/dev/<parent>/product-plan.md`; leave `product_plan` null (done uses `parentFeature`).
   - Append-if-exists (a plan already present from `origin/main`/parent), else create from the Step 2 template.
   - Commit with `git -C "$WORKDIR" add <path> docs/dev/<feature-name>/state.json && git -C "$WORKDIR" commit -m "docs: record product plan for <product-name>"`.
   - This commit rides the cycle's PR to `$INTEGRATION` — no direct push.
6. Verify no remaining `origin/$INTEGRATION` push for the product plan exists in spec (grep in Task 8).

### Task 7: Verify propagation — done check-off + dev continuation under PR-propagation
What: Trace that the restructured lifecycle keeps `done`'s check-off and `dev`'s continuation working, and confirm the now-set `product_plan` makes `done` Step 3's top-level branch fire. Add short visibility-timing notes; change no logic beyond what tracing proves necessary.
Used by: The cycle's own validation (success criterion "propagation intact, verified by tracing").
Depends on: Task 6 (sets `product_plan`; moves the write into the PR).
Files: plugins/dev/skills/done/SKILL.md (`:130-145`), plugins/dev/skills/dev/SKILL.md (`:128-141`)
Interfaces:
- Consumes: `state.json.product_plan` (top-level, set by Task 6) and `parentFeature` (already set by spec) that `done` Step 3 branches on; the merged integration tip `done` Step 2 detaches to (`:103`).
- Produces: confirmation notes only. `done` Step 3 top-level now fires because `product_plan` is non-null. `dev` Step 6 continuation reads the plan from the current checkout — now visible only **after** cycle-1's PR merges (the accepted **Fresh-decomposition abandonment** / **Concurrent fan-out** trade-off).

Implementation steps:
1. Trace `done` Step 2→3: Step 2 detaches at `origin/$INTEGRATION` (post-merge tip); the product plan rode cycle-1's PR, so it is present at that tip; Step 3 reads it, flips `- [ ]`→`- [x]` for this feature, and `push_integration` writes back. Confirm `product_plan` non-null (Task 6) so the top-level branch is reached. Add a one-line note at `done:132` that the plan is present because it merged via the cycle PR.
2. Trace `dev` Step 6 continuation (`:130`): it reads `docs/dev/product-plan.md` from the working checkout. Add a one-line note that under PR-propagation the plan appears after the creating cycle's PR merges (documenting the visibility timing; no logic change).
3. If tracing reveals a real break (not just timing), stop and surface it rather than silently patching — but the expected outcome is notes only.

### Task 8: Cross-file sweep — stale "3 setup questions" / `worktree_root` references
What: Grep every `dev:*` skill for phrasings this cycle invalidated and fix any straggler outside the files already edited.
Used by: The success criteria's grep checks ("no surviving '3 setup questions' phrasing", "no write of `worktree_root`", "no direct push to `origin/$INTEGRATION` for the product plan").
Depends on: Tasks 1, 2, 6 (the canonical wording/keys must be settled first).
Files: any plugins/dev/skills/*/SKILL.md a sweep flags; expected: none beyond Tasks 1/2/6.
Interfaces:
- Consumes: the settled wording from Tasks 1/2/6.
- Produces: grep-clean repo for the three success-criterion patterns.

Implementation steps:
1. `grep -rn "3 setup\|three setup\|three question\|3 question" plugins/dev/skills` → fix any hit outside init.
2. `grep -rn "worktree_root" plugins/dev/skills` → expect zero after Task 2; fix any straggler.
3. `grep -rn "origin/\$INTEGRATION\|HEAD:\$INTEGRATION\|_planroot" plugins/dev/skills/spec` → confirm the product-plan push is gone (Task 6); the only surviving `push_integration`/`origin/$INTEGRATION` references should be in `done` (legitimate) and unrelated to the product-plan write.
4. `grep -rn "Initialize /dev workflow\|git add.*config.json" plugins/dev/skills` → confirm no other skill assumes init committed its scaffolding (autopilot runs init but reads config with defaults if absent — no assumption of a commit).

## Edge Cases
| Edge case | Handled in | Approach |
|-----------|-----------|----------|
| Missing key at read time | Task 5 (belt) + Task 4 (suspenders) | Consumer uses documented default; migration also backfills. Neither depends on the other having run. |
| Unknown/future `schema_version` | Task 4 | Future-version guard: leave untouched, report; never downgrade/clobber. |
| Tuned-value preservation | Task 4 | Merge only adds absent keys; never overwrites a present value with a template default. |
| Uncommitted-not-pushed visibility | Task 3 | init leaves files unstaged; exit line states a worktree cut from `origin/main` won't see them until staged, committed, **and pushed**. |
| `worktree_root` in an existing config | Task 4 | Migration leaves it in place, does not error; new configs stop emitting it. |
| Fresh-decomposition abandonment | Task 6 / Task 7 | Product plan lives only in cycle-1's worktree until its PR merges; lost if cycle-1 abandoned. Accepted as rare; archive-to-`docs/decisions` mitigation is out of scope. |
| Concurrent fan-out (cycle-2 before cycle-1 merges) | Task 7 | cycle-2 (cut from `origin/main`) won't see the plan until cycle-1 merges; plan-creating cycle should merge first. Known limitation. |

## Out of Scope
- The six other open tech-debt entries (gate-path state writes, feature-slug allowlist, nested product plan, hardcoded reflect path, validate fix-loop verification, autopilot cross-note). Only *"dev:spec's product-plan procedure pushes straight to origin/main"* is folded (already recorded in `debt-pending.md`'s `## To Close`).
- The `debt-backfill` and `debt-linear-promotion` cycles.
- Redesigning init's stack detection, changelog detection, or the wording of the surviving question beyond what pruning requires.
- Changing `validate:71`'s checklist. That gate is a **constraint on this cycle's own diff** (it must add `component_policy`/`schema_version` to every reader's read list and document defaults), not a file this cycle edits.
- Archiving an abandoned product plan to `docs/decisions/`.
- Fixing the nested-product-plan-lifetime entry — *looked at* during Task 6/7 (adjacent), not fixed.

## Risks and Unknowns
- **`product_plan` was never wired before this cycle.** Task 6 sets it as part of the restructure because `done`'s top-level check-off (a stated success criterion) cannot fire without it. Risk: if some path already sets it that the grounding sweep missed, Task 6 could double-set. Mitigation: Task 6 sets it in exactly one place (the deferred write after Step 6); Task 8's sweep confirms no other setter.
- **Deferred-write sequencing.** The product-plan write moves from Step 2/Step 4 (pre-worktree) to after Step 6. Risk: Step 2's product-scale flow re-enters Steps 3–6 for the chosen feature, so the "prepared" content must survive until Step 6's write. Mitigation: Task 6 keeps the prepared content in the stage's working context and performs a single write at end of Step 6; the append-if-exists guard handles a plan already on `origin/main`.
- **`component_policy` default value choice.** Defaulting to `can-propose` is a judgment (permissive). If the project prefers a conservative default (`existing-only`), flip the one default in Tasks 2/5 — isolated, single-value change.
- **No test harness.** Verification is procedure-tracing + confirming embedded shell exits 0 on the healthy path. Risk of a logic slip that reads consistently. Mitigation: Task 8's greps are the mechanical backstop for the three grep-verifiable success criteria.
