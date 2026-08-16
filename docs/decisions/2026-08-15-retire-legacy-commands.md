# Retire Legacy Commands — Decision Log
*2026-08-15 · Branch: feature/retire-legacy-commands · PR #82*
*Handed off to autopilot at Spec*

## What was built

A new report-only `dev:secure` skill with whole-project and `diff` verbs, plus a security review and
a build check on every route to a PR — closing the capability gaps that made four legacy
`~/.claude/commands/` files worth keeping, and then documenting their retirement.

## Key decisions

- **Close the capability gap before retiring anything** → grounding found `/dev:fix` opened PRs
  unattended with *zero* security review (`grep -i security fix/SKILL.md` → no hits), while the
  seven-stage pipeline was covered. Retiring `security-review-diff.md` against that gap would have
  been a loss, not a consolidation. So §1–§3 ship the capability and §4 documents the retirement.
- **Name it `secure`, and make the skill correct its own implication** → the spec author twice argued
  that `secure` names an outcome the skill does not deliver and proposed `risk` or `audit`. The user
  chose `secure` on the grounds that the namespace's convention is single-word and verb-shaped
  (`fix`, `validate`, `build`, `plan`, `shape`, `reflect`). The cost is carried by a hard requirement:
  the frontmatter description **and** the skill's opening line must both state that it reports and
  modifies nothing. The name may not be the only thing telling the user what happens.
- **Report only; write nothing** → chosen over offer-to-capture and auto-capture. Keeps the new
  skill's blast radius at zero and makes the retirement an exact trade. The boundary is explicit: the
  skill writing nothing is a property of *the skill*, not a licence for its **caller** to drop
  findings — the lane still captures declined P3/Nits under its rigor floor.
- **The lane calls the skill rather than growing its own checklist** → one canonical implementation,
  no mirror to drift. Checkable: the security checklist's vocabulary appears zero times inside
  `dev:fix`'s new section.
- **Bounded inline fixing over stop-on-any-finding** → the spec author recommended stopping before
  the PR on any finding, matching what `pr.md` did. The user chose one round with a cold re-review,
  on the grounds that it keeps the fast path fast without letting an unreviewed fix through. The
  bound is what carries that argument: without the one-round cap and the re-review, this would be an
  unattended lane making security decisions unchecked.
- **One rule for a failing build and a failing suite** → the lane previously ran the suite and said
  only "record each result verbatim," never stating what a failure meant. Adding a blocking build
  check beside a merely-reported suite would have read as an oversight, so one rule covers both.
  This deliberately changes existing suite behavior.
- **The suite half is `dev:fix`-only, and the asymmetry is stated** → verified that `dev:validate`
  runs no suite at all (Steps 1–6 contain no invocation; `dev:build` runs tests during TDD). Saying
  so beats implying a symmetry that does not exist.
- **Architecture cycles keep their security carve-out** → the user was shown that those cycles still
  reach `dev:pr` and open unreviewed PRs, and chose to keep it. This cycle records the reasoning in
  `dev:validate` so it reads as a decision rather than an oversight, and the spec says plainly that
  "every route to a PR" therefore carries one named exception.

## Design choices

*Shape was skipped — no UI. Terminal output only.*

## Validation notes

- **3 loops run** (tier: deep), stopped by the **same-region recurrence** rule rather than by
  exhaustion — 3 of 5 loops used.
- **P2 — stale line citations.** Three cross-file citations the diff *added* were already wrong,
  shifted by the same diff's own earlier insertions; one pointed at the *architecture* severity
  table, the very scheme the sentence said the skill does not use. → replaced with section names.
- **P2 — wrong audit base.** The review diffed against the *local* default branch while the lane
  cuts its branch from `origin/` and the PR's base is the remote. A stale local ref is still an
  ancestor of HEAD, so the diff succeeds against a stale merge base and the audit covers unrelated
  commits. → origin-qualified `AUDIT_BASE` with a fallback.
- **P2 — argument injection.** The explicit `<base>` token reached `git diff` unvalidated. Measured:
  `git diff --output=FILE` **creates the file** and returns an empty diff, so the skill would report
  examining nothing while writing outside the repo — breaking its own zero-write invariant. →
  anchored ref allowlist plus `--end-of-options`.
- **P1 — introduced by loop 1's own fix**, caught by loop 2's cold re-review: `--end-of-options`
  placed *before* `--name-only` fatals with exit 128, which would have broken the diff verb on every
  run. Every other option must precede it.
- **P2 — found by executing the procedure rather than reading it.** Run from a worktree, the diff
  verb audits `$PRIMARY` and returns **0 changed files where the worktree has 13** — coming back
  *empty* rather than erroring, so a security gate would have reported "nothing to examine." Three
  prior reviews missed it. → `$PRIMARY` stays the audited tree (correct for `dev:fix`), but the verb
  now discloses: a notice naming both trees, the audited branch in the report header, and an
  empty-diff message naming branch and base.
- **Accepted as-is:** 3 P3 + 1 Nit, all inside the circling region, buffered to `docs/backlog/` as
  `debt-secure-tree-scoping-unsettled` and `debt-secure-report-fields-not-grounded-in-output`.

**The unsettled question, recorded rather than guessed:** which tree should `/dev:secure` audit when
invoked from inside a worktree? `dev:fix` needs `$PRIMARY`; a human standing in a worktree means the
tree they are looking at. That is a design call, not a fix-loop call.

**Two spec backtracks during Plan**, both committed with their reasoning inline:
- **SC11** declared `dev:autopilot` byte-identical while Scope §3 created a Validate stop that
  autopilot must document. Behavior recorded in one place only is a gap even when that place is
  correct. SC13 was added alongside for the two skill-enumerating surfaces (`dev:start`, README's
  Plugins table) that `dev:done` reaches in *neither* mode on an autopilot cycle.
- **SC3** asserted a whole-file grep of zero that measures **1** today — `fix/SKILL.md:76`, the
  `owner/name` allowlist's "argument-injection vector" prose. Read literally it would have forced
  Build to delete a load-bearing sentence. Re-scoped to the new section.

## Artifacts (archived)
Spec, plan, and validation committed at: 0f11bb8 on branch feature/retire-legacy-commands

## Retrospective
*Reviewed by dev:reflect · 2026-08-15*

**Spec:** 88%/Ready with `spec_revisions: 3` — and the *kind* of churn is diagnosable. One revision
came from the gated spec stage; the other two were Plan-stage backtracks, both the same defect class:
**a Success Criterion asserting a measurable check that nobody measured.** SC11 declared
`dev:autopilot` byte-identical without checking whether Scope §3's new Validate stop needed
documenting there; SC3 asserted a grep returns zero when it returns 1, and read literally would have
forced Build to delete correct security prose. Step 7's grounding inventory grounds as-is claims
about the *codebase* — and did that well, since "zero security in `dev:fix`" is the finding that
shaped the whole cycle — but never runs the greps the spec writes into its own criteria.
`challenge.blockers: 3` against `spec_revisions: 3` reads as the "both nets catching spillover" row,
and the spillover has one identifiable source.

**Shape:** skipped (no UI) — correct; terminal output only.

**Plan:** 4 challenger loops, 26 fixes applied, 0 dismissed, exiting clean. Not noise — every finding
was actionable, and the standout was structural: `dev:secure` and `dev:fix` resolved the base branch
with *opposite* precedence, so a stale `origin/HEAD` would have made the audit review a different
diff than the PR opened. `files_read_in_build: 4` says the resulting plan was specific enough that
Build barely re-read anything.

**Validate:** 3/5 loops, exited by the same-region recurrence rule rather than by exhaustion. Loop
1's own fix introduced a P1 (`--end-of-options` before `--name-only`, exit 128) that loop 2's cold
re-review caught — the mechanism working exactly as designed. **Two of the three P2s were found by
executing the procedure rather than reading it**, including one (`0 changed files where the worktree
has 13`) that three prior reading-based reviews all missed.

**Flow:** deep tier and no-ui both correctly detected; the handoff at Spec ran clean. **But the flow
finding that matters came from the user, not the counters** — see below.

**Token efficiency:** no outliers worth flagging. Spec dominates wall-clock (4h39m vs 8m plan / 7m
build / 31m validate), but that span is the interactive definition work plus two backtracks, which is
where the thinking belonged.

**User observations (Step 4 — the handed-off cycle's one pause):**
- **Project context does not survive between cycles.** "I as a human forget what milestone we're at
  and what's next... I have redirected us or skipped the order, not intentionally." No counter sees
  this. `dev:done` Step 8 does emit the milestone map and the next command — once, at the tail of the
  display, in the session that is ending. The user's preferred direction is **one worktree per
  project rather than per cycle**, so plan and context persist across cycles. Sized at 12 files.
- **The retrospective should run at the end of Validate**, so it ships inside the cycle's PR instead
  of being committed to the integration branch afterwards. This cycle is itself the evidence: PR #82
  merged, and then this decision log and this retrospective went to `main` outside any review.
  Notably a **recurrence** — `backlog-reflect-before-pr-merge` asked the same question and was closed
  the same day by the `fast-path` cycle, which built a lane that has no retrospective at all. It
  closed the question by sidestepping it while the pipeline it was about still has it.

**Suggestions:**
1. `dev:spec` Step 7 should **run** any grep or command a Success Criterion states as checkable and
   record the baseline — the rule this cycle just added to `dev:validate` Step 4 (step 3b), applied
   one stage earlier where a wrong criterion is cheapest to catch. Both Plan backtracks were this.
2. `dev:validate` Step 2 should prefer **executing** an added procedure over reading it when the diff
   contains shell. It is the single move that found what three reviews missed.
3. Carry "what's next" across the session boundary, per the user's observation above.
4. Move the retrospective ahead of the merge so it lands in the PR.
5. A close should record `closed_by:` — the prematurely-closed reflect item carries none, which is
   what made its close hard to attribute.

**Deferred to tech debt:** `debt-secure-tree-scoping-unsettled`,
`debt-secure-report-fields-not-grounded-in-output`, `backlog-project-context-lost-between-cycles`,
`backlog-reflect-before-pr-merge-retire-legacy-commands`
