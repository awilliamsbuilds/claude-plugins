# Resumable Dev Cycles — Implementation Plan

*Branch: feature/resumable-dev-cycles · 2026-07-03*

## Files

| File | Action | Purpose |
|------|--------|---------|
| `plugins/dev/skills/spec/SKILL.md` | Modify | state.json schema (`parentFeature`, `worktreePath`), nested product-plan writing, worktree offering, resume-mid-approval, exit-protocol message |
| `plugins/dev/skills/shape/SKILL.md` | Modify | Artifact-path argument, resume-mid-approval, exit-protocol message |
| `plugins/dev/skills/plan/SKILL.md` | Modify | Artifact-path argument, resume-mid-approval, exit-protocol message |
| `plugins/dev/skills/build/SKILL.md` | Modify | Artifact-path argument, exit-protocol message |
| `plugins/dev/skills/validate/SKILL.md` | Modify | Artifact-path argument, exit-protocol message |
| `plugins/dev/skills/pr/SKILL.md` | Modify | Artifact-path argument, nested-branch PR target, exit-protocol message |
| `plugins/dev/skills/done/SKILL.md` | Modify | Artifact-path argument, nested/master-plan-aware completion display |
| `plugins/dev/skills/dev/SKILL.md` | Modify | Nested/worktree-aware in-progress-session display, Invocation Reference update |
| `plugins/dev/skills/autopilot/SKILL.md` | Modify | Document worktree auto-accept behavioral rule |

## Tasks

### Task 1: dev:spec — schema, nested product plan, worktree offering
What: Establish the `state.json` schema fields every other task depends on (`parentFeature`, `worktreePath`), extend Step 4's Scope Check to write/update a product plan (nested at `docs/dev/<feature>/product-plan.md` when this Spec invocation is itself running inside an enclosing feature, top-level `docs/dev/product-plan.md` otherwise) instead of just asking "which first?", and extend Step 6 to offer `EnterWorktree` isolation when the cycle is a product-plan item at any depth.
Used by: Every subsequent task reads `parentFeature`/`worktreePath` from the state.json schema this task defines. Any future `/dev` session that decomposes a request into multiple cycles.
Depends on: nothing — first task.
Files: Modify `plugins/dev/skills/spec/SKILL.md`
Interfaces:
- Consumes: nothing
- Produces: `state.json` fields `parentFeature: string | null` (the enclosing feature's name if this cycle is a nested sub-milestone, else `null`) and `worktreePath: string | null` (the absolute worktree path if `EnterWorktree` was used, else `null`). Also produces the nested-vs-top-level product-plan file convention (`docs/dev/product-plan.md` vs `docs/dev/<feature>/product-plan.md`) that Tasks 6 and 7 read.

Implementation steps:
1. In the `state.json` initialization template (Step 6), add two fields after `linear_issue`: `"parentFeature": null` and `"worktreePath": null`.
2. In Step 4 (Scope Check + YAGNI Gate), replace "flag it: 'This covers three independent things — each needs its own /dev cycle. Which should we start with?'" with: flag it the same way, but also write the decomposition to a product plan before asking which to start. Determine the target path: if the *current* Spec invocation is itself running with a `parentFeature` already set in an in-progress state.json (i.e., this Spec call is happening inside an already-nested context), write to `docs/dev/<parentFeature>/product-plan.md`; otherwise write to the top-level `docs/dev/product-plan.md`. Use the same format as Step 2's existing product-plan template (Milestone headers, checkbox items). If the target file already exists, append the new items as a new milestone rather than overwriting.
3. In Step 6 (Create Feature Branch), before the `git checkout -b` line, add a check: is the feature being started an item inside *any* product plan (top-level `docs/dev/product-plan.md` or a nested `docs/dev/*/product-plan.md`)? If yes: **in standard mode**, offer worktree isolation: "This is part of a multi-cycle plan — want me to isolate it in its own worktree? (protects it from other work happening in this directory while it's in progress)" and wait for consent. **In autopilot mode**, per `dev:autopilot`'s own no-gate principle (it never stops for a yes/no question), auto-accept the worktree isolation without asking — it's the beneficial, non-destructive default, same pattern `dev:autopilot` Step 2 already uses for Shape's alternative-selection ("auto-select the recommended option, note the selection and reasoning"). If accepted (either by explicit consent or autopilot auto-accept), call `EnterWorktree` — if the matching product plan is nested (this feature belongs to an enclosing feature's `docs/dev/<parent>/product-plan.md`), the base ref must be the parent feature's own branch HEAD, not `origin/main` (pass whatever the native tool requires to branch from local HEAD rather than fresh from the default branch — consult the tool's own parameter docs for the current harness, since `EnterWorktree`'s `name`/`path` parameters don't directly expose a base-ref override; if the harness's `worktree.baseRef` setting is global and can't be overridden per-call, fall back to: create the worktree via `EnterWorktree`, then immediately rebase/reset its branch onto the parent feature's branch before proceeding). If the product plan is top-level, branch fresh from `origin/main` (the tool's default). Record whichever path was used in `worktreePath`, and if nested, record the enclosing feature's name in `parentFeature`.
4. If `EnterWorktree` is unavailable (not present in this harness) or the user declines: proceed with today's plain `git checkout -b` in the current directory, leaving `worktreePath`/`parentFeature` as recorded (parentFeature still gets set if nested, even without a worktree — it governs PR targeting in Task 6, independent of worktree usage).
5. In Step 1 (Read Context), add: before Step 2, check whether `spec.md` already exists for this feature (from a prior partial run) and `state.json`'s `stage` is still `"spec"` (i.e., artifact exists but hasn't been approved yet). If so, skip straight to Step 12 (re-display the existing spec.md for approval) rather than re-running Steps 2–11 from scratch — this is the resume-mid-approval case: a `/clear` that happens while the user is reviewing a freshly-written spec.md shouldn't cause the whole guided-questioning flow to run again.
6. In Step 12 (User Review Gate), change the message to match the shared exit-protocol format: state the artifact path, state it's safe to `/clear` now, and give the exact next command with the artifact-path argument (e.g. `/dev:plan docs/dev/<feature>/spec.md`, or `/dev:shape docs/dev/<feature>/spec.md` if UI is needed) — plus the worktree path if `worktreePath` is set. Determine the next-stage command the same way Step 12 already does (Shape if UI needed / Plan if no-ui / Build if Micro).

### Task 2: dev:shape — artifact-path argument, resume-mid-approval, exit-protocol message
What: Make `dev:shape` resolvable from a passed artifact path instead of only from conversation memory, avoid re-running the whole design flow if `/clear` happens mid-approval-wait, and match the shared exit-protocol message format on completion.
Used by: The exact resume command Task 1 prints when UI is needed (`/dev:shape docs/dev/<feature>/spec.md`).
Depends on: Task 1 (consumes the `worktreePath`/`parentFeature` fields Task 1 defines, to include worktree path in its own exit-protocol message).
Files: Modify `plugins/dev/skills/shape/SKILL.md`
Interfaces:
- Consumes: `state.json` fields `worktreePath`, `parentFeature` (Task 1)
- Produces: nothing new consumed by later tasks — shape is a leaf for this plan's purposes (Build/Validate/PR/Done don't read shape-specific new fields).

Implementation steps:
1. In Step 1 (Artifact Gate), add: this skill may be invoked with an artifact-path argument (e.g. `docs/dev/<feature>/spec.md`). If provided, derive `<feature>` from the path (the directory component) instead of requiring it to already be known from conversation context. If no argument is given, fall back to today's behavior (the feature must already be known — from `dev:dev`'s orchestration or an existing in-progress session).
2. Also in Step 1: if `design.md` already exists for this feature and `state.json`'s `stage` is still `"shape"`, skip straight to Step 11 (re-display for approval) rather than re-running the full design flow (mirrors Task 1 step 5's resume-mid-approval logic).
3. In Step 11 (User Review Gate), change the message to the shared exit-protocol format: artifact path, safe-to-`/clear` note, exact next command with argument (`/dev:plan docs/dev/<feature>/design.md`), plus worktree path from `state.json.worktreePath` if set.

### Task 3: dev:plan — artifact-path argument, resume-mid-approval, exit-protocol message
What: Same three changes as Task 2, applied to `dev:plan`.
Used by: The exact resume command Task 1 or Task 2 prints (`/dev:plan docs/dev/<feature>/spec.md` or `.../design.md`).
Depends on: Task 1 (consumes `worktreePath`/`parentFeature`).
Files: Modify `plugins/dev/skills/plan/SKILL.md`
Interfaces:
- Consumes: `state.json` fields `worktreePath`, `parentFeature` (Task 1)
- Produces: nothing new consumed by later tasks.

Implementation steps:
1. In Step 1 (Artifact Gate), accept an artifact-path argument (`spec.md` or `design.md` path) and derive `<feature>` from it; fall back to today's behavior if no argument given.
2. Also in Step 1: if `plan.md` already exists for this feature and `state.json`'s `stage` is still `"plan"`, skip straight to Step 8 (re-display for approval) rather than re-running Steps 2–7.
3. In Step 8 (User Review Gate), change the message to the shared exit-protocol format: artifact path, safe-to-`/clear` note, exact next command (`/dev:build docs/dev/<feature>/plan.md`), plus worktree path if set.

### Task 4: dev:build — artifact-path argument, exit-protocol message
What: Accept an artifact-path argument in Step 1, and change the completion notification to the shared exit-protocol format. No resume-mid-approval logic needed here — Build has no approval-wait pause (it runs straight through to Validate).
Used by: The exact resume command Task 3 prints (`/dev:build docs/dev/<feature>/plan.md`).
Depends on: Task 1 (consumes `worktreePath`/`parentFeature`).
Files: Modify `plugins/dev/skills/build/SKILL.md`
Interfaces:
- Consumes: `state.json` fields `worktreePath`, `parentFeature` (Task 1)
- Produces: nothing new consumed by later tasks.

Implementation steps:
1. In Step 1 (Artifact Gate), accept an artifact-path argument (`plan.md` path, or `spec.md` for Micro tier) and derive `<feature>` from it; fall back to today's behavior if no argument given.
2. In Step 6 (Update State on Completion), change the "In standard mode, notify" block to the shared exit-protocol format: confirmation that all plan tasks are committed, safe-to-`/clear` note, exact next command (`/dev:validate docs/dev/<feature>/plan.md`), plus worktree path if set.

### Task 5: dev:validate — artifact-path argument, exit-protocol message
What: Same two changes as Task 4, applied to `dev:validate`.
Used by: The exact resume command Task 4 prints (`/dev:validate docs/dev/<feature>/plan.md`).
Depends on: Task 1 (consumes `worktreePath`/`parentFeature`).
Files: Modify `plugins/dev/skills/validate/SKILL.md`
Interfaces:
- Consumes: `state.json` fields `worktreePath`, `parentFeature` (Task 1)
- Produces: nothing new consumed by later tasks.

Implementation steps:
1. In Step 1, accept an artifact-path argument and derive `<feature>` from it; fall back to today's behavior if no argument given.
2. In Step 6 (Update State + Commit)'s "In standard mode, notify" block, change to the shared exit-protocol format: loops run, clean/issues status, safe-to-`/clear` note, exact next command (`/dev:pr docs/dev/<feature>/validation.md`), plus worktree path if set.

### Task 6: dev:pr — artifact-path argument, nested-branch PR target, exit-protocol message
What: Accept an artifact-path argument, target the PR at the parent feature's branch instead of `main` when `state.json.parentFeature` is set (nested cycle), and change the completion notification to the shared exit-protocol format pointing at `dev:done`.
Used by: The exact resume command Task 5 prints (`/dev:pr docs/dev/<feature>/validation.md`). `dev:done` (Task 7) reads the PR's actual base branch indirectly via the same `parentFeature` field to know whether merging this PR completes a nested sub-milestone or the outer cycle.
Depends on: Task 1 (consumes `parentFeature`).
Files: Modify `plugins/dev/skills/pr/SKILL.md`
Interfaces:
- Consumes: `state.json` field `parentFeature` (Task 1) — read to decide PR base branch
- Produces: nothing new — `pr_url`/`pr_number` fields already exist in the schema.

Implementation steps:
1. In Step 1, accept an artifact-path argument (`validation.md` path) and derive `<feature>` from it; fall back to today's behavior if no argument given.
2. In Step 4 (Open PR), change `--base main` to be conditional: if `state.json.parentFeature` is set (non-null), target `--base <parentFeature's branch>` (read the parent feature's own `state.json.branch` field to get the exact branch name) instead of `main`. Only when `parentFeature` is null does the PR target `main`, as today.
3. In Step 5 (Update State + Commit)'s "In standard mode, display" block, change to the shared exit-protocol format: PR URL, safe-to-`/clear` note, exact next command (`/dev:done docs/dev/<feature>/validation.md` — or however `dev:done`'s artifact-path argument is defined in Task 7), plus worktree path if set.

### Task 7: dev:done — artifact-path argument, nested/master-plan-aware completion display
What: Accept an artifact-path argument, and enhance Step 8's completion display to explicitly name the completed item and remaining items when a product plan (top-level or nested) exists, with the exact `/clear` + next-command instructions — this is the cross-cycle counterpart to the other tasks' cross-stage exit protocol.
Used by: The exact resume command Task 6 prints. The user (or a fresh Claude session), reading this display to know what to do next across a potential `/clear`.
Depends on: Task 1 (consumes `parentFeature`, and the nested/top-level product-plan file convention).
Files: Modify `plugins/dev/skills/done/SKILL.md`
Interfaces:
- Consumes: `state.json` field `parentFeature` (Task 1); the product-plan file convention (`docs/dev/product-plan.md` or `docs/dev/<parent>/product-plan.md`) Task 1 established
- Produces: nothing new consumed by later tasks — Done is the terminal stage.

Implementation steps:
1. In Step 1, accept an artifact-path argument (`validation.md` path) and derive `<feature>` from it; fall back to today's behavior if no argument given.
2. In Step 3 ("Update Product Plan (if product-scale)"), generalize beyond `state.json.product_plan` (the old top-level-only field) to also check the nested case: if `state.json.parentFeature` is set, update `docs/dev/<parentFeature>/product-plan.md` (mark this item's checkbox complete) instead of (or in addition to, if both apply) the top-level `docs/dev/product-plan.md`.
3. In Step 8 (Display), after the existing completion summary, add: if a governing product plan exists (top-level or, per `parentFeature`, nested), explicitly state which item/milestone was just completed, list what remains, note it's safe to `/clear` now, and give the exact command to start the next item (`/dev:spec` with the next item's name, or the exact resume point if that next cycle was already partially started). This replaces the existing vaguer "Start feature-c next? Or pick a different cycle." prompt with the same exact-command precision the other tasks' exit protocols use.

### Task 8: dev:dev — nested/worktree-aware session display, Invocation Reference update
What: Update the orchestrator's Step 3 (in-progress session display) to show worktree path and nesting status when present, and document the new artifact-path-argument convention in the Invocation Reference table so it's discoverable without reading every stage skill.
Used by: Anyone running `/dev` with no arguments and an in-progress session — this is the first thing a resuming user sees.
Depends on: Task 1 (consumes `worktreePath`, `parentFeature`, and the product-plan file convention), and conceptually summarizes Tasks 2–7's shared artifact-path-argument convention (informational only — no code dependency, just needs those tasks' convention to be finalized before documenting it accurately).
Files: Modify `plugins/dev/skills/dev/SKILL.md`
Interfaces:
- Consumes: `state.json` fields `worktreePath`, `parentFeature` (Task 1)
- Produces: nothing — terminal, documentation-only task.

Implementation steps:
1. In Step 3 (Check for In-Progress Session), when displaying a found session, add the worktree path (if `worktreePath` is set) and a "(nested under <parentFeature>)" note (if `parentFeature` is set) to the existing `/dev session in progress: <feature-name>` display block.
2. In the Invocation Reference table, add a row documenting that every `/dev:<stage>` command accepts an optional artifact-path argument to resume without conversation memory, e.g. `/dev:plan docs/dev/<feature>/spec.md`.

### Task 9: dev:autopilot — document worktree auto-accept rule
What: Add the worktree-offer auto-accept behavior (Task 1 step 3) to `dev:autopilot`'s own Step 2 "Autopilot Behavioral Rules" list, so it's documented in the one place that enumerates all of autopilot's overrides of standard-mode behavior — same lesson as the earlier `remove-superpowers-convention` cycle, where a behavioral change written only in `dev:build` silently conflicted with `dev:autopilot` until both were updated together.
Used by: Anyone reading `dev:autopilot`'s behavioral-rules list to understand what it overrides; keeps this rule discoverable without having to read `dev:spec`'s Step 6 in full.
Depends on: Task 1 (mirrors the exact auto-accept behavior Task 1 step 3 defines).
Files: Modify `plugins/dev/skills/autopilot/SKILL.md`
Interfaces:
- Consumes: nothing (documentation mirror, not a code dependency)
- Produces: nothing — terminal, documentation-only task.

Implementation steps:
1. In Step 2 (Autopilot Behavioral Rules), add a new bullet after "Shape alternatives: auto-select": "**Worktree offer: auto-accept.** When `dev:spec` Step 6 would offer worktree isolation (cycle is part of a product plan), auto-accept without asking — beneficial, non-destructive default."

### Task 10: Verify no ExitWorktree calls introduced
What: Confirm the exit-protocol additions across all 9 modified files never call `ExitWorktree` — matches the spec's explicit design requirement and its own success criterion.
Used by: N/A — a verification checkpoint.
Depends on: Tasks 1–9 (verifies their combined output).
Files: none (read-only verification)
Interfaces:
- Consumes: nothing
- Produces: nothing — terminal verification task.

Implementation steps:
1. Run `grep -rn "ExitWorktree" plugins/dev/skills/*/SKILL.md`.
2. Expected: no output. If output appears, remove it before Build completes — no exit-protocol message should ever invoke `ExitWorktree`.

## Edge Cases
| Edge case | Handled in | Approach |
|-----------|-----------|----------|
| `/clear` happens while a spec/shape/plan artifact is written but not yet approved | Tasks 1, 2, 3 | Step 1 resume-mid-approval check: re-display existing artifact for approval instead of re-running the stage. |
| Nested cycle's PR needs to target the parent branch, not `main` | Task 6 | `parentFeature` (Task 1) governs `--base` target. |
| `EnterWorktree` unavailable or declined | Task 1 | Falls back to plain `git checkout -b`; `worktreePath` stays `null`. |
| Product plan already exists when a new decomposition is detected | Task 1 | Append as a new milestone, don't overwrite. |
| Exit-protocol messaging must never call `ExitWorktree` | Task 9 | Grep verification after all other tasks. |

## Out of Scope
- `dev:autopilot` changes (per spec — no natural pause points for exit-protocol messaging).
- Retroactive worktree/master-plan tracking for already-completed past cycles.
- Automatic worktree cleanup/garbage-collection.
- Depth cap on nested product plans.

## Risks and Unknowns
- **`EnterWorktree`'s base-ref override for nested worktrees**: the tool's parameters (`name`/`path`) don't obviously expose a per-call base-ref override; `worktree.baseRef` may be a global harness setting. Task 1 step 3 includes a fallback (rebase/reset onto the parent branch post-creation) in case a direct override isn't possible — investigate the actual harness behavior during Build and adjust the instructions if the fallback turns out to be unnecessary or insufficient.
- **Resume-mid-approval detection reliability**: Tasks 1–3's "does the artifact already exist and is the stage still X" check is a reasonable heuristic but could misfire if a user manually deletes an artifact file without updating `state.json`. Not expected to be common; no special handling planned beyond what's specified.
- **Nested product-plan file discovery in Task 1 step 2**: determining "is this Spec invocation happening inside an already-nested context" relies on the *current* state.json already having `parentFeature` set before this very Spec call — but for the *first* Spec call of a brand-new nested sub-milestone, state.json doesn't exist yet at Step 4 (it's created in Step 6, which comes after). Step 4 needs another signal — most likely: was this `dev:spec` invocation itself given an artifact-path argument pointing inside an existing feature's directory (`docs/dev/<parent>/...`)? Flagging this for explicit attention during Build — Task 1's implementation steps should derive nesting from the invocation context (e.g., an enclosing feature name passed alongside the request, or the fact that `dev:spec` was invoked from within an already-active parent cycle), not from a not-yet-created state.json.
