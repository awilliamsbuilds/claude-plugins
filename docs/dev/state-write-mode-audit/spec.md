# State-Write Mode Audit
*Branch: feature/state-write-mode-audit · Confidence: 90% — Ready · 2026-07-24*
*Cycle type: feature · Tier: deep*

## Intent

`/dev` runs in two modes: **standard** (approval gates between stages) and **autopilot** (no gates, chains straight through). A recurring defect class lives in that split: a `state.json` counter is written **at a gate** — "when the user approves, increment X" — so the write never executes in autopilot, which has no gates. The counter stays at its init value (usually `0`), and `dev:reflect` then reads X and reports it with no mode qualification, as if the number were real.

It is nasty precisely because `0` is a plausible value: nothing crashes, and every autopilot retrospective quietly reports counters that were structurally incapable of being anything else. This plugin has **three confirmed instances** (all already fixed — `challenge.applied`, `challenge.dismissed`, `metrics.spec_revisions`), and the last two challenger-adding cycles (`spec-challenger`, `plan-challenger`) each had to re-derive the invariant by hand. That is the recorded tech-debt entry this cycle pays: *"Sweep for gate-path state writes that are dead in autopilot"* (Recurrence 2).

This cycle does both halves: the **corrective sweep** of every other counter, and the **structural prevention** so a future counter cannot reintroduce the shape.

## Scope

1. **Sweep + fix.** Trace every **mode-sensitive counter** — `challenge.*`, `challenge_plan.*`, and the `metrics.*` / `validate.*` counters `dev:reflect` reads — across the writer skills to the mode(s) that actually execute each write. For each: either it is written in both modes, or it is genuinely mode-specific with its autopilot value equal to its init default, or it is a **defect** (a non-default autopilot value that depends on a gate write). Fix each defect write-side — move the write pre-gate, or give autopilot its own writer — mirroring the three historical fixes.
2. **Inline mode tags.** Annotate each mode-sensitive write site in the skill prose with a short tag naming its mode: `(writes: both)`, `(writes: autopilot-only)`, `(writes: standard; =default 0 in autopilot)`. The fact lives once, at its single source, so it cannot drift. Structural fields (`stage`, `completed[]`, `skipped[]`, `artifacts.*`, `confidence.*`, timestamps, `linear_issue`) stay untagged — they are written by every stage in both modes by construction and carry no mode risk.
3. **Prevention (plan-stage).** Extend the **existing** `## Mode symmetry` section of `plugins/dev/references/tech-debt.md` with the per-key write-mode rule. Require `dev:plan`'s task-template `Interfaces:` block to name, per new `state.json` key, which mode writes it. The **existing** interface-consistency lens of the `dev:plan` Step 7a challenger enforces it — no new enforcement machinery.

**Writer set (grounded, not recalled):** the eleven skills that write `state.json` keys are `spec`, `shape`, `plan`, `build`, `validate`, `pr`, `done`, `reflect`, `autopilot` (the nine the entry named) **plus `dev`** (writes `skipped[]` via its `skip` command) **and `fix`** (writes `linear_issue` + `stage`). `dev` and `fix` write structural fields with no cross-mode reflect read, so they are traced by the audit but are not defect sites. `init` and `debt` only read state (`init` writes `config.json`; `debt` resolves the paying cycle).

## Out of Scope

- **The six other open tech-debt entries** — autopilot grounding-gate cross-note, hardcoded repo path in `dev:reflect`, nested-product-plan lifetime, validate fix-loop verification, config-contract gate wording, stale `loops_max` derivation. Distinct defects; folding them in would blur the audit's focus.
- **A validate-stage enforcement check** — enforcement is plan-stage only (the challenger's interface lens), where the design decision is made before any code exists.
- **Any new standing file or per-key registry table** — deliberately rejected. A table is a second copy of a fact that already lives in the skills; it drifts on every future state-key change and a drifted safety-doc lies. Facts live inline at the write site instead.
- **Runtime code** — there is none; artifacts are `SKILL.md` markdown and one shared reference. Validation is prose-consistency review.
- **A read-side `dev:reflect` refactor** beyond what a discovered correctly-mode-specific-but-misread counter would require — expected to be none, because the invariant makes such counters not exist.

## Success Criteria

1. Every mode-sensitive `state.json` counter written by a `dev:*` skill is traced to the mode(s) that write it; any gate-only-in-autopilot write that `dev:reflect` reads is either fixed (moved pre-gate or given an autopilot writer) or confirmed to have its autopilot value equal to its init default.
2. Each mode-sensitive write site carries an inline mode tag; structural / mode-invariant fields are confirmed mode-invariant and left untagged.
3. `plugins/dev/references/tech-debt.md`'s `## Mode symmetry` section states the per-key write-mode rule.
4. `dev:plan`'s `Interfaces:` block requires each new `state.json` key to name its writing mode, and the Step 7a challenger's interface-consistency lens checks for its presence.
5. **No new standing file is created**, and no per-key registry table is introduced.
6. The three already-fixed instances remain correct — no regression — and `dev:reflect`'s existing counter reads stay valid.
7. The tag syntax is byte-consistent across every site (the interface-consistency property the feature itself enforces).

## Happy Path

1. Build traces every mode-sensitive counter write across the eleven writer skills to the mode(s) that execute it.
2. Each gate-only-in-autopilot defect found is fixed write-side (moved pre-gate, or given an autopilot writer), matching the three historical fixes.
3. Each mode-sensitive write site gains an inline tag naming its mode.
4. `references/tech-debt.md`'s `## Mode symmetry` section gains the per-key rule; `dev:plan`'s `Interfaces:` block gains the required "mode per new state key" field; the plan challenger's interface lens checks it.
5. A future cycle adding a new counter must declare its write-mode in the plan; an omission is caught by the challenger before Build — the recurrence is structurally prevented rather than left to per-cycle vigilance.

## Edge Cases

- **Legitimately mode-specific counter, correct at default** — e.g. `challenge.dismissed` (nothing declined in autopilot, so `0` is correct) or `challenge_plan.loops_run` (autopilot-only). Not a defect; the inline tag documents it, and the invariant holds ("no counter's *non-default* autopilot value depends on a gate write").
- **Genuinely mode-independent counter** — e.g. `validate.loops_run`, written on a mode-independent path. Tag says so; no fix.
- **A fourth (or further) live defect surfaces during the sweep** — fix it write-side exactly as the three historical instances were fixed; record it in the audit trail.
- **A correctly-mode-specific counter that `dev:reflect` nonetheless misreports** — if found, this is the one case needing a read-side reflect change; expected to be none, but the audit must actively confirm rather than assume.
- **`dev` / `fix` structural writes** (`skipped[]`, `linear_issue`, `stage`) — traced by the audit, confirmed to carry no cross-mode reflect read, left untagged. Their presence is why the writer set is eleven, not nine.
- **`dev:plan` writes its own mode-sensitive counters** (`challenge_plan.*`) — those write sites are tagged too, and plan's Interfaces block applying the new rule to itself is the self-consistency check.

## Audience

The repo owner (awilliamsbuilds) running `/dev`. The audit's outputs are read by future `/dev` cycles (via the inline tags and the contract rule) and enforced automatically at the plan gate.

## Technical Constraints

- `plugins/dev/references/tech-debt.md` is a **shared contract** loaded by `init`, `build`, `validate`, `reflect`, `done`, `debt`, and `spec`. Edits must be additive and must not break those consumers.
- Prose-only change; there is no test harness, so validation is prose-consistency review (as in the `plan-challenger` cycle).
- **Load-bearing invariant:** *no counter's non-default autopilot value may depend on a gate write* — inherited verbatim from `plan-challenger`'s SC5. The audit classifies every counter against it.
- **Tag syntax must be consistent across all sites** — the interface-consistency property the feature is simultaneously enforcing; an inconsistent tag would be the exact bug this cycle exists to catch.

## Dependencies

- Relies on `dev:reflect`'s counter-reader surface (which counters it reads) — grounded this stage.
- Relies on `dev:plan`'s `Interfaces:` / `Consumes:` / `Produces:` block and its Step 7a challenger interface-consistency lens as the prevention's home and enforcer — grounded this stage.
- Touches the shared `references/tech-debt.md` contract; changes must stay compatible with its seven consumers.

## UI Needed

No. This is a workflow-mechanism change to skill prose and one shared reference. There is no user-facing UI.

---
*Auto-filled dimensions: none*
*Grounding inventory: Enumerated state.json writers from code (`grep -c state.json` across 14 skills, then read each candidate's write sites) → writer set is eleven, not the entry's nine: added `dev` (writes `skipped[]`, line 99 `skip` command) and `fix` (writes `linear_issue` + `stage`, lines 97–108); confirmed `init` (0 mentions, writes config.json not state) and `debt` (reads only, resolves paying cycle) are non-writers. Verified the recurring defect shape and its three already-fixed instances against the tracker entry and `dev:reflect`'s counter reads. Verified the prevention target: `dev:plan` task template `Interfaces:`/`Consumes:`/`Produces:` block (lines 82–84), reinforced by Step 6 self-review (line 166) and the Step 7a challenger interface lens (line 212). Confirmed `references/tech-debt.md` already carries a `## Mode symmetry` section stating this exact rule and citing the three instances — the prevention extends it rather than creating a new file. Pass-4 debt cross-check: source entry folded to `## To Close`; six other open entries left open by user decision.*
