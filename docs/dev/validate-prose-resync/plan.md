# Validate Prose Re-sync — Implementation Plan
*Branch: feature/validate-prose-resync · 2026-08-19*

## Files

| File | Action | Purpose |
|------|--------|---------|
| `plugins/dev/skills/validate/SKILL.md` | Modify | All four edits: new step 3c, step 4's composition clause, the fix-diff checklist question, the converging-cascade exemption |

No other file under `plugins/` is touched — Success Criterion 6. The `CLAUDE.md` Component Registry
row is **not** a task here: `dev:done` Step 4 is that table's sole writer (`done/SKILL.md:217`,
invariant #8 at `:296`), and SC6 excludes it from the diff check by name.

**Grounding for the one out-of-file claim this plan makes.** Task 3 adds a question to the fix-diff
re-review checklist, whose owning step declares itself canonical over a mirror in `dev:fix`
(`validate/SKILL.md:187-188`). Checked before writing this plan: `fix/SKILL.md:700-701` reads
"a marked mirror of `dev:validate` Step 4 step 8, which stays canonical… the cap is pinned to 1
rather than tier-derived." The pinned cap is what makes the spec's Out of Scope deferral sound — a
one-round bound cannot produce the multi-loop cascade this cycle addresses — so the mirror
deliberately diverges here rather than drifting. Task 3 records that divergence in the canonical
side's own text so the gap is declared rather than silent.

**Anchoring note for the builder.** Every line number below is **pre-insertion** — measured against
`validate/SKILL.md` as it stands before Task 1 runs. Task 1 inserts a new block mid-file, so Tasks
2–4's cited lines shift downward by the length of that insertion. Anchor on the **quoted text** each
task gives, not on the number; the numbers are there to locate the region on a first read.

## Tasks

### Task 1: Add step 3c — the prose re-sync rule
What: Insert a new numbered step `3c` in Step 4's fix loop, after step 3b and before step 4, stating
that a fix which edits a fenced code block must re-read the prose inside the smallest enclosing
heading and reconcile any statement that no longer describes the block.
Used by: The fix-loop executor reading Step 4 top-to-bottom; Task 3's checklist question enforces it.
Depends on: nothing — first task.
Files: modify `plugins/dev/skills/validate/SKILL.md`
Interfaces:
- Consumes: nothing
- Produces: the step label **`3c`**, cited by Task 2's composition clause and by Task 3's rationale
  for the checklist question. (The phrase "smallest enclosing heading" is internal to this task —
  no later task consumes it.)
- State keys: none — this task introduces no `state.json` key (SC6 forbids one)
- Shared procedure: none — `dev:fix` carries no counterpart to step 3c, and the spec's Out of Scope
  defers adding one

Implementation steps:
1. Anchor on the end of step 3b (the paragraph ending "…the reviewer disproving it costs a loop.",
   currently `validate/SKILL.md:175`) and insert the new step immediately after it, before the
   line beginning `4. Attempt P3 fixes`.
2. Write the trigger as a relation, not a word list: the rule fires when a fix **edits a fenced code
   block**, and what it checks is whether the surrounding prose **still describes the block**. Counts,
   ordinals and enumerations may appear only as *illustrative* of what commonly goes stale — never as
   the definition of the trigger. (SC1's test: the rule's own statement of what to check names the
   relation, not an enumeration of word types.)
3. State the boundary as the **smallest enclosing heading**, and give the measured reason in one
   sentence: both stale sentences on the observed cycle fell inside the same `###` subsection, and a
   whole-file re-read costs **5.5× the tokens** (~1,062 against ~5,825 for that file) for no evidenced
   additional catch. Quote the token ratio and name its denominator; do not quote the line ratio —
   it has a different denominator and reads misleadingly as the reciprocal.
4. Carry the fallback for a block under no heading: re-read the whole file. Give the one-line reason
   (a file small enough to have no headings is cheap to re-read), so no second boundary rule is needed.
5. State that reconciliation edits ride the **same** loop commit — step 7's commit — so no additional
   loop is spent on them.
6. State why the position is pinned rather than folded into step 4: step 4 carries the P3 circuit
   breaker (`validate/SKILL.md:177`), and a rule living there would inherit it and switch itself off
   for the remainder of the cycle in exactly the situation where prose is most likely going stale.
7. Note that cross-file staleness is already step 3a's job, so this rule is intra-file only and does
   not duplicate it.

### Task 2: State how step 3c composes with step 4's "do not rewrite correct prose" rule
What: Add a composition clause so a reader following both rules is never in contradiction, expressed
in the **defect-class vs polish** classification step 4 already defines.
Used by: The fix-loop executor who has just read step 3c and then reaches step 4's prose rule.
Depends on: Task 1 — the clause names step `3c` and cannot be written before that label exists.
Files: modify `plugins/dev/skills/validate/SKILL.md`
Interfaces:
- Consumes: the step label `3c` from Task 1
- Produces: nothing later tasks rely on — terminal for the composition thread
- State keys: none
- Shared procedure: none

Implementation steps:
1. Locate step 4's existing sentence *"Leave the second kind to Step 5a's carrying-cost test — do not
   rewrite correct prose during the fix loop"* (`validate/SKILL.md:176`). Leave that sentence intact —
   it is load-bearing and the spec forbids weakening it.
2. Append a short clause to step 4 tying the two together: prose that **this loop's own code edit just
   made wrong** is defect-class by step 4's existing definition ("a statement that is wrong,
   self-contradictory, or ambiguous") and is fixed inline under step 3c; prose that is merely
   improvable stays deferred to Step 5a exactly as today.
3. State explicitly that step 3c **adds a trigger for finding defect-class prose and does not widen
   what counts as defect-class**, and that it grants no licence to polish. SC3 requires the
   non-widening to be demonstrable from the text, so say it rather than implying it.
4. Add the reciprocal half-sentence inside step 3c pointing at step 4's classification, so the reader
   who arrives at 3c first is not left to discover the interaction two steps later.

### Task 3: Add the enforcement question to the fix-diff re-review checklist
What: Add one question to the existing fix-diff re-review checklist asking whether a fix changed a
code block whose surrounding prose no longer describes it.
Used by: Step 8's cold re-reviewer subagent, which already receives this checklist verbatim.
Depends on: Task 1 — the question is the enforcement surface for step 3c and is meaningless without it.
Files: modify `plugins/dev/skills/validate/SKILL.md`
Interfaces:
- Consumes: step 3c's rule from Task 1
- Produces: nothing later tasks rely on — terminal task
- State keys: none — enforcement rides the existing checklist, so no `validation.md` section and no
  `state.json` key is added (SC4, SC6)
- Shared procedure: the fix-diff re-review checklist is declared **canonical** here, with a mirror in
  `dev:fix`'s `### Review` (`fix/SKILL.md:700-701`). This task keeps the canonical designation and
  **does not** edit the mirror — see step 3 below.

Implementation steps:
1. Locate the one-paragraph checklist at `validate/SKILL.md:200` (the run-on line of questions ending
   "…obey the healthy-path exit-code rule below?").
2. Append one question in the same voice as its siblings: *Did this fix change a code block whose
   surrounding prose no longer describes it?* Keep it a question inside that existing paragraph — no
   new dispatch, no new artifact, no new section (SC4).
3. In the step 8 bullet that declares the mirror (`validate/SKILL.md:187-188`), record the divergence
   in one clause rather than propagating the edit: `dev:fix`'s cap is pinned to 1, so the multi-loop
   prose cascade is structurally unreachable there, and its mirror deliberately omits this question.
   Editing `fix/SKILL.md` is forbidden by SC6 and by the spec's Out of Scope; leaving the drift
   unmarked is what the canonical/mirror convention exists to prevent, so the divergence is declared
   on the canonical side.
4. Say, in that same clause, that the mirror does **not** name this divergence back — `fix/SKILL.md`
   still reads "Two divergences" and is not edited by this cycle. The repo's convention is that a
   divergence is named at both ends; here it is named at one, deliberately. A reader who checks the
   mirror and finds a different count needs the asymmetry stated, or the canonical text reads as
   simply wrong about its own counterpart.

### Task 4: Give the same-region recurrence rule a converging-cascade exemption
What: Amend step 8's same-region recurrence rule so it distinguishes a converging cascade from a loop
circling one unsettled decision, and state which behavior each shape gets in **both** modes.
Used by: The fix-loop executor deciding, at step 8, whether to iterate again or route to Step 4a.
Depends on: nothing — it edits a different region of Step 4 than Tasks 1–3 and shares no text with them.
Files: modify `plugins/dev/skills/validate/SKILL.md`
Interfaces:
- Consumes: nothing
- Produces: nothing later tasks rely on — terminal task
- State keys: none — the exemption is evaluated from the loop's own findings, not from a persisted
  counter (SC6)
- Shared procedure: none — no other skill documents the same-region recurrence rule (verified by
  grep across `plugins/dev/skills/*/SKILL.md`: the only hits outside `validate/SKILL.md` are
  `recurrence-merge`, an unrelated tech-debt procedure)

Implementation steps:
1. Locate the **Same-region recurrence** bullet (`validate/SKILL.md:189`). Leave its existing trigger
   and its existing standard/autopilot fork intact; the exemption is additive.
2. Add the exemption with all three signals stated:
   - severity is **non-increasing across the rounds and strictly lower than the first round's**
     (the observed cascade ran P2 → P3 → P3). Write it this way deliberately, and say why in the
     text: "monotonically falling" would exclude the very cascade this was built from, whose last
     two rounds were both P3;
   - **no code changed after the first round** — subsequent rounds edited prose only;
   - the findings are **consequences of the same earlier edit** rather than competing answers to one
     unsettled question.
3. State the behavior for **both** branches of the existing fork, not just the standard one:
   where the exemption applies, standard **continues the loop** rather than routing to Step 4a, and
   autopilot **continues fixing in that region** rather than buffering out of it. Say why the
   autopilot half matters more: it is the mode with no human present to override a misfire, so a
   converging cascade there would silently stop being fixed and be carried to the buffer instead.
4. State that where the exemption does **not** apply, today's behavior is unchanged in both modes —
   the circling shape still routes to Step 4a (standard) / stops fixing in-region and buffers
   (autopilot).
5. Ground the exemption in one sentence: on the observed cycle this rule triggered from loop 3 onward
   and was overridden by documented human judgment recorded in `validation.md`. A rule that needs a
   written override to behave correctly is itself a defect.

## Edge Cases

| Edge case | Handled in | Approach |
|-----------|-----------|----------|
| Fix edits prose only, no code | Task 1 | Trigger is a changed fenced block; the rule does not fire |
| Edited block sits under no heading | Task 1 | Fall back to the whole file; stated with its one-line reason |
| Enclosing heading is very large | Task 1 | Boundary is *smallest* enclosing, so a nested `####` binds tighter than its parent `##` |
| Re-read reveals a genuine defect, not stale English | Task 1 | Normal P1/P2, fixed through the loop as usual — not a re-sync edit |
| Re-read finds prose that is stale but only improvable | Task 2 | Deferred to Step 5a under the existing polish rule; 3c finds it, does not licence fixing it |
| Cascade that is genuinely circling | Task 4 | Exemption does not apply; today's Step 4a routing stands, in both modes |
| Cross-file staleness (canonical/mirror counterpart) | Task 1 | Already step 3a's job; 3c is intra-file and says so |
| `dev:fix`'s mirrored checklist diverges | Task 3 | Divergence declared on the canonical side; `fix/SKILL.md` is not edited |

## Out of Scope

- Editing `plugins/dev/skills/fix/SKILL.md` — its cap is pinned to 1, so the cascade is structurally
  unreachable there. Deferred deliberately, and the divergence is marked (Task 3 step 3).
- Any new `state.json` key or `validation.md` section — enforcement rides the existing checklist.
- `loops_max`, tier derivation, the loop's P1/P2 fix ordering, Step 5a's buffer, Step 5b's build check.
- `debt-artifact-path-rule-artifact-component-unconstrained` and `debt-primary-cd-failure-unchecked`,
  which name the same file but are adjacent clauses.
- `backlog-reflect-before-pr-merge-retire-legacy-commands` — Milestone 3, edits the stage *tail*.
- The `CLAUDE.md` Component Registry row — `dev:done` Step 4 owns that table.
