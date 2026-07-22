---
name: dev:build
description: "Stage 4 of the /dev workflow. Implements the plan. Feature cycles produce TDD code committed per task. Architecture cycles produce ADR documents. Requires plan.md (or spec.md Implementation Note for Micro tier)."
---

# dev:build — Build Stage

**Announce:** "I'm using dev:build to implement the plan."

**First action, before anything else:** run `date -u +%Y-%m-%dT%H:%M:%SZ` and hold onto the output — this is `build_start`, recorded in Step 6. Capturing it now, before any other work, keeps it accurate to when the stage actually began.

## Purpose

Implement the plan. Produce committed code (feature cycle) or committed decision documents (architecture cycle) on the feature branch.

This skill supersedes `superpowers:test-driven-development` and `superpowers:systematic-debugging` for the duration of the `/dev` session — do not invoke them separately.

**Anti-Pattern: "The Plan Needs Updates, I'll Just Do It While Building."**
If implementation reveals the plan needs changes, stop, update plan.md, commit the update, then continue. Plan and code stay in sync.

## Resolve the working directory (do this first)

This stage never relies on the shell's current directory or current branch. Compute the
primary checkout, then locate this cycle's directory:

    PRIMARY=$(dirname "$(git rev-parse --git-common-dir)")

Find the cycle directory — first hit wins — by testing for `docs/dev/<feature>/state.json` under:
1. `$PRIMARY/.dev-worktrees/<feature>/`   → active worktree cycle
2. `$PRIMARY/`                            → legacy in-place cycle (worktreePath null)

Set `WORKDIR` to whichever matched. For the rest of this stage: run every git command as
`git -C "$WORKDIR" …`, and read/write all artifacts under `$WORKDIR/docs/dev/<feature>/…`.
Never `cd`, never assume the current branch.

## Step 1: Artifact Gate

May be invoked with an artifact-path argument (`plan.md` path, or `spec.md` for Micro tier). If given, derive `<feature>` from the path instead of requiring it already be known from conversation context. If no argument is given, fall back to today's behavior. **Validate before using:** the path must match `docs/dev/<feature>/<artifact>.md` with `<feature>` matching `^[a-z0-9][a-z0-9-]*$` and containing no `..` segments — matching the kebab-case convention feature names are always created with (see `dev:spec`'s "derive from the stated intent, kebab-case"). If it doesn't match, treat the argument as invalid and fall back to today's behavior rather than using the parsed value.

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

**When a Test Fails Unexpectedly:**
If a test fails that you didn't expect to fail — not the TDD red-phase, but an existing test breaking, or a new test failing for a reason other than "not implemented yet" — stop before patching. Read the full error and stack trace. Check what changed since it last passed (`git -C "$WORKDIR" diff`, recent commits). Form one specific hypothesis for the cause. Make the smallest change that tests that hypothesis. If it doesn't resolve it, form a new hypothesis rather than stacking a second change on top of the first.

If 3 hypotheses fail: stop — this is a genuine blocker, not a symptom to keep patching. In standard mode, surface the 3 failed hypotheses to the user and wait for guidance; do not attempt a 4th fix unprompted. If the user's guidance points to the plan or approach being wrong rather than the code, follow the Backtrack Trigger (Step 4) to correct plan.md before continuing. **Autopilot mode:** this is one of autopilot's genuine-blocker stop conditions (see `dev:autopilot` Step 2) — stop and surface the failed hypotheses rather than attempting a 4th fix.

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
git -C "$WORKDIR" add docs/dev/<feature>/<decision>.md
git -C "$WORKDIR" commit -m "arch: document <decision title>"
```

Build is complete when all plan tasks are checked off and each major decision has a committed document.

## Step 3: Targeted Adjacent Improvements

When working in existing code, you will encounter related problems. Apply this rule:

**Fix what affects this feature. Don't ignore it. Don't refactor the world.**

Specifically: if a file you're modifying has grown too large, a broken abstraction you need to build on, or unclear boundaries in code you're touching — fix it as part of this build. Update plan.md with the additional change. Commit the improvement separately (one commit for the targeted fix, then continue with the original task).

If the improvement is larger than can be handled within this cycle, don't do it now — and don't write it into plan.md, which `dev:done` Step 7 deletes, and no stage reads that section before it goes. Instead, apply **the carrying-cost test** from `../../references/tech-debt.md`:

- **Qualifies** → append an entry at the end of the `## To Record` section — immediately before `## To Close`, never at end-of-file — in `$WORKDIR/docs/dev/<feature>/debt-pending.md`, creating the buffer from the contract's template if it doesn't exist. Set `**Files:**` to the files the improvement would touch — you know them precisely at this point, and `dev:spec`'s cross-check keys its matching on that field. Tag it `*Source: dev:build · <feature>*`.
- **Doesn't qualify** → drop it. A one-off local cleanup isn't worth carrying.

Escape any Markdown heading in text you copy into the entry — indent by two spaces or fence it, per the contract's field rules. The buffer is parsed by heading.

Include the buffer in the commit for the task that surfaced the finding — don't add a commit of its own.

**Mode rule:** this is unconditional and self-applied. It runs identically in standard and autopilot mode, is never gated on user confirmation, and writes no `state.json` counter.

Only the *deferred* branch changes destination. In-scope adjacent fixes are still fixed inline and still update plan.md, exactly as above.

## Step 4: Backtrack Trigger

If during Build you discover that plan.md is wrong or insufficient:
1. Stop the current task
2. Update plan.md with the correction
3. Commit: `plan: update task N — [what changed and why]`
4. In standard mode: update state.json — remove "plan" from `completed[]`, set `stage` to "plan", commit state
5. Continue building from the corrected plan
6. Notify user: "Updated plan.md (task N needed [correction]). Continuing from updated plan."

## Step 5: Track Files Read

**Each time you read a file to understand context (not to write it), update state.json immediately: increment `metrics.files_read_in_build`.** Do this inline as you work — don't batch it at the end. Concretely: right after each Read call that's for context (not for a file you're about to edit), make the counter-bump Edit to state.json before your next tool call — treat it as part of the same step as the read, not a separate cleanup task.

## Step 6: Update State on Completion

When all plan tasks are done and tests pass:

Update state.json:
- Add `"build"` to `completed[]`
- Set `stage` to `"validate"`
- Record `metrics.stage_timestamps.build_start` (the value captured at the very top of this skill, before Step 1) and `metrics.stage_timestamps.build_end` (run `date -u +%Y-%m-%dT%H:%M:%SZ` now)

```bash
git -C "$WORKDIR" add docs/dev/<feature>/state.json
git -C "$WORKDIR" commit -m "build: complete <feature> implementation"
```

In standard mode, notify:
```
Build complete. All plan tasks done, tests passing.
Ready for Validate.

Safe to /clear now — resume with: /dev:validate docs/dev/<feature>/plan.md
[If worktreePath is set: Worktree: <worktreePath>]
```

**Autopilot mode:** Update state and proceed automatically.
