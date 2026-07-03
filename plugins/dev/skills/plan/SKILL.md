---
name: dev:plan
description: "Stage 3 of the /dev workflow. Transforms spec + design into an ordered, implementation-ready task list. Applies the isolation principle to every task. Shows a visual sequence flow before writing plan.md. Requires spec.md and design.md (or spec.md alone in no-ui mode)."
---

# dev:plan — Planning Stage

**Announce:** "I'm using dev:plan to create the implementation plan."

**First action, before anything else:** run `date -u +%Y-%m-%dT%H:%M:%SZ` and hold onto the output — this is `plan_start`, recorded in Step 7. Capturing it now, before any other work, keeps it accurate to when the stage actually began.

## Purpose

Transform spec + design into a concrete sequence of changes that Build can execute without guessing.

This skill supersedes `superpowers:writing-plans` for the duration of the `/dev` session — do not invoke it separately.

**Anti-Pattern: "Just Start Building."**

<HARD-GATE>
Do NOT start Build without an approved plan. This gate is not skippable in standard mode.
Exception: Micro tier — spec.md includes an Implementation Note section that serves as the plan. Build reads that section directly. When tier is "micro" in state.json, skip this entire skill and tell the user: "Micro tier uses the Implementation Note in spec.md as the plan. Proceed to Build."
</HARD-GATE>

## Step 1: Artifact Gate

May be invoked with an artifact-path argument (`spec.md` or `design.md` path). If given, derive `<feature>` from the path instead of requiring it already be known from conversation context. If no argument is given, fall back to today's behavior. **Validate before using:** the path must match `docs/dev/<feature>/<artifact>.md` with `<feature>` matching `^[a-z0-9][a-z0-9-]*$` and containing no `..` segments. If it doesn't match, treat the argument as invalid and fall back to today's behavior rather than using the parsed value.

Read `docs/dev/<feature>/state.json` first. Check:
- If `tier == "micro"`: exit per the HARD-GATE exception above
- If `artifacts.spec` is null: STOP — "Plan requires spec.md. Run /dev:spec first."
- If mode is not `no-ui` and `skipped` does not include `"shape"` and `artifacts.design` is null: STOP — "Plan requires design.md. Run /dev:shape first, or use /dev:plan with no-ui mode."

**Resume-mid-approval check:** if `plan.md` already exists for this feature and `state.json.stage` is still `"plan"`, skip straight to Step 8 to re-display it for approval rather than re-running Steps 2–7.

Read once, work from this throughout:
- `docs/dev/<feature>/spec.md`
- `docs/dev/<feature>/design.md` (if it exists)

## Step 2: Isolation Principle

Every task in the plan must answer all three of these questions independently:
1. **What does it do?** — one clear purpose
2. **How is it used?** — what calls it / what does the user do
3. **What does it depend on?** — what must exist before this task

If any of the three can't be answered without reading adjacent tasks, the task boundary needs work. When a file would grow large from a single task, split the task.

Apply this principle while building the task list. Use it as a checklist during self-review.

## Step 3: Build Task List

From the spec's Happy Path + Edge Cases + Success Criteria + design.md user flows and component inventory:

1. Enumerate every discrete implementation action
2. Order them so no task depends on something created later
3. Group parallel tasks (tasks with no dependency on each other) explicitly
4. For Deep tier: identify unknowns and risks — they go in a `## Risks and Unknowns` section

Each task format:
```
### Task N: [Name]
What: [one-sentence purpose]
Used by: [what calls this / user action that triggers it]
Depends on: [Task N-1, or "nothing — first task"]
Files: [create/modify list]
Interfaces:
- Consumes: [what this task uses from earlier tasks — exact signatures, or "nothing"]
- Produces: [what later tasks rely on — exact names and types, or "nothing — terminal task"]

Implementation steps:
1. [specific step]
2. [specific step]
```

## No Placeholders

Every task must contain the actual content Build needs. Never write: "TBD", "similar to Task N" (repeat the content instead — each task must be understandable on its own, per the Isolation Principle in Step 2), "add appropriate error handling" / "handle edge cases" without naming which edge case and how, or references to names/types not defined in any task's `Produces:`.

## Step 4: Comprehension Check (Standard mode only)

Before writing plan.md, open the visual companion browser. Show the implementation sequence as a flow diagram:
- Tasks as nodes (numbered)
- Dependencies as arrows
- Files to be created labeled "NEW", files to be modified labeled "MODIFY"
- Parallel tasks grouped visually

Display: **"Here's the order I'll build this — does the sequence look right?"**

This is the last chance to catch sequencing errors before Build starts.

If user requests reordering or changes: update the task list, show updated diagram. Repeat until confirmed.

**Autopilot mode:** Internal self-review substitutes. Check: does every task's dependencies exist before it runs? Fix any out-of-order tasks silently, continue.

## Step 5: Write plan.md

Write to `docs/dev/<feature>/plan.md`:

```markdown
# [Feature Name] — Implementation Plan
*Branch: feature/xxx · YYYY-MM-DD*

## Files

| File | Action | Purpose |
|------|--------|---------|
| [path] | Create / Modify | [one line] |

## Tasks

### Task 1: [Name]
What: [purpose]
Used by: [consumer]
Depends on: nothing
Files: [list]
Interfaces:
- Consumes: nothing
- Produces: [exact names/types later tasks rely on]

[implementation steps]

### Task 2: [Name]
...

## Edge Cases
| Edge case | Handled in | Approach |
|-----------|-----------|----------|
| [case] | Task N | [how] |

## Out of Scope
- [item not being done in this cycle]
```

**Deep tier only — append:**
```markdown
## Risks and Unknowns
- [risk]: [mitigation or "investigate in Task N"]
```

Scale to complexity: a Micro feature plan might be 10 lines total. A complex Standard plan might be 80 lines.

## Step 6: Artifact Self-Review

After writing plan.md:
1. Is every spec requirement accounted for in a task?
2. Does the sequence make sense — no task depends on something created later?
3. Does every task answer: what / how used / depends on?
4. Are edge cases assigned to specific tasks?
5. Are there any "do X and Y" tasks that should be split?
6. Do the `Consumes:`/`Produces:` names and types line up across tasks? A dependency named differently in the task that produces it versus the task that consumes it is a plan bug — fix it before Build starts.
7. Does any task change a stage skill's stopping, gating, or approval behavior (e.g. a new STOP condition, a new autopilot-blocker, a new hard gate)? If so, check whether `dev:autopilot`'s Step 2 "When autopilot stops" list — or any other skill that documents or depends on that behavior — needs a matching update, and add a task for it if it does. A behavioral change that's only written in one place is a plan gap, even if that one place is correct.
8. For any task whose implementation steps involve a multi-step git/gh sequence with ordering dependencies (commit, push, PR creation, branch switching): mentally trace the exact command sequence end-to-end and confirm each command's prerequisites are actually satisfied by the point it runs — not just that the task's prose reads consistently. Concretely: is the file actually staged before the commit that references it? Is a branch actually pushed to the remote before a command that requires it to exist there (e.g. `gh pr create --base <branch>`)? A task can be internally consistent and still fail on execution — this check catches that class of bug before Build, not after.

Fix any issues inline. No need to re-review after fixing.

## Step 7: Update State + Commit

Update state.json:
- Set `artifacts.plan` to the path
- Record `metrics.stage_timestamps.plan_start` (the value captured at the very top of this skill, before Step 1) and `metrics.stage_timestamps.plan_end` (run `date -u +%Y-%m-%dT%H:%M:%SZ` now)

```bash
git add docs/dev/<feature>/plan.md docs/dev/<feature>/state.json
git commit -m "plan: write implementation plan for <feature>"
```

## Step 8: User Review Gate (Standard mode)

```
Plan written and committed to docs/dev/<feature>/plan.md.

Please review it and let me know if you'd like any changes before we start building.

Safe to /clear now — resume with: /dev:build docs/dev/<feature>/plan.md
[If worktreePath is set: Worktree: <worktreePath>]
```

Wait for explicit user approval.

When approved: update state.json — add `"plan"` to `completed[]`, set `stage` to `"build"`. Commit state update.

**Autopilot mode:** No gate. After self-review, update state and proceed.
