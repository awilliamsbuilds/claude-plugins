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
   else. Step 1's phrase "the remaining-stage list" has no referent in Step 3. `completed[]` is
   touched by every stage skill except `dev:autopilot` — nine of them write or read it, four read it
   as a precondition — and `dev:autopilot` has zero references to it.

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
**before** that entry point are skipped, never re-entered; from the entry point onward every row
stage executes in order, whether or not it appears in `completed[]`. The distinction only matters on
a non-contiguous `completed[]` — `["spec", "build"]` resolves to Plan and then re-runs Build, which
is correct, since a Build recorded before a re-planned Plan is stale. No stage is exempted, PR
included; the un-producible shape that would re-enter PR is recorded as backlog rather than guessed
at here.

The rule composes with the existing tier-row selection rather than replacing it. Step 3 already picks
one of three rows (Micro / Standard-Deep + no-ui / Standard-Deep + UI), and a skipped Shape is absent
from its row — so a skipped stage can never be selected as "first unfinished."

`completed[]` is the authority; `stage` is a hint. Where they disagree — `stage: "build"` with
`completed: ["spec", "shape"]` — the run starts at Plan. This never skips work: the worst case is
redoing a stage that succeeded but was never recorded, which is recoverable, where the inverse
(building with no `plan.md`, unattended) is not.

An absent or empty `completed[]` — every cold start — selects Spec, which is the first stage of every
row; row selection then proceeds on the `skipped[]` that Spec writes, unchanged from today.

**2. The announce line and `handoff_at` report the resolved stage.**

Step 1's `Resuming from <current-stage>` prints the stage the run will actually start at, not the raw
`stage` field. Today the announce and the execution are separate readings of state that were never
connected; a resume rule that leaves them separate keeps the same class of defect alive in the
message instead of the behavior.

The same resolved value feeds `handoff_at`. `autopilot:78` currently writes it from `stage` as read
before the `mode` flip; under item 1 that can differ from the stage the run actually starts at, which
is what `autopilot:81` says the field means ("the first stage that runs unattended") and what
`dev:done` Step 5 renders into the decision log (`done:328`). On item 1's own divergence example the
run would start at Plan while the log read "Handed off to autopilot at Build." `handoff_at` binds to
the **resolved** start stage, so the announce line, the first stage executed, and the marker
downstream consumers read are one value resolved once.

**3. The terminal case is stated, not left to fall through.**

`"done"` is never added to `completed[]` — `dev:done` writes no completion entry, and its Step 7
`rm -rf`s the cycle directory (`done:504`) — so "every row stage in `completed[]`" is unreachable and
must not be the trigger for anything. Instead: when the earliest unfinished row stage is **Done**,
autopilot runs Done normally. That is the reachable end-of-cycle case.

A cycle that has already finished Done has no `state.json` at all, and Step 1's existing
`No /dev cycle found for <feature>` STOP (`autopilot:39`) already covers it. **No new stop condition**
— and therefore no edit to `dev:autopilot`'s "When autopilot stops" list.

**4. Gated stages record completion before handing over the command.**

In `dev:spec` Step 13, `dev:shape` Step 11, and `dev:plan` Step 8, the resume block — both the
`Safe to /clear now — resume with: …` line and the autopilot handoff offer where one is printed —
moves **below** the `When approved` state write. The operator receives a continuation command only
once `completed[]` records the stage it hands off from.

This makes the three gated stages consistent with the three ungated ones, which already write then
print: `build` (`completed[]` at Step 6, resume line after), `validate` (Step 6, then the line), and
`pr` (Step 5, then the line). The correct ordering is already the repo's majority convention.

The move takes the **whole block**: the `Safe to /clear now — resume with: …` line, the autopilot
handoff offer where one prints, and the `[If worktreePath is set: Worktree: <worktreePath>]` line,
which stays **last** so it still applies to both commands (`spec:648`, `shape:239`). Three adjacent
paragraphs describe the block's old position and are rewritten with it:

- **"What this offer deliberately does not do"** (`spec:650`, `shape:241`) — asserts the offer prints
  *above* `Wait for explicit user approval` and that "everything below is untouched." False after the
  move.
- **The idempotence paragraph** (`spec:654`, `shape:245`) — "the same text re-renders" no longer
  covers an offer that has left the gate block.
- **Item 5's paragraph**, below.

`dev:plan` Step 8 has no handoff offer and none of these paragraphs — only the resume line and the
`Worktree:` line move there.

**5. Every site documenting the early-paste path as harmless is rewritten — four, not two.**

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

**Two further sites depend on those paragraphs' claim and are rewritten with them.** `autopilot:81`
justifies a `"spec"`/`"shape"` value for `handoff_at` with "a path **both gates document as
harmless**," and `dev:done` Step 5 at `done:328` uses the same phrase to explain a decision log
reading "at Shape." Both would cite documentation this cycle deletes. Both keep their **behavior**
unchanged — `handoff_at`'s value domain stays open, the log still renders as-is — and lose only the
deleted justification, restated as: a user who types `/dev:autopilot` at a gate before approving has
still handed off there, and the marker records it accurately.

This is the `dev:plan` Step 8 cross-skill ripple rule (`plan:177`) applied: `dev:done` is a fifth
file in this cycle purely because it cites a claim being removed.

## Out of Scope

- **No new stage token.** `/dev:autopilot plan docs/dev/<feature>/spec.md` was considered and
  declined. The command text an operator types does not change, and no printer site changes its
  wording — six printer sites carry this command (`spec:641`, `spec:644`, `shape:235`, `dev:252`,
  `autopilot:50`, `autopilot:179`) plus the Component Registry row at `CLAUDE.md:29`, and a token
  would give each of those seven a value to keep correct.
- **No way to force a re-run through autopilot.** Deliberately given up with the token. To redo a
  finished stage, invoke that stage's own skill.
- **`/dev`'s jump-to-stage (Step 5a) keeps its re-run hole.** `/dev build` on a cycle with `build` in
  `completed[]` still re-runs it. Standard mode is attended — the operator typed it and can watch it
  — where autopilot runs unattended to a merged PR. That asymmetry is what made this worth fixing on
  the autopilot side only.
- **No test harness.** This repo has no executable tests for skill prose; `backlog-dev-skill-test-harness`
  tracks that gap and is not paid here.
- **The other fourteen open backlog items touching these files.** Surfaced at Step 7 and left open.

## Success Criteria

1. `/dev:autopilot docs/dev/<feature>/spec.md` on a cycle with `completed: ["spec", "shape"]` runs
   **Plan** first. `spec.md` is byte-identical before and after the handoff.
2. No free-text instruction is needed to get that behavior.
3. On a cycle with `completed: […, "pr"]`, autopilot runs **Done** and nothing else.
4. Reading `dev:autopilot` Step 3 top to bottom answers "which stage does this start at" without
   consulting another skill.
5. In each of `dev:spec` Step 13, `dev:shape` Step 11, and `dev:plan` Step 8, the `completed[]` write
   appears **above** the resume/handoff command in the step's own text — and no sentence in either
   `dev:spec` or `dev:shape` still says the offer prints above `Wait for explicit user approval`.
6. `grep -rn 'harmless' plugins/dev/skills/` returns no hit describing pasting-the-command-early as
   harmless. (One unrelated hit at `done:602` — "harmlessly otherwise", about a git fetch — is
   expected to remain.)
7. `dev:autopilot`'s "When autopilot stops" list is **unchanged** — this cycle adds no stop condition.
8. `dev:autopilot` Step 1 derives the announce line and `handoff_at` from the same resolved start
   stage, not from the raw `stage` field.

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
- **Only Done remains** — Done runs. `"done"` is never recorded in `completed[]`, so its absence is
  never a signal of unfinished work, and a cycle past Done has no `state.json` to resolve at all.
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
  documents or depends on it. Scope item 5 exists because of it, and it is why `dev:done` is in the
  file set. Applied in the other direction, it is also why item 3 adds *nothing*: no stop condition
  is introduced, so the stop list and its mirrors stay untouched.
- Duplication across skills is named at both ends by repo convention. `dev:shape`'s rewritten
  paragraph must keep citing `dev:spec` Step 13 as canonical rather than diverging silently.
- No executable verification exists for these files; correctness is established by reading.

## Dependencies

None. No other cycle blocks this, and it blocks none. It touches **five** skill files —
`dev:autopilot`, `dev:spec`, `dev:shape`, `dev:plan`, and `dev:done` (the last only because it cites
a claim being removed) — with no shared reference file (`references/tech-debt.md`,
`references/entry-adapters.md`) changed. The Component Registry row is reconciled at Done by
`dev:done` Step 4a, as on any cycle.

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
  nine skills touch the field (`spec` initializes and writes it; `build`, `shape`, `plan`, `validate`,
  `pr` write it; `dev`, `reflect`, `fix`, `validate`, `pr` read it — four as a hard precondition);
  **zero** hits in `autopilot/SKILL.md`. The load-bearing half is the zero. The first draft said
  "read by seven skills," conflating readers with touchers.*
- *"Autopilot has no stage information" — **claim inverted after checking.** `autopilot/SKILL.md:63`
  reads `stage`, and `:71` prints `Resuming from <current-stage>`. The gap is that Step 3
  (`:133–143`) never binds it. Spec reframed accordingly.*
- *"Step 3 truncates at `stage`" — read `autopilot/SKILL.md:133–143`: "Execute stages in sequence for
  the applicable tier" over three Spec-initial lists, no truncation rule. Verified absent.*
- *"`dev:spec`'s resume-mid-approval check caused the re-run" — **false.** That check requires
  `stage == "spec"`; the incident had `stage: "plan"`. The re-run came from Step 3's list.*
- *"No stage skill refuses re-entry when already complete" — swept the **six** stage gates that exist
  (`shape:41–44`, `plan:49–52`, `build:41–44`, `validate:38`, `pr:34`, `done:43`; Spec has no gate of
  this shape, being first): every one is a *forward* precondition, none an already-done check.
  Verified absent. Two of these were cited a line low in the first draft — the `<HARD-GATE>` marker
  opens at `:41` in `shape` and `build`, with the content at 42–44.*
- *"`\"done\"` is never written to `completed[]`" — `grep -n 'completed' plugins/dev/skills/done/SKILL.md`
  → one hit, the unrelated prose "cycles-completed count" at `:154`. Zero writes. Confirmed with
  `done:504`'s `rm -rf "$WORKDIR/docs/dev/<feature>/"`. This is why Scope item 3 adds no stop
  condition; the first draft asserted an unreachable trigger.*
- *"The early-paste claim lives in two paragraphs" — **under-swept in the first draft.**
  `grep -rn 'harmless' plugins/dev/skills/` → `shape:243`, `autopilot:81`, `done:328` (plus an
  unrelated `done:602`). `dev:spec`'s paragraph states the same claim in different words. Four sites,
  and `dev:done` enters the file set because of it.*
- *Set of sites printing the artifact-path form, enumerated by
  `grep -rn '/dev:autopilot docs/dev' plugins/ docs/ CLAUDE.md README.md` → `spec:641`, `spec:644`,
  `shape:235`, `dev:252`, `autopilot:50`, `autopilot:179`, `CLAUDE.md:29`. The `autopilot:50` site is
  the multi-hit STOP and would not have been recalled from memory.*
- *Gate-ordering sweep (`grep -rn 'Safe to /clear\|resume with:'` + reading each state write):
  write-then-print in `build:146→160`, `validate:427→450`, `pr:206→222`; print-then-write in
  `spec:638→When approved`, `shape:232→251`, `plan:266→285`. This is what established item 4 as a
  consistency fix rather than a new convention.*
- *Open-debt intersection: **15** active `docs/backlog/` items list one or more of these files.
  `debt-autopilot-handoff-stage-not-explicit` folded into scope; fourteen left open.*
- ***The first draft said 10.*** *That sweep ran against the pre-expansion file set
  (`autopilot`, `spec`, `shape`, `dev`) and was never re-run after `plan` and `done` entered scope.
  This is `debt-spec-grounding-sweep-file-set-lags-scope` — an open item in this very store — biting
  inside the cycle that surfaced it. Recorded here rather than silently corrected, because the
  recurrence is the evidence that item is worth paying.*
