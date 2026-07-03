---
name: dev:autopilot
description: "No-gate orchestrator for the /dev workflow. Chains all stages end-to-end without approval gates or browser interaction. Self-review substitutes for comprehension checks. Spec questions capped at spec_max_questions, then auto-fills. Stops only on true blockers. Invoked via /dev:autopilot or /dev auto."
---

# dev:autopilot — No-Gate Orchestrator

**Announce:** "I'm using dev:autopilot to run the full /dev workflow without approval gates."

## Purpose

Chain all applicable stages end-to-end without stopping for user approval. Trade interactivity for speed. Use when you trust the spec enough to let the AI run the full cycle.

**When autopilot stops:** Only on genuine blockers — PR can't be merged, P1/P2 issues remain after loop limit, confidence is too low even after auto-fill, or 3 root-cause hypotheses fail for an unexpected test failure during Build (see `dev:build`'s "When a Test Fails Unexpectedly"). Everything else runs through.

## Step 1: Initialize

Check for `docs/dev/config.json`. If missing, run dev:init in autopilot mode (no questions — infer everything from codebase scan).

Check for in-progress session. If found:

```
/dev session in progress: <feature-name>
<stage-status-line>

Resuming from <current-stage> in autopilot mode.
```

If no in-progress session: begin from Spec.

Set mode to `"autopilot"` in state.json.

## Step 2: Autopilot Behavioral Rules

These rules apply throughout all stages. They override the standard-mode behaviors described in each stage skill:

**No approval gates.** After each stage completes: read that the artifact exists and is non-empty (sanity check), then move immediately to the next stage. Do not ask "Continue?"

**No browser, no visual companion.** At every point where standard mode would open the visual companion browser, substitute a self-review instead:
- Re-read the accumulated inputs for that decision point
- Check for contradictions or ambiguities
- Make a decision, record it in the artifact with "Design decision:" prefix
- Continue

**Spec questioning is capped.** Ask questions one at a time up to `spec_max_questions` (from config.json, default 10). After the cap:
- If Ready (85%) is not reached AND confidence hasn't increased in the last 2 questions → auto-fill remaining unscored dimensions via inference
- Record each auto-filled dimension in `confidence.auto_filled[]` with the inferred value
- If confidence is still below High (65%) after auto-fill → STOP: "Confidence too low to proceed without human input. Current score: XX%. Please clarify: [top 2 unscored dimensions]."

**Shape alternatives: auto-select.** Present 2-3 alternatives internally, select the recommended one, note the selection and reasoning in design.md under "Design decision."

**Worktree offer: auto-accept.** When `dev:spec` Step 6 would offer worktree isolation (cycle is part of a product plan), auto-accept without asking — beneficial, non-destructive default.

**Backtrack is silent.** When a later stage discovers an earlier artifact gap:
1. Fix the earlier artifact
2. Commit the fix with message: `autopilot: backtrack — update <spec|plan> for <reason>`
3. Update state.json accordingly
4. Continue — do not pause

**Validate: extended auto-fix.** After the loop limit, attempt one additional auto-fix pass. If P1/P2 remain → STOP: surface the issues and require human input.

## Step 3: Stage Execution

Execute stages in sequence for the applicable tier:

**Tier detection:** same as dev:spec (see stage skill). The autopilot detects tier from the initial request.

**Micro tier:** Spec → Build → Validate → PR → Done
**Standard/Deep + no-ui:** Spec → Plan → Build → Validate → PR → Done
**Standard/Deep + UI:** Spec → Shape → Plan → Build → Validate → PR → Done

After each stage:

```
[Stage] complete → [brief one-line summary of what was produced]
Proceeding to [Next Stage]...
```

This gives visibility without gates.

## Step 4: Report on Completion

When Done completes (or when autopilot stops on a blocker):

```
/dev autopilot complete: <feature-name>

Stages run:
  Spec ✓   [confidence: XX%]
  Shape ✓  [or "Shape skipped (no-ui)"]
  Plan ✓
  Build ✓
  Validate ✓ [N loops]
  PR ✓       [PR URL]
  Done ✓

Retrospective appended to docs/decisions/YYYY-MM-DD-<feature>.md
```

If stopped on a blocker, show the blocker and what's needed to continue.

## Invocation

- `/dev:autopilot` — start or resume in autopilot mode
- `/dev:autopilot no-ui` — autopilot, skip Shape
- The main `/dev` skill redirects `/dev auto` to this skill
