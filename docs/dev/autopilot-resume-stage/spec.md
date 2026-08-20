# Autopilot Resume Stage
*Branch: feature/autopilot-resume-stage · Confidence: 100% — Ready · 2026-08-19*
*Cycle type: feature · Tier: standard*

## Intent

A handoff to autopilot re-runs stages the cycle has already finished.

Observed on `extract-review-skills`: `/dev:autopilot docs/dev/extract-review-skills/spec.md` was
invoked on a cycle whose `state.json` read `stage: "plan"` with an approved, committed spec. The run
opened by reviewing and editing the spec again, and the challenger loop's commits grew it from 200 to
546 lines. The operator had to add "the next step is plan, do not run a review of the spec again" in
free text to get the documented behavior — an instruction that is not part of the interface.

Two independent defects produce this, and fixing either alone leaves the hole open:

1. **Autopilot never uses the stage it reads.** Step 1 reads `stage` and even announces
   `Resuming from <current-stage>`, but Step 3 says "Execute stages in sequence for the applicable
   tier" over three lists that each begin at **Spec**, and defines no rule for starting anywhere
   else. Step 1's phrase "the remaining-stage list" has no referent in Step 3. `completed[]` is read
   by seven skills; `dev:autopilot` is not one of them.

2. **The three gated stages hand over the resume command before recording the stage as finished.**
   `dev:spec`, `dev:shape`, and `dev:plan` print `Safe to /clear now — resume with: …` (and the
   autopilot handoff offer) *above* `Wait for explicit user approval`, and write `completed[]` only
   in the `When approved` block below it. So the command is in the operator's hands one full step
   before the state it depends on exists.

Defect 2 is what makes defect 1 unfixable in isolation: a resume rule keyed on `completed[]` is only
as good as the guarantee that `completed[]` is current when the operator is given the command.

## Scope

**1. Autopilot resumes at the first unfinished stage.**

`dev:autopilot` Step 3 gains an explicit start-stage rule: begin at the **earliest stage in the
selected tier sequence that is not present in `completed[]`**, and run from there to the end. Stages
already in `completed[]` are skipped, never re-entered.

The rule composes with the existing tier-row selection rather than replacing it. Step 3 already picks
one of three rows (Micro / Standard-Deep + no-ui / Standard-Deep + UI), and a skipped Shape is absent
from its row — so a skipped stage can never be selected as "first unfinished."

`completed[]` is the authority; `stage` is a hint. Where they disagree — `stage: "build"` with
`completed: ["spec", "shape"]` — the run starts at Plan. This never skips work: the worst case is
redoing a stage that succeeded but was never recorded, which is recoverable, where the inverse
(building with no `plan.md`, unattended) is not.

**2. The announce line reports the resolved stage.**

Step 1's `Resuming from <current-stage>` prints the stage the run will actually start at, not the raw
`stage` field. Today the announce and the execution are separate readings of state that were never
connected; a resume rule that leaves them separate keeps the same class of defect alive in the
message instead of the behavior.

**3. A cycle with nothing left to run stops.**

When every stage in the selected row is in `completed[]`, autopilot STOPs, reports that the cycle is
already complete, and lists the stages that ran. It does not fall through to Spec. This is a new stop
condition and carries its ripple: `dev:autopilot`'s `## Purpose` "When autopilot stops" list and the
`dev:autopilot` row of the CLAUDE.md Component Registry.

**4. Gated stages record completion before handing over the command.**

In `dev:spec` Step 13, `dev:shape` Step 11, and `dev:plan` Step 8, the resume block — both the
`Safe to /clear now — resume with: …` line and the autopilot handoff offer where one is printed —
moves **below** the `When approved` state write. The operator receives a continuation command only
once `completed[]` records the stage it hands off from.

This makes the three gated stages consistent with the three ungated ones, which already write then
print: `build` (`completed[]` at Step 6, resume line after), `validate` (Step 6, then the line), and
`pr` (Step 5, then the line). The correct ordering is already the repo's majority convention.

**5. The two "harmless early paste" paragraphs are rewritten.**

`dev:spec` Step 13 and `dev:shape` Step 11 each carry a paragraph titled **"The command is only
meaningful after approval"** which documents pasting-before-approving as harmless and instructs
against fixing it:

> "Nothing breaks: autopilot resumes *at Spec* … **Do not add a guard**; a guard would require the
> offer to know about approval state, which is the coupling this design avoids."

That reasoning is sound today and false under item 1 — "resumes at Spec" stops being harmless and
becomes the re-run this cycle exists to remove. Both paragraphs are rewritten to state the new
ordering. The anti-guard argument is **honored, not overridden**: no guard is added, because moving
the print below the write removes the state the guard would have had to inspect. `dev:shape`'s copy
names `dev:spec` Step 13 as canonical, and must keep doing so.

## Out of Scope

- **No new stage token.** `/dev:autopilot plan docs/dev/<feature>/spec.md` was considered and
  declined. The command text an operator types does not change, and no printer site changes its
  wording — six sites print this command (`spec:641`, `spec:644`, `shape:235`, `dev:252`,
  `autopilot:50`, `autopilot:179`) and a token would give each one a value to keep correct.
- **No way to force a re-run through autopilot.** Deliberately given up with the token. To redo a
  finished stage, invoke that stage's own skill.
- **`/dev`'s jump-to-stage (Step 5a) keeps its re-run hole.** `/dev build` on a cycle with `build` in
  `completed[]` still re-runs it. Standard mode is attended — the operator typed it and can watch it
  — where autopilot runs unattended to a merged PR. That asymmetry is what made this worth fixing on
  the autopilot side only.
- **No test harness.** This repo has no executable tests for skill prose; `backlog-dev-skill-test-harness`
  tracks that gap and is not paid here.
- **The other nine open backlog items touching these files.** Surfaced at Step 7 and left open.

## Success Criteria

1. `/dev:autopilot docs/dev/<feature>/spec.md` on a cycle with `completed: ["spec", "shape"]` runs
   **Plan** first. `spec.md` is byte-identical before and after the handoff.
2. No free-text instruction is needed to get that behavior.
3. On a cycle where every stage in the row is in `completed[]`, autopilot prints the
   already-complete STOP and runs nothing.
4. Reading `dev:autopilot` Step 3 top to bottom answers "which stage does this start at" without
   consulting another skill.
5. In each of `dev:spec` Step 13, `dev:shape` Step 11, and `dev:plan` Step 8, the `completed[]` write
   appears **above** the resume/handoff command in the step's own text.
6. Neither `dev:spec` nor `dev:shape` still describes pasting-the-command-early as harmless.
7. `dev:autopilot`'s "When autopilot stops" list names the nothing-left-to-run stop.

## Happy Path

1. Operator finishes Spec in standard mode and approves it at the gate.
2. The stage writes `"spec"` into `completed[]`, sets `stage` to the next stage, and commits — then
   prints the resume line and the autopilot handoff offer.
3. Operator runs `/clear` and pastes `/dev:autopilot docs/dev/<feature>/spec.md`.
4. Autopilot resolves `WORKDIR`, reads `completed[]` and `skipped[]`, selects the tier row, and finds
   the earliest row stage absent from `completed[]` — Plan.
5. It announces `Resuming from plan in autopilot mode` and runs Plan → Build → Validate → PR → Done.
6. Spec and Shape are untouched. No challenger re-runs on an approved artifact.

## Edge Cases

- **`stage` disagrees with `completed[]`** (crash mid-stage, or a manual `/dev <stage>` jump) —
  `completed[]` wins; start at the earliest unfinished row stage.
- **Every row stage finished** — STOP with the already-complete report (Scope item 3).
- **A stage crashed partway and was never recorded** — it is not in `completed[]`, so it is re-entered
  and re-run. Correct: it never finished.
- **Operator pastes the command before approving** — no longer reachable, because the command is not
  printed until approval has been recorded. The path this closes is the one the current prose calls
  harmless.
- **Operator `/clear`s at the gate without approving** — the resume command was never printed, and
  `completed[]` correctly lacks the stage. Re-invoking resumes at that stage, which is right: it was
  never approved.
- **Cycles predating this change** — `completed[]` has always been written by every stage, so no
  migration and no back-compat branch. A cycle mid-flight when this ships resolves normally.
- **Legacy in-place cycles** (`worktreePath: null`) — unaffected; the rule reads `state.json`, and
  `WORKDIR` resolution is untouched.

## UI Needed

No. Four Markdown skill files and one registry row.

## Technical Constraints

- Skill prose is the deliverable — the "code" is instructions an agent follows, so ambiguity is the
  failure mode, not a runtime error. Every rule must be readable in one pass without cross-skill
  lookup.
- `dev:plan`'s **cross-skill behavior ripple** rule (`plan/SKILL.md:177`) binds this cycle: a change
  to a stage skill's stopping or gating behavior must carry a task updating every other skill that
  documents or depends on it. Scope items 3 and 5 exist because of it.
- Duplication across skills is named at both ends by repo convention. `dev:shape`'s rewritten
  paragraph must keep citing `dev:spec` Step 13 as canonical rather than diverging silently.
- No executable verification exists for these files; correctness is established by reading.

## Dependencies

None. No other cycle blocks this, and it blocks none. It touches four skill files and one CLAUDE.md
row, with no shared reference file (`references/tech-debt.md`, `references/entry-adapters.md`)
changed.

## Audience

Solo operator of this plugin repo, running `/dev` cycles on their own projects. The reader of the
changed files is the agent executing a stage; the beneficiary is the operator who pastes a handoff
command and expects it to do what it says.

---
*Auto-filled dimensions: happy_path, ui_needed, dependencies — derived from the four answered
decisions rather than asked directly. None were inferred against missing information: the happy path
is the mechanical consequence of the resume rule plus the reordering, UI is settled by the deliverable
being Markdown, and the dependency set is the swept file list.*

*Grounding inventory:*
- *"Autopilot never reads `completed[]`" — `grep -rn 'completed' plugins/dev/skills/*/SKILL.md` →
  readers in `build`, `dev`, `pr`, `plan`, `validate`, `shape`, `reflect`, `fix`; **zero** hits in
  `autopilot/SKILL.md`. Verified.*
- *"Autopilot has no stage information" — **claim inverted after checking.** `autopilot/SKILL.md:63`
  reads `stage`, and `:71` prints `Resuming from <current-stage>`. The gap is that Step 3
  (`:133–143`) never binds it. Spec reframed accordingly.*
- *"Step 3 truncates at `stage`" — read `autopilot/SKILL.md:133–143`: "Execute stages in sequence for
  the applicable tier" over three Spec-initial lists, no truncation rule. Verified absent.*
- *"`dev:spec`'s resume-mid-approval check caused the re-run" — **false.** That check requires
  `stage == "spec"`; the incident had `stage: "plan"`. The re-run came from Step 3's list.*
- *"No stage skill refuses re-entry when already complete" — swept all seven stage gates
  (`shape:42`, `plan:49–52`, `build:42`, `validate:38`, `pr:34`, `done:43`): every one is a *forward*
  precondition, none an already-done check. Verified absent.*
- *Set of sites printing the artifact-path form, enumerated by
  `grep -rn '/dev:autopilot docs/dev' plugins/ docs/ CLAUDE.md README.md` → `spec:641`, `spec:644`,
  `shape:235`, `dev:252`, `autopilot:50`, `autopilot:179`, `CLAUDE.md:29`. The `autopilot:50` site is
  the multi-hit STOP and would not have been recalled from memory.*
- *Gate-ordering sweep (`grep -rn 'Safe to /clear\|resume with:'` + reading each state write):
  write-then-print in `build:146→160`, `validate:427→450`, `pr:206→222`; print-then-write in
  `spec:638→When approved`, `shape:232→251`, `plan:266→285`. This is what established item 4 as a
  consistency fix rather than a new convention.*
- *Open-debt intersection: 10 active `docs/backlog/` items list one or more of these files.
  `debt-autopilot-handoff-stage-not-explicit` folded into scope; nine left open.*
