# Autopilot Resume Stage — Decision Log
*2026-08-20 · Branch: feature/autopilot-resume-stage · PR #88*
*Handed off to autopilot at Plan*

## What was built

A handoff to autopilot now resumes at the first unfinished stage instead of re-running stages the
cycle has already finished.

## Key decisions

**`completed[]` is the authority; `stage` is only a hint.** → Where they disagree, the run starts at
the earliest unfinished row stage. The asymmetry is deliberate: the worst case under this rule is
redoing a stage that succeeded but was never recorded, which is recoverable, where the inverse —
building with no `plan.md`, unattended — is not.

**Fix both defects or neither.** → Autopilot never using the stage it read, and the three gated
stages handing over the resume command *before* recording completion, are independent bugs. A resume
rule keyed on `completed[]` is only as good as the guarantee that `completed[]` is current when the
operator receives the command, so the reordering is a precondition of the rule rather than a
companion cleanup.

**Move the print, don't add a guard.** → The prior design argued explicitly against a guard, on the
grounds that it would couple the offer to approval state. That constraint was honored rather than
overridden: moving the print below the `When approved` write removes the state a guard would have had
to inspect. The anti-coupling argument survives; only its conclusion about *where the text sits*
changed.

**The skip applies only ahead of the entry point.** → From the entry point onward every row stage
executes, even one already in `completed[]`. A non-contiguous `["spec","build"]` resolves to Plan and
deliberately re-runs Build, because a Build recorded before a re-planned Plan is stale work that must
not reach Validate. Discovered during validation, when the first phrasing left the two readings
ambiguous.

**Resolve once, at the start of the run.** → The rule picks an entry point; it is not re-evaluated
between stages. Without that, a mid-run `completed[]` change could be read as sending an in-flight
run backwards.

**No new stage token, and no new stop condition.** → `/dev:autopilot plan <path>` was considered and
declined at spec: six printer sites plus a registry row would each gain a value to keep correct. And
because `"done"` is never written to `completed[]`, the end-of-cycle case is "the resolved start stage
is Done, so run Done" — reachable and ordinary — rather than a new terminal condition. The
"When autopilot stops" list is untouched.

**PR re-entry was deliberately left unsolved.** → See the retrospective below; this was the cycle's
most expensive decision and it was reached by reversal.

## Validation notes

- 3 loops run (tier: standard). Final status clean — no open P1, P2, or P3.
- **Both Step 2 reviewers returned zero P1/P2 on the build diff.** Every P1/P2 recorded here was
  raised by a fix-diff cold re-review against a fix the validation stage had just made.
- **P2 (loop 2)** — loop 1 generalized the start-stage rule but left Step 4's completion report keyed
  on `completed[]` membership: one rule split across two steps, half updated. A re-run Build rendered
  both `✓` and `— already complete`, the latter falsely claiming an earlier invocation ran it.
  Resolved by keying the report on position relative to the entry point.
- **P1 (loop 3)** — loop 2 added a PR carve-out justified by "the re-run stages pushed their commits
  to the same branch." False: `pr/SKILL.md:142` is the only feature-branch push in the pipeline
  (measured: zero push sites in `build`, `validate`, `plan`, `shape`). Skipping the stage skips the
  push, so `dev:done` would merge a stale remote head and then force-delete the branch — silent loss
  of the run's work. Resolved by **removing** the carve-out, not patching it.
- **P3s, all fixed:** the canonical (`dev:spec` Step 13) left vaguer than its own mirror on the exact
  point the cycle changed; `dev:plan` Step 8 not answering whether the relocated block prints in
  autopilot; a stale membership instruction left in `plan.md`; and a `**Cost if not paid:**`
  paragraph written outside its buffer fence, where `dev:done`'s verbatim lift would have dropped it.
- **One nit accepted as-is:** the explanatory paragraphs in `dev:spec` Step 13 and `dev:shape` Step 11
  now precede the block they describe. Correct but out of order. Deliberately **not** recorded to
  `docs/backlog/` — the carrying-cost test asks what the next cycle pays, and the honest answer is a
  few seconds of re-reading, with no systemic gap behind it.
- **Build:** no build system detected (B5). Not rendered as a pass.
- **Security:** clean on every pass; no ecosystem scanner applies, reported as not-applicable rather
  than as a passing audit. The reviewer noted the change is a net security improvement — it closes
  the window in which a handoff command could be pasted before approval and run a stage unattended
  without the Design Status confirmation.
- Cycle artifacts were backtracked twice so `spec.md` and `plan.md` state what shipped rather than
  what was tried. `metrics.spec_revisions` is 1.

## Artifacts (archived)
Spec, plan, and validation committed at: 6fbd82a on branch feature/autopilot-resume-stage

## Retrospective
*Reviewed by dev:reflect · 2026-08-20*

**Spec:** 4 challenger blockers against 1 revision, 0 dismissed — the "author's own grounding pass is
weak, challenger catching it" quadrant, working as designed. The spec caught itself in one place worth
keeping: its grounding inventory recorded that the open-debt sweep said 10 when the answer was 15,
because the sweep ran against the pre-expansion file set and was never re-run after `plan` and `done`
entered scope — `debt-spec-grounding-sweep-file-set-lags-scope` recurring inside the cycle that
surfaced it. Confidence 100%/Ready was not overconfident: all three auto-filled dimensions survived
Build unchanged.

**Shape:** Skipped (no-ui) — correctly; the deliverable is five Markdown files.

**Plan:** Challenger ran 2 blocker-driven loops, 10 fixes applied, 0 dismissed. Both blockers were
real and both would have shipped: the Branch paragraphs whose claims the move falsified (which the
plan itself instructed Build to leave alone), and the offer copy reading "approve above, then /clear
and run" printed *below* the approval. A third catch corrected a wrong Registry-ownership citation
inherited from the spec.

**Validate:** 3 loops / 3 max — reached the cap but exited **clean**, not by exhaustion. The pattern
that matters: **both Step 2 reviewers returned zero P1/P2 on the build diff.** Every P1/P2 recorded
this cycle came from a fix-diff cold re-review of a fix the validation stage had just made. Spec and
Plan did their job; the loop budget was spent on defects validation introduced.

**Flow:** Tier (standard) and no-ui both correct, no unnecessary stages, no backtrack into an earlier
stage's skill. Two artifact backtracks, both correct and both cheap.

**Token efficiency:** `files_read_in_build` 8, `visual_screens_shown` 0 — no outliers. The 17h spec
span is an overnight session gap plus the backtrack's `spec_end` re-stamp, not a signal. The three
fix-diff re-reviews cost ~260k subagent tokens and two of the three returned a real P1/P2 — the cold
dispatch paid for itself.

**Suggestions:**
- `dev:validate` Step 4 step 3b should require measuring **every conjunct of a compound claim**, not
  the conjunct that is easiest to check. This cycle's P1 was one sentence containing two claims; the
  cheap half (`artifacts.pr_url` exists) was verified and the load-bearing half ("the re-run stages
  pushed their commits") was not.
- `dev:validate` Step 4 step 8's **same-region recurrence rule has no severity floor on its autopilot
  arm**. It says to stop fixing in-region and buffer the remaining findings — but the finding in the
  circling region here was a **P1**, and buffering it would have shipped a known correctness blocker.
  The stage escaped only because the region was deleted outright, which the rule does not require.
- **Scope creep entered through the fix loop.** Loop 1's reviewer flagged PR re-entry as "latent, not
  live" — explicitly out of scope — and the fix loop implemented it as behavior anyway, then spent two
  loops getting it wrong. Step 4 classifies P3s as defect-class vs polish but says nothing about a P3
  that proposes **new behavior outside spec scope**, which should be deferred rather than built where
  it gets neither spec review nor plan review.

**Deferred to tech debt:** `debt-validate-3b-partial-measurement-of-compound-claims`,
`debt-same-region-recurrence-no-severity-floor-autopilot`,
`debt-fix-loop-admits-out-of-scope-behavior-changes` (plus
`debt-autopilot-pr-re-entry-not-idempotent`, recorded at Validate).
