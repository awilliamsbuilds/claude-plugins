---
name: dev:build
description: "Stage 4 of the /dev workflow. Implements the plan. Feature cycles produce TDD code committed per task. Architecture cycles produce ADR documents. Requires plan.md (or spec.md Implementation Note for Micro tier)."
---

# dev:build — Build Stage

**Announce:** "I'm using dev:build to implement the plan."

## Purpose

Implement the plan. Produce committed code (feature cycle) or committed decision documents (architecture cycle) on the feature branch.

**Anti-Pattern: "The Plan Needs Updates, I'll Just Do It While Building."**
If implementation reveals the plan needs changes, stop, update plan.md, commit the update, then continue. Plan and code stay in sync.

## Step 1: Artifact Gate

<HARD-GATE>
Read state.json. If `tier == "micro"`, look for `spec.md` and its `## Implementation Note` section — that is the plan. If `artifacts.plan` is null AND tier is not "micro", STOP:

"Build requires plan.md. Run /dev:plan first."
</HARD-GATE>

Read once at stage start, work from this throughout:
- `docs/dev/<feature>/state.json` — cycle_type, tier
- `docs/dev/<feature>/plan.md` — full task list (or spec.md Implementation Note for Micro)
- `docs/dev/<feature>/spec.md` — success criteria and scope

## Step 2: Cycle Type Behavior

### Feature Cycle

Implement each plan task in order. For each task:

1. **Write tests first** — before implementation, write the failing test that describes the expected behavior. Run it to confirm it fails.
2. **Implement** — write minimal code to make the test pass.
3. **Run tests** — confirm they pass.
4. **Commit atomically** — one commit per plan task. Commit message: `[task N]: [task name]`

Each commit references its plan task number so the branch history tells the full implementation story.

Build is complete when:
- Branch has commits ahead of main
- All plan tasks are checked off
- Tests pass

**When to deviate from TDD:**
- Configuration files, migrations, and scaffolding: test after, not before
- Third-party integrations where test setup is disproportionately complex: comment the tradeoff in the code

### Architecture Cycle

Produce decision documents committed to the feature branch. Documents live at `docs/dev/<feature>/` during the cycle; moved to `docs/decisions/` at Done.

ADR format:
```markdown
# [Decision Title]
*Status: accepted · Date: YYYY-MM-DD*

## Context
What situation required this decision.

## Decision
What was decided, with brief rationale.

## Consequences
What this enables, what it forecloses, what it requires next.
```

Each plan task corresponds to one decision document. Commit per document:
```bash
git add docs/dev/<feature>/<decision>.md
git commit -m "arch: document <decision title>"
```

Build is complete when all plan tasks are checked off and each major decision has a committed document.

## Step 3: Targeted Adjacent Improvements

When working in existing code, you will encounter related problems. Apply this rule:

**Fix what affects this feature. Don't ignore it. Don't refactor the world.**

Specifically: if a file you're modifying has grown too large, a broken abstraction you need to build on, or unclear boundaries in code you're touching — fix it as part of this build. Update plan.md with the additional change. Commit the improvement separately (one commit for the targeted fix, then continue with the original task).

If the improvement is larger than can be handled within this cycle, note it in plan.md under a `## Deferred Improvements` section. Don't do it now.

## Step 4: Backtrack Trigger

If during Build you discover that plan.md is wrong or insufficient:
1. Stop the current task
2. Update plan.md with the correction
3. Commit: `plan: update task N — [what changed and why]`
4. In standard mode: update state.json — remove "plan" from `completed[]`, set `stage` to "plan", commit state
5. Continue building from the corrected plan
6. Notify user: "Updated plan.md (task N needed [correction]). Continuing from updated plan."

## Step 5: Track Files Read

**Each time you read a file to understand context (not to write it), update state.json immediately: increment `metrics.files_read_in_build`.** Do this inline as you work — don't batch it at the end.

## Step 6: Update State on Completion

When all plan tasks are done and tests pass:

Update state.json:
- Add `"build"` to `completed[]`
- Set `stage` to `"validate"`
- Record `stage_timestamps.build_end`

```bash
git add docs/dev/<feature>/state.json
git commit -m "build: complete <feature> implementation"
```

In standard mode, notify:
```
Build complete. All plan tasks done, tests passing.
Ready for Validate. Run /dev:validate (or /dev to continue the flow).
```

**Autopilot mode:** Update state and proceed automatically.
