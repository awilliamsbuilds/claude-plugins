# Autopilot Resume Stage — Implementation Plan
*Branch: feature/autopilot-resume-stage · 2026-08-20*

The deliverable is skill prose in five Markdown files. There is no executable verification (spec
`## Technical Constraints`), so every task names the exact anchor it edits and the exact claim the
new text must make.

**Line numbers are pre-edit addresses.** Every `file:NNN` in this plan was read against the files as
they stand before any task runs. Within a task, the numbers cited *after* that task's own cut or
insert step no longer point where they say — Task 1 removes eight lines before it cites `:650`,
`:652`, `:654`, `:677`, `:679`. Each anchor is therefore paired with a paragraph title or a verbatim
quote, and **the title or quote governs**: find the text, not the line. Re-read the file after each
edit rather than trusting a later number.

## Files

| File | Action | Purpose |
|------|--------|---------|
| plugins/dev/skills/spec/SKILL.md | Modify | Step 13 — move the resume block below the `When approved` write; rewrite the three paragraphs that describe its old position (**canonical** for this procedure) |
| plugins/dev/skills/shape/SKILL.md | Modify | Step 11 — same move, mirror of Task 1; keeps citing `dev:spec` Step 13 as canonical |
| plugins/dev/skills/plan/SKILL.md | Modify | Step 8 — same move, mirror of Task 1; resume line + `Worktree:` line only, no offer and none of the three paragraphs |
| plugins/dev/skills/autopilot/SKILL.md | Modify | Step 3 — the start-stage rule; Step 4 — the completion report marks inherited stages; Step 1 — announce line and `handoff_at` bind to the resolved start stage, and the `:81` justification loses the deleted citation |
| plugins/dev/skills/done/SKILL.md | Modify | Step 5 (`:328`) — restate the justification that cited the deleted "harmless" claim; rendering behavior unchanged |

Tasks 1–3 (the gate reorder) run before Tasks 4–6 (the consumers). That order is deliberate: the
resume rule in Task 4 is keyed on `completed[]`, and it is only sound once `completed[]` is
guaranteed current when the operator receives the command — spec `## Intent`, "Defect 2 is what makes
defect 1 unfixable in isolation."

## Tasks

### Task 1: Move the Spec gate's resume block below the state write

What: In `dev:spec` Step 13, relocate the resume/handoff block from above `Wait for explicit user
approval` to below the `When approved` state write, and rewrite the three paragraphs that assert its
old position.
Used by: The operator at the Spec gate, who now receives a continuation command only after
`completed[]` records `"spec"`. Task 4's `completed[]`-keyed resume rule depends on that guarantee.
Depends on: nothing — first task.
Files: modify `plugins/dev/skills/spec/SKILL.md`
Interfaces:
- Consumes: nothing
- Produces: **the gate resume-block ordering** — gate body → wait → approve → state write + commit →
  *then* print the resume block. Tasks 2 and 3 mirror this. Also produces the replacement sentence
  for the early-paste claim, restated in `dev:autopilot` (Task 5) and `dev:done` (Task 6):
  *a user who types `/dev:autopilot` at a gate before approving has still handed off there, and the
  marker records it accurately.*
- State keys: none — this task introduces no new `state.json` key. The `completed[]` and `stage`
  writes at `spec:677` are existing writes whose text and mode are unchanged; only what is printed
  after them changes.
- Shared procedure: **gate resume-block ordering** — this task is the **canonical** implementation.
  Tasks 2 and 3 are mirrors of it.

Implementation steps:

1. Read `plugins/dev/skills/spec/SKILL.md` lines 620–679 (Step 13) in full before editing.

2. **Cut** these lines out of the fenced gate block at `spec:629–646`, leaving the rest of the block
   in place:
   - `Safe to /clear now — resume with: /dev:<next-stage> docs/dev/<feature-name>/spec.md` (`:638`)
   - the two bracketed Branch B offer paragraphs (`:639–641` Plan, `:642–644` Build)
   - `[If worktreePath is set: Worktree: <worktreePath>]` (`:645`)

   What stays in the gate block: the `Spec written and committed to …` line, `[Step 12a's verdict,
   verbatim]`, the `[If the verdict has findings: Reply \`apply\` …]` line, and `Please review it and
   let me know if you'd like any changes before we continue.` The blank line that separated the
   review prompt from the resume line goes with the cut.

3. Move the sentence at `spec:648` — "Keep the `Worktree:` line last so it applies to both commands.
   The `/dev:autopilot` command resolves the worktree itself — it runs from anywhere in the repo,
   with no `cd` asked of the user." — down with the block. It is a rule about the block, so it
   belongs wherever the block lands.

4. **Paste** the cut block, in a fence of its own, immediately below the `When approved:` paragraph
   at `spec:677` and above the `**Autopilot mode:**` line at `:679`. Introduce it with one sentence:

   > Then print the resume block:

   Preserve the block's internal order exactly: resume line, then the Branch A/B offer lines, then
   the `Worktree:` line **last**. Branch A/B *selection* is unchanged — it is still the next-stage
   determination made at `spec:622–627`, and that passage keeps its position at the top of Step 13.
   One clause inside it is rewritten by step 4a below; nothing else in `:622–627` is touched.

4a. Rewrite the Branch A clause at `spec:626`. It currently reads: "**Branch A — next stage is
   Shape.** No offer. Shape is definition, not execution, so this gate is not a pre-execution gate;
   the block below renders byte-identically to today." The final clause is false once step 2 cuts
   eight lines out of that block. Keep the first two sentences; replace "the block below renders
   byte-identically to today" with a statement that this gate prints **no offer**, so the resume line
   printed after approval is the only continuation command it hands over. Do not otherwise touch
   `:622–627`.

4b. Rewrite the offer's lead-in clause in **both** Branch B lines (`spec:640` for Plan, `spec:643` for
   Build). Each currently ends `… run unattended: approve above, then /clear and run`. Printed below
   the `When approved` write, "approve above" instructs the operator to do something they have already
   done, and contradicts the ordering steps 5–6 of this task assert. Change the clause to
   `… run unattended: /clear now and run`. The `/dev:autopilot docs/dev/<feature-name>/spec.md`
   **command line itself is untouched** (`spec:641`, `spec:644`) — only the prose leading into it
   changes.

5. Rewrite the paragraph titled **"What this offer deliberately does not do"** (`spec:650`). It
   currently claims the offer prints above `Wait for explicit user approval` and that "everything
   below … is untouched." Both are false after step 4. The rewritten paragraph must state:
   - the offer is still static text: it adds no prompt, consumes no user answer, writes no state, and
     does not end the session;
   - it now prints **after** the `When approved` state write, so a user who wants the gated flow
     simply ignores the extra line, exactly as before;
   - the approval flow itself — `Wait for explicit user approval`, Path A, Path B, and the
     `When approved` state write — is unchanged in content and order. Only what prints after it moved.

6. Rewrite the paragraph titled **"The command is only meaningful after approval."** (`spec:652`).
   Retitle it **"The command is not printed until approval is recorded."** It must state:
   - the resume line and the offer print below the `When approved` state write, so the operator
     cannot receive either one while `completed[]` still lacks `"spec"`;
   - **no guard was added.** The anti-guard argument in the old paragraph is honored, not overridden:
     moving the print below the write removes the state a guard would have had to inspect, so the
     offer still knows nothing about approval state. Say this explicitly — a reader who remembers the
     old paragraph must be able to see the constraint was kept rather than dropped.
   - Do **not** carry over the words "harmless" or "Nothing breaks: autopilot resumes *at Spec*."
     Success criterion 6 greps for `harmless` across `plugins/dev/skills/`.

7. Rewrite the idempotence paragraph at `spec:654` ("Because the offer holds no state, a gate
   re-display after a Path A or Path B revision is idempotent — the same text re-renders."). After
   the move the offer is no longer part of what re-renders. The replacement must state: a Path A or
   Path B revision re-displays the **gate body** — which holds no state and so re-renders identically
   — while the resume block prints once, after approval, and is therefore never re-rendered by a
   revision loop.

8. Update the `**Autopilot mode:**` line at `spec:679`. Its trailing sentence — "Because the gate
   does not render, the autopilot offer never prints here either." — reasons from the offer being
   inside the gate block, which step 4 ends. Replace that sentence with one that reasons from the new
   position: in autopilot no gate renders and no approval is taken, so neither the gate body nor the
   resume block prints. The rest of the line (no gate; Step 12a's loop has resolved or escalated;
   update state and notify the orchestrator to proceed) is unchanged.

9. Re-read Step 13 top to bottom and confirm all four hold: the `completed[]` write now appears
   **above** the resume command in the step's own text; no sentence anywhere in the file still says
   the offer prints above `Wait for explicit user approval` (success criterion 5); the Branch A clause
   at `:626` no longer claims byte-identical rendering; and no remaining sentence describes the resume
   block as part of what the gate renders.

### Task 2: Move the Shape gate's resume block below the state write

What: In `dev:shape` Step 11, relocate the resume/handoff block from above `Wait for explicit user
approval` to below the `When approved` state write, and rewrite the three paragraphs that assert its
old position — including the one that argues about the Design Status confirmation.
Used by: The operator at the Shape gate, who now receives a continuation command only after
`completed[]` records `"shape"`. Same guarantee Task 4's rule depends on.
Depends on: Task 1 — this task mirrors the ordering Task 1 establishes, and must match it.
Files: modify `plugins/dev/skills/shape/SKILL.md`
Interfaces:
- Consumes: **gate resume-block ordering** from Task 1 (gate body → wait → approve → state write +
  commit → print the resume block), and Task 1's replacement sentence for the early-paste claim.
- Produces: nothing — no later task reads this file.
- State keys: none — no new `state.json` key. The `completed[]`/`stage` write at `shape:251` is an
  existing write, unchanged.
- Shared procedure: **gate resume-block ordering** — **mirror of Task 1**, which is canonical.
  Per the Isolation Principle the branch structure is restated here in full rather than deferred:

  > **Branch A — next stage is Shape.** No offer; the block is the resume line plus the `Worktree:`
  > line. *At this gate Branch A is unreachable* — Shape's next stage is always Plan — and `shape:224`
  > already names it as considered-and-unreachable. Keep that line as-is.
  > **Branch B — next stage is Plan or Build.** The offer prints; the block is the resume line, then
  > the offer, then the `Worktree:` line last. At this gate Branch B is always taken (`shape:225`).
  > **Path A / Path B revision** — re-displays the gate body only; the resume block is not
  > re-rendered, because it prints once, after approval. (`dev:shape` Step 11 has no challenger and so
  > no Path A/Path B split of its own — it has one "if changes requested" path at `shape:249`. The
  > rule applies to that path.)
  > **When approved** — write `completed[]` + `stage`, commit, *then* print the block.

  The one structural divergence from Task 1, stated because it is real and not a drift: this gate
  carries a **Design Status confirmation** (`shape:247`) between the gate body and
  `Wait for explicit user approval`. It stays exactly where it is; the resume block moves past it to
  below the state write.

Implementation steps:

1. Read `plugins/dev/skills/shape/SKILL.md` lines 220–253 (Step 11) in full before editing.

2. **Cut** these lines out of the fenced gate block at `shape:227–237`:
   - `Safe to /clear now — resume with: /dev:plan docs/dev/<feature>/design.md` (`:232`)
   - the three-line offer, `Or hand the rest of the cycle to autopilot — Plan → Build → Validate → PR
     → Done run unattended: approve above, then /clear and run` + `  /dev:autopilot
     docs/dev/<feature>/design.md` (`:233–235`)
   - `[If worktreePath is set: Worktree: <worktreePath>]` (`:236`)

   What stays: the `Design written and committed to …` line and `Please review it and let me know if
   you'd like any changes before we move to Plan.`

3. Move the sentence at `shape:239` ("Keep the `Worktree:` line last …") down with the block, as in
   Task 1 step 3.

4. **Paste** the cut block, in its own fence, immediately below the `When approved:` line at
   `shape:251` and above the `**Autopilot mode:**` line at `:253`, introduced with `Then print the
   resume block:`. Preserve internal order: resume line, offer, `Worktree:` line last.

   The Branch A/B paragraphs at `shape:222–225` keep their position above the gate body — they govern
   *whether* the offer prints, not where it prints. One clause inside them is rewritten by step 4a
   below.

4a. Rewrite the Branch B clause at `shape:225`. It currently reads: "**Branch B — next stage is Plan.**
   Always taken; the offer prints on every render of this gate." The second half is false after step
   4: a Path-equivalent re-display (the "if changes requested" path at `shape:249`) renders the gate
   body **without** the resume block. Keep "Always taken"; replace "the offer prints on every render
   of this gate" with a statement that the offer prints **once**, in the resume block below the
   `When approved` write — not on a gate re-display.

   Leave the Branch A clause at `shape:224` alone. It says Branch A is unreachable from this gate and
   is named only so a reader comparing this site to `dev:spec` Step 13 sees it was considered — a
   claim the move does not touch.

4b. Rewrite the offer's lead-in clause at `shape:234`, which currently ends `… run unattended: approve
   above, then /clear and run`. Printed below the `When approved` write, "approve above" tells the
   operator to do something already done. Change it to `… run unattended: /clear now and run`. The
   `/dev:autopilot docs/dev/<feature>/design.md` **command line itself is untouched** (`shape:235`).
   This mirrors Task 1 step 4b, which makes the same edit at `spec:640` and `spec:643`.

5. Rewrite the paragraph titled **"What this offer deliberately does not do"** (`shape:241`). It
   currently argues that because the offer cannot be "accepted," there is no path by which it can
   pre-empt the Design Status question — an argument built on the offer printing *before* that
   question. The rewrite must state:
   - the offer is still static text: no prompt, no consumed answer, no state write, does not end the
     session;
   - it now prints after the `When approved` state write, which is **below** the Design Status
     confirmation — so the confirmation is reached and answered before the offer exists at all. The
     old concern is not merely still-handled, it is structurally gone. Say it that way.
   - the Design Status confirmation, `Wait for explicit user approval`, and the `When approved` write
     are unchanged in content and order.

6. Rewrite the paragraph titled **"The command is only meaningful after approval."** (`shape:243`) —
   the file's one `harmless` hit. Retitle it **"The command is not printed until approval is
   recorded."** It must state:
   - the resume line and offer print below the `When approved` state write, so the operator cannot
     receive either while `completed[]` lacks `"shape"`, and cannot receive them without having
     answered the Design Status question;
   - no guard was added, for the same reason as the canonical;
   - **and it must keep citing `dev:spec` Step 13 as the canonical statement** (the old text ends "for
     the same reason as the canonical at `dev:spec` Step 13"). Spec `## Technical Constraints`:
     duplication is named at both ends, and this citation must not be dropped in the rewrite.
   - Do not carry over the word "harmless."

7. Rewrite the idempotence paragraph at `shape:245` the same way as Task 1 step 7: a re-display after
   requested changes re-renders the **gate body**, which holds no state; the resume block prints once,
   after approval, and is never re-rendered.

8. Update the `**Autopilot mode:**` line at `shape:253` the same way as Task 1 step 8 — replace
   "Because the gate does not render, the autopilot offer never prints here either." with reasoning
   from the new position: in autopilot no gate renders and no approval is taken, so neither the gate
   body nor the resume block prints.

9. Re-read Step 11 and confirm all four hold: the `completed[]` write appears above the resume
   command; no sentence in the file still says the offer prints above `Wait for explicit user
   approval`; the Branch B clause at `:225` no longer claims the offer prints on every render; and no
   remaining sentence describes the resume block as part of what the gate renders.

### Task 3: Move the Plan gate's resume line below the state write

What: In `dev:plan` Step 8, relocate the resume line and the `Worktree:` line from above `Wait for
explicit user approval` to below the `When approved` state write.
Used by: The operator at the Plan gate, who now receives `/dev:build …` only after `completed[]`
records `"plan"`.
Depends on: Task 1 — mirrors the ordering it establishes.
Files: modify `plugins/dev/skills/plan/SKILL.md`
Interfaces:
- Consumes: **gate resume-block ordering** from Task 1.
- Produces: nothing — no later task reads this file.
- State keys: none — no new `state.json` key. The `completed[]`/`stage` write at `plan:285` is an
  existing write, unchanged.
- Shared procedure: **gate resume-block ordering** — **mirror of Task 1**, which is canonical. Branch
  structure restated in full, since it differs here by *absence* and a reader must be able to see the
  absence is intended:

  > **Branch A / Branch B** — *neither exists at this gate.* `dev:plan` Step 8 prints no autopilot
  > offer at all, so there is no offer branch to select and nothing to add. The block that moves is
  > the resume line plus the `Worktree:` line, and only those two.
  > **Path A (challenger-applied fixes) / Path B (user-originated changes)** — both re-display the
  > gate body only; the resume block is not re-rendered, because it prints once, after approval.
  > **When approved** — write `completed[]` + `stage`, carry pending `challenge_plan.*` writes,
  > commit, *then* print the block.

  This task also does **not** touch the three paragraphs Tasks 1 and 2 rewrite: `dev:plan` Step 8
  carries none of them (spec `## Scope` item 4). Confirm by reading — do not add them.

Implementation steps:

1. Read `plugins/dev/skills/plan/SKILL.md` lines 254–287 (Step 8) in full before editing.

2. **Cut** from the fenced gate block at `plan:257–268` (the fence opens at `:257`; `:256` is blank):
   - `Safe to /clear now — resume with: /dev:build docs/dev/<feature>/plan.md` (`:266`)
   - `[If worktreePath is set: Worktree: <worktreePath>]` (`:267`)

   What stays: `Plan written and committed to …`, `[Step 7a's verdict, verbatim]`, the
   `[If the verdict has findings: …]` line, and `Please review it and let me know if you'd like any
   changes before we start building.`

3. **Paste** the two cut lines, in their own fence, immediately below the `When approved:` paragraph
   at `plan:285` and above the `**Autopilot mode:**` line at `:287`, introduced with `Then print the
   resume block:`. Keep the `Worktree:` line last.

4. Check the cross-reference at `plan:201` (Step 7a's opening): it quotes Step 8 as saying *"Safe to
   /clear now — resume with /dev:build docs/dev/<feature>/plan.md"*. The quoted **text** is unchanged
   by this task, so the citation stays accurate and needs no edit. Verify this by reading rather than
   assuming; if the quote were to name the line's *position* it would need rewriting, and it does not.

5. Update the `**Autopilot mode:**` line at `plan:287` only if it reasons from the block's old
   position. Read it: it currently says "No gate. Step 7a's revision loop has already resolved or
   escalated; update state and proceed. (Do not write `challenge_plan.dismissed` in autopilot.)" —
   this makes no positional claim and no offer claim, so leave it unchanged. Do not edit it into
   matching Tasks 1 and 2; those two had a sentence about the offer that this file does not carry.

6. Re-read Step 8 and confirm the `completed[]` write appears above the resume command.

### Task 4: Give `dev:autopilot` Step 3 an explicit start-stage rule

What: Add to `dev:autopilot` Step 3 the rule that a run begins at the earliest stage in the selected
tier row that is absent from `completed[]`, and runs from there to the end — then make Step 4's
completion report distinguish stages this run executed from stages it inherited as already complete.
Used by: Every autopilot invocation on a resumed cycle — this is the behavior change the cycle exists
for. Task 5 reads the value this rule resolves.
Depends on: Tasks 1, 2, 3 — the rule is keyed on `completed[]`, and is only sound once the three gated
stages record completion before handing over the resume command.
Files: modify `plugins/dev/skills/autopilot/SKILL.md`
Interfaces:
- Consumes: **gate resume-block ordering** from Tasks 1–3, as the precondition that makes
  `completed[]` current at the moment the operator receives the command.
- Produces: **the resolved start stage** — that exact phrase, defined here as "the earliest stage in
  the selected tier row that is not present in `completed[]`." Task 5 consumes it by that name.
- State keys: none — this task introduces no new `state.json` key. It adds a **reader** of the
  existing `completed[]`, which is written by `dev:spec`, `dev:shape`, `dev:plan`, `dev:build`,
  `dev:validate`, and `dev:pr`. No write-mode declaration is needed because nothing new is written.
- Shared procedure: none — no other task states this rule.

Implementation steps:

1. Read `plugins/dev/skills/autopilot/SKILL.md` lines 133–150 (Step 3) in full before editing.

2. Leave the **Tier detection** paragraph (`:137`), the **UI vs no-ui detection** paragraph (`:139`),
   and the three tier rows (`:141–143`) exactly as they are. The new rule composes with row selection
   and does not replace it — spec `## Scope` item 1.

3. Insert a new bolded paragraph, **Start stage**, immediately **after** the three tier rows at
   `:143` and before the `After each stage:` template at `:145`. Order matters: the rule selects a
   position within a row, so the row must already be selected when it is read. It must state:

   - **The run begins at the earliest stage in the selected row that is not present in `completed[]`,
     and runs from there through the end of the row.** Call that stage **the resolved start stage** —
     use that exact phrase, because Step 1 refers to it by name.
   - Stages already in `completed[]` are **skipped, never re-entered.**
   - **`completed[]` is the authority; `stage` is a hint.** Where they disagree — `stage: "build"`
     with `completed: ["spec", "shape"]` — the run starts at Plan. Give that reasoning: the worst case
     under this rule is redoing a stage that succeeded but was never recorded, which is recoverable,
     where the inverse — building with no `plan.md`, unattended — is not.
   - **An absent or empty `completed[]` selects Spec**, which is the first stage of every row. That is
     every cold start; row selection then proceeds on the `skipped[]` that Spec writes, unchanged from
     today.
   - **A skipped stage can never be selected.** A skipped Shape is absent from the `+ no-ui` row
     entirely, so the earliest-unfinished search never sees it. This is why the rule composes with row
     selection rather than needing its own `skipped[]` check.
   - **Resolve once, at the start of the run.** The rule picks the entry point; it is not re-evaluated
     between stages. State this explicitly. Without it, the silent-backtrack rule at `:114–123` — and
     `dev:build`'s standard-mode backtrack at `build/SKILL.md:133`, which *removes* `"plan"` from
     `completed[]` — could be read as sending an in-flight run backwards to a stage it already
     executed.

4. Add the terminal case as its own short paragraph, immediately after **Start stage** (spec `## Scope`
   item 3). It must state:
   - when the resolved start stage is **Done**, autopilot runs Done normally — that is the reachable
     end-of-cycle case;
   - `"done"` is never added to `completed[]` (`dev:done` writes no completion entry, and its Step 7
     `rm -rf`s the cycle directory at `done/SKILL.md:504`), so "every row stage in `completed[]`" is
     unreachable and must not be the trigger for anything;
   - a cycle that has already finished Done has no `state.json`, and Step 1's existing
     `No /dev cycle found for <feature>` STOP already covers it.

5. **Add no stop condition.** Do not edit the "When autopilot stops" list in `## Purpose` (`:14`).
   Success criterion 7 requires that list unchanged, and spec `## Technical Constraints` names this as
   `dev:plan`'s cross-skill ripple rule applied in the negative direction: no new stopping behavior is
   introduced, so the stop list and every mirror of it stay untouched.

6. Make Step 4's completion report honest about a resumed run. The template at `autopilot:158–171`
   prints every row stage with a `✓` and a stage-specific metric (`Spec ✓ [confidence: XX%]`,
   `Validate ✓ [N loops]`). Once this task lets a run start mid-row, those lines assert work the
   invocation did not do — on success criterion 3's `completed: […, "pr"]` case the report would claim
   six stages ran when only Done did.

   Add one bracketed alternative to the template, in the shape the template already uses for
   `[or "Shape skipped (no-ui)"]`: a stage that was already in `completed[]` at the start of the run
   renders as **`<Stage> — already complete`** instead of `✓` plus metrics. Add one sentence below the
   fence stating that only stages this invocation actually executed carry `✓` and metrics.

   **Do not use the word "skipped" in the new form.** The template's existing `Shape skipped (no-ui)`
   already owns that word for a different meaning — a stage the cycle never runs at all, versus one
   that ran under a previous invocation. Two senses of "skipped" on adjacent lines of the same report
   is exactly the ambiguity an operator cannot resolve from the report alone.

   This is not a new stop condition and does not touch the `## Purpose` stop list — it is the report
   line for a run that completed normally, having started partway down its row.

7. Re-read Step 3 top to bottom and confirm a reader gets the answer to "which stage does this start
   at" **without having to open another skill** (success criterion 4). The test is whether the answer
   *requires* the lookup, not whether citations appear: Step 3 already cites `dev:spec` Step 12 and
   `spec/SKILL.md:478` in the UI-detection paragraph step 2 preserves verbatim, and step 3's own
   resolve-once rationale cites `build/SKILL.md:133`. Those are supporting references for reasoning
   stated in full on the page, and they stay. What must not happen is the rule itself being stated
   elsewhere and pointed at from here.

### Task 5: Bind Step 1's announce line and `handoff_at` to the resolved start stage

What: In `dev:autopilot` Step 1, derive both the `Resuming from <current-stage>` announce line and the
`handoff_at` write from Task 4's resolved start stage instead of from the raw `stage` field, and
restate the `:81` justification that cited the claim Tasks 1 and 2 delete.
Used by: The operator reading the announce line; `dev:done` Step 5 and `dev:reflect` Step 4, which
read `handoff_at`.
Depends on: Task 4 — consumes the resolved start stage by name. Also Tasks 1 and 2, which delete the
"both gates document as harmless" claim this step currently cites.
Files: modify `plugins/dev/skills/autopilot/SKILL.md`
Interfaces:
- Consumes: **the resolved start stage** from Task 4, by that exact phrase; and Task 1's replacement
  sentence for the early-paste claim.
- Produces: **the unchanged `handoff_at` value domain** — the statement that the domain stays open
  (any stage name, not an enum) and that a gate-stage value is recorded rather than corrected. Task 6
  consumes it by that name, and its `dev:done` Step 5 sentence must not contradict it. No other task
  reads this file.
- State keys: no **new** key. `handoff_at` already exists and keeps its existing
  `(writes: autopilot-only)` mode — this task changes only what value is written, not who writes it or
  when. Do not alter the write-mode annotation at `:78`.
- Shared procedure: none.

Implementation steps:

1. Read `plugins/dev/skills/autopilot/SKILL.md` lines 63–86 (Step 1's state-reading and mode-flip
   region) in full before editing.

2. Amend the paragraph at `:63` ("**Read `tier` and `stage` from the resolved `state.json`, not from
   the request.**") to also read **`completed[]`**, and to say that `tier`, `skipped[]`, and
   `completed[]` together resolve the start stage **per Step 3's Start stage rule**. Cite Step 3 by
   name rather than restating the rule — Task 4's is the single statement of it. This forward
   reference to a later step matches the one already at `:61`, which defers to "Step 3's **UI vs
   no-ui detection** rule below."

   Add the degenerate case in one sentence: on a cold start there is no `state.json`, `completed[]` is
   absent, and the resolved start stage is Spec — so Step 1 always has a value, and no ordering
   problem arises from the rule living in Step 3.

3. Change the announce template at `:67–72` so `Resuming from <current-stage> in autopilot mode.`
   reads from the resolved start stage. Replace the placeholder `<current-stage>` with
   `<resolved-start-stage>` and add one sentence below the fence stating that this is the stage the run
   will actually start at, not the raw `stage` field — the two were previously separate readings of
   state, and a resume rule that left them separate would keep the same defect alive in the message
   instead of the behavior (spec `## Scope` item 2).

   Leave `<stage-status-line>` as-is.

4. In the first mode branch at `:78`, change the `handoff_at` value from "the value of `stage` **as
   read before the flip**" to **the resolved start stage**. Keep everything else about the branch
   intact: it still fires only when a prior session existed with `mode` reading `"standard"`, and both
   writes still go in the same `state.json` update.

   Keep the surrounding instruction at `:76` that state is read **before** any stage of this run has
   executed, and before the `mode` flip — that constraint is unchanged and still load-bearing.

   But amend its *justification*. It currently reads "Read `stage` **before** flipping `mode` —
   reading it after records the stage autopilot advances to rather than the one it took over at."
   After this task the value no longer comes from `stage`, so that sentence points a reader at the
   wrong input. Restate it in terms of the field the rule now depends on: read **`completed[]`** before
   any stage of this run has executed, because a stage this invocation completes would otherwise be
   counted as one it inherited, and the marker would name a stage the run did not take over at.

5. Leave the second mode branch at `:79` untouched: no prior session, or `mode` already `"autopilot"`
   → do not write `handoff_at` at all; absent is the value.

6. Rewrite the paragraph at `:81`. Two things change and one must not:
   - **The reasoning for the approved-path value.** It currently says the value is `"plan"` (or
     `"build"` on micro) "because gate approval advances `stage` to the next stage before the user
     pastes the command." Under Task 4 that is no longer the mechanism. Restate it: on the approved
     path the gate has written the stage into `completed[]` before the command was printed at all
     (Tasks 1–3), so the earliest unfinished row stage — and therefore `handoff_at` — is Plan, or
     Build on micro.
   - **The deleted citation.** Replace "A user who pastes the command *before* approving — a path both
     gates document as harmless — legitimately produces `"spec"` or `"shape"` here" with Task 1's
     replacement sentence, **stated by cause rather than by route**: `handoff_at` names whatever stage
     `completed[]` does not yet record, and the marker reports it accurately. Two distinct paths reach
     a `"spec"`/`"shape"` value and the wording must cover both — (a) a user who types
     `/dev:autopilot` unprompted at a gate before approving, so `completed[]` lacks that stage; and
     (b) an **approved Branch A Spec gate on a UI cycle**, where `completed[]` holds only `"spec"` and
     the earliest unfinished row stage is legitimately Shape. Route (b) is ordinary correct operation,
     not an early paste, so a clause naming only (a) would read as an anomaly report for the common
     case. Do not use the word "harmless."
   - **What must not change:** the value domain stays **deliberately open** — any stage name, not an
     enum — and the final sentence about the Validate and PR gates (no offer is printed there, but a
     user who types `/dev:autopilot` has still handed off, and the marker records that stage
     accurately) stays as it is.

7. Leave the **Read contract for downstream consumers** paragraph at `:83` unchanged — absent
   `handoff_at` still means "no handoff," including on every cycle predating this feature, never an
   error. Leave `:85` unchanged: this is still the key's only write site, and the gates still write
   nothing.

8. Re-read Step 1 and confirm the announce line and `handoff_at` are two uses of **one** resolved
   value, not two readings of state (success criterion 8).

### Task 6: Restate `dev:done` Step 5's justification for a gate-stage `handoff_at`

What: In `dev:done` Step 5, replace the clause citing "which both gates document as harmless" with
Task 1's replacement sentence. Rendering behavior is unchanged.
Used by: The reader of a decision log whose `handoff_at` reads `"spec"` or `"shape"`, and the agent
deciding whether to "correct" it (it must not).
Depends on: Tasks 1 and 2, which delete the documentation this line cites; and Task 5, whose `:81`
rewrite this line must not contradict.
Files: modify `plugins/dev/skills/done/SKILL.md`
Interfaces:
- Consumes: Task 1's replacement sentence for the early-paste claim; the unchanged `handoff_at` value
  domain from Task 5.
- Produces: nothing — terminal task.
- State keys: none — no new `state.json` key. `handoff_at` is read here, never written.
- Shared procedure: none. This is the third restatement of Task 1's sentence (the others are Task 2's
  Step 11 paragraph and Task 5's `:81` paragraph), but each is one sentence inside a differently
  argued paragraph, not a procedure with branches — so no canonical/mirror designation applies.

Implementation steps:

1. Read `plugins/dev/skills/done/SKILL.md` lines 326–331 in full before editing.

2. Edit the sentence at `:328`: "A log that *does* read 'at Shape' or 'at Spec' is not corrupt — it
   records a user who pasted the command before approving the gate, which both gates document as
   harmless." Keep the first half. Replace the trailing clause with a **cause-based** statement
   matching Task 5 step 6: it records the stage `completed[]` did not yet hold when autopilot took
   over, which the marker reports accurately. Do not use the word "harmless," and do not narrow it to
   the early-paste route — an approved Branch A Spec gate on a UI cycle legitimately renders "at
   Shape," and that is ordinary operation rather than an anomaly.

3. Change nothing else in the region. Specifically, all of these stay exactly as they are:
   - `<Stage>` is the `handoff_at` value capitalized;
   - it names the **first stage that ran unattended**, not the gate stage;
   - the expected rendering on the Shape-gate route is "Handed off to autopilot at Plan," not "at
     Shape";
   - "Render the value as it stands; never correct it.";
   - the **When `handoff_at` is absent** paragraph at `:330` — byte-identical template, no blank line,
     no placeholder, no "n/a".

4. Verify success criterion 6: `grep -rn 'harmless' plugins/dev/skills/` must return exactly one hit,
   `done/SKILL.md:602` ("harmlessly otherwise", about a git fetch), which is unrelated and expected to
   remain.

## Edge Cases

| Edge case | Handled in | Approach |
|-----------|-----------|----------|
| `stage` disagrees with `completed[]` (crash mid-stage, or a manual `/dev <stage>` jump) | Task 4 step 3 | `completed[]` wins; start at the earliest unfinished row stage. The rule states the divergence example and the reasoning for choosing recoverable-over-unrecoverable. |
| Only Done remains | Task 4 step 4 | Done runs normally. `"done"` is never recorded in `completed[]`, so its absence is never a signal of unfinished work. |
| Cycle already past Done | Task 4 step 4 | No `state.json` exists; Step 1's existing `No /dev cycle found` STOP covers it. No new stop condition. |
| A stage crashed partway and was never recorded | Task 4 step 3 | Not in `completed[]` → re-entered and re-run. Correct: it never finished. |
| Operator pastes the command before approving | Tasks 1, 2, 3 | No longer reachable via the printed offer — the command is not printed until approval is recorded. Tasks 1 step 6 and 2 step 6 state this in place of the old "harmless" paragraphs. |
| Operator types `/dev:autopilot` unprompted at a gate | Task 5 step 6 | `completed[]` correctly lacks that stage, so the resolved start stage is that stage and `handoff_at` records it accurately. The value domain stays open. |
| Operator `/clear`s at the gate without approving | Tasks 1, 2, 3 (by construction) | The resume command was never printed and `completed[]` correctly lacks the stage; re-invoking resumes at that stage, which is right — it was never approved. |
| Cold start (absent or empty `completed[]`) | Task 4 step 3 | Selects Spec, the first stage of every row; row selection then proceeds on the `skipped[]` Spec writes, unchanged from today. |
| Micro tier | Task 4 step 2 | Row selection is untouched, so Micro still takes its own row and never consults the UI/no-ui rule. The start-stage rule operates within whichever row was selected. |
| Silent backtrack mid-run removes a `completed[]` entry | Task 4 step 3 | The rule resolves **once**, at the start of the run — it is not re-evaluated between stages, so an in-flight run is never sent backwards. |
| Cycles predating this change | Task 4 step 3 (no task needed) | `completed[]` has always been written by every stage, so no migration and no back-compat branch. A cycle mid-flight when this ships resolves normally. |
| Legacy in-place cycles (`worktreePath: null`) | none — unaffected | The rule reads `state.json`; `WORKDIR` resolution is untouched by every task. |

## Out of Scope

- **No new stage token.** `/dev:autopilot plan docs/dev/<feature>/spec.md` was declined at spec. The
  six printer sites (`spec:641`, `spec:644`, `shape:235`, `dev:252`, `autopilot:50`, `autopilot:179`)
  and the Component Registry row keep their **command text** exactly as it stands — no argument, no
  token, no path change. Tasks 1 and 2 move two of those sites within their files and reword only the
  **lead-in prose** around them (steps 4b), never the command line itself. `dev:252`, `autopilot:50`,
  and `autopilot:179` are not touched at all.
- **No way to force a re-run through autopilot.** To redo a finished stage, invoke that stage's own
  skill.
- **`/dev`'s jump-to-stage (Step 5a) keeps its re-run hole.** `dev/SKILL.md` is not in the file set.
- **`dev:build`, `dev:validate`, `dev:pr` gates.** Already write-then-print (`build:146→160`,
  `validate:427→450`, `pr:206→222`) — they are the convention Tasks 1–3 bring the other three into
  line with, and they need no edit.
- **`dev/SKILL.md:70` and `:252`.** Both describe the offer as *printed at the Spec and Shape gates*.
  That stays true after the move — the offer still prints at those gates, just later within them — so
  neither is a sixth file. Checked at plan time by reading both lines; Build must not edit them.
- **The Component Registry row for `dev:autopilot`** (`CLAUDE.md:29`), which currently says the skill
  "reads `tier`/`stage` from the resolved `state.json`". Reconciled at Done by `dev:done` **Step 4**,
  which is that table's sole writer (`done:217`) — **not** Step 4a, which is hard-forbidden from
  touching it (`done:241`, and invariant #8 at `done:296`). Spec `## Dependencies` cites Step 4a; that
  citation is wrong and this line corrects it. Either way it is not a Build task.
- **No test harness.** `backlog-dev-skill-test-harness` tracks that gap and is not paid here.
- **The other fourteen open backlog items touching these files.** Surfaced at spec Step 7, left open.
