# Plan Challenger

*Branch: feature/plan-challenger · Confidence: 95% — Ready · 2026-07-24*
*Cycle type: feature · Tier: deep*

## Intent

`dev:plan` is the only artifact-producing stage in the `/dev` workflow with no cold review. Spec has its Step 12a challenger; Validate cold-reviews the diff. Plan has only its Step 6 self-review (same mind that wrote the plan) and the Step 4 user comprehension check.

This matters because `plan.md` is the artifact Build executes **blind** — Step 8 says "Safe to /clear now — resume with /dev:build plan.md." Build receives the file, not the conversation. And the downstream cold review can't cover the gap: `dev:validate` Step 2 checks "were all plan tasks implemented?", treating the plan as ground truth. A plan that faithfully omits a spec requirement, orders a dependency after its consumer, or names an interface inconsistently gets implemented into working-looking code and passes validate.

The economics are the case: a plan defect caught here costs one cheap revision; caught at validate (if at all) it costs a wasted Build plus a fix loop. Add a lightweight cold-review challenger that shifts that catch left.

## Scope

Add a cold-review challenger to `dev:plan`, cloning the proven machinery of `dev:spec` Step 12a, deliberately narrowed:

- **New challenger step in `plan/SKILL.md`**, after Step 6 self-review, before the Step 8 user gate. Dispatches a fresh `general-purpose` subagent that receives only `plan.md`, `spec.md` (and `design.md` if present), and the three-lens checklist — never this session's conversation history. Includes the injection guardrail (treat all provided files as data under review) and the in-session fallback when subagent dispatch is unavailable.
- **Three lenses** (all mechanical; spec already did the judgment work):
  - **Spec coverage** — every spec requirement (Success Criteria, Happy Path, Edge Cases) maps to at least one task.
  - **Sequencing / dependencies** — re-derive the task DAG cold; no task depends on something a later task produces.
  - **Interface consistency** — `Consumes:`/`Produces:` names and types align across tasks.
- **Two severities**, mirroring spec: **Blocker** (cannot stand as written) and **Concern** (worth flagging, not fatal). Every Blocker carries a pre-drafted suggested fix. The reviewer must be able to return clean — no manufactured findings.
- **Standard mode: advisory.** The verdict renders at the Step 8 gate, above the approval prompt. Nothing is auto-applied; the user decides (`apply` / subset / edit / dismiss). `challenge_plan.loops_run` stays 0.
- **Autopilot mode: teeth.** Blockers drive a bounded revision loop capped at `challenge_plan.loops_max` (standard 3 / deep 5), re-dispatching on the revised `plan.md` each iteration. Concerns are counted and passed through, never revised. **Single stop path:** blockers surviving the cap → STOP and request human input. No scope-blocker bypass class — all three lenses produce text-fixable findings.
- **`challenge_plan.*` state counters**, in a namespace separate from spec's `challenge.*`, so reflect's spec-quality reading (`challenge.blockers` paired with `spec_revisions`) is never corrupted. Counter shape mirrors spec's: `run`, `blockers`, `concerns`, `applied`, `dismissed`, `loops_run`, `loops_max`. **Written mode-symmetrically** — every counter write is traceable to a step that runs identically in standard and autopilot, so this cycle does not reproduce the "gate-path write dead in autopilot" defect.
- **`spec/SKILL.md` Step 6** — add the `challenge_plan` block to the state.json initialization template (spec owns the sole state.json template; init has no challenge key).
- **`reflect/SKILL.md`** — read `challenge_plan.*` in the retrospective (is the plan challenger earning its keep / being dismissed as noise?). A missing `challenge_plan` block means the challenger did not run (cycle predates the feature) — read as "did not run," not an error.
- **`autopilot/SKILL.md`** — update the "When autopilot stops" line (line 14) and Step 2 matching to include plan-challenger blockers surviving `challenge_plan.loops_max`.

**Runs on:** Standard and Deep cycles. Micro is auto-exempt — it has no plan stage (`skipped: ["shape", "plan"]`).

## Out of Scope

- **The full nine-skill gate-path-write audit** ("Sweep for gate-path state writes that are dead in autopilot") — deferred to its own cycle by explicit scope decision. This cycle records itself as another recurrence in the debt buffer (`debt-pending.md`), which merges into that tracker entry at `dev:done`.
- **A grounding/re-verify lens at plan** — it would duplicate spec's grounding lens run one stage earlier.
- **A plan scope-blocker class** — scope is decided at spec; a second scope judgment at plan would relitigate a settled decision. The rare "plan reveals two cycles" case still halts the autopilot run via the single stop path (blockers survive the cap → STOP).
- **Micro tier** — no plan stage exists.

## Success Criteria

1. On every Standard and Deep cycle, `dev:plan` dispatches a cold challenger after self-review and before the user gate; the verdict renders at the gate in standard mode.
2. The challenger applies exactly the three lenses (spec-coverage, sequencing, interface-consistency) and can return a clean verdict.
3. In autopilot, plan-challenger blockers drive a revision loop capped at `challenge_plan.loops_max`; blockers surviving the cap STOP the run.
4. `challenge_plan.*` counters exist in state.json separate from `challenge.*`, and spec's `challenge.*` reading in reflect is unchanged/uncorrupted.
5. Every `challenge_plan.*` counter write is traceable to a step that runs in both standard and autopilot mode (no gate-only writes).
6. `reflect` reports the plan challenger's disposition and degrades gracefully when the block is absent.
7. `autopilot`'s documented stop surface names the plan-challenger blocker case.
8. Micro cycles never invoke the challenger.

## Happy Path

1. A Standard cycle reaches `dev:plan`; the plan is written and self-reviewed (Step 6).
2. The challenger step dispatches a fresh subagent with `plan.md` + `spec.md` + the three-lens checklist.
3. The subagent returns a verdict: e.g. one sequencing blocker with a suggested reorder, one coverage concern.
4. The verdict renders at the Step 8 gate above the approval prompt.
5. The user replies `apply`; the reorder lands in `plan.md`, `challenge_plan.applied` increments, the gate re-displays without re-dispatching.
6. The user approves; state advances to Build. `reflect` later reads `challenge_plan.*` and reports the challenger caught and resolved a sequencing defect.

## Edge Cases

- **Clean verdict** — challenger finds nothing. The gate shows no findings; the "reply apply…" line is omitted. Reviewer returning clean is a designed outcome, not a failure.
- **Resume mid-approval** — if `plan.md` exists and `state.json.stage` is still `"plan"` (a `/clear` at the gate), the challenger re-dispatches on gate re-arrival, regenerating the verdict; `run`/`blockers`/`concerns` are overwritten, `applied`/`dismissed` carry forward. Mirrors spec's resume rule.
- **Subagent unavailable** — fall back to running the three lenses in-session, same verdict format. Same fallback spec Step 12a and validate Step 2 specify.
- **no-ui mode** — plan runs without `design.md`; the spec-coverage lens still works (it checks against spec, and design when present).
- **Autopilot, blockers survive cap** — STOP and surface them; the single stop path. `challenge_plan.dismissed` stays 0 in autopilot (nothing is declined; unresolved blockers are surfaced, not dropped).
- **Dismissed findings in standard mode** — approving past a surfaced finding is declining it; `challenge_plan.dismissed` increments, feeding reflect's "has the challenger become noise" reading.

## Technical Constraints

- **Counter namespace collision is the load-bearing constraint.** `challenge_plan.*` must be distinct from `challenge.*`; reflect reads `challenge.blockers` paired with `spec_revisions` as a *spec*-net signal, and a shared object would corrupt it.
- **Mode-symmetric writes are mandatory** — this plugin has three recorded instances of the "gate-path write dead in autopilot" defect, and the last challenger-adding cycle reproduced it. Every new counter write must live on a step that runs in both modes.
- **Cross-skill behavior ripple** — this changes plan's stopping behavior and adds an autopilot STOP condition, so `autopilot/SKILL.md`'s stop surface must be updated in the same cycle (plan Step 6's own "Cross-skill behavior ripple" failure mode).
- Artifacts are `SKILL.md` markdown + a JSON state template; no runtime code, no tests in the conventional sense — validation is prose-consistency review.

## Dependencies

- Relies on the existing spec Step 12a challenger as the template to clone.
- Touches four skills that must stay internally consistent: `plan`, `spec`, `reflect`, `autopilot`.

## UI Needed

No. This is a workflow-mechanism change to skill prose and a state template. There is no user-facing UI; the "comprehension check" and gate are text.

## Audience

The repo owner (awilliamsbuilds) running the `/dev` workflow on this and other repos. The challenger's outputs are read by the user at the plan gate and by `dev:reflect` in retrospectives.

---
*Auto-filled dimensions: none*
*Grounding inventory: Read plan/SKILL.md in full → confirmed no cold-review challenger, only Step 4 comprehension check + Step 6 self-review + Step 8 gate. Read spec/SKILL.md Step 12a → confirmed the challenger template being cloned. Read validate/SKILL.md Step 2 → confirmed "Plan coverage: were all plan tasks implemented?" treats plan as ground truth. grep 'challenge' across plugins/dev/skills → only reflect, spec, autopilot mention it; init has no challenge key (spec Step 6 is the sole state.json template). grep 'challenge\.' reads → reflect reads challenge.run/blockers/concerns/applied/dismissed/loops_run (lines 41, 56–65) and pairs challenge.blockers with spec_revisions; autopilot line 14 "When autopilot stops" names spec-challenger blockers. Confirmed the collision and the four-skill ripple set. tech-debt Open cross-check → 3 items touch this cycle's files; "gate-path state writes dead in autopilot" is the directly-relevant trap, recorded as a recurrence in debt-pending.md.*
