# Retro Inside PR — Decision Log
*2026-08-23 · Branch: feature/retro-inside-pr · PR #92*
*Handed off to autopilot at Plan*

## What was built
Four `dev:done` steps — the Component Registry update, docs-prose reconciliation, decision log, and `dev:reflect` retrospective — moved into `dev:pr` Step 5, between its state write and its push, so a cycle's own reasoning lands in the PR a human reviews rather than being committed to the integration branch after the merge.

## Key decisions

**Place the block between Step 5's state write and its push → both constraints are real and they pin the position exactly.** After the write, because the decision log's `PR #N` header reads `artifacts.pr_number` and `dev:reflect` Step 1 reads `pr_created`. Before the push, because that push is what carries the commits into PR #N's diff. Above the write hides `pr_created`; below the push leaves the content out of the diff. This is also why the work could not simply move to the end of Validate, where no PR number exists yet — and changing the log's header would break comparability with every existing decision log.

**`dev:done`'s surviving steps keep their old numbers (1, 2, 3, 6a, 7, 8) → renumbering costs more than the gap.** Collapsing 6a → 4 would invalidate eleven prose references to "`dev:done` Step 6a" across `references/tech-debt.md`, `references/entry-adapters.md`, `debt/SKILL.md`, `spec/SKILL.md`, `fix/SKILL.md` and `reflect/SKILL.md` — files the spec's own 12-file surface excludes. Keeping the numbers is also what makes the spec's count of exactly three broken citations correct: all three break on shifted *line numbers*, not on a renumber.

**Three retro inputs dropped rather than deferred → none is worth a second write to a merged file.** Merge outcome is binary and `dev:done` Step 2 already STOPs loudly when it is not clean; the Step 3 plan check-off is mechanical and the plan file is itself the record; the Step 6a flush result is already listed by `dev:reflect` Step 3's `**Deferred to tech debt:**` line.

**`dev:reflect` Step 6's gate became three-way rather than staying yes/no → the acting path had to stop being the default.** "Yes" edits a skill and opens a second PR in-session; run pre-merge, that PR branches from a `main` lacking this cycle's edits — and this cycle edits `done`, `pr`, `reflect` and `fix`, the likeliest targets of such a suggestion. Naming the path `fix now`, beside `backlog` and `debt` which act on nothing, makes the collision a choice made with its cost visible instead of a trap. The carrying-cost test gates **both** recording choices, per the contract's "every capture site".

**`dev:pr` re-entry is idempotent resume, never a stop → the alternative loses work silently.** The obvious one-line fix — skip the stage when `pr_url` is set — was already measured wrong on an earlier cycle: the feature branch is published in exactly one place, so skipping the stage skips the push, and `dev:done` would then merge a stale remote head and force-delete the branch. Reusing the PR and always pushing is what keeps `dev:autopilot`'s "no row stage is exempted" rule honest without adding a stop condition.

**§P9's slug allowlist anchored per segment → the documented security property was not the delivered one.** `^[A-Za-z0-9._-]+/…` put `-` inside the character class, so `-foo/bar` passed while both §P9 and `dev:reflect` claimed it was rejected as an argument-injection vector into `gh --repo`. Adopting the anchored form `dev:fix` had already proven makes the claim true at all four copies.

**Two files edited outside the spec's stated surface, deliberately.** `migrate-tracker/SKILL.md` restated the §P9 regex verbatim — a property claim, not a citation, and SC6 forbids such a claim anywhere in `plugins/dev/`; it also carried two `done/SKILL.md:255` citations this cycle's own deletion staled. `debt/SKILL.md` held a fourth producing-stage roster that became wrong because `dev:pr` became a producing stage. Both are recorded in `validation.md` § Notes rather than left for a reviewer to infer.

## Validation notes
- 3 loops run (tier: deep, max 5). Final status clean; no P1 or P2 open.
- Both reviewers ran cold and were issued together; all six code bullets ran. **Neither returned a P1, and security returned no P2.**
- Loop 1 — two P2s: the re-entry commit guard had been applied to 1 of 4 sites; `dev:pr`'s `## Purpose` clause was missed. Seven P3s besides, including a retrospective-replace anchored on the *first* `## Retrospective` (which could discard committed sections of a meta-cycle's log) and four `file:line` citations this cycle staled.
- Loop 2 — three defect-class P3s, all false claims: an architecture-cycle example that does not hold (`dev:reflect` has no such carve-out), a bare-push claim contradicting its own Step 6 rewrite, and a fourth producing-stage roster.
- Loop 3 — one P2: loop 2's *cosmetic* roster-ordering edit had duplicated `dev:validate` in the canonical Mode-symmetry roster. That is Step 4's **circuit breaker** trigger; it fired, the P2 was fixed, and the four remaining prose P3s were buffered with fixes pre-drafted rather than risking another cosmetic pass.
- Step 3b measurement caught what both reviewers passed: `head -n 0` is illegal on BSD `head` (exit 1), so the first replace-branch would have broken on a log whose heading is line 1. Replaced with one `awk` pass, re-measured across four fixtures plus two consecutive re-entries.
- P3s accepted as-is: the four buffered as `retro-inside-pr-deferred-prose-p3s`, each verified non-load-bearing. Nits not recorded: `../..` passing the slug allowlist (pre-existing, no statable cost) and column-wrap overruns (pure polish).

## Artifacts (archived)
Spec, plan and validation committed at: f875e01ea5d06594d7dd99ef9565ace2ce3143ec on branch feature/retro-inside-pr

## Note on this cycle's own execution
This is the **last** cycle whose decision log and retrospective land on `main` after the merge. It ran under the previously-deployed skills, where `dev:done` still owned Steps 4/4a/5/6; the change it merged takes effect from the next cycle, which will carry both inside its own PR.

## Retrospective
*Reviewed by dev:reflect · 2026-08-23*

**Spec:** Healthy quadrant — 3 challenger blockers caught against 0 spec revisions, which is the "author's grounding pass is weak, challenger is catching it — working as designed" reading. Confidence 100%/Ready held up: nothing in Build or Validate contradicted the spec, and the grounding inventory's measured counts (35 citation-bearing lines, the six post-merge commit sites) were still accurate at Build.

**Shape:** Skipped (no UI).

**Plan:** `metrics.stage_timestamps.plan_end` is stamped at Step 7, which runs *before* Step 7a's cold review and its autopilot revision loop. This cycle's Plan reports 6 minutes; it actually took ~34. The 28 minutes of challenger loops are silently attributed to the gap before Build. `dev:spec` already solves the analogous problem — Step 13 re-stamps `spec_end` on every revision — so the fix is a known shape, not a new design. The mis-measurement grows with tier: deep allows 5 iterations.

**Validate:** 3/5 loops, clean. Two things worth recording. First, **Step 4's circuit breaker fired for what appears to be the first time**, and was right: a *cosmetic* roster-ordering edit in loop 2 duplicated `dev:validate` in the canonical Mode-symmetry roster, which loop 3 caught as a P2. The rule's premise — that this diff's prose is more fragile than its open P3s are valuable — was demonstrated rather than assumed. Second, **Step 3b's measure-before-commit rule caught a defect both cold reviewers passed**: `head -n 0` is illegal on BSD `head`, so the first retrospective-replace branch would have broken on a log whose heading is line 1. Two independent reviewers read that snippet and neither ran it.

**Flow:** Deep + no-ui was right. The handoff at Plan worked cleanly — `handoff_at` recorded it, and the decision log rendered it correctly.

**Token efficiency:** `files_read_in_build` = 8 on a 13-file change, because Plan named exact files and exact edits. The plan challenger's 4 loops are where the cost went: 14 fixes, of which 6 were blocker-driven and 8 concern-driven. This is the first cycle to exercise `applied_concerns` (added by `challenger-loop-economics`), and the split is the interesting part — most of the plan's revision effort went to non-fatal findings.

**Suggestions:**
1. Re-stamp `plan_end` after Step 7a's revision loop, mirroring `dev:spec` Step 13's `spec_end` handling, so Plan's duration includes the challenger.
2. Consider whether the fix-diff re-review should be told to *run* the shell snippets it reviews. Step 3b already requires the fixer to measure; the reviewers were not asked to, and the one portability defect this cycle produced was found by measurement, not review.

**Deferred to tech debt:** `retro-inside-pr-deferred-prose-p3s`, `debt-plan-end-excludes-challenger-loop`, `debt-fix-diff-reviewers-not-asked-to-run-snippets`.

**User observations:** none raised.
