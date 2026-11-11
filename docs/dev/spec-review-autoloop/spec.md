# Spec Review Autoloop
*Branch: feature/spec-review-autoloop · Confidence: 87% — Ready · 2026-11-10*
*Cycle type: feature · Tier: standard*

## Intent

In a gated `/dev` cycle, the cold review at the Spec gate (`dev:spec` Step 12a) and the Plan gate
(`dev:plan` Step 7a) runs once and then hands every finding to the user. In practice the user accepts
the suggested fixes without reading them closely, and then, when the first round was heavy, asks for a
second review by hand to check the fixes and catch anything missed. Both of those steps are routine,
and the user is doing them manually on most cycles.

This cycle makes the review loop run itself: each round's fixes are applied without asking, and
another round runs automatically when the last one was heavy. One rule governs the loop in every
place it runs — Spec and Plan, gated and autopilot — so there is a single statement of when the loop
continues and when it stops.

## Scope

1. **The loop rule (one rule, four sites).** Spec and Plan cold reviews, in both standard (gated) and
   autopilot mode, run this loop:
   - A **round** is one cold-review dispatch and its verdict.
   - A round is **heavy** when its verdict contains **at least one Blocker, or 5 or more Concerns**.
     Otherwise it is **light**.
   - **Light round:** apply every suggested fix from that round, commit
     (`spec|plan: apply challenger fixes for <feature>`), then exit the loop. No further review.
   - **Heavy round with rounds remaining:** apply every suggested fix from that round, commit, and
     dispatch the next round against the revised artifact.
   - **Heavy round on the last allowed round:** apply **none** of that round's fixes. Exit the loop
     with that round's findings unresolved. A heavy round's fixes are never applied unreviewed: they
     either get a following review round or go to the user.
   - **Round limit** = the existing tier caps, unchanged: `challenge.loops_max` /
     `challenge_plan.loops_max` (micro 1 / standard 3 / deep 5; micro never reaches Plan).
   - `challenge.loops_run` / `challenge_plan.loops_run` count rounds in **both** modes, and become
     `(writes: both)`.

2. **Standard-mode gate (Spec Step 13, Plan Step 8).** The gate renders once, after the loop exits.
   - It shows a short **per-round log**: for each round, its finding tally (the existing per-lens
     header) and a one-line list of the fixes applied.
   - **Light exit:** fixes are already committed. The only question is approval of the artifact.
   - **Limit-hit exit:** the gate also lists the unresolved findings from the last round verbatim, with
     their suggested fixes, under a line stating the round limit was reached. The user can `apply`
     them, edit, rescope, or approve as-is.
   - The user can still revert or edit any auto-applied fix before approving. That is a Path B
     (user-originated) change.
   - The resume-block ordering (`dev:spec` Step 13, canonical) is unchanged.

3. **Autopilot.** Same rule. A limit-hit exit **STOPs** and surfaces the unresolved findings, as
   blockers-surviving-the-cap does today. The trigger now also covers 5+ concerns, so a concern-heavy
   final round STOPs too. `dev:autopilot`'s two challenger-loop sections and its `## Purpose` stop list
   restate the new rule.

4. **Rules this replaces.** These are replaced in place (no history narrated in the skill files):
   - "Mode behaviour — standard: advisory" and "autopilot: teeth" in Spec 12a and Plan 7a. Both modes
     now run the loop; they differ only in the exit (gate vs STOP).
   - "Concerns: countable, foldable, never loop-extending." 5+ concerns now makes a round heavy. Fewer
     than 5 concerns never extends the loop.
   - The standard-mode **Re-run rule** ("once per gate arrival, `apply` never re-dispatches"). The loop
     now re-dispatches by the rule above. A Path A `apply` of limit-hit leftovers at the gate does
     **not** start a new loop, so a gate's `apply` never re-dispatches.
   - The `loops_run` "autopilot-only; unused in standard mode" lines.
   - The "Which commit carries the counters" paragraphs in Spec 12a / Plan 7a ("Step 12a/7a does
     **not** commit"). Each loop round's commit carries the counters, in both modes.
   - Other sentences that become false under the loop rule:
     - autopilot:153: "standard mode never loops, so one retry per stage and one per round are
       indistinguishable there"
     - autopilot:151: "`loops_run` is the blocker-driven number"
     - spec:700 / plan:249: "In standard mode Step 13/8 writes them at the gate", and "unactioned
       concerns pass through by design"
     - spec:710: "Pair it with `loops_run` … loops are what blockers actually drive"
     - spec:682: "In standard mode a scope blocker is advisory like any other finding" (see Scope 5)

5. **Scope blockers (Spec only).** Unchanged in substance. A right-sizing blocker cannot be fixed by
   editing text, so a round containing one exits the loop immediately and applies none of that round's
   fixes. Standard surfaces it at the gate; autopilot STOPs.

6. **Counters.** `applied` / `applied_concerns` are incremented by the loop in both modes, with the
   existing Blocker/Concern split. `dismissed` stays `(writes: standard)` and now counts only findings
   the user declines **at the gate**: limit-hit leftovers approved past, or auto-applied fixes the user
   reverts. `applied`/`applied_concerns` are not decremented on a revert: a reverted fix counts in
   both `applied` and `dismissed`. `dev:reflect`'s readings of `dismissed` and `loops_run` are updated to match (loops now run
   in gated cycles, and `dismissed` no longer measures how often the user skips the brief).

7. **Folded debt — plan errored dispatch** (`debt-plan-challenger-errored-dispatch-undefined`).
   `dev:plan` Step 7a carries the errored-dispatch rule as a marked mirror of `dev:spec` Step 12a
   (canonical): no `loops_run` advance, `blockers`/`concerns` set `null`, one retry per stage, second
   error STOPs. `dev:autopilot`'s plan-challenger section drops "the errored-dispatch rule does not
   apply here", and its stop list names a twice-errored plan dispatch.

8. **Folded debt — `plan_end` timing** (`debt-plan-end-excludes-challenger-loop`). `plan_end` is
   re-stamped after Step 7a's loop exits, and on each gate revision, mirroring `dev:spec`'s `spec_end`
   re-stamp. `spec_end` is likewise re-stamped after Step 12a's loop exits, in addition to its
   existing Path A/B re-stamps, so gated cycles keep counting review time inside Spec now that the
   fixes land in the loop rather than through Path A.

9. **Resume mid-approval (Spec Step 1, Plan Step 1).** A resumed gate re-enters the loop with
   `loops_run` **carried forward**, so the loop gets only the rounds it has left. A resume after a
   limit-hit exit (`loops_run == loops_max`) dispatches no new round. It re-dispatches once to
   regenerate the leftover findings, since the verdict text is not persisted, and re-renders the gate
   with them, without applying them. That dispatch is not a round and does not advance `loops_run`.
   Today's Step 1 checks reset only `run`/`blockers`/`concerns`. That stays true, and `loops_run`
   joins the carried-forward set.

## Out of Scope

- `dev:validate`'s code-review fix loop (P1–Nit severities, its own `validate.loops_max`). The user's
  request is about the spec/plan review. Validate already auto-loops.
- The review lenses, the Blocker/Concern definitions, and the verdict format. This cycle changes what
  happens *after* a verdict, not how one is produced.
- New `config.json` keys. The threshold (5 concerns) and the caps are fixed in the skill text. They can
  be made configurable later if the numbers turn out wrong.
- The plan challenger gaining a scope-blocker class. Plan still has none.
- Migrating in-flight cycles. A cycle mid-gate keeps whatever its loaded skill text says.

## Success Criteria

1. In a standard-mode Spec or Plan stage, the user is never asked whether to apply cold-review fixes,
   except for leftovers from a limit-hit or scope-blocker exit.
2. A heavy round, with rounds remaining, is followed by another dispatch with no user prompt.
3. A light round ends the loop with its fixes applied and committed, and the gate asks only for
   approval.
4. No heavy round's fixes are ever applied without a following review round or the user seeing them.
5. The loop never exceeds `loops_max` dispatches, not counting the one errored-dispatch retry.
6. The rule (heavy = ≥1 Blocker or ≥5 Concerns; limit = tier cap) is stated canonically once, in
   `dev:spec` Step 12a. `dev:plan` Step 7a mirrors it and `dev:autopilot` restates it.
   `grep -n 'loops_run.*autopilot-only\|never loop-extending\|never a reason to loop\|once per gate arrival\|standard mode never loops\|blocker-driven number\|advisory' plugins/dev/skills/{spec,plan,autopilot}/SKILL.md`
   returns no hit that contradicts the rule.
7. Both folded debt items' **Done looks like** conditions hold, and both are queued in
   `debt-pending.md` `## To Close`.

## Happy Path

1. Spec Step 12 commits `spec.md`.
2. Step 12a, round 1: 1 Blocker, 2 Concerns. Heavy. All 3 fixes are applied and committed, and round 2
   dispatches.
3. Round 2: 0 Blockers, 1 Concern. Light. The fix is applied and committed, and the loop exits.
4. Step 13 gate: per-round log (round 1: ⛔1 ⚠️2, 3 fixes; round 2: ⚠️1, 1 fix), then "approve the
   spec?".
5. User approves. State write, then the resume block, as today.

## Edge Cases

- **Clean round 1.** Light with nothing to apply. The gate shows "round 1: clean" and asks for approval.
- **Micro (cap 1), heavy round 1.** None of its fixes are applied. The gate lists them as unresolved
  under the limit-reached line.
- **Fix in round N reintroduces an earlier finding.** No special handling. The cap bounds it.
- **Errored dispatch mid-loop.** Spec: the existing rule. Plan: the newly mirrored rule (Scope 7). An
  error is not a round, and does not consume the cap.
- **Resume mid-approval** (`/clear` at the gate). See Scope 9: `loops_run` carries forward, and a
  limit-hit cycle re-renders its leftovers rather than looping again. `applied`/`applied_concerns`/
  `dismissed` carry forward as today.
- **User reverts an auto-applied fix at the gate.** This is a Path B change: `spec_revisions`
  increments and `dismissed` increments by the reverted count. No re-review.
- **Autopilot, concern-heavy final round.** It STOPs where it previously would have exited. This is
  the cost of one rule across modes, chosen deliberately.

## Technical Constraints

- These are prose-only skill edits. There is no executable code and no test suite. Verification is a
  read-through plus the Success Criteria 6 grep.
- Canonical/mirror discipline: `dev:spec` Step 12a is canonical, `dev:plan` Step 7a mirrors it and
  says so, and `dev:autopilot` restates it and says so.
- `state.json` key set unchanged. Only `(writes: …)` annotations change.

## Dependencies

None.

## UI Needed

No.

---
*Auto-filled dimensions: edge_cases, dependencies (inferred, not asked)*
*Grounding inventory: grep 'Mode behaviour — standard: advisory' / 'Re-run rule' → spec/SKILL.md:674,684 and plan/SKILL.md:243,259 (standard runs once per gate arrival, `apply` never re-dispatches) — verified; grep 'never loop-extending\|never a reason to loop' → spec/SKILL.md:653,678, autopilot/SKILL.md:151,155; grep 'loops_run.*autopilot-only' → spec:711, plan:256; grep 'plan_end' → plan/SKILL.md:192 only (stamped in Step 7, before 7a); grep -rln 'challenge\.' plugins → spec, plan, autopilot, reflect (reflect:42–85 reads dismissed/loops_run), references/telemetry.md:103–112 (copies keys verbatim; no wording change needed); README.md: no challenger prose; open debt intersect → 2 plan-challenger items folded in, the rest not touched by this scope.*
