# Challenger Loop Economics — Implementation Plan
*Branch: feature/challenger-loop-economics · 2026-08-22*

## Plan-wide constraints

- **Prose-only surface.** No test runner. Every task's verification is reading the changed prose
  against the success criterion it carries.
- **No new `file:line` citations.** Spec §Out of Scope defers
  `debt-cross-file-line-citations-go-stale-silently` on the grounding that this cycle breaks zero new
  citations. Every cross-reference these tasks add must name a **section or step** (`dev:spec`
  Step 12a, `dev:validate`'s "A reviewer that cannot run stops the stage"), never a line number.
  Task 5's template edit adds two lines above `spec/SKILL.md:478`, so a new citation below it would
  be born stale.
- **state.json changes are additive only.** One new key, `applied_concerns`, in two blocks. Nothing
  is renamed or removed (SC11).

## Files

| File | Action | Purpose |
|------|--------|---------|
| `plugins/dev/skills/spec/SKILL.md` | Modify | Step 12a: Blocker/Concern definitions, exit-as-consequence, drafting-history prohibition, errored-dispatch rule, `applied_concerns` semantics; Step 13 Path A: one new increment line; state.json template: new key in both blocks |
| `plugins/dev/skills/plan/SKILL.md` | Modify | Step 7a: divergence sentence below the Output contract, `challenge_plan.applied_concerns` semantics, SC5-invariant bullet extended; Step 8 Path A: one new increment line |
| `plugins/dev/skills/autopilot/SKILL.md` | Modify | Spec- and plan-challenger sections gain the counter split and the errored-dispatch rule; `## Purpose` stop list gains the twice-errored dispatch |
| `plugins/dev/skills/reflect/SKILL.md` | Modify | Reads `applied_concerns` in both namespaces; `null` counter semantics |
| `CLAUDE.md` | Modify | Component Registry rows for `dev:spec`, `dev:autopilot`, `dev:plan`, `dev:reflect` |

## Tasks

### Task 1: Tighten Blocker, widen Concern in Step 12a's Output contract
What: Redefine `dev:spec` Step 12a's **Blocker** as a two-member class — build-breaking, or right-sizing — and **Concern** as everything else worth flagging, each with a concrete example.
Used by: The cold reviewer reads the Output contract when classifying findings; the autopilot revision loop reads the classification to decide whether to run another round.
Depends on: nothing — first task.
Files: `plugins/dev/skills/spec/SKILL.md` (modify)
Interfaces:
- Consumes: nothing
- Produces: the tightened **Blocker** two-member definition and the widened **Concern** definition in Step 12a's `**Output contract.**` block — the text Task 2's exit sentence, Task 7's divergence sentence, and Task 12's registry row all refer to.
- Shared procedure: none — `dev:plan` Step 7a's Blocker definition is a **deliberate divergence**, not a mirror, and Task 7 states why. Do not touch it here.

Implementation steps:
1. In `plugins/dev/skills/spec/SKILL.md`, locate `**Output contract.** Two severities:` inside `## Step 12a: Cold Review` (currently ~line 582).
2. Replace the **Blocker** bullet. The current text reads: *"cannot stand as written: a requirement reads two ways, sections contradict, a load-bearing claim is unverified, in-scope spans two cycles."* The replacement states a class with exactly two members:
   - **(a) build-breaking** — a builder following the spec literally ships something broken. Give one concrete example drawn from a real class of finding, e.g. a requirement that reads two ways so two builders would ship different behavior, or a load-bearing as-is claim that is false so the work is built on a wrong premise.
   - **(b) right-sizing** — in-scope spans more than one cycle. Carry this criterion over **unchanged in meaning** from the current bullet; it is the class Step 12a's existing **Scope-blocker exception** paragraph depends on. Give one concrete example.
3. Replace the **Concern** bullet — currently *"worth flagging, not fatal"* — with "everything else worth flagging: a finding a builder can act on or ignore without shipping something broken." Give one concrete example drawn from a real class of finding, e.g. a duplicate section label or an imprecise line range.
4. Do **not** add a third severity, a numeric threshold, or a "kind" field. The class has two members and the file has two severities.
5. Leave the **Scope-blocker exception** paragraph byte-unchanged — member (b) is exactly what it keys on, so it keeps working with no edit.
6. Leave the `Verdict format:` fenced block's shape unchanged (`Clarity ⛔1 · Consistency ✅ · Scope ⚠️1 · Grounding ✅`); this task changes what earns a `⛔`, not how one renders.

### Task 2: State the loop exit as a consequence of the definitions
What: Add one sentence to Step 12a saying the loop's exit follows from Task 1's definitions plus the existing "concerns never extend the loop" rule — no new step, test, or severity concept.
Used by: A future editor deciding whether the loop needs an exit test; the cold reviewer and the autopilot loop, which must not look for a mechanism that does not exist.
Depends on: Task 1 — the sentence names the definitions Task 1 writes.
Files: `plugins/dev/skills/spec/SKILL.md` (modify)
Interfaces:
- Consumes: Task 1's tightened **Blocker** / widened **Concern** definitions in Step 12a's Output contract.
- Produces: nothing — terminal for the exit-rule thread.

Implementation steps:
1. Add **one sentence** as adjacent prose immediately below Step 12a's `**Output contract.**` bullet block, after Task 1's edit.
2. The sentence states: once a bookkeeping finding classifies as a Concern rather than a Blocker, the existing **Concerns: countable, foldable, never loop-extending** rule ends the loop by itself — the loop is already gated on blockers existing, so tightening what counts as one is the whole mechanism.
3. **Add nothing else.** No separate exit step, no exit test, no second severity concept, no counter (SC2). If the sentence seems to want a worked example, that belongs in Task 1's definitions instead.
4. Do not renumber or add a step heading. This is prose inside Step 12a.

### Task 3: Add the drafting-history prohibition to Step 12a
What: Instruct the revision loop that a revision replaces text rather than appending an account of the text it replaced, and draw the line explicitly at drafting history vs. product reasoning.
Used by: Every path that revises `spec.md` after its first draft — autopilot's revision loop, and the standard-mode gate's Path A/Path B edits.
Depends on: nothing — independent of Tasks 1 and 2; touches a different paragraph of Step 12a.
Files: `plugins/dev/skills/spec/SKILL.md` (modify)
Interfaces:
- Consumes: nothing
- Produces: nothing — terminal task for the drafting-history thread.

Implementation steps:
1. Insert a new bolded paragraph in `## Step 12a: Cold Review`, immediately **after** the `**Concerns: countable, foldable, never loop-extending.**` paragraph and **before** `**Scope-blocker exception.**`. Both neighbours constrain what a revision may do, which is why it belongs between them.
2. State the rule: a revision **replaces** the text it corrects. It does not append an account of what an earlier draft got wrong, why round 2 differed from round 1, or what the challenger caught — `spec.md` carries no drafting history.
3. State the line explicitly (SC4): the prohibition covers **drafting history**, not **product reasoning**. Name `## Out of Scope` as unaffected — explaining why something is excluded is product reasoning about the feature, not an account of an earlier draft.
4. State the "no replacement home needed" grounding in one clause: product reasoning is already durable because `dev:done` generates the decision log's Key Decisions from `spec.md` and `plan.md`, and `git log -p` on the spec already shows what each round changed. Cite `dev:done` by **step name, not line number** (plan-wide constraint).
5. This rule is **not mode-split** — it holds in standard and autopilot alike. Do not write an autopilot-only variant.

### Task 4: Add the errored-dispatch rule to Step 12a
What: Define what happens when a challenger dispatch returns an error instead of a verdict — counters, retry, STOP, and how a standard-mode STOP is recovered.
Used by: Step 12a's dispatch in both modes; `dev:autopilot`'s stop list (Task 10) names the STOP this task creates.
Depends on: nothing — independent of Tasks 1–3; touches a different paragraph of Step 12a.
Files: `plugins/dev/skills/spec/SKILL.md` (modify)
Interfaces:
- Consumes: nothing
- Produces: the STOP condition **"a challenger dispatch errored twice"** — the exact behavior Task 10 adds to `dev:autopilot`'s `## Purpose` stop list, and the `null` counter values Task 11's reflect prose reads.
- State keys: no new key. `challenge.blockers` and `challenge.concerns` gain a third legal value, `null`, alongside their existing integers. Their write mode is unchanged — `(writes: both)`, per Step 12a's existing counter semantics.

Implementation steps:
1. Insert a new bolded paragraph in `## Step 12a: Cold Review`, immediately **after** the `**Re-run rule.**` paragraph and **before** `**Counter-write semantics.**`, so it sits directly above where the counters it sets are defined.
2. Open with the rule: **an errored dispatch is not an iteration.** When a dispatch returns an error rather than a verdict:
   - do **not** advance `challenge.loops_run`;
   - set `challenge.blockers` and `challenge.concerns` to `null` rather than leaving the previous round's values in place;
   - **retry once** — the retry is once per stage, not once per round;
   - a **second** error **STOPs** the stage and surfaces the failure.
3. State that `null` is a third value distinct from `0`: `0` means a round ran and found nothing; `null` means no round produced a verdict.
4. State that `challenge.run` is **unaffected** by an error — it records whether *any* dispatch this stage returned a verdict, so a clean round followed by an errored one leaves it `true`. `run: false` alongside `blockers: null` is the shape meaning no dispatch ever returned.
5. State that the rule is **not mode-split** (SC5): it holds identically in standard and autopilot, matching `dev:validate`'s **"A reviewer that cannot run stops the stage."** Cite that by section heading — verified present in `plugins/dev/skills/validate/SKILL.md` as the heading `### A reviewer that cannot run stops the stage`, whose body withholds the stage from `completed[]` and leaves `stage` un-advanced.
6. State the standard-mode recovery (SC7), both halves:
   - Recovery is cheap: `spec.md` is already committed and `stage` is still `"spec"`, so re-running `/dev:spec` re-enters at Step 12a through the **resume-mid-approval check** in Step 1. Verified: that check already exists in `plugins/dev/skills/spec/SKILL.md` Step 1 and reads *"skip straight to **Step 12a** — a resumed gate is a new gate arrival, so the challenger re-dispatches and regenerates the verdict."* No new re-entry mechanism is needed and none may be added.
   - The **Step 13 gate does not render on a STOP.** There is no "could not run" gate variant, and no path approves a spec whose cold review never returned a verdict. Letting the gate render without a verdict would invite approving a spec that got no cold review at all — the exact condition Step 12a exists to prevent.
7. Do **not** edit Step 13 itself. This statement lives in Step 12a beside the STOP it qualifies; adding a variant branch to Step 13 is what step 6's second half forbids.

### Task 5: Initialize `applied_concerns: 0` in both blocks of the state.json template
What: Add the new counter to `spec/SKILL.md`'s state.json template in the `challenge` block and the `challenge_plan` block.
Used by: Every cycle initialized after this change; Tasks 6, 8, and 11 all read or write the key this task creates.
Depends on: nothing — independent of Tasks 1–4; a different region of the same file.
Files: `plugins/dev/skills/spec/SKILL.md` (modify)
Interfaces:
- Consumes: nothing
- Produces: the state.json key `applied_concerns` (integer, initialized `0`) in **both** the `challenge` and `challenge_plan` blocks — the key Task 6's semantics, Task 8's mirrored semantics, Task 9's autopilot loops, and Task 11's reflect reads all name.
- State keys: `challenge.applied_concerns` `(writes: both)` and `challenge_plan.applied_concerns` `(writes: both)`. Both mirror the write mode of the existing `applied` counter they sit beside: the autopilot revision loop writes them (Task 6 / Task 8 / Task 9), and in standard mode each gate's **Path A increment list** writes them — a list that enumerates its counters explicitly, so Tasks 6 and 8 each add the missing line rather than assuming coverage. Neither counter's non-default autopilot value depends on a gate write, so the invariant stated in **`dev:plan` Step 7a's counter bullet** ("no counter's *non-default* autopilot value depends on a gate write") continues to hold. Note that bullet's `SC5` label refers to a **prior cycle's** success criterion, not this cycle's errored-dispatch SC5; Task 8 extends the bullet's enumeration without touching that label.

Implementation steps:
1. Locate the state.json template fenced block in `plugins/dev/skills/spec/SKILL.md` (currently ~line 219, in the state-initialization step).
2. In the `"challenge"` object, add `"applied_concerns": 0` on the line that currently reads `"applied": 0, "dismissed": 0,` — keeping `applied` first, so the total reads before its component.
3. Make the **identical** edit in the `"challenge_plan"` object. Both blocks must carry the key: `spec/SKILL.md`'s template is the single initialization point and no later stage re-guards these values (spec §Technical Constraints).
4. Change nothing else in the template. No counter is renamed or removed (SC11); every state.json written before this cycle stays readable by every reader this cycle touches.
5. Do **not** add a `loops_max`-style tier line for this key — it is a counter, not a cap, and needs no per-tier seeding.

### Task 6: Extend Step 12a's counter-write semantics for `applied_concerns` (canonical)
What: State in Step 12a which fixes increment `applied` and which additionally increment `applied_concerns`.
Used by: The autopilot revision loop and the standard-mode gate, both of which write these counters; Task 8 mirrors this text for `challenge_plan`.
Depends on: Task 5 — the key must exist in the template before its write semantics are defined.
Files: `plugins/dev/skills/spec/SKILL.md` (modify)
Interfaces:
- Consumes: `challenge.applied_concerns` (integer, init `0`) from Task 5.
- Produces: the **canonical** counter-write semantics for the `applied` / `applied_concerns` pair — the branch structure Task 8 restates for `challenge_plan` and Task 9 summarizes in `dev:autopilot`.
- State keys: `challenge.applied_concerns` `(writes: both)` — no new key introduced here; Task 5 introduces it, this task defines its writes.
- Shared procedure: **counter-write semantics for the `applied` / `applied_concerns` pair.** This task is the **canonical** implementation; Task 8 is a mirror of it. Step 12a already states that its counter semantics govern both challengers, and `dev:plan` Step 7a already defers to it — this task keeps that relationship and does not invert it.

Implementation steps:
1. In `## Step 12a: Cold Review`, extend the `**Counter-write semantics.**` bullet list. Keep the existing `applied` bullet's meaning intact: `applied` remains the **total** of fixes the challenger caused, `(writes: both)`, cumulative, never reset here.
2. Add `challenge.applied_concerns` `(writes: both)` as a cumulative counter alongside it, and state the full branch structure explicitly:
   - **A fix landed for a Blocker** increments `applied` only.
   - **A fix landed for a Concern** increments `applied` **and** `applied_concerns`.
   - Therefore blocker-driven fixes are `applied - applied_concerns`, and `applied` keeps its current meaning as the total. No fix increments `applied_concerns` without also incrementing `applied`.
   - **Autopilot:** the revision loop writes both itself, per iteration — there is no gate.
   - **Standard:** the Step 13 gate's Path A list writes both. That list enumerates its counters explicitly, so it does **not** cover `applied_concerns` by inheritance — step 3 below adds the line.
3. Edit Step 13 Path A accordingly. It currently reads `- increment challenge.applied by the number of findings applied`; insert directly after it `- increment challenge.applied_concerns by the number of those findings that were Concerns`. **This is the only edit Step 13 takes for this counter** — add no other statement there, and do not touch the surrounding Path A/Path B structure.
4. State the purpose in one clause so the counter is not mistaken for a severity: the split exists so concern-driven growth is **attributable** — on the cycle that produced this item, nobody could say how much of the 346-line growth concerns caused.
5. Leave the existing `**Reading `applied` in autopilot.**` paragraph's claim intact — `applied` is still "fixes the challenger caused," not "blockers found." Extend it only to note that `applied_concerns` is what makes that reading checkable rather than inferred.
6. Do **not** make concerns loop-extending. Concerns stay foldable and never extend the loop (Task 2's rule); this task changes the **instrument**, not the behavior.

**Does not collide with Task 4.** Task 4's step 7 pins "do not edit Step 13," which is about not adding a *gate-rendering variant* for the errored-dispatch STOP. Step 3 here edits Path A's counter list, a different concern in a different part of Step 13. Both hold.

### Task 7: Add the divergence sentence below Step 7a's Output contract
What: Add one sentence of adjacent prose to `dev:plan` Step 7a naming why its Blocker definition diverges from Step 12a's — interpretive vs. mechanical lenses — while leaving the Blocker bullet byte-unchanged.
Used by: A future editor who reads Step 12a's tightened definition and would otherwise "fix" Step 7a to match, silently making a precise mechanical test vaguer.
Depends on: Task 1 — the sentence names the definition Task 1 writes.
Files: `plugins/dev/skills/plan/SKILL.md` (modify)
Interfaces:
- Consumes: Task 1's tightened Blocker definition in `dev:spec` Step 12a.
- Produces: nothing — terminal for the divergence thread.

Implementation steps:
1. In `plugins/dev/skills/plan/SKILL.md` `## Step 7a: Cold Review`, locate `**Output contract.** Two severities:` (currently ~line 226) and its two bullets.
2. **The Blocker bullet is byte-unchanged** (SC3). Do not edit, reword, or reformat it. Verify after editing that the bullet reading *"**Blocker** — cannot stand as written: a spec requirement is uncovered, a task depends on a later task's output, an interface name/type is inconsistent across tasks."* is identical to its pre-edit form.
3. Add **one sentence** as a new paragraph **below the Output contract bullet block** — not inside the bullet, and not inside the `**Every Blocker must carry a pre-drafted suggested fix**` paragraph that follows.
4. The sentence states: Step 7a's Blocker definition deliberately diverges from `dev:spec` Step 12a's build-breaking bar because the plan's three lenses are **mechanical** (coverage, sequencing, interfaces) while the spec's are **interpretive** — severity inflated there and not here, and rewording a precise mechanical test into build-breaking language would make it vaguer.
5. Reference Step 12a **by step name only** — no line number (plan-wide constraint).

### Task 8: Mirror the `applied_concerns` semantics into Step 7a
What: State in `dev:plan` Step 7a which fixes increment `challenge_plan.applied` and which additionally increment `challenge_plan.applied_concerns`.
Used by: The autopilot plan-challenger revision loop and the Step 8 gate, both of which write these counters.
Depends on: Task 5 (the key exists in the template) and Task 6 (the canonical text this mirrors).
Files: `plugins/dev/skills/plan/SKILL.md` (modify)
Interfaces:
- Consumes: `challenge_plan.applied_concerns` (integer, init `0`) from Task 5; Task 6's canonical branch structure.
- Produces: nothing — terminal for the plan-side counter thread.
- State keys: `challenge_plan.applied_concerns` `(writes: both)` — no new key introduced here; Task 5 introduces it, this task defines its plan-side writes.
- Shared procedure: **counter-write semantics for the `applied` / `applied_concerns` pair.** This task is a **mirror of Task 6**, which is canonical. Mark it as such in the prose: Step 7a already states that `dev:spec` Step 12a's counter semantics govern both challengers, so this text defers rather than competes.

Implementation steps:
1. In `plugins/dev/skills/plan/SKILL.md` `## Step 7a: Cold Review`, extend the `**Counter-write semantics.**` bullet list. Keep the existing `challenge_plan.applied` bullet's meaning intact: still the **total**, `(writes: both)`, cumulative, never reset here.
2. Restate the branch structure **in full** — the Isolation Principle forbids "same as Task 6," and two independently-written implementations of one procedure drift:
   - **A fix landed for a Blocker** increments `challenge_plan.applied` only.
   - **A fix landed for a Concern** increments `challenge_plan.applied` **and** `challenge_plan.applied_concerns`.
   - Blocker-driven fixes are `applied - applied_concerns`; no fix increments `applied_concerns` without also incrementing `applied`.
   - **Autopilot:** the revision loop writes both itself, per iteration.
   - **Standard:** the Step 8 gate's Path A list writes both. That list enumerates its counters explicitly, so it does **not** cover `applied_concerns` by inheritance — step 3 below adds the line.
3. Edit Step 8 Path A accordingly. It currently reads `- increment challenge_plan.applied by the number of findings applied`; insert directly after it `- increment challenge_plan.applied_concerns by the number of those findings that were Concerns`. **This is the only edit Step 8 takes for this counter** — add no other statement there, and do not touch the surrounding Path A/Path B structure.
4. Extend Step 7a's existing invariant bullet — the one reading *"The SC5 invariant holds by construction: no counter's non-default autopilot value depends on a gate write — `applied` has an autopilot-path writer here (the revision loop), and `dismissed`'s autopilot-correct value is its init default `0`"* — to name `applied_concerns` as also having an autopilot-path writer (the revision loop). Extend the **enumeration only**; leave the `SC5` label alone, since it refers to a prior cycle's criterion. An enumeration that silently omits a third counter is how the next editor concludes the invariant was never checked for it.
5. Add the one-clause deference: this is the same rule as `dev:spec` Step 12a's, which governs both challengers — named by step, not line.
6. This task carries the **counter shape** change only. It must not touch Step 7a's Blocker definition (Task 7's step 2 pins that byte-unchanged), and it must not import Step 12a's build-breaking bar by reference.

### Task 9: Carry the counter split and the errored-dispatch rule into `dev:autopilot`'s challenger sections
What: Update `dev:autopilot` Step 2's spec-challenger and plan-challenger paragraphs so the loop they describe writes `applied_concerns` and does not count an errored dispatch as an iteration.
Used by: The autopilot orchestrator, which runs both loops from these paragraphs rather than from the stage skills' prose.
Depends on: Task 4 (the errored-dispatch rule), Task 6 (the canonical counter semantics), Task 8 (the plan-side mirror).
Files: `plugins/dev/skills/autopilot/SKILL.md` (modify)
Interfaces:
- Consumes: Task 4's errored-dispatch rule; Task 6's and Task 8's `applied` / `applied_concerns` branch structure.
- Produces: nothing — terminal for the autopilot loop-body thread.
- State keys: `challenge.applied_concerns` `(writes: both)`, `challenge_plan.applied_concerns` `(writes: both)` — introduced by Task 5; this task states the autopilot-side write for both.
- Shared procedure: **counter-write semantics for the `applied` / `applied_concerns` pair.** This task is a **summary restatement**, not a third independent definition: `dev:spec` Step 12a (Task 6) is **canonical** and `dev:plan` Step 7a (Task 8) is its **mirror**. Say so in the prose and cite Step 12a by step name, so an editor reading `autopilot/SKILL.md` alone can see where the rule is owned — the repo's convention is that duplication is named at **both** ends.

Implementation steps:
1. In `**Spec challenger: bounded revision loop.**` (currently ~line 139), extend the existing sentence *"`applied` therefore counts blocker and concern fixes alike; `loops_run` is the blocker-driven number"* so it also names `applied_concerns`: a concern fix increments both `applied` and `applied_concerns`; a blocker fix increments `applied` only; blocker-driven fixes are the difference.
2. In the same paragraph, add the errored-dispatch behavior in the loop's own terms: an errored dispatch does **not** advance `challenge.loops_run`, sets `challenge.blockers` / `challenge.concerns` to `null`, retries once, and STOPs on a second error. Defer to `dev:spec` Step 12a as the statement of the rule rather than restating its full reasoning — the rule is not mode-split, so autopilot carries the loop-bookkeeping half only.
3. In `**Plan challenger: bounded revision loop.**` (currently ~line 141), make the matching `applied_concerns` edit for `challenge_plan`, restating the branch structure rather than pointing at the paragraph above it.
4. **Do not** add an errored-dispatch rule to the plan-challenger paragraph. Spec §Scope item 3 scopes the errored-dispatch rule to the spec challenger; the counter *shape* change is what applies to both.
5. Leave the **scope-blocker bypass** asymmetry exactly as it stands — spec challenger has one, plan challenger explicitly does not.

### Task 10: Name the twice-errored dispatch in `dev:autopilot`'s stop list
What: Add the new STOP condition to the "When autopilot stops" list in `dev:autopilot`'s `## Purpose`.
Used by: The operator reading what can halt an unattended run; `dev:done`'s and `dev:reflect`'s accounts of why a run stopped.
Depends on: Task 4 — the STOP must exist before it is listed.
Files: `plugins/dev/skills/autopilot/SKILL.md` (modify)
Interfaces:
- Consumes: Task 4's STOP condition, "a challenger dispatch errored twice."
- Produces: nothing — terminal task.

Implementation steps:
1. Locate the `**When autopilot stops:**` sentence in `## Purpose` (currently ~line 14).
2. Add one clause to the existing comma-separated list, phrased to match its neighbours (which read *"a build failure at Validate (see `dev:validate` Step 5b)"*, *"a reviewer that cannot run at Validate (see `dev:validate` Step 2)"*): a challenger dispatch that errored twice at Spec, citing `dev:spec` Step 12a.
3. Place it adjacent to the existing challenger clauses (`a spec-challenger scope blocker`, `challenger blockers remaining after challenge.loops_max revisions`) so the challenger stop conditions read together.
4. Change nothing else in the sentence — the list's other clauses and the trailing `dev:reflect` Step 4 pause note stay as they are.

### Task 11: Teach `dev:reflect` to read `applied_concerns` and `null` counters
What: Extend `dev:reflect`'s metric-extraction list to read `challenge.applied_concerns` and `challenge_plan.applied_concerns` in the two namespaces it already reads separately, and to read a `null` counter as "no verdict returned this round."
Used by: The retrospective's spec-quality and plan-quality readings.
Depends on: Task 5 (the key exists) and Task 4 (the `null` value exists).
Files: `plugins/dev/skills/reflect/SKILL.md` (modify)
Interfaces:
- Consumes: `challenge.applied_concerns` / `challenge_plan.applied_concerns` (integer, may be absent) from Task 5; the `null` value for `blockers` / `concerns` from Task 4.
- Produces: nothing — terminal task.

Implementation steps:
1. In the "Extract key metrics from state.json" list, add `applied_concerns` to the `challenge.*` bullet and to the `challenge_plan.*` bullet — **both**, in the two namespaces the file already reads separately (SC10). Do not merge the two bullets.
2. State that a **missing** `applied_concerns` reads as **"not recorded"**, never as `0` — matching the file's existing missing-block semantics, which already say a missing `challenge` block means the challenger did not run and is *"not an error and not a zero-finding run."* Cycles predating this change are not retrofitted.
3. State that a `null` counter means **"no verdict returned this round,"** distinct from `0` meaning **"a round ran and found nothing."** Apply this to `blockers` and `concerns`, the two counters Task 4 can set `null`.
4. Add no numeric thresholds for the new counter, in either namespace — the file's existing rule for `challenge_plan` is *"Keep it qualitative — **no numeric thresholds** (no distribution of these counters exists yet)"*, and no distribution of `applied_concerns` exists either. If a qualitative reading is added to the plan-quality or spec-quality section, it must say what the counter *attributes* (how much churn concerns caused), not what value is good.

### Task 12: Update the Component Registry rows
What: Update `CLAUDE.md`'s Component Registry rows for `dev:spec`, `dev:autopilot`, `dev:plan`, and `dev:reflect` to describe the changed behavior.
Used by: Every future session — the registry is auto-loaded context and is how the next cycle finds this behavior.
Depends on: Tasks 1–11 — the rows describe behavior those tasks land.
Files: `CLAUDE.md` (modify)
Interfaces:
- Consumes: the changed behavior from every prior task.
- Produces: nothing — terminal task.

Implementation steps:
1. `dev:spec` row: Step 12a's Blocker is now a **two-member class** (build-breaking, plus the right-sizing criterion carried over so the scope-blocker exception survives), Concern absorbs the rest, and the loop's exit is a **consequence** of those definitions plus the existing concerns rule — no new exit mechanism. Also: the drafting-history prohibition, the errored-dispatch rule (no `loops_run` advance, `null` counters, one retry, second error STOPs, **not mode-split**), and `applied_concerns` as the **canonical** half of the counter split.
2. `dev:autopilot` row: the stop list now names a twice-errored challenger dispatch at Spec; both challenger loops write `applied_concerns`. **Correct the existing row's trailing claim** — it currently ends *"The 'When autopilot stops' list in `## Purpose` is unchanged by this cycle…"*, which Task 10 makes false. Rewrite that clause rather than appending a contradicting one.
3. `dev:plan` row: Step 7a's Blocker definition is **deliberately unchanged** and now carries adjacent prose naming the interpretive-vs-mechanical divergence from Step 12a; its counter semantics are a **mirror** of Step 12a's canonical `applied` / `applied_concerns` pair.
4. `dev:reflect` row: reads `applied_concerns` in both namespaces, treats a missing key as "not recorded" and a `null` counter as "no verdict returned."
5. Update the `*Last updated by /dev · YYYY-MM-DD*` stamp under `## Component Registry` to this cycle's date.
6. Touch no other row.

## Edge Cases

| Edge case | Handled in | Approach |
|-----------|-----------|----------|
| Errored dispatch | Task 4 | One retry per stage (not per round), `loops_run` not advanced, `blockers`/`concerns` set `null`, second error STOPs — identical in both modes |
| Scope blockers must survive the tightening | Task 1 | Blocker defined as a two-member class whose member (b) is the right-sizing criterion; Step 12a's Scope-blocker exception paragraph left byte-unchanged so it keeps keying on it |
| `challenge.run` after a mixed sequence | Task 4 | Stated explicitly: `run` records whether *any* dispatch this stage returned a verdict, so clean-then-errored leaves it `true`; `run: false` + `blockers: null` is the never-returned shape |
| A reviewer that mis-classifies severity defeats the exit | Tasks 1, 2 | Accepted deliberately — no backstop test is added (SC2 forbids the second severity concept). The failure surfaces at Reflect as high `blockers` against low `spec_revisions` persisting across cycles |
| Round 1 returns 0 Blockers | Task 2 | Unchanged — the loop is already gated on blockers existing, which is why the exit needs no new mechanism |
| Historical `state.json` has no `applied_concerns` | Task 11 | Read as "not recorded," never `0`, matching the file's existing missing-block semantics; no retrofit |
| Standard mode | Tasks 1, 4, 6 | Nothing is mode-split: definitions change what the Step 13 gate displays, the errored-dispatch STOP holds in both modes, and the counter pair is `(writes: both)` |
| Step 13 gate on a STOP | Task 4 | Explicitly does not render; no "could not run" gate variant is added, and recovery is re-running `/dev:spec` through Step 1's existing resume-mid-approval check |
| `dev:plan` Step 7a's Blocker definition | Tasks 7, 8 | Byte-unchanged and verified so after editing; only adjacent prose and the counter shape change |

## Out of Scope

Carried from spec §Out of Scope — no task may widen into these:

- **The plan challenger's Blocker definition** — mechanical lenses, self-limiting in the recorded history (blockers 0, 1, 1, 0, 0). Task 7 explains the divergence; it does not close it.
- **Lowering the deep-tier cap from 5 to 3** — the kind-based exit is now what stops the loop; the cap is a rarely-binding backstop.
- **`debt-cross-file-line-citations-go-stale-silently`** — not folded in. The plan-wide "no new `file:line` citations" constraint keeps this cycle's promise of zero newly-broken citations without paying the item.
- **Persisting the challenger verdict text** — unchanged.
- **Numeric thresholds for the new counter in `dev:reflect`** — no distribution exists yet.
- **Telemetry schema changes** — owned by `telemetry-schema` in the `dev-observability` plan.
