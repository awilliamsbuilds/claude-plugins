# Spec Review Autoloop — Implementation Plan
*Branch: feature/spec-review-autoloop · 2026-11-10*

## Files

| File | Action | Purpose |
|------|--------|---------|
| plugins/dev/skills/spec/SKILL.md | Modify | Canonical loop rule (Step 12a), new gate (Step 13), resume (Step 1) |
| plugins/dev/skills/plan/SKILL.md | Modify | Mirror of the loop rule, errored-dispatch mirror, gate (Step 8), resume (Step 1), `plan_end` re-stamp |
| plugins/dev/skills/autopilot/SKILL.md | Modify | Restate the rule in both challenger sections, and update the stop list |
| plugins/dev/skills/reflect/SKILL.md | Modify | Readings of `loops_run` / `dismissed` / `applied` under the loop rule |
| plugins/dev/references/telemetry.md | Modify | Adjacent fix (Build): the `null`-counter note now covers `challenge_plan` too, since Task 3 mirrors the errored-dispatch rule |

## The Loop Rule (the procedure every task below implements or restates)

Stated here once so each task can restate it verbatim. Tasks still restate it in full, per the Isolation Principle.

- **Round:** one cold-review dispatch that returns a verdict. An errored dispatch is not a round.
- **Heavy round:** the verdict has ≥1 Blocker **or** ≥5 Concerns. Otherwise the round is **light**.
- **Branches** (evaluated after each round, both modes):
  1. **Scope blocker present** (spec only): apply none of the round's fixes and exit with `exit: scope`.
  2. **Light:** apply every suggested fix, commit `<stage>: apply challenger fixes for <feature>`, and exit with `exit: clean`. A light round with zero findings applies nothing, makes no commit, and exits `clean`.
  3. **Heavy, `loops_run < loops_max` after this round:** apply every suggested fix, commit, and dispatch the next round on the revised artifact.
  4. **Heavy, `loops_run == loops_max` after this round:** apply none of the round's fixes and exit with `exit: limit`. The findings stay unresolved.
- `loops_run` increments by 1 per round (verdict returned), in both modes. Cap: `loops_max` (micro 1 / standard 3 / deep 5).
- **Exit handling:** standard renders the gate once (Task 2 / Task 4). Autopilot continues on `clean` and STOPs on `limit` or `scope`, surfacing the unresolved findings.
- **Counters per applied fix:** a Blocker fix increments `applied`. A Concern fix increments `applied` and `applied_concerns`. Each round's commit carries the counter writes.

## Tasks

### Task 1: Canonical loop rule in `dev:spec` Step 12a
What: Replace Step 12a's mode-split advisory/teeth text with the single loop rule, making Step 12a the canonical statement.
Used by: `dev:spec` Step 13 (Task 2) renders the loop's exit. `dev:plan` Step 7a (Task 3) and `dev:autopilot` (Task 5) mirror or restate it. `dev:reflect` (Task 6) reads its counters.
Depends on: nothing — first task
Files: plugins/dev/skills/spec/SKILL.md
Interfaces:
- Consumes: nothing
- Produces: the named rule "**the review loop**" with terms *round*, *heavy round*, *light round*, and exits `clean` / `limit` / `scope`, all defined in Step 12a. A `### The review loop` sub-heading (or a bold paragraph lead of the same name) that Tasks 2–6 cite as "`dev:spec` Step 12a's review loop".
- State keys: no new key. `challenge.loops_run` changes annotation from `(writes: autopilot-only)` to `(writes: both)`.
- Shared procedure: "the review loop". **Canonical** here. Task 3 is its mirror, and Task 5 restates it.

Implementation steps:
1. Replace **"Mode behaviour — standard: advisory"** and **"Mode behaviour — autopilot: teeth"** (spec:674–676) with one **"The review loop"** paragraph block. It states the definitions and the four branches from "The Loop Rule" above, the `loops_max` cap (micro 1 / standard 3 / deep 5), and this mode split, which concerns the exit only: standard renders Step 13 once after exit, while autopilot continues on `clean` and STOPs on `limit`/`scope`, surfacing unresolved findings. Include one sentence of reasoning: a heavy round's fixes are never applied unreviewed, because they either get a following round or go to a human.
2. Replace **"Concerns: countable, foldable, never loop-extending."** (spec:678) with **"Concerns: counted, applied, loop-extending only at five."** Concerns are counted in `challenge.concerns`. Every light or non-final round applies its concern fixes in both modes. 5+ concerns make a round heavy. Fewer than 5 never extend the loop.
3. Rewrite spec:653 ("The autopilot loop's exit follows from these two definitions plus …never loop-extending…"). The loop's exit now follows from the Blocker/Concern definitions plus the heavy-round threshold, in both modes. Still no separate exit step and no second severity concept.
4. Rewrite **Scope-blocker exception** (spec:682). A round containing a scope blocker takes branch 1 in both modes: no fixes applied, exit `scope`. Standard surfaces it at Step 13, and acting on it means rescoping through Step 4. Autopilot STOPs. Delete "In standard mode a scope blocker is advisory like any other finding."
5. Replace **Re-run rule** (spec:684). Dispatches are driven only by the review loop. A Path A `apply` at the Step 13 gate (leftovers from a `limit` exit) does **not** re-dispatch or start a new loop.
6. Errored-dispatch paragraph (spec:686–696). Retitle it "An errored dispatch is not a round", and rewrite spec:692's re-entry sentence to "re-enters the review loop with `loops_run` carried forward". Otherwise keep it. Change "Retry once — once per stage, not once per round" to add that this now matters in both modes, since both loop. Confirm that no sentence claims standard mode does not loop.
7. Counter-write semantics (spec:698–711):
   - Replace "In standard mode Step 13 writes them at the gate. In autopilot there is no gate, so the revision loop writes…" with "The review loop writes `applied` and `applied_concerns` itself, per round, in both modes. Step 13's Path A writes them only for `limit`/`scope` leftovers the user applies at the gate."
   - Replace the `dismissed` sentence ("stays `0` in autopilot — … unactioned concerns pass through by design …") with: `dismissed` `(writes: standard; =default 0 in autopilot)` counts findings the user declines at the Step 13 gate (leftovers approved past, or auto-applied fixes reverted). In autopilot it stays 0, because unresolved findings STOP rather than being declined.
   - Add: a reverted auto-applied fix is not subtracted from `applied`/`applied_concerns`, so it counts in both `applied` and `dismissed`.
   - Replace the "Autopilot:/Standard:" sub-bullets under "Which counter a fix increments" with "The review loop writes both, per round, in both modes. Step 13's Path A writes both for leftovers it applies, naming each counter directly."
   - Rewrite **"Reading `applied` in autopilot"** (spec:708–710). Drop "loops are what blockers actually drive". Instead, `loops_run` counts rounds and a round is extended by a blocker **or** 5+ concerns, so pair `loops_run` with `blockers`/`concerns` (the last round's tally) and `applied_concerns` to tell which drove it.
   - Change the `challenge.loops_run` bullet to `(writes: both)`: increments per round in both modes.
8. Replace **"Which commit carries the counters"** (spec:713). Each review-loop round that applies fixes commits `spec: apply challenger fixes for <feature-name>` and that commit carries the counters. A round that applies nothing (a zero-finding light round, or a `limit`/`scope` exit) commits nothing, and its counter writes ride the next commit (Step 13's Path A or approval commit in standard, the next stage's commit in autopilot).
9. Add a **`spec_end` re-stamp** to the loop's exit: after the loop exits (any exit), re-stamp `metrics.stage_timestamps.spec_end`. This is in addition to Step 13's Path A/B re-stamps.
10. Keep the drafting-history prohibition, dispatch, lenses, verdict format and Fallback untouched. Update only the sentence in the prohibition that names "autopilot's revision loop and … the standard-mode gate's Path A and Path B edits", so it reads "the review loop (both modes) and the gate's Path A and Path B edits".

### Task 2: `dev:spec` Step 13 gate and Step 1 resume
What: Make the Step 13 gate render the loop's outcome (per-round log + one approval question), and make Step 1's resume carry `loops_run` forward.
Used by: the user at the standard-mode Spec gate. The resume path after `/clear`.
Depends on: Task 1 (cites "`dev:spec` Step 12a's review loop" and its exits `clean`/`limit`/`scope`)
Files: plugins/dev/skills/spec/SKILL.md
Interfaces:
- Consumes: Task 1's review loop, exits `clean` / `limit` / `scope`, and its counter semantics
- Produces: the **per-round log** gate format (also restated by Task 4 for Plan); the resume rule "carry `loops_run` forward; at `loops_run == loops_max` re-dispatch once to regenerate leftovers, not counted as a round"
- State keys: none new

Implementation steps:
1. Replace the gate body template (spec:725–734) with:
   ```
   Spec written and committed to docs/dev/<feature-name>/spec.md.

   Cold review — <N> round(s):
     Round 1: <per-lens tally header> — applied <k> fix(es): <one line each, ≤ 8 words>
     Round 2: …
   [exit clean, final round had zero findings: "Round <n>: clean"]

   [exit limit: "Round limit (<loops_max>) reached — these findings are unresolved:" then the last round's findings verbatim with suggested fixes]
   [exit scope: "Scope blocker — this spec spans more than one cycle:" then the scope finding verbatim, plus any other findings from that round]
   [exit limit or scope only: Reply `apply` to take the suggested fixes, apply selectively, edit directly, rescope, or approve as-is.]

   Every fix above is committed. Revert or edit any of them, or approve the spec.
   ```
2. **Path A** (spec:744–753): restrict to leftovers from a `limit`/`scope` exit. Keep its increment list (`applied`, `applied_concerns`, `dismissed` for declined leftovers), the `spec_end` re-stamp, the "do not increment `spec_revisions`" rule, and the commit. Keep "re-display the gate **without re-dispatching**".
3. **Path B** (spec:758): add that reverting an auto-applied fix is a Path B change. It increments `spec_revisions` and increments `challenge.dismissed` by the number of fixes reverted, with no change to `applied`/`applied_concerns`, and no re-review.
4. **When approved** (spec:764): keep the rule that approving past unactioned findings increments `dismissed`, now scoped to `limit`/`scope` leftovers (auto-applied fixes are not "unactioned").
5. **Step 1 resume-mid-approval check** (spec:54): replace "a resumed gate is a new gate arrival, so the challenger re-dispatches… `run`, `blockers`, and `concerns` are overwritten; `applied`, `applied_concerns`, and `dismissed` carry forward" with these two branches:
   - `challenge.loops_run < challenge.loops_max`: re-enter Step 12a's review loop with `loops_run` carried forward, so only the remaining rounds are available.
   - `challenge.loops_run == challenge.loops_max`: dispatch once to regenerate the leftover findings, because verdict text is not persisted. This dispatch is not a round: do not advance `loops_run` and apply nothing. Then render Step 13 as a `limit` exit.
   - On that limit-resume, the gate's per-round log shows only `<loops_run> round(s) ran; per-round detail not persisted`. The regenerated verdict renders under the limit line whatever its weight, and zero findings renders as "no unresolved findings". If the regenerating dispatch errors, Step 12a's errored-dispatch rule applies (one retry, then STOP).
   - Both branches: `run`/`blockers`/`concerns` are overwritten by any dispatch; `applied`, `applied_concerns`, `dismissed`, `loops_run` carry forward.
6. Leave the resume-block ordering, Branch A/B offer logic and the "What this offer deliberately does not do" paragraphs untouched.

### Task 3: `dev:plan` Step 7a — mirror of the review loop, errored-dispatch mirror, `plan_end`
What: Make Step 7a run the same review loop as `dev:spec` Step 12a (mirror), add the errored-dispatch rule (mirror), and re-stamp `plan_end` after the loop.
Used by: `dev:plan` Step 8 (Task 4); `dev:autopilot` plan-challenger section (Task 5).
Depends on: Task 1 (cites it as canonical; must match its final wording)
Files: plugins/dev/skills/plan/SKILL.md
Interfaces:
- Consumes: Task 1's review loop definition and errored-dispatch rule (`dev:spec` Step 12a)
- Produces: plan-side review loop with exits `clean` / `limit` (no `scope` exit); `challenge_plan.*` counter semantics; `plan_end` re-stamp rule
- State keys: no new key. `challenge_plan.loops_run` annotation changes from `(writes: autopilot-only)` to `(writes: both)`.
- Shared procedure: "the review loop" — **mirror of Task 1**; also "errored-dispatch rule" — **mirror of `dev:spec` Step 12a** (canonical, existing)

Implementation steps:
1. Replace **"Mode behaviour — standard: advisory"** and **"autopilot: teeth"** (plan:243–245) with a **"The review loop"** block, marked "mirror of `dev:spec` Step 12a's review loop (canonical)". Restate in full:
   - Round = a dispatch that returns a verdict.
   - Heavy = ≥1 Blocker or ≥5 Concerns. Light = otherwise.
   - Branches: **(1) Light:** apply every fix, commit `plan: apply challenger fixes for <feature>`, exit `clean`. A zero-finding light round applies and commits nothing. **(2) Heavy with rounds remaining:** apply every fix, commit, re-dispatch on the revised `plan.md`. **(3) Heavy on the last allowed round:** apply none, exit `limit`.
   - Cap `challenge_plan.loops_max` (standard 3 / deep 5; micro never reaches Plan).
   - Exit handling: standard renders Step 8 once, while autopilot continues on `clean` and STOPs on `limit`.
   - **No scope exit:** keep the existing "There is NO scope-blocker bypass class" sentence and its reasoning.
2. Replace the "see `dev:spec` Step 12a's 'Concerns: countable, foldable, never loop-extending'" reference with "Concerns: counted, applied, loop-extending only at five — as `dev:spec` Step 12a states".
3. Add an **"An errored dispatch is not a round"** paragraph, marked "mirror of `dev:spec` Step 12a (canonical)". Restate it in full: a dispatch that returns an error (subagent fails, dispatch refused, non-verdict output) does not advance `challenge_plan.loops_run`, and sets `challenge_plan.blockers`/`concerns` to `null`. It is retried once per stage (not per round), and a second error STOPs the stage in both modes. It is distinct from the Fallback (no subagent facility: run in-session, produce a real verdict), and the discriminator is whether a verdict came back. `null` ≠ `0`. `challenge_plan.run` records whether any dispatch returned a verdict. Standard-mode recovery: re-run `/dev:plan`, which re-enters via Step 1's resume check. Step 8's gate does not render on a STOP; there is no "could not run" variant.
4. Counter-write semantics (plan:247–257). Make the same changes as Task 1 step 7, with `challenge_plan.*` names: the loop writes `applied`/`applied_concerns` per round in both modes; Step 8 Path A writes them only for `limit` leftovers; the `dismissed` sentence is as in Task 1 step 7; a revert is not subtracted; `challenge_plan.loops_run` becomes `(writes: both)`. Keep the SC5-invariant bullet, and update its wording to "the review loop" as the autopilot-path writer.
5. Replace **Re-run rule** (plan:259) with the same text as Task 1 step 5, citing Step 8.
6. Replace **"Which commit carries the counters"** (plan:261) with the same text as Task 1 step 8 (commit message `plan: apply challenger fixes for <feature>`; a no-fix round's writes ride Step 8's commit in standard or Build's first commit in autopilot).
7. **`plan_end` re-stamp:** in Step 7, leave the first `plan_end` stamp. Add to the review-loop block: "after the loop exits (any exit), re-stamp `metrics.stage_timestamps.plan_end`". (The Path A/B re-stamps are Task 4 steps 2–3's job.) This mirrors `dev:spec`'s `spec_end` re-stamps and closes `debt-plan-end-excludes-challenger-loop`.

### Task 4: `dev:plan` Step 8 gate and Step 1 resume
What: Make the Plan gate render the loop's outcome with the per-round log, and make Step 1's resume carry `loops_run` forward.
Used by: the user at the standard-mode Plan gate. The resume path after `/clear`.
Depends on: Task 2 (restates its gate format and resume rule), Task 3 (cites Step 7a's review loop and exits `clean`/`limit`)
Files: plugins/dev/skills/plan/SKILL.md
Interfaces:
- Consumes: Task 3's plan-side review loop and exits. Task 2's per-round log format and resume rule.
- Produces: nothing — terminal for Plan
- State keys: none new
- Shared procedure: "per-round log gate" and "resume carry-forward". **Mirror of Task 2** (canonical in `dev:spec` Step 13 / Step 1).

Implementation steps:
1. Replace the Step 8 gate body (plan:265–273) with the per-round log, restated in full:
   ```
   Plan written and committed to docs/dev/<feature>/plan.md.

   Cold review — <N> round(s):
     Round 1: <per-lens tally header> — applied <k> fix(es): <one line each, ≤ 8 words>
     …
   [exit clean, final round zero findings: "Round <n>: clean"]

   [exit limit: "Round limit (<loops_max>) reached — these findings are unresolved:" then the last round's findings verbatim with suggested fixes, then: Reply `apply` to take the suggested fixes, apply selectively, edit directly, or approve as-is.]

   Every fix above is committed. Revert or edit any of them, or approve the plan to start building.
   ```
   There is no scope variant, because Plan has no scope exit.
2. **Path A:** restrict it to `limit` leftovers. Keep its increment list (`challenge_plan.applied`, `challenge_plan.applied_concerns`, `challenge_plan.dismissed` for declined leftovers) and its commit. Add a `plan_end` re-stamp, and keep "without re-dispatching".
3. **Path B:** add that reverting an auto-applied fix is a Path B change. It increments `challenge_plan.dismissed` by the number reverted, with no change to `applied`/`applied_concerns`, and no re-review. It re-stamps `plan_end`.
4. **When approved:** scope the "approved past unactioned findings → increment `dismissed`" rule to `limit` leftovers.
5. **Step 1 resume-mid-approval check** (plan:54): replace it with the two branches from Task 2 step 5, using `challenge_plan.*` names and Step 7a / Step 8:
   - `loops_run < loops_max`: re-enter Step 7a's review loop with `loops_run` carried forward.
   - `loops_run == loops_max`: dispatch once to regenerate leftovers, without counting a round or applying anything, then render Step 8 as a `limit` exit.
   - On that limit-resume, the per-round log shows only `<loops_run> round(s) ran; per-round detail not persisted`. The regenerated verdict renders under the limit line whatever its weight, and zero findings renders as "no unresolved findings". An erroring regenerating dispatch follows Step 7a's errored-dispatch rule.
   - Both: `run`/`blockers`/`concerns` are overwritten by any dispatch, and `applied`, `applied_concerns`, `dismissed`, `loops_run` carry forward.

### Task 5: `dev:autopilot` — restate the rule, update the stop list
What: Bring autopilot's two challenger sections and its `## Purpose` stop list in line with the single review loop and the plan errored-dispatch rule.
Used by: `dev:autopilot` runs. Readers checking when autopilot stops.
Depends on: Task 1, Task 3 (restates both; must match final wording)
Files: plugins/dev/skills/autopilot/SKILL.md
Interfaces:
- Consumes: Task 1's review loop (canonical), Task 3's plan mirror and plan errored-dispatch rule
- Produces: nothing — terminal
- State keys: none new
- Shared procedure: "the review loop". **Restatement** of Task 1, marked as a summary that names `dev:spec` Step 12a as canonical and `dev:plan` Step 7a as mirror.

Implementation steps:
1. **## Purpose stop list** (autopilot:14): replace "challenger blockers remaining after `challenge.loops_max` revisions" and "plan-challenger blockers remaining after `challenge_plan.loops_max` revisions" with "a spec or plan review loop that exits on its round limit — a final round with a blocker or 5+ concerns (see `dev:spec` Step 12a's review loop)". Change "a challenger dispatch that errored twice at Spec" to "a challenger dispatch that errored twice at Spec or Plan". Keep "a spec-challenger scope blocker".
2. **"Spec challenger: bounded revision loop"** (autopilot:151): rewrite as a summary restatement. Each round applies every suggested fix. A round is heavy at ≥1 blocker or ≥5 concerns. A heavy round with rounds remaining re-dispatches, and a light round exits. A heavy round on the last allowed round applies nothing and STOPs, surfacing the findings. Cap `challenge.loops_max` (1/3/5). Scope blockers apply nothing and STOP immediately. Keep the `applied`/`applied_concerns` split sentences. Delete "A concern is never a reason to loop…" and "`loops_run` is the blocker-driven number". Replace them with "`loops_run` counts rounds, in both modes". Name `dev:spec` Step 12a as canonical, and note that standard mode runs the same loop and differs only in exit (the gate instead of STOP).
3. **"Spec challenger — an errored dispatch is not an iteration"** (autopilot:153): rename to "Spec and plan challengers — an errored dispatch is not a round". Delete "standard mode never loops, so one retry per stage and one per round are indistinguishable there". Replace it with "both modes loop, so the per-stage scoping matters everywhere; a deep-tier run reading it per-round would grant five retries instead of one". State that it applies to both challengers: `dev:spec` Step 12a is canonical and `dev:plan` Step 7a is the mirror.
4. **"Plan challenger: bounded revision loop"** (autopilot:155): rewrite as the same summary as step 2, with `challenge_plan.*` names and cap `challenge_plan.loops_max` (standard 3 / deep 5). Keep the no-scope-blocker-bypass sentence. Delete "The **errored-dispatch rule does not apply here**…" and replace it with "The errored-dispatch rule applies (see above)." Change "If blockers remain after the cap → STOP" to "A heavy final round → STOP".

### Task 6: `dev:reflect` — readings under the loop rule
What: Update reflect's metric readings so `loops_run`, `dismissed`, and `applied` are read correctly when gated cycles also loop.
Used by: `dev:reflect` Steps 1–2, invoked from `dev:pr` Step 5d.
Depends on: Task 1, Task 3 (reads the counter semantics they define)
Files: plugins/dev/skills/reflect/SKILL.md
Interfaces:
- Consumes: Task 1 / Task 3 counter semantics (`loops_run` `(writes: both)`, `dismissed` = declined at the gate, revert counts in both `applied` and `dismissed`)
- Produces: nothing — terminal
- State keys: none new

Implementation steps:
1. In Step 1's `challenge.*` / `challenge_plan.*` extraction bullets (reflect:42–43), add: "`loops_run` counts review rounds in both modes. On cycles predating the review loop it is `0` in standard mode, meaning one advisory round ran, not that none did. Read it alongside `run`."
2. Replace the `challenge.dismissed` reading (reflect:70) with: "`challenge.dismissed` counts what the user declined **at the gate**: limit/scope leftovers approved past, or auto-applied fixes reverted. A high value on a cycle that hit its round limit says the leftovers weren't worth fixing. A high value from reverts says the challenger's fixes were wrong, which is a signal about the brief."
3. In the `challenge.applied_concerns` reading (reflect:71), replace "read a large concern share alongside `loops_run`" with "read it alongside `loops_run`, which since the review loop is extended by blockers **or** 5+ concerns, so a concern-heavy share can itself explain extra rounds".
4. In the plan-quality bullet (reflect:85), update the `challenge_plan.dismissed` phrase to match step 2's meaning, using "plan" names.
5. Keep "no numeric thresholds" untouched. The 5-concern threshold is the loop's rule, not a reflect reading.

### Task 7: Verify
What: Prove the edits satisfy Success Criteria 1–7.
Used by: Build's completion check; Validate's reviewers read the result.
Depends on: Tasks 1–6
Files: none (read-only checks); docs/dev/spec-review-autoloop/debt-pending.md already holds both `## To Close` bullets (SC7)
Interfaces:
- Consumes: all files from Tasks 1–6
- Produces: nothing — terminal task

Implementation steps:
1. Run `grep -n 'loops_run.*autopilot-only\|never loop-extending\|never a reason to loop\|once per gate arrival\|standard mode never loops\|blocker-driven number\|advisory' plugins/dev/skills/{spec,plan,autopilot}/SKILL.md`. Every hit must be consistent with the review loop. Fix any that isn't.
2. Run `grep -n 'review loop' plugins/dev/skills/{spec,plan,autopilot}/SKILL.md`. Confirm spec states it canonically once, plan marks it as a mirror, and autopilot marks it as a restatement.
3. Read Spec Step 12a, Step 13, Step 1 and Plan Step 7a, Step 8, Step 1 end-to-end against the four branches in "The Loop Rule". Confirm a heavy final round never applies fixes, and confirm Path A never re-dispatches.
4. `grep -n 'errored' plugins/dev/skills/plan/SKILL.md plugins/dev/skills/autopilot/SKILL.md`: the plan mirror exists and autopilot no longer says the rule does not apply to Plan (SC7, debt 1).
5. `grep -n 'plan_end' plugins/dev/skills/plan/SKILL.md`: re-stamped after the loop and in Path A/B (SC7, debt 2).
6. `cat docs/dev/spec-review-autoloop/debt-pending.md`: both close-intent bullets present.

## Edge Cases

| Edge case | Handled in | Approach |
|-----------|-----------|----------|
| Clean round 1 | Task 1 branch 2, Task 2/4 gate | Light round, zero findings: nothing applied, gate shows "Round 1: clean" |
| Micro (cap 1), heavy round 1 | Task 1 branch 4, Task 2 gate | Apply none, exit `limit`, leftovers listed at the gate |
| Fix reintroduces earlier finding | Task 1 cap | No special handling; cap bounds it |
| Errored dispatch mid-loop | Task 1 step 6 (spec), Task 3 step 3 (plan) | Not a round, `null` counters, one retry per stage, second error STOPs |
| Resume after `/clear`, rounds remaining | Task 2 step 5, Task 4 step 5 | Re-enter loop with `loops_run` carried forward |
| Resume after limit-hit exit | Task 2 step 5, Task 4 step 5 | One regenerating dispatch, not a round, render `limit` gate |
| User reverts an auto-applied fix | Task 2 step 3, Task 4 step 3 | Path B: `dismissed` += reverted, `applied` unchanged, spec `spec_revisions` += 1 |
| Autopilot, concern-heavy final round | Task 5 step 1–2 | STOP, as the one rule requires |
| Scope blocker (spec only) | Task 1 step 4 | Apply none, exit `scope`; standard gate / autopilot STOP |

## Out of Scope
- `dev:validate`'s fix loop
- Review lenses, Blocker/Concern definitions, verdict format
- New `config.json` keys
- A plan scope-blocker class
- Migrating in-flight cycles
- CLAUDE.md Component Registry (updated by `dev:pr` Step 5a)
