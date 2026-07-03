# Absorb Superpowers Into Dev Plugin — Implementation Plan

*Branch: feature/remove-superpowers-convention · 2026-07-02*

## Files

| File | Action | Purpose |
|------|--------|---------|
| `plugins/dev/skills/dev/SKILL.md` | Modify | Add supersede note for `brainstorming`, `writing-plans` |
| `plugins/dev/skills/spec/SKILL.md` | Modify | Add supersede note for `brainstorming` |
| `plugins/dev/skills/shape/SKILL.md` | Modify | Add supersede note for `brainstorming` |
| `plugins/dev/skills/plan/SKILL.md` | Modify | Add `Interfaces` block, "No Placeholders" rule, type-consistency check, supersede note for `writing-plans` |
| `plugins/dev/skills/build/SKILL.md` | Modify | Add root-cause-before-fix rule, supersede note for `test-driven-development`, `systematic-debugging` |
| `plugins/dev/skills/validate/SKILL.md` | Modify | Change Step 2 to dispatch fresh subagent reviews, supersede note for `requesting-code-review` |

## Tasks

**Parallel Group A — all 7 tasks below are independent; no task depends on another.**

### Task 1: Supersede note on dev/SKILL.md
What: Add a short note stating the `/dev` entry point supersedes `superpowers:brainstorming` and `superpowers:writing-plans` for the duration of an active `/dev` session — those skills should not be separately invoked.
Used by: Read by Claude at the start of any `/dev` invocation (Step 1 of `dev/SKILL.md`); prevents the global `using-superpowers` meta-instruction from redundantly firing those two skills.
Depends on: nothing.
Files: Modify `plugins/dev/skills/dev/SKILL.md`

Implementation steps:
1. Add a `## Superpowers Supersession` section near the top of `dev/SKILL.md` (after Purpose, before Step 1): "While a `/dev` session is active (a `docs/dev/<feature>/state.json` exists for the current feature), this workflow supersedes `superpowers:brainstorming` and `superpowers:writing-plans`. Do not invoke those skills separately — each `/dev` stage already contains the equivalent capability inline."
2. Commit: `plan: task 1 — supersede note on dev entry point` (commit happens in Build, not here — this plan just specifies the change).

### Task 2: Supersede note on spec/SKILL.md
What: State that `dev:spec` supersedes `superpowers:brainstorming` — its confidence-meter-driven questioning already covers brainstorming's ground.
Used by: Read whenever `dev:spec` runs, whether via the `/dev` orchestrator or invoked standalone as `/dev:spec`.
Depends on: nothing.
Files: Modify `plugins/dev/skills/spec/SKILL.md`

Implementation steps:
1. Add one line under Purpose: "This skill supersedes `superpowers:brainstorming` for the duration of the `/dev` session — do not invoke it separately."

### Task 3: Supersede note on shape/SKILL.md
What: State that `dev:shape` supersedes `superpowers:brainstorming`'s design-presentation phase — its "2-3 approaches" step already covers this ground.
Used by: Read whenever `dev:shape` runs.
Depends on: nothing.
Files: Modify `plugins/dev/skills/shape/SKILL.md`

Implementation steps:
1. Add one line under Purpose: "This skill supersedes `superpowers:brainstorming`'s design phase for the duration of the `/dev` session — do not invoke it separately."

### Task 4: Absorb writing-plans content into plan/SKILL.md
What: Add an `Interfaces:` block to the per-task template (`Consumes:` what a task uses from earlier tasks with exact signatures; `Produces:` what later tasks rely on with exact names/types), an explicit "No Placeholders" rule (no "TBD", "similar to Task N", "add appropriate error handling" — steps must show actual content), a type/signature-consistency check added to Step 6 Self-Review, and a supersede note for `superpowers:writing-plans`.
Used by: Read whenever `dev:plan` runs to produce `plan.md`; the `Interfaces` block is then read by `dev:build` when implementing each task, so it knows the exact contract between tasks without re-reading neighboring tasks in full.
Depends on: nothing.
Files: Modify `plugins/dev/skills/plan/SKILL.md`

Implementation steps:
1. Add one line under Purpose: "This skill supersedes `superpowers:writing-plans` for the duration of the `/dev` session — do not invoke it separately."
2. In the Step 3 task-format block, add after `Files:` and before `Implementation steps:`:
   ```
   Interfaces:
   - Consumes: [what this task uses from earlier tasks — exact signatures, or "nothing"]
   - Produces: [what later tasks rely on — exact names and types, or "nothing — terminal task"]
   ```
3. In the Step 5 `plan.md` template, mirror the same `Interfaces:` addition inside the Task 1 example block.
4. Add a new subsection after Step 3 titled "No Placeholders": "Every task must contain the actual content Build needs. Never write: 'TBD', 'similar to Task N' (repeat the content instead — Build may work tasks out of order), 'add appropriate error handling' / 'handle edge cases' without naming which edge case and how, or references to names/types not defined in any task's `Produces:`."
5. In Step 6 Artifact Self-Review, add a 6th checklist item: "Do the `Consumes:`/`Produces:` names and types line up across tasks? A dependency named differently in the task that produces it versus the task that consumes it is a plan bug — fix it before Build starts."

### Task 5: Absorb systematic-debugging content into build/SKILL.md
What: Add a condensed root-cause-before-fix rule for test failures discovered unexpectedly during implementation — read the error completely, check what changed, form one specific hypothesis, test it minimally, don't stack fixes — distinct from the existing Step 4 Backtrack Trigger (which governs when the *plan itself* is wrong). Add a supersede note for `superpowers:test-driven-development` and `superpowers:systematic-debugging`.
Used by: Read whenever `dev:build` runs; the root-cause rule applies specifically when a test fails that wasn't expected to fail (as opposed to the TDD red-phase, where failure is expected).
Depends on: nothing.
Files: Modify `plugins/dev/skills/build/SKILL.md`

Implementation steps:
1. Add one line under Purpose: "This skill supersedes `superpowers:test-driven-development` and `superpowers:systematic-debugging` for the duration of the `/dev` session — do not invoke them separately."
2. Add a new subsection after Step 2's "When to deviate from TDD" (still inside Step 2, Feature Cycle) titled "When a Test Fails Unexpectedly": "If a test fails that you didn't expect to fail (not the TDD red-phase — an existing test breaks, or your new test fails for a reason other than 'not implemented yet'), stop before patching. Read the full error and stack trace. Check what changed since it last passed (`git diff`, recent commits). Form one specific hypothesis for the cause. Make the smallest change that tests the hypothesis. If it doesn't resolve it, form a new hypothesis rather than stacking a second change on top of the first. If 3 hypotheses fail, stop and flag it to the user — the plan or the approach may be wrong, not just the code."
3. Confirm this new subsection doesn't contradict the adjacent "When to deviate from TDD" bullets (different concern: that's about *whether* to write the test first, this is about *what to do when a test unexpectedly fails*) — verified during Step 6 self-review below.

### Task 6: Fresh-subagent review dispatch in validate/SKILL.md
What: Change Step 2's Feature Cycle review behavior so code review and security review each dispatch as a fresh `general-purpose` subagent (via the Agent tool) rather than running inline in the current session. Each subagent receives only: the diff (`git diff BASE_SHA..HEAD_SHA` where `BASE_SHA` is the commit before Build started), `spec.md` success criteria, and `plan.md` tasks — explicitly not this session's conversation history. The main session receives each subagent's findings and continues the existing Step 3 (Issue Classification) and Step 4 (Fix Loop) unchanged. If subagent dispatch is unavailable in the current harness, fall back to today's in-session review. Add a supersede note for `superpowers:requesting-code-review`.
Used by: Read whenever `dev:validate` runs Step 2 during a feature cycle (architecture cycles are unaffected — they don't use this review path).
Depends on: nothing.
Files: Modify `plugins/dev/skills/validate/SKILL.md`

Implementation steps:
1. Add one line under Purpose: "This skill supersedes `superpowers:requesting-code-review` for the duration of the `/dev` session — do not invoke it separately."
2. Rewrite the "Feature Cycle — Parallel Reviews" subsection under Step 2: replace "Run both reviews simultaneously" with instructions to dispatch two `general-purpose` subagents in parallel (one per review type), each prompted with: description of what was built (from `plan.md`'s Files table), the diff since branch creation, `spec.md`'s Success Criteria, and the specific checklist (code review bullets or security review bullets, unchanged from today's list). Explicitly instruct: do not give the subagent this session's conversation history — only the artifacts listed.
3. Add a fallback line: "If subagent dispatch isn't available in the current harness, run both review checklists in-session as before."
4. Leave Step 3 (Issue Classification) and Step 4 (Fix Loop) untouched — they already consume "issues found" generically regardless of where the review ran.

### Task 7: Verify dev:init scaffold has no superpowers references
What: Re-confirm (already checked clean during Spec stage via grep, re-verify at Build time since the codebase may have changed) that `dev:init`'s generated scaffold — `docs/dev/config.json` template, generated `CLAUDE.md` Component Registry section — contains no reference to `superpowers`.
Used by: N/A — a verification checkpoint supporting the "fully self-contained" success criterion.
Depends on: nothing.
Files: none (read-only verification of `plugins/dev/skills/init/SKILL.md`)

Implementation steps:
1. Run `grep -rn "superpowers" plugins/dev/skills/init/SKILL.md`.
2. Expected: no output. If output appears, add it as a new task and fix before Build completes.

## Edge Cases

| Edge case | Handled in | Approach |
|-----------|-----------|----------|
| User explicitly invokes a `superpowers` skill directly outside any `/dev` context | Tasks 1–6 | Supersede notes are scoped to "while a `/dev` session is active" — not a blanket suppression. |
| `dev:build`'s existing "When to deviate from TDD" vs. new root-cause rule | Task 5 | Different concerns — deviation governs *whether* to write tests first; root-cause rule governs *what to do when a test unexpectedly fails*. Verified non-contradictory during self-review. |
| Subagent dispatch unavailable in current harness (validate) | Task 6 | Explicit fallback to in-session review — not a hard new dependency. |
| Skill invoked standalone (e.g. `/dev:plan` without the orchestrator) | Tasks 1–6 | Supersede notes and absorbed content live in each individual stage skill, not just the entry point. |

## Out of Scope

- Changes to the `superpowers` plugin itself.
- Cycle #3 (context-clearing between stages / worktree vs. branch decision) and Cycle B (`dev:start` skill) — separate `/dev` cycles.
- Retroactive cleanup of `docs/superpowers/` in other repos (e.g. `dev-plugin-design-archive`).
- Adopting `writing-plans`' subagent-driven *execution* model for `dev:build` — only the review-isolation technique is adopted (Task 6), not plan execution.
- Porting `systematic-debugging`'s full four-phase process or Red Flags table verbatim — Task 5 is intentionally condensed.
