# Autopilot Handoff at Pre-Execution Gates — Implementation Plan
*Branch: feature/autopilot-handoff · 2026-08-02*

## Files

| File | Action | Purpose |
|------|--------|---------|
| plugins/dev/skills/build/SKILL.md | Modify | Absolute `PRIMARY` (T1) |
| plugins/dev/skills/debt/SKILL.md | Modify | Absolute `PRIMARY` (T1) |
| plugins/dev/skills/dev/SKILL.md | Modify | Absolute `PRIMARY` (T1) · handoff-aware sequencing (T5) · Invocation Reference rows (T9) |
| plugins/dev/skills/done/SKILL.md | Modify | Absolute `PRIMARY` (T1) · decision-log handoff line (T7) |
| plugins/dev/skills/fix/SKILL.md | Modify | Absolute `PRIMARY` (T1) |
| plugins/dev/skills/plan/SKILL.md | Modify | Absolute `PRIMARY` (T1) |
| plugins/dev/skills/pr/SKILL.md | Modify | Absolute `PRIMARY` (T1) |
| plugins/dev/skills/reflect/SKILL.md | Modify | Absolute `PRIMARY` (T1) · marker-aware Step 4 (T6) |
| plugins/dev/skills/shape/SKILL.md | Modify | Absolute `PRIMARY` (T1) · handoff offer, mirror (T4) |
| plugins/dev/skills/spec/SKILL.md | Modify | Absolute `PRIMARY` (T1) · handoff offer, canonical (T3) |
| plugins/dev/skills/validate/SKILL.md | Modify | Absolute `PRIMARY` (T1) |
| plugins/dev/skills/autopilot/SKILL.md | Modify | Artifact-path arg + `WORKDIR` block (T2) · grounding cross-note (T8) |
| plugins/dev/skills/start/SKILL.md | Modify | Workflow-reference rows for the new invocation form (T9) |

`plugins/dev/skills/migrate-tracker/SKILL.md` is **not** in scope for T1 — it already derives
`PRIMARY` absolute (Step 1) and is the source of the canonical snippet.

## Tasks

### Task 1: Absolute `PRIMARY` derivation across the eleven stage skills
What: Replace the relative `PRIMARY=$(dirname "$(git rev-parse --git-common-dir)")` one-liner with an absolute, failure-checked derivation in every `/dev` skill that computes it.
Used by: Every stage skill's working-directory block; Task 2 copies the resulting snippet verbatim into `dev:autopilot`.
Depends on: nothing — first task.
Files: modify `plugins/dev/skills/{build,debt,dev,done,fix,plan,pr,reflect,shape,spec,validate}/SKILL.md`
Interfaces:
- Consumes: nothing
- Produces: **the canonical `PRIMARY` snippet** — the exact two-line bash form below, referred to by that name in Task 2
- Shared procedure: `PRIMARY` derivation. This task is the **canonical** implementation. Task 2 introduces a twelfth instance of the same procedure in `dev:autopilot` and is a **mirror** of this task.

Implementation steps:
1. Adopt this exact form as the canonical snippet (it is the form already proven in `plugins/dev/skills/migrate-tracker/SKILL.md` Step 1):
   ```bash
   GIT_COMMON=$(git rev-parse --git-common-dir) || { echo "Not a git repository."; exit 1; }
   PRIMARY=$(cd "$(dirname "$GIT_COMMON")" && pwd)
   ```
2. Replace the single indented line at `build/SKILL.md:26`, `debt/SKILL.md:41`, `done/SKILL.md:15`, `plan/SKILL.md:15`, `pr/SKILL.md:15`, `reflect/SKILL.md:15`, `shape/SKILL.md:15`, `validate/SKILL.md:15` with the two-line snippet, preserving each file's existing indentation so it stays inside the "Resolve the working directory" block.
3. `fix/SKILL.md:87` — the line sits inside an existing fenced ```bash block; replace it in place with both lines.
4. `spec/SKILL.md:141` — the line sits inside the Step 6 worktree-creation block, immediately above `git -C "$PRIMARY" fetch origin`. Replace it with both lines; leave the three `git -C "$PRIMARY" …` commands that follow untouched.
5. `dev/SKILL.md:39` — this site is **prose**, not a code block: `Compute \`PRIMARY=$(dirname …)\`, then scan for state.json in both locations…`. Rewrite it as a short lead-in sentence followed by a fenced ```bash block containing the two-line snippet, then keep the existing "then scan for state.json in both locations" sentence and the two glob paths exactly as they are.
6. Add one sentence of rationale at **one** site only — `plan/SKILL.md`, since Plan is where the printed resume command is first exercised — reading: *From a primary checkout `git rev-parse --git-common-dir` returns a relative path (`.git` at the repo root), which `dirname` reduces to `.`; the `cd` in a command-substitution subshell absolutizes it without changing the caller's directory.* Do not repeat this paragraph in the other ten files — a one-line snippet is self-evident once explained once, and eleven copies drift.
7. Verify with `grep -rn 'PRIMARY=' plugins/dev/skills/*/SKILL.md` — every hit must be the `cd …&& pwd` form. This is the check that satisfies Success Criterion 7.

### Task 2: `dev:autopilot` Step 1 — artifact-path argument and explicit `WORKDIR` resolution
What: Give `dev:autopilot` the artifact-path invocation form and a working-directory resolution block, so a resume command pasted into a cleared session finds the right cycle worktree.
Used by: The handoff command printed by Task 3 and Task 4; also `/dev:autopilot docs/dev/<feature>/<artifact>.md` typed by hand.
Depends on: Task 1 (supplies the canonical `PRIMARY` snippet this task copies).
Files: modify `plugins/dev/skills/autopilot/SKILL.md`
Interfaces:
- Consumes: the canonical `PRIMARY` snippet from Task 1
- Produces: **the `/dev:autopilot <artifact-path>` contract** — `/dev:autopilot docs/dev/<feature>/<artifact>.md` resolves `<feature>` from the path and runs the cycle from its worktree. Tasks 3 and 4 print commands in exactly this form.
- Shared procedure: `PRIMARY` derivation / `WORKDIR` resolution — **mirror of Task 1**. Task 1's canonical branch structure, restated in full: derive `GIT_COMMON` with the `||` failure branch that exits on "Not a git repository"; derive `PRIMARY` by `cd "$(dirname "$GIT_COMMON")" && pwd` inside a command-substitution subshell; then a two-branch first-hit-wins search for `docs/dev/<feature>/state.json` — branch 1 `$PRIMARY/.dev-worktrees/<feature>/` (active worktree cycle), branch 2 `$PRIMARY/` (legacy in-place cycle, `worktreePath` null) — setting `WORKDIR` to whichever matched. Neither branch is guarded by `worktreePath`; that field is a set/null predicate only, never the resolver.

Implementation steps:
1. Insert a new `## Resolve the working directory (do this first)` section **after the `**When autopilot stops:**` paragraph (line 14) and immediately before `## Step 1: Initialize` (line 16)** — that paragraph belongs to `## Purpose` and must stay under it, not be orphaned beneath the new heading. Match the wording and structure of the block in `plan/SKILL.md:10–23` — including the closing "run every git command as `git -C "$WORKDIR" …`" and "Never `cd`, never assume the current branch" sentences.
2. In that section, use the Task 1 canonical snippet for `PRIMARY`, then the two-location first-hit-wins test described in the `Shared procedure:` line above.
3. Add argument parsing to Step 1, ahead of the existing "Check for in-progress session" text: *May be invoked with an artifact-path argument (`spec.md` or `design.md` path). If given, derive `<feature>` from the path instead of scanning. **Validate before using:** the path must match `docs/dev/<feature>/<artifact>.md` with `<feature>` matching `^[a-z0-9][a-z0-9-]*$` and containing no `..` segments. If it doesn't match, treat the argument as invalid and fall back to the scan.* Use the wording already in `plan/SKILL.md` Step 1 so the eleven stage skills and the orchestrator state one rule.
4. Keep the existing no-argument behavior intact: no argument → scan for an in-progress session → if none, begin from Spec. The artifact-path form is additive.
5. **Source `tier` and `stage` from the resolved `state.json`, not from the request.** Step 3's tier-detection line currently reads "The autopilot detects tier from the initial request" (`autopilot/SKILL.md:79`) — on a pasted resume command there *is* no initial request, so a micro cycle would otherwise have no way to select its `Spec → Build → Validate → PR → Done` sequence. Add to Step 1: on the artifact-path form (and on any resumed session), read `tier` and `stage` from the resolved `state.json` and use them to pick the remaining-stage list; amend the Step 3 line to "detects tier from the initial request, or reads `tier` from `state.json` when resuming." This is what makes Success Criterion 4 hold.
6. Leave the existing announcement and `Set mode to "autopilot" in state.json` line where they are — the mode flip stays autopilot's job, per spec §Technical Constraints.
7. Fix the dangling citation at line 54: `any git it runs uses git -C "$WORKDIR" per the canonical WORKDIR resolution` currently points at nothing. Repoint it to the section added in step 1 above ("per the working-directory resolution at the top of this skill"). Do **not** create a shared canonical block — that is spec §Out of Scope.
8. Add `/dev:autopilot docs/dev/<feature>/<artifact>.md` as a fourth bullet in the `## Invocation` list (currently lines 115–119), described as "resume a gated cycle in autopilot from the named artifact, deriving the feature from the path."

### Task 3: Handoff offer at `dev:spec` Step 13 (canonical)
What: Render an autopilot handoff offer at the Spec gate when the next stage is an execution stage, and on `yes` write the handoff marker, print the resume instructions, and end the session.
Used by: A user approving a spec in a no-UI standard/deep cycle, or in a micro cycle.
Depends on: Task 2 (the printed command must resolve, or the offer is a broken promise).
Files: modify `plugins/dev/skills/spec/SKILL.md`
Interfaces:
- Consumes: the `/dev:autopilot <artifact-path>` contract from Task 2
- Produces: **`state.json.handoff_at`** — top-level string key, values `"spec"` or `"shape"`, **absent** when no handoff was accepted. It records the *gate stage at which the cycle handed off*; every stage after it ran unattended. Read by Tasks 5, 6, 7. Also produces **the handoff offer procedure**, mirrored by Task 4.
- State keys: `handoff_at` `(writes: standard; absent in autopilot)` — autopilot has no gates, so the offer never renders there and the key is never written; every reader must treat absence as today's behavior.
- Shared procedure: the handoff offer. This task is the **canonical** implementation (it carries the next-stage condition and the micro branch). Task 4 is a mirror.

Implementation steps:
1. Step 13 already opens by determining the next-stage command (Shape / Plan / Build). Reuse that determination — do not recompute it — as the offer's condition.
2. Add the offer's branch structure immediately after the gate block, before "Wait for explicit user approval":
   - **Branch A — next stage is Shape.** No offer. The gate renders byte-identically to today. State the reason inline: a pre-execution gate is one whose next stage is the cycle's first *execution* stage, and Shape is definition, not execution.
   - **Branch B — next stage is Plan (`"shape" ∈ skipped[]`) or Build (micro tier).** Append one line to the gate block, below the existing `Safe to /clear now` / `Worktree:` lines:
     ```
     The stages from here are execution — Plan, Build, Validate, PR, Done.
     Want to run them unattended in autopilot? (yes / no)
     ```
3. Specify the **`yes`** path as an ordered sequence:
   a. Perform the normal approval state update first — add `"spec"` to `completed[]`, set `stage` to the next stage, carry any pending `challenge.*` writes from Step 12a — exactly as the existing "When approved" paragraph specifies.
   b. Additionally set `handoff_at` to `"spec"` in the same state write.
   c. Commit both in one commit: `git -C "$WORKDIR" add docs/dev/<feature-name>/spec.md docs/dev/<feature-name>/state.json` then `git -C "$WORKDIR" commit -m "spec: approve and hand off to autopilot for <feature-name>"`. Staging `spec.md` alongside `state.json` is harmless when spec.md is unchanged and correct when Path A or B revised it.
   d. Print the handoff block:
     ```
     Handing off to autopilot at Spec. Remaining stages run unattended:
     <Plan → Build → Validate → PR → Done, or Build → Validate → PR → Done for micro>

     Run /clear, then paste:

       /dev:autopilot docs/dev/<feature-name>/spec.md

     [If worktreePath is set: Worktree: <worktreePath>]
     The command resolves the worktree itself — run it from anywhere in the repo, no cd needed.
     ```
   e. **End the session.** Do not invoke the next stage, do not return to `dev:dev`. State this explicitly — it is spec §Scope 2 and the only reason no second code path exists.
4. Specify the **`no`** path: proceed through the existing approval flow with no state write beyond the normal approval, no extra prompt, and no change to the next-stage command (Success Criterion 5).
5. Add one sentence recording idempotency: the offer holds no state of its own, so when Path A or Path B re-displays the gate it re-renders unchanged.
6. Add one sentence to the existing `**Autopilot mode:** No gate.` paragraph: the offer is unreachable in autopilot by construction, so no mode check guards it and `handoff_at` is never written there.

### Task 4: Handoff offer at `dev:shape` Step 11 (mirror of Task 3)
What: Render the same autopilot handoff offer at the Shape gate and, on `yes`, write the marker, print the resume instructions, and end the session.
Used by: A user approving a design in a UI standard/deep cycle — the spec's Happy Path route.
Depends on: Task 3 (canonical procedure and the `handoff_at` key definition).
Files: modify `plugins/dev/skills/shape/SKILL.md`
Interfaces:
- Consumes: `state.json.handoff_at` (writes value `"shape"`); the `/dev:autopilot <artifact-path>` contract from Task 2
- Produces: nothing new — writes the key Task 3 defines
- State keys: `handoff_at` `(writes: standard; absent in autopilot)` — same key, second write site; no new key introduced
- Shared procedure: the handoff offer — **mirror of Task 3**.

Implementation steps:
1. **Restate Task 3's branch structure in full, as it applies here** — do not write "same as Task 3":
   - **Branch A — next stage is Shape.** *Unreachable from this gate.* Shape's next stage is always Plan, so the no-offer branch never fires here. Say so in one line rather than omitting it, so a reader comparing the two sites sees the branch was considered, not lost.
   - **Branch B — next stage is Plan.** Always taken. The offer renders on every Shape approval.
2. **Placement and acceptance are two different things here — keep them separate.** In the real file the gate block is `shape/SKILL.md:221–228` and the Design Status confirmation is line 230, *after* it. So:
   - **Print** the offer inside the Step 11 gate block, below the existing `Safe to /clear now` / `Worktree:` lines:
     ```
     The stages from here are execution — Plan, Build, Validate, PR, Done.
     Want to run them unattended in autopilot? (yes / no)
     ```
   - **Do not accept** the `yes` path until Design Status has been confirmed and recorded in design.md. If the user answers `yes` before that confirmation has happened, ask the Design Status question first, record the answer, and only then run step 3.
   This is the one place the mirror diverges from Task 3's canonical: Spec's gate has no analogous post-gate confirmation, so Task 3 needs no such ordering rule. State that divergence in one line at this site so a reader comparing the two gates sees it is deliberate. A `yes` that ended the session before Design Status was settled would hand Plan a design with no locked/directional marker — the exact thing Step 11's existing confirmation exists to prevent.
3. `yes` path, ordered:
   a. Normal approval state update — add `"shape"` to `completed[]`, set `stage` to `"plan"`, and ensure the confirmed Design Status is already recorded in design.md.
   b. Additionally set `handoff_at` to `"shape"`.
   c. Commit both: `git -C "$WORKDIR" add docs/dev/<feature>/design.md docs/dev/<feature>/state.json` then `git -C "$WORKDIR" commit -m "shape: approve and hand off to autopilot for <feature>"`.
   d. Print the handoff block:
     ```
     Handing off to autopilot at Shape. Remaining stages run unattended:
     Plan → Build → Validate → PR → Done

     Run /clear, then paste:

       /dev:autopilot docs/dev/<feature>/design.md

     [If worktreePath is set: Worktree: <worktreePath>]
     The command resolves the worktree itself — run it from anywhere in the repo, no cd needed.
     ```
   e. **End the session.** Do not invoke Plan, do not return to `dev:dev`.
4. `no` path: the existing approval flow, unchanged — no state write beyond the normal approval, no extra prompt.
5. Add the idempotency sentence: the offer holds no state, so a re-displayed gate after requested changes re-renders it unchanged.
6. Add one sentence to `**Autopilot mode:** No gate.`: unreachable by construction, `handoff_at` never written there.

### Task 5: `dev:dev` Step 5 — handoff-aware stage sequencing
What: Stop the orchestrator from printing its `Continue? (yes / skip / stop)` prompt after a stage whose gate accepted a handoff.
Used by: `dev:dev` after Spec or Shape completes in an orchestrated standard-mode cycle.
Depends on: Task 3 (defines `handoff_at` and its values).
Files: modify `plugins/dev/skills/dev/SKILL.md`
Interfaces:
- Consumes: `state.json.handoff_at` (read only)
- Produces: nothing — terminal for this branch
- State keys: none introduced

Implementation steps:
1. In Step 5, ahead of the "**Display the next stage and offer:**" block, insert a precondition: after the completed stage's state write, re-read `state.json`. If `handoff_at` is set, the stage skill's own gate has already printed the handoff instructions and ended the session — **exit cleanly without printing the Continue prompt and without invoking the next stage.**
2. State why in one line: the stage skills own their gates, so `dev:dev` must not append a "Continue?" to a gate that just said the session ends. Absent `handoff_at`, Step 5 behaves exactly as today.
3. Leave Step 5a (Jump to Stage), Step 6, and the stage-sequence-by-tier lists untouched — a handed-off cycle is still fully resumable through the ordinary `/dev` resume path (spec §Edge Cases, "User answers yes but never runs the command").

### Task 6: `dev:reflect` — run the user-observation turn on a handed-off cycle
What: Make Step 4's user-observation turn fire when the cycle was handed off, even though `mode` reads `"autopilot"` by then.
Used by: `dev:done` Step 6, which invokes `dev:reflect` at the end of every cycle.
Depends on: Task 3 (defines `handoff_at`).
Files: modify `plugins/dev/skills/reflect/SKILL.md`
Interfaces:
- Consumes: `state.json.handoff_at` (read only)
- Produces: nothing — terminal task
- State keys: none introduced

Implementation steps:
1. Step 1 "Extract key metrics from state.json" — add a bullet: `handoff_at` — the gate stage at which the cycle handed off to autopilot, or absent if it ran in a single mode throughout. **An absent key means no handoff** (including every cycle predating this feature) — read it as "no handoff," not as an error, matching how the list already handles a missing `challenge` block.
2. Step 4's heading and opening condition currently read "(standard mode)". Change the condition to: run this step when `mode` is `"standard"` **or** when `handoff_at` is set. Update the heading to `## Step 4: Invite User Observations (standard mode, or any handed-off cycle)`.
3. Change the closing `**Autopilot mode:** skipped` paragraph to `**Autopilot mode (no handoff):** skipped` and add one sentence: a handed-off cycle had a human at its definition stages, so the observation this step exists to capture — friction the counters cannot see — is available and worth asking for; only a cycle that was autopilot from the start skips it.
4. Do not touch Step 6's skill-update gate — a user observation raised here already flows into it unchanged.

### Task 7: `dev:done` Step 5 — record the handoff in the decision log
What: Add one conditional line to the decision-log template naming the handoff stage, so a mixed-mode cycle is distinguishable from a pure-autopilot one.
Used by: Every completed cycle's decision log at `docs/decisions/YYYY-MM-DD-<feature>.md`.
Depends on: Task 3 (defines `handoff_at` and its values).
Files: modify `plugins/dev/skills/done/SKILL.md`
Interfaces:
- Consumes: `state.json.handoff_at` (read only)
- Produces: nothing — terminal task
- State keys: none introduced

Implementation steps:
1. In the Step 5 template, directly below the `*YYYY-MM-DD · Branch: feature/<name> · PR #N*` header line, add: `[If handoff_at is set: *Handed off to autopilot at <stage>* — where <stage> is the capitalized marker value, Spec or Shape.]`
2. State the absence rule explicitly next to the template: when `handoff_at` is absent the template is **byte-identical to today** — no blank line, no placeholder, no "n/a". This is spec §Scope 4 and the property that keeps existing decision logs comparable.
3. Leave the rest of Step 5 — the `git add` / `commit` / `push_integration` sequence and every other section of the template — unchanged.

### Task 8: `dev:autopilot` Step 2 — grounding-gate cross-note
What: Add a one-line cross-reference from autopilot's spec-questioning rules to the `dev:spec` grounding gate, so autopilot's own text stops reading as though inference can clear the path to proceed.
Used by: A reader of `dev:autopilot` Step 2 trying to understand what auto-fill can and cannot do.
Depends on: Task 2 (same file; sequencing avoids overlapping edits to `autopilot/SKILL.md`).
Files: modify `plugins/dev/skills/autopilot/SKILL.md`
Interfaces:
- Consumes: nothing
- Produces: nothing — terminal task
- State keys: none introduced

Implementation steps:
1. In the `**Spec questioning is capped.**` rule (currently lines 45–48), append one line below the auto-fill bullets: *Auto-fill does not satisfy `dev:spec` Step 7's grounding gate — per Step 8, confidence cannot cross the proceed threshold while a load-bearing as-is claim is unverified, regardless of the weighted score. An unverified claim surfaces here through the existing "confidence too low even after auto-fill" STOP.*
2. Keep it to that one cross-note. Restating the gate's rules here would create a second copy that drifts from `spec/SKILL.md` — the failure `debt-autopilot-grounding-gate` was filed against in the first place.
3. This satisfies the item's *Done looks like* exactly; the close-intent is already buffered in `docs/dev/autopilot-handoff/debt-pending.md` `## To Close` and executes at `dev:done` Step 6a. No plan task closes it.

### Task 9: Document the handoff and the autopilot artifact-path form in the reference surfaces
What: Add the `/dev:autopilot docs/dev/<feature>/<artifact>.md` invocation form and the handoff offer to the two skills whose job is to tell the user how `/dev` is invoked.
Used by: A user reading `dev:dev`'s Invocation Reference or running `/dev:start` to remember the workflow.
Depends on: Task 2 (the invocation form) and Task 5 (which edits a different section of the same `dev/SKILL.md`, so sequencing after it keeps the two edits from overlapping).
Files: modify `plugins/dev/skills/dev/SKILL.md`, `plugins/dev/skills/start/SKILL.md`
Interfaces:
- Consumes: the `/dev:autopilot <artifact-path>` contract from Task 2; `state.json.handoff_at` by name only (documented, not read)
- Produces: nothing — terminal task
- State keys: none introduced

Implementation steps:
1. `dev/SKILL.md` Invocation Reference (the table at lines 159–173): the existing `/dev:<stage> docs/dev/<feature>/<artifact>.md` row explicitly scopes itself to "every `dev:<stage>` skill" and so does **not** cover the orchestrator. Add a row directly below it: `/dev:autopilot docs/dev/<feature>/<artifact>.md` → "Resume a gated cycle in autopilot from the named artifact — what the handoff offer at the Spec and Shape gates prints. Derives `<feature>` from the path."
2. `start/SKILL.md` line 69 currently reads `` `dev:autopilot` — no-gate full-cycle runner ``. Extend it to name the resume form: "— no-gate full-cycle runner; also accepts an artifact path to resume a gated cycle mid-flight."
3. `start/SKILL.md` line 53 describes `dev:autopilot` as "alternative to the gated flow above." Add half a sentence: it is also the *continuation* of that flow, offered at the Spec and Shape gates once definition is settled.
4. Do not restate the offer's mechanics or the marker's semantics in either file — these are reference surfaces. One clause each, pointing at behavior Tasks 3 and 4 own.

## Edge Cases

| Edge case | Handled in | Approach |
|-----------|-----------|----------|
| Spec gate in a UI cycle (next stage is Shape) | Task 3 | Branch A — no offer; gate renders byte-identically to today |
| Spec gate re-displayed after a revision (Path A or B) | Task 3 step 5 | Offer holds no state; re-display re-renders it unchanged |
| Shape gate — "next stage is Shape" branch | Task 4 step 1 | Unreachable here; stated in one line rather than dropped |
| User answers yes but never runs the command | Task 5 step 3 | Marker records intent only; cycle stays resumable via the ordinary `/dev` path. `mode` is still flipped by `dev:autopilot` Step 1 on actual invocation |
| User pastes the command without clearing first | Task 2 | Works identically; only the context benefit is lost. No guard |
| Cycle already in autopilot mode | Tasks 3 step 6, 4 step 6 | Unreachable by construction — autopilot has no gates. No mode check at the offer site |
| Legacy in-place cycle (`worktreePath: null`) | Task 2 step 2 | `WORKDIR` resolution branch 2 falls back to `$PRIMARY` |
| Standalone stage invocation (`/dev:shape docs/dev/<f>/spec.md`) | Tasks 3, 4 | Offer lives in the stage skill's own gate, not in `dev:dev` Step 5, so it renders outside the orchestrator |
| Orchestrated cycle — `dev:dev` would prompt Continue after a handoff | Task 5 | Step 5 precondition reads `handoff_at` and exits cleanly |
| Cycle predating this feature (`handoff_at` absent) | Tasks 6 step 1, 7 step 2 | Absence means "no handoff" — today's behavior, not an error |
| `git rev-parse` run outside a repository | Task 1 step 1 | `||` failure branch exits rather than letting `dirname ""` → `.` silently make `$PRIMARY` the cwd |

## Out of Scope

- Extracting a shared canonical WORKDIR block that all skills reference (spec §Out of Scope). Task 2 inlines correct resolution at its own site; the dangling citation at `autopilot/SKILL.md:54` is repointed, not resolved into a new shared artifact.
- Making `dev:reflect` Step 4 unconditional for all modes.
- Any handoff in the reverse direction (autopilot → gated).
- An offer at the Validate or PR gates.
- `debt-state-advancement-commit-durability` and `debt-spec-grounding-citation-unverified` — not in this cycle's edit path.
- Component Registry updates — `dev:done` Step 4 owns those, not a plan task.
