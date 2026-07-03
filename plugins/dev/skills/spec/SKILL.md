---
name: dev:spec
description: "Stage 1 of the /dev workflow. Builds a specification through guided questions with a confidence meter. Creates the feature branch, determines cycle tier, and produces spec.md committed to the branch."
---

# dev:spec — Specification Stage

**Announce:** "I'm using dev:spec to build the feature specification."

## Purpose

Turn a feature idea into a concrete, committed `spec.md` through guided questions. Produces the artifact that every subsequent stage depends on.

This skill supersedes `superpowers:brainstorming` for the duration of the `/dev` session — do not invoke it separately.

**Anti-Pattern: "This Feature Is Simple, Skip the Spec."**
Every feature goes through Spec. Simple features are where unexamined assumptions cause the most wasted Build work. The spec can be short — it must exist.

## Step 1: Read Context

Read these files once at stage start. Work from this reading throughout — do not re-read mid-stage:
- `docs/dev/config.json` — autopilot settings (spec_max_questions, spec_min_confidence)
- `CLAUDE.md` — audience and technical constraints (pre-fills confidence dimensions)

Determine mode from state.json if it exists, or from how the skill was invoked (`/dev:spec` = stage-only, mode from state; invoked by dev orchestrator = standard mode).

**Resume-mid-approval check:** if this feature's `spec.md` already exists and its `state.json.stage` is still `"spec"` (the artifact was written but never approved — e.g. a `/clear` happened while waiting at Step 12), skip straight to Step 12 to re-display it for approval. Do not re-run Steps 2–11 from scratch.

**Nesting detection:** determine whether this Spec invocation is itself happening inside an already-active parent cycle (i.e., the feature about to be specced is a sub-milestone of a cycle already in progress), so Step 4 knows where to write a product plan if needed. Check, in order:
1. Was this invocation given an explicit parent-feature hint (e.g. invoked as part of a parent cycle's own Build/Plan work, with an instruction naming the enclosing feature)? If so, use it.
2. Otherwise, check the current branch: if `git branch --show-current` matches an existing `docs/dev/<parent>/state.json`'s `branch` field, and that parent's `stage` is not `"done"`, this Spec invocation is running inside that parent's branch — treat it as nested under `<parent>`.
3. Otherwise, this is a top-level (non-nested) Spec invocation.

Record the result (a feature name or "none") for use in Steps 4 and 6 — this becomes `state.json.parentFeature` once state.json is created in Step 6.

## Step 2: Scale Detection

Before any questions, assess the scope of the request.

**Product scale** — request describes a full app, platform, or system with multiple independent deliverables (e.g., "build a task manager", "create a portfolio platform", "build the full auth system with multi-tenancy"):
1. Acknowledge: "This is product-scale — let me map it into cycles first."
2. Map the product into sub-features grouped by milestone
3. **Standard mode:** Show the milestone map in the visual companion browser — "Here's how I'd break this down. Does this structure look right?"
4. **Autopilot mode:** Self-review the breakdown for completeness, continue without browser
5. Determine the target file using Step 1's Nesting Detection result: if a parent feature was found, `docs/dev/<parent>/product-plan.md` (nested); otherwise the top-level `docs/dev/product-plan.md`. Record in that file:
   ```markdown
   # [Product Name] — Product Plan
   *Created: YYYY-MM-DD · Cycles completed: 0/N*

   ## Milestone 1: [Name]
   - [ ] feature-name (feature)
   - [ ] decision-name (architecture)

   ## Milestone 2: [Name]
   - [ ] feature-name (feature)
   ```
   If the target file already exists, append as a new milestone rather than overwriting.
6. Commit the product plan — to `main` if top-level (not a feature branch yet); to the parent feature's own branch if nested (that branch is already checked out, per Step 1's nesting-detection check 2):
   ```bash
   git add docs/dev/product-plan.md   # or docs/dev/<parent>/product-plan.md if nested
   git commit -m "docs: record product plan for <product-name>"
   ```
7. Ask: "Which feature should we start with? I'd suggest [Milestone 1 first item]."
8. Proceed with the chosen feature as a normal feature-scale spec

**Feature scale** (default) — single bounded deliverable. Proceed to Step 3.

## Step 3: Cycle Type

Determine from stated intent — ask if unclear:

- **Feature** — intent is to implement: a UI feature, API endpoint, plugin, data migration. Build produces code.
- **Architecture** — intent is to decide or design: choose tech stack, define a data model, write an ADR, establish contracts. Build produces committed documentation.

Record `cycle_type: "feature" | "architecture"` in state.json.

## Step 4: Scope Check + YAGNI Gate

For feature-scale: check if the single request describes multiple independent sub-features (e.g., "add auth, billing, and analytics"). If so, flag it: "This covers N independent things — each needs its own /dev cycle. Which should we start with?" — and, before asking, **write the decomposition to a product plan** rather than letting it live only in conversation memory:

- If the Nesting Detection result from Step 1 found a parent feature: write/update `docs/dev/<parent>/product-plan.md` (nested product plan, scoped to that parent's own sub-milestones).
- Otherwise: write/update the top-level `docs/dev/product-plan.md`.
- Use the same format as Step 2's product-plan template (Milestone headers, `- [ ]` checkbox items). If the target file already exists, append the new items as a new milestone — don't overwrite existing ones.
- **Commit it immediately, before proceeding** — same as Step 2's product-scale path: `git add` the file and `git commit -m "docs: record product plan for <product-name>"` (to `main` if top-level, to the parent's branch if nested — that branch is already checked out). This must happen now, not deferred to Step 6 — if Step 6's worktree offer is accepted, `EnterWorktree` only carries *committed* history into the new worktree; an uncommitted product-plan.md would be silently orphaned in the original directory.
- This is the mechanism that closes the gap where a request's multi-cycle nature only becomes clear through conversation (Step 4) rather than being obvious up front (Step 2) — both paths now produce the same durable, committed artifact.

As questions surface requirements throughout this stage: when a requirement isn't essential to the stated goal, name it explicitly and ask: "Is [requirement] in scope for this cycle?" Default to out.

## Step 5: Tier Detection

Detect complexity tier before any questions. Show the detected tier and allow override.

**Micro** — all signals must be present:
- Intent is clearly bounded: bug fix, copy change, config tweak, single-function change
- No UI changes
- Estimated files touched: ≤ 2
- No cross-cutting concerns

**Deep** — any one signal is sufficient:
- Cycle type is architecture
- Cross-cutting concern: auth, permissions, billing, data model, API contracts
- Estimated files touched: ≥ 10
- Change affects behavior across multiple existing features

**Standard:** everything else.

Display: "This looks like a [Micro/Standard/Deep]-tier change — I'll use a [shorter/standard/extended] flow. Override?"

Set `skipped[]` in state.json immediately based on tier:
- Micro: `skipped: ["shape", "plan"]`
- Standard/Deep: `skipped: []`

## Step 6: Create Feature Branch

Create the branch before asking any questions. All artifacts commit to this branch.

**Worktree offer:** first, check whether this feature is an item in *any* product plan — the top-level `docs/dev/product-plan.md`, or (per Step 1's Nesting Detection) a nested `docs/dev/<parent>/product-plan.md`. If it is:
- **Standard mode:** offer isolation — "This is part of a multi-cycle plan — want me to isolate it in its own worktree? (protects it from other work happening in this directory while it's in progress)" and wait for consent.
- **Autopilot mode:** auto-accept without asking, per `dev:autopilot`'s no-gate principle (see `dev:autopilot` Step 2) — it's the beneficial, non-destructive default.
- If accepted: call `EnterWorktree`. If this cycle is top-level (no parent), branch fresh from `origin/main` as the tool defaults to — nothing further needed. If this cycle is nested (Step 1 found a parent feature), the new worktree's branch must instead point at the parent feature's own branch HEAD: read the parent's `state.json.branch` field, then — immediately after `EnterWorktree` creates the new worktree and before any other work happens in it — run `git reset --hard <parent-branch>` inside the new worktree. (`reset --hard`, not `rebase`: the new branch was just created with zero unique commits, so there's nothing to replay — a hard reset onto the parent branch is the simplest unambiguous way to make the new branch start from the parent's current tip.)
- If `EnterWorktree` is unavailable in this harness, or declined: fall through to the plain-branch behavior below unchanged. `worktreePath` stays `null` either way if not used.

```bash
git checkout -b feature/<feature-name>
# For Micro: git checkout -b fix/<feature-name>
# For architecture cycles: git checkout -b arch/<feature-name>
```

(Skip this plain `git checkout -b` if a worktree was created above — `EnterWorktree` already created and switched to the branch.)

Feature name: derive from the stated intent, kebab-case, 2-4 words.

Get the exact timestamp before writing state.json: run `date -u +%Y-%m-%dT%H:%M:%SZ` and use that value for both `startedAt` and `metrics.stage_timestamps.spec_start` below — don't estimate or leave the placeholder text in place.

Initialize `docs/dev/<feature-name>/state.json`:
```json
{
  "version": "1.0",
  "feature": "<feature-name>",
  "branch": "feature/<feature-name>",
  "mode": "standard",
  "stage": "spec",
  "completed": [],
  "skipped": [],
  "startedAt": "<ISO timestamp>",
  "artifacts": {
    "spec": "docs/dev/<feature-name>/spec.md",
    "design": null,
    "plan": null,
    "validation": null,
    "pr_url": null,
    "pr_number": null
  },
  "validate": {
    "loops_run": 0,
    "loops_max": 3,
    "p1_open": [], "p2_open": [], "p3_open": [], "nits_open": []
  },
  "confidence": {
    "final_score": 0,
    "final_level": "Low",
    "dimensions": {
      "intent": false, "scope": false, "success_criteria": false,
      "happy_path": false, "edge_cases": false, "out_of_scope": false,
      "ui_needed": false, "technical_constraints": false,
      "audience": false, "dependencies": false
    },
    "auto_filled": []
  },
  "cycle_type": "feature",
  "tier": "standard",
  "product_plan": null,
  "linear_issue": null,
  "parentFeature": null,
  "worktreePath": null,
  "metrics": {
    "spec_questions_asked": 0,
    "visual_screens_shown": 0,
    "files_read_in_build": 0,
    "stage_timestamps": {
      "spec_start": "<output of date -u +%Y-%m-%dT%H:%M:%SZ, run just now>"
    }
  }
}
```

If CLAUDE.md was read in Step 1 and contains audience/technical info, pre-fill those confidence dimensions as true and set initial score accordingly (audience = 5%, technical_constraints = 5%).

Set `parentFeature` to the feature name found by Step 1's Nesting Detection (or `null` if top-level). Set `worktreePath` to the worktree's path if the Worktree Offer above created one (or `null` if working in-place).

Commit the initial state.json:
```bash
git add docs/dev/<feature-name>/state.json
git commit -m "spec: initialize /dev session for <feature-name>"
```

## Step 7: Guided Questioning

Ask questions one at a time to fill the confidence dimensions. Show the confidence meter after each answer.

**Confidence dimensions and weights:**
| Dimension | Weight |
|-----------|--------|
| Intent | 20% |
| Scope | 15% |
| Success criteria | 15% |
| Happy path | 10% |
| Edge cases | 10% |
| Out of scope | 10% |
| UI needed | 5% |
| Technical constraints | 5% |
| Audience | 5% |
| Dependencies | 5% |

**Confidence levels:**
- 🔴 Low (0–39%): Keep going
- 🟡 Sufficient (40–64%): Risky to proceed
- 🟢 High (65–84%): Default proceed threshold
- ✅ Ready (85–100%): Ideal

**Display after each answer:**
```
Confidence: 58% — Sufficient ↑ from 43%
Still needed for High: edge cases, out of scope, success criteria
```

**Questioning rules:**
- One question per message — never two questions in one turn
- Prefer multiple choice when options can be enumerated
- Ask about the most impactful unscored dimension first
- **Increment `metrics.spec_questions_asked` in state.json after each question — do this before moving on.** This is a state.json edit, not a mental note: after sending a question, edit state.json and bump the number before you send the next one. If you can't point to the Edit call that changed it, it hasn't happened.

**Proceed thresholds:**
- Standard mode: continue until High (65%) reached. Offer early exit at Sufficient (40%): "We're at Sufficient (40%) — enough to proceed, though some things may surface later. Continue or keep going?"
- Autopilot mode: target Ready (85%). Cap at `spec_max_questions`. If cap reached and still below Ready AND confidence hasn't increased in last 2 questions → auto-fill remaining unscored dimensions via inference, record in `confidence.auto_filled[]`. If still below High (65%) after auto-fill → stop and request human input.
- Deep tier: threshold is Ready (85%); lower thresholds not available for override.

**Micro tier:** Only ask about intent and scope. Skip remaining questions. Write spec with Implementation Note section instead of separate plan.md.

## Step 8: Comprehension Check (Standard mode only)

After confidence threshold is reached, before writing spec.md:

Open the visual companion browser. Show a structured summary:

**Feature-scale:**
- Feature name, cycle type, tier, one-line intent
- Scope boundary: what's in / what's out
- Happy path (numbered steps)
- Success criteria
- Confidence snapshot (score, level, any auto-filled dimensions)

**Product-scale (decomposition):**
- Proposed milestone structure with feature list
- Cycle types noted
- Suggested first cycle highlighted

Display: **"Here's what I understood — does this match your intent?"**

This is an understanding check, not a design review. User confirms or corrects the AI's interpretation before it gets locked into an artifact.

**Autopilot mode:** Skipped. Re-read the full Q&A, check for contradictions internally, continue.

## Step 9: Write spec.md

Write to `docs/dev/<feature-name>/spec.md`. Scale length to complexity — a simple feature may need five lines per section; a complex one may need a paragraph.

**Required sections (always present):**

```markdown
# [Feature Name]
*Branch: feature/xxx · Confidence: 87% — Ready · YYYY-MM-DD*
*Cycle type: feature | architecture · Tier: micro | standard | deep*

## Intent
What problem does this solve, and why now?

## Scope
What's in this cycle.

## Out of Scope
What we're explicitly not doing now.

## Success Criteria
Observable outcomes. How we know it's done.

## Happy Path
1. [trigger]
2. [step]
3. [success state]
```

**Contextual sections (include when non-trivial):**

```markdown
## Edge Cases
Error states, limits, failure modes worth designing for.

## Audience
Who uses this. (Usually one line from CLAUDE.md / init config.)

## Technical Constraints
Performance requirements, breaking change risks, platform limits.

## Dependencies
What this blocks on or relies on.

## UI Needed
Yes / No. Determines whether Shape stage runs.
```

**Micro tier only — append instead of a separate plan.md:**

```markdown
## Implementation Note
Files to touch: [file1, file2]
Approach: [one paragraph describing the change]
```

**Footer (always):**

```markdown
---
*Auto-filled dimensions: [list any dimensions inferred rather than answered directly, or "none"]*
```

## Step 10: Artifact Self-Review

After writing spec.md, check with fresh eyes:
1. **Placeholder scan** — any "TBD", "TODO", incomplete sections? Fix them inline.
2. **Internal consistency** — do any sections contradict each other?
3. **Scope check** — focused enough for a single build cycle, or needs decomposition?
4. **Ambiguity check** — can any requirement be interpreted two ways? Pick one, state it explicitly.

Fix issues inline. No need to re-review after fixing.

## Step 11: Update State + Commit

Update `docs/dev/<feature-name>/state.json`:
- Set `confidence.final_score` and `confidence.final_level`
- Set all dimension booleans correctly
- Set `confidence.auto_filled` to list of auto-filled dimensions (or empty array)
- Set `stage` to `"spec"` (stays as current stage until spec is approved)
- Set `artifacts.spec` to the path
- Record `metrics.stage_timestamps.spec_end` — run `date -u +%Y-%m-%dT%H:%M:%SZ` and write the output in; `spec_start` was already set in Step 6

```bash
git add docs/dev/<feature-name>/spec.md docs/dev/<feature-name>/state.json
git commit -m "spec: write spec for <feature-name> (confidence: XX%)"
```

## Step 12: User Review Gate (Standard mode)

Determine the next-stage command the same way as before (Shape if UI needed, Plan if no-ui, Build if Micro tier), and its exact argument (`docs/dev/<feature-name>/spec.md`).

```
Spec written and committed to docs/dev/<feature-name>/spec.md.

Please review it and let me know if you'd like any changes before we continue.

Safe to /clear now — resume with: /dev:<next-stage> docs/dev/<feature-name>/spec.md
[If worktreePath is set: Worktree: <worktreePath>]
```

Wait for explicit user approval. If changes requested: update spec.md, re-run Step 10, re-commit, re-display gate.

When approved: update state.json — add `"spec"` to `completed[]`, set `stage` to next stage. Commit the state update.

**Autopilot mode:** No gate. After self-review, update state and notify orchestrator to proceed.
