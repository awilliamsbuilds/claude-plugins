# Name Evaluation Rubric — Decision Log
*2026-07-18 · Branch: feature/name-evaluation-rubric · PR #27*

## What was built
Folded Lexicon's name-*evaluation* methodology into the `craft-name` skill so it weighs meaning and strategic fit alongside sound — a neutral phoneme→sensation mapping, an onset–center–coda test, three soft gates (off-category pull, scale, ownability), and a balanced-sheet verdict format.

## Key decisions

- **Keep the method, strip the answer key** → the source rubric ships reverse-engineered from one client's strategic brief (an AI/security/investigation platform), so its phoneme *verdicts* ("hard stops = good, soft endings = weak") are biased toward that brief. Adopted the phoneme→*sensation* mapping as neutral signals and bound "good vs. bad" to the project's own Step 1 target adjectives, rather than importing the rubric's fixed target-attribute checklist, Diamond framing, or 0–3 scoring sheet.
- **Soft flags, not hard gates** → deliberately departed from the rubric's hard two-gate Kill/Hold/Advance model. All three gates (off-category pull, scale, ownability) surface as prominent warnings a human weighs; a phonetically excellent name that trips a gate is still presented as a finalist with the flag called out, preserving the skill's advisory "here are the trade-offs" tone.
- **Scale gate is conditional** → tool-vs-platform sizing is only a liability when a platform/master brand is the goal; for a single-purpose app or an intended sub-brand, tool-sized is correct, so the gate stays quiet or routes to "good sub-brand" rather than flagging a problem.
- **Ownability as a modifier, not a first-class score** → generalized the rubric's hardwired AI/fintech/security categories to "the categories relevant to this project," and layered it onto the existing Step 9 (marketplace friction) signal rather than duplicating that checklist.
- **Reconcile, don't append** → replaced the old `## Quick Phonetic Heuristics` section outright with one `## Sound Symbolism: Phoneme → Sensation` section (single neutral "Reads as" column) instead of bolting a second, overlapping list beside it — honoring the spec's length-discipline and no-duplicated-guidance constraints on an already ~680-line file.
- **Standard tier, Shape skipped** → single-file Markdown skill-content change, no UI surface, so the Shape stage was correctly skipped.

## Validation notes
- 1 loop run (tier: standard, max: 3) — clean, no open P1/P2/P3.
- Code review and security review ran as fresh diff-only subagents (seeing only `7e62c59..a176a72`, spec Success Criteria, and the plan task list). Both returned no blockers: all four plan tasks and six success criteria met, no reintroduced "hard = good" bias, config contract untouched; no injection surface, no secrets, input-only source path not committed.
- 2 Nits fixed in loop 1: aligned the "trademark review" recommendation label across the Step 9 feed / Ownability gate / balanced-sheet option list; clarified that the futuristic-letters caution is about the *letter/spelling* (X/Z/K/V), distinct from the /v/ phoneme-sensation row.
- 1 Nit surfaced and accepted as-is: the two new sections sit after the Scoring Template, so Steps 4 and 9 forward-reference them — locality only (sections are bold and findable, mirroring where the old heading lived); relocating whole sections for no correctness gain was declined.

## Artifacts (archived)
Spec, plan, and validation committed at: 1f801bdec0e90d3bd4ed76f137562309302de4bc on branch feature/name-evaluation-rubric

## Retrospective
*Reviewed by dev:reflect · 2026-07-18*

**Spec:** Confidence 88% (Ready) matched actual clarity — Build needed no plan updates and Validate came back clean, so the score wasn't inflated. The two auto-filled dimensions (happy_path, dependencies) were both correct: happy_path was fully inferable from the skill's own existing process, and dependencies were genuinely trivial (single-file, input-only source). 3 questions asked, well under the 10 cap — appropriate for a well-scoped single-file change.
**Shape:** Skipped — correct call (Markdown skill-content change, no UI surface).
**Plan:** Accurate, no mid-build updates. The four tasks were correctly ordered as sequential edits to one file with only Task 4 carrying a true logical dependency; `files_read_in_build` = 2 (SKILL.md + state) confirms the plan was specific enough that Build didn't need to go hunting.
**Validate:** 1 / 3 loops — clean after one loop (2 Nits fixed, 1 surfaced-and-accepted). The diff-only fresh-subagent framing worked well: reviewers caught real label-drift and a phoneme/letter conflation without the benefit of session history. No P1/P2 slipped through — consistent with a prose-only diff.
**Flow:** Standard tier was right — enough conceptual surface (generalization principle, three gates, reconciliation risk) to warrant real Plan/Validate stages, not Micro. No unnecessary stages. Active work (plan_start → validate_end) was ~19 min; the ~2-day spec span was wall-clock gap, not effort.
**Token efficiency:** No outliers. `files_read_in_build` = 2 is minimal; `visual_screens_shown` = 0 as expected for a no-UI cycle. `stage_timestamps` fully populated.
**Suggestions:** One process observation, not a skill-edit request: this cycle ran entirely against a live concurrent session that owned the working tree on another branch, forcing every write (pr state.json, and all of done's main-branch commits) into isolated `git worktree`s. The dev:pr / dev:done skills assume the feature branch (or main) is the checked-out tree and use bare `git`/`git branch -d`; they have no guidance for the concurrent-session case. Worth considering whether dev:pr/dev:done should detect "current branch != expected branch" and either warn or default to a worktree. Deferred — not editing a skill from inside a cross-branch run.
