# Autopilot Handoff at Pre-Execution Gates — Implementation Plan
*Branch: feature/autopilot-handoff · 2026-08-02*

## Files

| File | Action | Purpose |
|------|--------|---------|
| plugins/dev/skills/build/SKILL.md | Modify | Absolute `PRIMARY` (T1) |
| plugins/dev/skills/debt/SKILL.md | Modify | Absolute `PRIMARY` (T1) |
| plugins/dev/skills/dev/SKILL.md | Modify | Absolute `PRIMARY` (T1) · Invocation Reference row (T8) |
| plugins/dev/skills/done/SKILL.md | Modify | Absolute `PRIMARY` (T1) · decision-log handoff line (T7) |
| plugins/dev/skills/fix/SKILL.md | Modify | Absolute `PRIMARY` (T1) |
| plugins/dev/skills/plan/SKILL.md | Modify | Absolute `PRIMARY` (T1) |
| plugins/dev/skills/pr/SKILL.md | Modify | Absolute `PRIMARY` (T1) |
| plugins/dev/skills/reflect/SKILL.md | Modify | Absolute `PRIMARY` (T1) · marker-aware Step 4 (T6) |
| plugins/dev/skills/shape/SKILL.md | Modify | Absolute `PRIMARY` (T1) · printed offer, mirror (T5) |
| plugins/dev/skills/spec/SKILL.md | Modify | Absolute `PRIMARY` (T1) · printed offer, canonical (T4) |
| plugins/dev/skills/validate/SKILL.md | Modify | Absolute `PRIMARY` (T1) |
| plugins/dev/skills/autopilot/SKILL.md | Modify | Artifact-path arg + `WORKDIR` + `tier`/`stage` read (T2) · marker write (T3) · grounding cross-note (T9) |
| plugins/dev/skills/start/SKILL.md | Modify | Workflow-reference rows for the new invocation form (T8) |

`plugins/dev/skills/migrate-tracker/SKILL.md` is **not** in scope for T1 — it already derives
`PRIMARY` absolute (Step 1) and is the source of the canonical snippet.

**No task touches `dev:dev`'s Step 5 sequencing.** The offer is static text in a gate that otherwise
behaves exactly as today, so the orchestrator needs no handoff awareness. That is the design property
spec §Scope 2 is protecting; if a task ever needs to teach `dev:dev` about handoffs, the offer has
stopped being a printed alternative and the spec has drifted.

## Tasks

### Task 1: Absolute `PRIMARY` derivation across the eleven stage skills
What: Replace the relative `PRIMARY=$(dirname "$(git rev-parse --git-common-dir)")` one-liner with an absolute, failure-checked derivation in every `/dev` skill that computes it.
Used by: Every stage skill's working-directory block; Task 2 copies the resulting snippet verbatim into `dev:autopilot`.
Depends on: nothing — first task.
Files: modify `plugins/dev/skills/{build,debt,dev,done,fix,plan,pr,reflect,shape,spec,validate}/SKILL.md`
Interfaces:
- Consumes: nothing
- Produces: **the canonical `PRIMARY` snippet** — the exact two-line bash form below, referred to by that name in Task 2
- State keys: none introduced
- Shared procedure: `PRIMARY` derivation. This task is the **canonical** implementation. Task 2 introduces a twelfth instance in `dev:autopilot` and is a **mirror** of it.

Implementation steps:
1. Adopt this exact form as the canonical snippet (already proven in `plugins/dev/skills/migrate-tracker/SKILL.md` Step 1):
   ```bash
   GIT_COMMON=$(git rev-parse --git-common-dir) || { echo "Not a git repository."; exit 1; }
   PRIMARY=$(cd "$(dirname "$GIT_COMMON")" && pwd)
   ```
2. Replace the single indented line at `build/SKILL.md:26`, `debt/SKILL.md:41`, `done/SKILL.md:15`, `plan/SKILL.md:15`, `pr/SKILL.md:15`, `reflect/SKILL.md:15`, `shape/SKILL.md:15`, `validate/SKILL.md:15` with the two-line snippet, preserving each file's existing indentation so it stays inside the "Resolve the working directory" block.
3. `fix/SKILL.md:87` — the line sits inside an existing fenced ```bash block; replace it in place with both lines.
4. `spec/SKILL.md:141` — the line sits inside the Step 6 worktree-creation block, immediately above `git -C "$PRIMARY" fetch origin`. Replace it with both lines; leave the three `git -C "$PRIMARY" …` commands that follow untouched.
5. `dev/SKILL.md:39` — this site is **prose**, not a code block: `Compute \`PRIMARY=$(dirname …)\`, then scan for state.json in both locations…`. Rewrite as a short lead-in sentence, then a fenced ```bash block with the two-line snippet, then keep the existing "then scan for state.json in both locations" sentence and both glob paths exactly as they are.
6. Add one sentence of rationale at **one** site only — `plan/SKILL.md`, since Plan is where the printed resume command is first exercised: *From a primary checkout `git rev-parse --git-common-dir` returns a relative path (`.git` at the repo root), which `dirname` reduces to `.`; the `cd` in a command-substitution subshell absolutizes it without changing the caller's directory.* Do not repeat this paragraph in the other ten files — eleven copies drift.
7. Verify with `grep -rn 'PRIMARY=' plugins/dev/skills/*/SKILL.md` — every hit must be the `cd …&& pwd` form. This check satisfies Success Criterion 7.

### Task 2: `dev:autopilot` Step 1 — artifact-path argument, `WORKDIR` resolution, `tier`/`stage` read
What: Give `dev:autopilot` the artifact-path invocation form, a working-directory resolution block, and a `state.json` read for `tier`/`stage`, so a resume command pasted into a cleared session finds the right worktree and runs the right stage sequence.
Used by: The commands printed by Tasks 4 and 5; also `/dev:autopilot docs/dev/<feature>/<artifact>.md` typed by hand.
Depends on: Task 1 (supplies the canonical `PRIMARY` snippet this task copies).
Files: modify `plugins/dev/skills/autopilot/SKILL.md`
Interfaces:
- Consumes: the canonical `PRIMARY` snippet from Task 1
- Produces: **the `/dev:autopilot <artifact-path>` contract** — `/dev:autopilot docs/dev/<feature>/<artifact>.md` resolves `<feature>` from the path, resolves `WORKDIR`, and reads `tier`/`stage` from the resolved `state.json`. Tasks 4, 5 and 8 print or document commands in exactly this form. Also produces **the resolved `state.json` read point** that Task 3 hooks the marker write onto.
- State keys: none introduced (Task 3 adds the marker at this task's read point)
- Shared procedure: `PRIMARY` derivation / `WORKDIR` resolution — **mirror of Task 1**. Task 1's canonical branch structure, restated in full: derive `GIT_COMMON` with the `||` failure branch that exits on "Not a git repository"; derive `PRIMARY` by `cd "$(dirname "$GIT_COMMON")" && pwd` inside a command-substitution subshell; then a two-branch first-hit-wins search for `docs/dev/<feature>/state.json` — branch 1 `$PRIMARY/.dev-worktrees/<feature>/` (active worktree cycle), branch 2 `$PRIMARY/` (legacy in-place cycle, `worktreePath` null) — setting `WORKDIR` to whichever matched. Neither branch is guarded by `worktreePath`; that field is a set/null predicate only, never the resolver.

Implementation steps:
1. Insert a new `## Resolve the working directory (do this first)` section **after the `**When autopilot stops:**` paragraph (line 14) and immediately before `## Step 1: Initialize` (line 16)** — that paragraph belongs to `## Purpose` and must stay under it, not be orphaned beneath the new heading. Match the wording and structure of `plan/SKILL.md:10–23`, including the closing "run every git command as `git -C "$WORKDIR" …`" and "Never `cd`, never assume the current branch" sentences.
2. In that section, use the Task 1 canonical snippet for `PRIMARY`, then the two-location first-hit-wins test described in the `Shared procedure:` line above.
3. Add argument parsing to Step 1, ahead of the existing "Check for in-progress session" text: *May be invoked with an artifact-path argument (`spec.md` or `design.md` path). If given, derive `<feature>` from the path instead of scanning. **Validate before using:** the path must match `docs/dev/<feature>/<artifact>.md` with `<feature>` matching `^[a-z0-9][a-z0-9-]*$` and containing no `..` segments. If it doesn't match, treat the argument as invalid and fall back to the scan.* Use the wording already in `plan/SKILL.md` Step 1 so the stage skills and the orchestrator state one rule.
4. Keep the existing no-argument behavior intact: no argument → scan for an in-progress session → if none, begin from Spec. The artifact-path form is additive.
5. **Source `tier` and `stage` from the resolved `state.json`, not from the request.** Step 3's tier line currently reads "The autopilot detects tier from the initial request" (`autopilot/SKILL.md:79`) — a pasted resume command carries no initial request, so a micro cycle would have no way to select its `Spec → Build → Validate → PR → Done` sequence. Add to Step 1: on the artifact-path form (and on any resumed session), read `tier` and `stage` from the resolved `state.json` and use them to pick the remaining-stage list. Amend the Step 3 line to "detects tier from the initial request, or reads `tier` from `state.json` when resuming." This is what makes Success Criterion 4 hold.
6. Fix the dangling citation at line 54: `any git it runs uses git -C "$WORKDIR" per the canonical WORKDIR resolution` currently points at nothing. Repoint it to the section added in step 1 ("per the working-directory resolution at the top of this skill"). Do **not** create a shared canonical block — spec §Out of Scope.
7. Add `/dev:autopilot docs/dev/<feature>/<artifact>.md` as a fourth bullet in the `## Invocation` list (currently lines 115–119): "resume a gated cycle in autopilot from the named artifact, deriving the feature from the path."

### Task 3: `dev:autopilot` Step 1 — write the handoff marker on the mode flip
What: Record `handoff_at` at the one moment a handoff is observable — when autopilot flips a cycle whose `mode` is `"standard"` over to `"autopilot"`.
Used by: `dev:reflect` Step 4 (Task 6) and `dev:done` Step 5 (Task 7).
Depends on: Task 2 (supplies the resolved `state.json` read point and the `stage` value the marker records).
Files: modify `plugins/dev/skills/autopilot/SKILL.md`
Interfaces:
- Consumes: the resolved `state.json` read point from Task 2 (`mode`, `stage`)
- Produces: **`state.json.handoff_at`** — top-level string key holding the stage name the cycle was resumed at (`"spec"`, `"shape"`, or any later stage on a manual handoff). **Absent** when no `"standard"` → `"autopilot"` flip occurred. Read by Tasks 6 and 7.
- State keys: `handoff_at` `(writes: autopilot-only)` — the only write site is this task. There is no standard-mode writer: the gates in Tasks 4 and 5 print text and write nothing, so no standard-side default is needed and none of the autopilot-correct values depend on a gate write.

Implementation steps:
1. Locate Step 1's existing `Set mode to "autopilot" in state.json` line (currently line 31). Replace it with a two-branch rule, stated explicitly so the marker cannot drift from the flip it records:
   - **`mode` is currently `"standard"`** — this is a handoff. Set `handoff_at` to the value of `stage` **as read before the flip** (the stage this invocation is resuming at), then set `mode` to `"autopilot"`. Both writes go in the same `state.json` update.
   - **`mode` is already `"autopilot"`, or there is no prior session** (a fresh cycle starting from Spec) — set `mode` to `"autopilot"` as today and **do not write `handoff_at` at all.** Absent is the value; do not write `null`, `false`, or an empty string. This is what makes Success Criterion 8 hold.
2. Order matters and must be stated: read `stage` **before** flipping `mode`, or the marker records the stage autopilot advances to rather than the one it took over at.
3. Note that the marker is deliberately not restricted to `"spec"`/`"shape"`. No offer is printed at the Validate or PR gates, but a user who types `/dev:autopilot` there has still handed off, and recording that stage accurately is correct for criterion 6.
4. State the read contract for downstream consumers in one line here, since this is the key's definition site: an absent `handoff_at` means "no handoff," including on every cycle that predates this feature — never an error.
5. Do not touch the announcement block (lines 22–27) or `Resuming from <current-stage> in autopilot mode` — the existing text already reports the resume; the marker records it durably.

### Task 4: Printed autopilot offer at `dev:spec` Step 13 (canonical)
What: Add a second resume command to the Spec gate's exit block, offering the rest of the cycle in autopilot — but only when the next stage is an execution stage.
Used by: A user approving a spec in a no-UI standard/deep cycle, or in a micro cycle.
Depends on: Task 2 (the printed command must resolve cold, or the offer is a broken promise). Not dependent on Task 3 — this task writes no state.
Files: modify `plugins/dev/skills/spec/SKILL.md`
Interfaces:
- Consumes: the `/dev:autopilot <artifact-path>` contract from Task 2
- Produces: **the printed-offer procedure**, mirrored by Task 5
- State keys: none — the gate writes nothing for this feature. The existing approval writes in Step 13 are untouched.
- Shared procedure: the printed offer. This task is the **canonical** implementation (it carries the next-stage condition and the micro branch). Task 5 is a mirror.

Implementation steps:
1. Step 13 already opens by determining the next-stage command (Shape / Plan / Build). Reuse that determination — do not recompute it — as the offer's condition.
2. Add the branch structure governing whether the offer prints:
   - **Branch A — next stage is Shape.** No offer; the gate block renders byte-identically to today. State the reason inline: a pre-execution gate is one whose next stage is the cycle's first *execution* stage, and Shape is definition, not execution.
   - **Branch B — next stage is Plan (`"shape" ∈ skipped[]`) or Build (micro tier).** Print the offer.
3. Under Branch B, extend the gate block's existing exit lines — currently `Safe to /clear now — resume with: /dev:<next-stage> docs/dev/<feature-name>/spec.md` followed by the conditional `Worktree:` line — so they read:
   ```
   Safe to /clear now — resume with: /dev:<next-stage> docs/dev/<feature-name>/spec.md
   Or hand the rest of the cycle to autopilot — <Plan → Build → Validate → PR → Done, or
   Build → Validate → PR → Done for micro> run unattended: /clear, then
     /dev:autopilot docs/dev/<feature-name>/spec.md
   [If worktreePath is set: Worktree: <worktreePath>]
   ```
   Keep the `Worktree:` line last so it applies to both commands.
4. Add one line stating that the command resolves the worktree itself — it runs from anywhere in the repo, no `cd` required. This is Success Criterion 2's user-facing promise.
5. **State what this task deliberately does not do**, since it is the property the whole design rests on: the offer is static text. It adds no prompt, consumes no user answer, writes no state, and does not end the session. The approval flow below it — "Wait for explicit user approval," Path A, Path B, and the `When approved` state write — is untouched. A user who wants the gated flow simply ignores the extra line (Success Criterion 5).
6. Because the offer holds no state, the gate re-displays after a Path A or Path B revision are idempotent — the same text re-renders. Say so in one line.
7. Add one sentence to the existing `**Autopilot mode:** No gate.` paragraph: the gate does not render in autopilot, so the offer never prints there.

### Task 5: Printed autopilot offer at `dev:shape` Step 11 (mirror of Task 4)
What: Add the same second resume command to the Shape gate's exit block.
Used by: A user approving a design in a UI standard/deep cycle — the spec's Happy Path route.
Depends on: Task 4 (canonical procedure).
Files: modify `plugins/dev/skills/shape/SKILL.md`
Interfaces:
- Consumes: the `/dev:autopilot <artifact-path>` contract from Task 2; the printed-offer procedure from Task 4
- Produces: nothing — terminal task
- State keys: none — the gate writes nothing for this feature
- Shared procedure: the printed offer — **mirror of Task 4**.

Implementation steps:
1. **Restate Task 4's branch structure in full as it applies here** — do not write "same as Task 4":
   - **Branch A — next stage is Shape.** *Unreachable from this gate.* Shape's next stage is always Plan, so the no-offer branch never fires here. Say so in one line rather than omitting it, so a reader comparing the two sites sees the branch was considered, not lost.
   - **Branch B — next stage is Plan.** Always taken; the offer prints on every Shape gate render.
2. Extend the Step 11 gate block's exit lines (currently `shape/SKILL.md:226–227`) to read:
   ```
   Safe to /clear now — resume with: /dev:plan docs/dev/<feature>/design.md
   Or hand the rest of the cycle to autopilot — Plan → Build → Validate → PR → Done run
   unattended: /clear, then
     /dev:autopilot docs/dev/<feature>/design.md
   [If worktreePath is set: Worktree: <worktreePath>]
   ```
3. Add the same "resolves the worktree itself, no `cd` needed" line as Task 4 step 4.
4. **Restate the does-not-do clause in full:** static text, no prompt, no consumed answer, no state write, no session end. The Design Status confirmation at line 230 and the `Wait for explicit user approval` / `When approved` flow below it are untouched and still run in their existing order. Note explicitly why this matters here and not at Spec: Shape's gate is followed by a Design Status confirmation, and because the offer cannot be "accepted," there is no path by which it can pre-empt that confirmation.
5. Add the idempotency line: re-displays after requested changes re-render the same text.
6. Add one sentence to `**Autopilot mode:** No gate.`: the gate does not render in autopilot, so the offer never prints there.

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
1. Step 1 "Extract key metrics from state.json" — add a bullet: `handoff_at` — the stage at which a gated cycle was handed off to autopilot, or absent if the cycle ran in one mode throughout. **An absent key means no handoff** (including every cycle predating this feature) — read it as "no handoff," not as an error, matching how the list already handles a missing `challenge` block.
2. Step 4's heading and opening condition currently read "(standard mode)". Change the condition to: run this step when `mode` is `"standard"` **or** when `handoff_at` is set. Update the heading to `## Step 4: Invite User Observations (standard mode, or any handed-off cycle)`.
3. Change the closing `**Autopilot mode:** skipped` paragraph to `**Autopilot mode (no handoff):** skipped` and add one sentence: a handed-off cycle had a human at its definition stages, so the friction this step exists to capture is available and worth asking for; only a cycle that was autopilot from the start skips it. This pairing is what Success Criteria 6 and 8 test against each other.
4. Do not touch Step 6's skill-update gate — a user observation raised here already flows into it unchanged.

### Task 7: `dev:done` Step 5 — record the handoff in the decision log
What: Add one conditional line to the decision-log template naming the handoff stage, so a mixed-mode cycle is distinguishable from a pure-autopilot one.
Used by: Every completed cycle's decision log at `docs/decisions/YYYY-MM-DD-<feature>.md`.
Depends on: Task 3 (defines `handoff_at`).
Files: modify `plugins/dev/skills/done/SKILL.md`
Interfaces:
- Consumes: `state.json.handoff_at` (read only)
- Produces: nothing — terminal task
- State keys: none introduced

Implementation steps:
1. In the Step 5 template, directly below the `*YYYY-MM-DD · Branch: feature/<name> · PR #N*` header line, add: `[If handoff_at is set: *Handed off to autopilot at <stage>* — where <stage> is the capitalized marker value, e.g. Spec or Shape.]`
2. State the absence rule explicitly beside the template: when `handoff_at` is absent the template is **byte-identical to today** — no blank line, no placeholder, no "n/a". This is spec §Scope 4 and Success Criterion 8, and it is what keeps existing decision logs comparable.
3. Leave the rest of Step 5 unchanged — the `git add` / `commit` / `push_integration` sequence and every other template section.

### Task 8: Document the new invocation form in the reference surfaces
What: Add the `/dev:autopilot docs/dev/<feature>/<artifact>.md` form to the two skills whose job is to tell the user how `/dev` is invoked.
Used by: A user reading `dev:dev`'s Invocation Reference or running `/dev:start`.
Depends on: Task 2 (the invocation form).
Files: modify `plugins/dev/skills/dev/SKILL.md`, `plugins/dev/skills/start/SKILL.md`
Interfaces:
- Consumes: the `/dev:autopilot <artifact-path>` contract from Task 2
- Produces: nothing — terminal task
- State keys: none introduced

Implementation steps:
1. `dev/SKILL.md` Invocation Reference (table at lines 159–173): the existing `/dev:<stage> docs/dev/<feature>/<artifact>.md` row explicitly scopes itself to "every `dev:<stage>` skill" and so does **not** cover the orchestrator. Add a row directly below it: `/dev:autopilot docs/dev/<feature>/<artifact>.md` → "Resume a gated cycle in autopilot from the named artifact — the alternative command printed at the Spec and Shape gates. Derives `<feature>` from the path."
2. `start/SKILL.md` line 69 currently reads `` `dev:autopilot` — no-gate full-cycle runner ``. Extend it: "— no-gate full-cycle runner; also accepts an artifact path to take over a gated cycle mid-flight."
3. `start/SKILL.md` line 53 describes `dev:autopilot` as "alternative to the gated flow above." Add half a sentence: it is also the *continuation* of that flow, printed as an option at the Spec and Shape gates once definition is settled.
4. Do not restate the offer's mechanics or the marker's semantics in either file — these are reference surfaces. One clause each, pointing at behavior Tasks 3–5 own.

### Task 9: `dev:autopilot` Step 2 — grounding-gate cross-note
What: Add a one-line cross-reference from autopilot's spec-questioning rules to the `dev:spec` grounding gate, so autopilot's own text stops reading as though inference can clear the path to proceed.
Used by: A reader of `dev:autopilot` Step 2 trying to understand what auto-fill can and cannot do.
Depends on: Tasks 2 and 3 (same file; sequencing after them keeps the three `autopilot/SKILL.md` edits from overlapping).
Files: modify `plugins/dev/skills/autopilot/SKILL.md`
Interfaces:
- Consumes: nothing
- Produces: nothing — terminal task
- State keys: none introduced

Implementation steps:
1. In the `**Spec questioning is capped.**` rule (currently lines 45–48), append one line below the auto-fill bullets: *Auto-fill does not satisfy `dev:spec` Step 7's grounding gate — per Step 8, confidence cannot cross the proceed threshold while a load-bearing as-is claim is unverified, regardless of the weighted score. An unverified claim surfaces here through the existing "confidence too low even after auto-fill" STOP.*
2. Keep it to that one cross-note. Restating the gate's rules here would create a second copy that drifts from `spec/SKILL.md` — the failure `debt-autopilot-grounding-gate` was filed against in the first place.
3. This satisfies the item's *Done looks like* exactly. The close-intent is already buffered in `docs/dev/autopilot-handoff/debt-pending.md` `## To Close` and executes at `dev:done` Step 6a — no plan task closes it.

## Edge Cases

| Edge case | Handled in | Approach |
|-----------|-----------|----------|
| Spec gate in a UI cycle (next stage is Shape) | Task 4 step 2 | Branch A — no offer; gate renders byte-identically to today |
| Spec gate re-displayed after a revision (Path A or B) | Task 4 step 6 | Offer is static text holding no state; re-display re-renders it unchanged |
| Shape gate — "next stage is Shape" branch | Task 5 step 1 | Unreachable here; stated in one line rather than dropped |
| Offer pre-empting Shape's Design Status confirmation | Task 5 step 4 | Impossible by construction — the offer can't be "accepted", so the confirmation and approval flow below it still run in order |
| User never runs the offered command | Tasks 4 step 5, 5 step 4 | Nothing was recorded; the cycle continues down the gated path with no residue and no stale marker |
| User pastes the command without clearing first | Task 2 | Works identically; only the context benefit is lost. No guard |
| Cycle already in autopilot mode | Tasks 3 step 1, 4 step 7, 5 step 6 | Gate never renders, so the offer never prints; no `"standard"` → `"autopilot"` flip occurs, so no marker is written |
| Autopilot cycle from a cold start (no prior session) | Task 3 step 1 | Second branch — `mode` set as today, `handoff_at` never written. Success Criterion 8 |
| Handoff at a stage past Shape (manual `/dev:autopilot` at Validate/PR) | Task 3 step 3 | No offer printed there, but the flip is real, so the marker records that stage accurately |
| Micro cycle resumed by a pasted command | Task 2 step 5 | `tier` read from the resolved `state.json`, not inferred from an absent initial request |
| Legacy in-place cycle (`worktreePath: null`) | Task 2 step 2 | `WORKDIR` resolution branch 2 falls back to `$PRIMARY` |
| Standalone stage invocation (`/dev:shape docs/dev/<f>/spec.md`) | Tasks 4, 5 | Offer lives in the stage skill's own gate, not in `dev:dev` Step 5, so it prints outside the orchestrator |
| Cycle predating this feature (`handoff_at` absent) | Tasks 3 step 4, 6 step 1, 7 step 2 | Absence means "no handoff" — today's behavior, not an error |
| `git rev-parse` run outside a repository | Task 1 step 1 | `\|\|` failure branch exits rather than letting `dirname ""` → `.` silently make `$PRIMARY` the cwd |

## Out of Scope

- Extracting a shared canonical WORKDIR block that all skills reference (spec §Out of Scope). Task 2 inlines correct resolution at its own site; the dangling citation at `autopilot/SKILL.md:54` is repointed, not resolved into a new shared artifact.
- Any change to `dev:dev` Step 5 sequencing — see the note under Files.
- Making `dev:reflect` Step 4 unconditional for all modes.
- Any handoff in the reverse direction (autopilot → gated).
- An offer printed at the Validate or PR gates. (The *marker* still records a handoff made there manually — Task 3 step 3.)
- `debt-state-advancement-commit-durability` and `debt-spec-grounding-citation-unverified` — not in this cycle's edit path.
- Component Registry updates — `dev:done` Step 4 owns those, not a plan task.
