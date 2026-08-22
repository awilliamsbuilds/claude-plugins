# Challenger Loop Economics
*Branch: feature/challenger-loop-economics · Confidence: 100% — Ready · 2026-08-22*
*Cycle type: feature · Tier: standard*

## Intent

`dev:spec` Step 12a's autopilot revision loop is bounded only by a count. Nothing tests whether a
round's findings are still worth another round, so on a deep-tier cycle the loop runs its full five
rounds regardless of what it finds. On `extract-review-skills` that cost five cold subagent
dispatches, 51 applied fixes, and a spec that grew 200 → 546 lines — while the findings decayed to a
duplicate label and an off-by-one line range by round 2.

Three consequences follow, and this cycle settles all of them together because each one is an edit to
the same twenty lines of `spec/SKILL.md`: splitting them across cycles means three cycles re-editing
one region.

The loop is already gated on blockers existing — a round returning zero blockers ends it today. What
it lacks is a test of what *kind* of blocker keeps it going.

## Scope

Four changes, all to `/dev`'s own process prose.

**1. Blocker means "a builder following this literally ships something broken."**
`dev:spec` Step 12a's Output contract currently defines Blocker as *"cannot stand as written: a
requirement reads two ways, sections contradict, a load-bearing claim is unverified, in-scope spans
two cycles."* That is broader than the bar the loop should run against. Tighten it, and widen Concern
to absorb what falls out.

**The right-sizing class survives the tightening unchanged.** A finding that in-scope spans more than
one cycle does not make a builder ship something broken, so the tightened bar alone would demote it to
a Concern — and a Concern can never STOP. That would silently delete Step 12a's scope-blocker
exception, which bypasses the loop and STOPs immediately, and which this cycle's Out of Scope
reasoning depends on. Blocker is therefore defined as a two-member class: the build-breaking bar, plus
the existing right-sizing criterion carried over verbatim.

The exit rule is a **consequence of this change, not a new mechanism.** Step 12a already states that
concerns are "never loop-extending" — never a reason to run another iteration, re-dispatch, or STOP.
Once a bookkeeping finding is a Concern rather than a Blocker, the existing rule stops the loop with
no new step, no new counter, and no second severity concept.

**2. `spec.md` carries no drafting history.**
Nothing in `spec/SKILL.md` currently instructs the loop to write revision rationale — the growth is
emergent, so this is a new constraint rather than an amended one. The rule draws its line at drafting
history, not at reasoning: a revision replaces text; it does not append an account of the text it
replaced. `## Out of Scope` explaining why something is excluded is product reasoning and is
unaffected.

There is no replacement home. Product reasoning is already captured permanently — `dev:done`
generates the decision log's Key Decisions from `spec.md` and `plan.md` — and `git log -p` on the spec
already shows what each round changed. Only "why draft 2 was wrong" is discarded, and it has no reader.

**3. An errored dispatch is not an iteration.**
When a dispatch returns an error instead of a verdict: do not advance `challenge.loops_run`, and set
`challenge.blockers` / `challenge.concerns` to `null` rather than leaving the previous round's values
in place. Retry once. A second error STOPs and surfaces the failure.

**The STOP is not mode-split.** `dev:validate`'s "A reviewer that cannot run stops the stage" applies
in both modes, and this rule matches it rather than inventing a second answer to the same question. A
standard-mode STOP costs almost nothing to recover from: `spec.md` is already committed, `stage` is
still `"spec"`, so re-running `/dev:spec` re-enters at Step 12a through the resume-mid-approval check
that already exists. Letting the Step 13 gate render without a verdict would instead invite approving
a spec that got no cold review at all — the exact condition Step 12a exists to prevent.

`null` is a third value distinct from `0`: `0` means a round ran and found nothing, `null` means no
round produced a verdict. `challenge.run` is unaffected by an error — it records whether any dispatch
this stage returned a verdict, so a clean round followed by an errored one leaves it `true`.

**4. `applied` splits so concern-driven growth is attributable.**
Concerns stay foldable in autopilot — the existing rationale holds, and nothing measured disproves it.
What changes is the instrument: `challenge.applied` merges blocker fixes and concern fixes into one
number, so on the cycle that produced this item nobody can say how much of the 346-line growth
concerns caused. Add `applied_concerns` alongside `applied`; `applied` keeps its current meaning as
the total, so blocker-driven fixes are `applied - applied_concerns`.

**Files:** `plugins/dev/skills/spec/SKILL.md` (Step 12a, Step 13, state.json template),
`plugins/dev/skills/autopilot/SKILL.md` (spec-challenger section, stop list),
`plugins/dev/skills/plan/SKILL.md` (divergence sentence, counter shape),
`plugins/dev/skills/reflect/SKILL.md` (reads the new counter), `CLAUDE.md` (Component Registry).

## Out of Scope

- **The plan challenger's Blocker definition.** Grounded in history: plan-challenger blockers across
  recorded cycles run 0, 1, 1, 0, 0 — never above 1, with one record noting an exit at 2/3. The
  runaway is spec-only. Plan's three lenses are mechanical (coverage, sequencing, interfaces) and
  self-limiting, where spec's are interpretive, which is why severity inflated there and not here.
  Rewording a precise mechanical test into build-breaking language would make it vaguer.
  The counter *shape* change (item 4) does apply to `challenge_plan` — shape symmetry, not severity.
- **Lowering the deep-tier cap from 5 to 3.** Named in the source item as an open judgment; disposed
  of here rather than left open. The kind-based exit is now what stops the loop, so the cap is a
  backstop that rarely binds. Lowering it adds a second mechanism doing the same job, and rounds 1–2
  of the incident cycle caught load-bearing defects — early rounds earn their keep.
- **`debt-cross-file-line-citations-go-stale-silently`.** 37 `file:line` citations exist across 6
  skills; 5 sit in this cycle's edit surface, one already broken (`autopilot/SKILL.md:149` cites
  `spec/SKILL.md:478`, which today reads `## Happy Path`). This cycle's only edit above line 478 is
  the state.json template at ~219; the sole citation into `spec/SKILL.md` below that point is `:478`,
  already broken, and the only other citation into the file (`fix/SKILL.md:363` → `spec/SKILL.md:161`)
  sits above the template and is unaffected. **Zero new citations break.** Folding it in would be
  opportunistic rather than caused by this work, and the item's own "Done looks like" is a contract
  decision across a dozen skills.
- **Persisting the challenger verdict text.** Out of scope; `spec/SKILL.md:51` already documents that
  it is not persisted and this cycle does not change that.
- **Numeric thresholds for the new counter in `dev:reflect`.** No distribution exists yet, matching
  reflect's existing "no numeric thresholds" rule for `challenge_plan`.
- **Telemetry schema changes** — owned by `telemetry-schema` in the `dev-observability` plan.

## Success Criteria

1. `dev:spec` Step 12a's Output contract defines **Blocker** as either (a) a finding where a builder
   following the spec literally ships something broken, or (b) a right-sizing finding that in-scope
   spans more than one cycle — the existing scope-blocker class, carried over unchanged — and
   **Concern** as everything else worth flagging. Both definitions carry at least one concrete example
   drawn from a real class of finding.
2. Step 12a states in one sentence that the loop's exit is a consequence of those definitions plus the
   existing "concerns never extend the loop" rule. **No separate exit step, exit test, or second
   severity concept is added.**
3. `dev:plan` Step 7a's Blocker definition bullet is byte-unchanged. One sentence naming why it
   diverges from Step 12a's — interpretive vs mechanical lenses — is added as **adjacent prose below
   the Output contract block**, not inside the bullet.
4. Step 12a states the drafting-history prohibition, and the rule explicitly distinguishes drafting
   history from product reasoning, naming `## Out of Scope` as unaffected.
5. An errored dispatch does not advance `challenge.loops_run` and sets `challenge.blockers` /
   `challenge.concerns` to `null`. One retry; a second error STOPs. **This rule is stated once and is
   not mode-split** — it holds identically in standard and autopilot, matching `dev:validate`'s
   "A reviewer that cannot run stops the stage."
6. `dev:autopilot`'s "When autopilot stops" list names the twice-errored challenger dispatch.
7. Step 12a states that a standard-mode STOP is recovered by re-running `/dev:spec`, which re-enters
   at Step 12a via the Step 1 resume-mid-approval check. The Step 13 gate does **not** render on a
   STOP — there is no "could not run" gate variant, and no path approves a spec whose cold review
   never returned a verdict.
8. `spec/SKILL.md`'s state.json template initializes `applied_concerns: 0` in **both** the `challenge`
   and `challenge_plan` blocks.
9. Step 12a's and Step 7a's counter-write semantics each state which fixes increment `applied` and
   which additionally increment `applied_concerns`.
10. `dev:reflect` reads **both** `challenge.applied_concerns` and `challenge_plan.applied_concerns`,
    in the two namespaces it already reads separately, and treats a missing key as "not recorded" —
    matching its existing missing-block semantics — never as `0`. It also documents `null` counters as
    "no verdict returned this round," distinct from `0` meaning "a round ran and found nothing."
11. **No counter is renamed or removed.** Every state.json written before this cycle stays readable by
    every reader this cycle touches.
12. `CLAUDE.md`'s Component Registry rows for `dev:spec`, `dev:autopilot`, `dev:plan`, and
    `dev:reflect` describe the changed behavior.

## Happy Path

The autopilot run this cycle is trying to produce:

1. Autopilot reaches Step 12a and dispatches the cold reviewer.
2. Round 1 returns 2 Blockers and 3 Concerns. The loop applies both blocker fixes and folds in 2
   mechanical concern fixes. `loops_run: 1`, `applied: 4`, `applied_concerns: 2`. No prose explaining
   what round 1 got wrong is added to `spec.md`.
3. Re-dispatch. Round 2 returns 0 Blockers and 2 Concerns — a duplicate label and an imprecise line
   range, neither of which would make a builder ship something broken.
4. Concerns cannot extend the loop, so it exits at round 2 with 3 of 5 rounds unused.
5. Autopilot proceeds to the next stage. `dev:reflect` later reads `applied: 4` /
   `applied_concerns: 2` and can attribute the churn.

## Edge Cases

- **Errored dispatch.** Covered by scope item 3. The retry is once, not per-round, and the STOP is
  identical in both modes.
- **Scope blockers are untouched.** SC1 defines Blocker as a two-member class precisely so the
  right-sizing criterion survives; Step 12a's scope-blocker exception still bypasses the loop and
  STOPs immediately. A scope blocker therefore never reaches the exit rule and cannot interact with it.
- **`challenge.run` after a mixed sequence.** A clean round 1 followed by an errored round 2 leaves
  `run: true` — it records whether any dispatch returned a verdict this stage, not whether the last
  one did. `run: false` alongside `blockers: null` is the shape meaning no dispatch ever returned.
- **A reviewer that mis-classifies severity defeats the exit.** Accepted, deliberately: option
  "tighten the definition" was chosen over "tighten and add a backstop test" because a backstop
  reintroduces the second severity concept SC2 forbids. The failure is visible at Reflect — high
  `challenge.blockers` against low `spec_revisions` is already read as "the challenger is catching
  what the author's grounding missed," and a mis-classifying reviewer shows up as that pattern
  persisting across cycles.
- **Round 1 returns 0 Blockers.** The loop never runs. Unchanged from today.
- **A historical `state.json` has no `applied_concerns`.** Read as not recorded (SC10). Cycles predating
  this one are not retrofitted.
- **Standard mode.** `challenge.loops_run` stays `0` and no loop runs — unchanged. The tightened
  definitions still change what the Step 13 gate displays, since the verdict renders there.

## Audience

The `/dev` workflow's own operator — one person, running these skills on their own repos. Changes are
prose in `SKILL.md` files, read by Claude at runtime and by the operator when debugging a stage.

## Technical Constraints

- **Prose-only surface.** These are Markdown skill files with no test runner. Verification is by
  reading the changed prose against the success criteria, per this repo's established practice.
- **state.json changes must be additive.** `dev:reflect` reads cycles written before this change; a
  rename or removal breaks them silently (SC11).
- **`spec/SKILL.md`'s state.json template is the single initialization point** for both `challenge` and
  `challenge_plan`. No later stage re-guards these values, so the template must carry the new key for
  both blocks.
- **`plan/SKILL.md` Step 7a defers to Step 12a** for the concerns rule and counter semantics, stating
  Step 12a "governs both challengers." Any edit to those shared statements changes Plan by reference —
  which is intended for the counter shape and must be avoided for the Blocker definition.

## Dependencies

- `autopilot-resume-stage` (Milestone 1) must be merged — both cycles edit `autopilot/SKILL.md`.
  Verified merged: `docs/dev/product-plans/dev-process-hardening.md` shows it `[x]`, and the decision
  record `docs/decisions/2026-08-20-autopilot-resume-stage.md` exists.

## UI Needed

No.

---
*Auto-filled dimensions: none*
*Grounding inventory: `spec/SKILL.md:603` + `autopilot/SKILL.md:139` → loop bounded by count only, no kind test anywhere; `spec/SKILL.md:612` → `blockers` overwritten per dispatch, nothing clears it; `spec/SKILL.md:616` → `loops_run` "increments per autopilot iteration", with no condition that a verdict returned — so an errored round advances it; grep `rationale|justif|explain` across `spec/SKILL.md` → **zero hits**, inverting the assumption that an instruction exists to amend; `grep -rn 'challenge\.' plugins/` → readers are exactly `spec`, `plan`, `autopilot`, `reflect` (the `humanize` hit is the English word); `docs/decisions/2026-08-17-extract-review-skills.md:3` → "Handed off to autopilot at Spec", confirming `loops_run: 5` came from the autopilot loop; sweep of `docs/decisions/` for plan-challenger outcomes → blockers 0, 1, 1, 0, 0 with one early exit at 2/3, so the runaway is spec-only; `done/SKILL.md:355` → `rm -rf "$WORKDIR/docs/dev/<feature>/"`, so `spec.md` does not survive the cycle; `done/SKILL.md:313` → decision log's Key Decisions generated from `spec.md`/`plan.md`, so product reasoning is already durable; `validate/SKILL.md:121` → "A reviewer that cannot run stops the stage" precedent; `validate/SKILL.md:236-243` → same-region recurrence + converging-cascade exemption, the repo's existing kind-based loop rule; `sed -n '478p' spec/SKILL.md` → `## Happy Path`, confirming `autopilot/SKILL.md:149`'s citation is broken today.*
