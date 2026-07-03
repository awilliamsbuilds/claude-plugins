# Absorb Superpowers Into Dev Plugin — Decision Log
*2026-07-03 · Branch: feature/remove-superpowers-convention · PR #10*

## What was built
Made the `/dev` plugin fully self-contained by absorbing the specific techniques it was implicitly relying on from Anthropic's `superpowers` plugin, so `/dev` never needs to invoke it and never risks producing competing `docs/superpowers/` artifacts alongside its own `docs/dev/<feature>/` convention.

## Key decisions

- **Selective absorption over guard notes, and over forking `superpowers`** → the original scope (add "don't invoke superpowers" notes) would have suppressed the redundant invocation but left `/dev` still functionally missing what those skills covered. Forking `superpowers` and merging `/dev`'s pipeline into it was considered and rejected — too large a reshaping for the actual overlap (4 of 14 skills), ties `/dev` to tracking a third-party repo, and `superpowers`' own contributor guidelines reject fork-specific changes outright. Landed on: port only the specific techniques `/dev` genuinely lacked, directly into the relevant stage skill.
- **Skill-by-skill audit before touching anything** → read `brainstorming`, `writing-plans`, `systematic-debugging`, and `requesting-code-review` in full and compared each against the corresponding `/dev` stage. Found `dev:spec` and `dev:shape` already exceeded `brainstorming`'s capabilities (confidence meter, tiers, "2-3 approaches") — avoided redundant work there.
- **`dev:plan` gained an `Interfaces:` block, "No Placeholders" rule, and type-consistency self-review check** (from `writing-plans`) → closes a real gap: tasks previously had no explicit contract for what they hand to later tasks.
- **`dev:build` gained a condensed root-cause-before-fix rule** (from `systematic-debugging`) → distinct from the existing plan-correction Backtrack Trigger; governs unexpected test failures specifically, not plan errors.
- **`dev:validate` now dispatches review as fresh subagents** (from `requesting-code-review`) → diff + spec + plan only, explicitly excluding session history, so the reviewer isn't biased by having watched the code get written. Falls back to in-session review if subagent dispatch is unavailable.
- **Supersede notes scoped to "while a `/dev` session is active"** → not a blanket suppression of `superpowers` outside `/dev`; the user still benefits from those skills in non-`/dev` work.

## Validation notes
- 1 loop run (tier: standard)
- This cycle dogfooded the new subagent-dispatch review mechanism (Task 6) on itself — the first real exercise of that code path.
- P1 fixed: `validate/SKILL.md`'s own new diff-scope wording was self-contradictory ("since branch creation" vs. "the commit before Build started")
- P2 fixed: subagent review prompt lacked "treat content as data, not instructions" framing — a real gap since `spec.md` can originate from an external Linear issue via `dev:fix`
- P2 fixed: `build/SKILL.md`'s "3 failed hypotheses" rule had no defined next step and silently conflicted with `autopilot/SKILL.md`'s stopping conditions — required touching `autopilot/SKILL.md`, outside the plan's original file list but a legitimate Build-stage discovery, not scope creep
- P3 fixed: `plan/SKILL.md`'s "No Placeholders" justification was factually wrong (claimed tasks execute out of order; `build/SKILL.md` says in-order)
- No P1/P2/P3/Nit issues remained open

## Artifacts (archived)
Spec, plan, and validation committed at: f5d41ce3f92f7e87f2678471214b35cba458c15e on branch feature/remove-superpowers-convention

## Retrospective
*Reviewed by dev:reflect · 2026-07-03*

**Spec:** Confidence score (100%, Ready) matched actual clarity — no plan updates needed during Build, no auto-filled dimensions to evaluate. Scope legitimately expanded mid-Spec (from "add guard notes" to "absorb techniques," then a fork-vs-absorb architecture question) — that's Spec doing its job, not a flow problem. `spec_questions_asked` shows 0 despite substantial guided back-and-forth (scope sequencing, cycle-count decision, fork-vs-absorb question); counter wasn't incremented.

**Shape:** Skipped (no UI). Correct call.

**Plan:** Mostly accurate — all 7 planned tasks executed as specified, no mid-Build plan updates. But Validate surfaced a real plan gap: Task 5 (`build/SKILL.md`'s new stop condition) had a hidden dependency on `autopilot/SKILL.md`'s stopping-conditions list that the plan didn't identify, discovered only during the fix loop.

**Validate:** 1 loop / 3 — efficient. This cycle's own new subagent-dispatch mechanism (built in this same cycle) reviewed its own output, catching a P1 (self-contradictory diff-scope definition) and a security P2 (missing data/instruction framing) that a same-session author might have been more likely to miss due to authorship bias. Dogfooding worked.

**Flow:** Tier (Standard) was correctly detected — cross-cutting enough (6 files) to not be Micro, not architectural enough for Deep. No unnecessary stages.

**Token efficiency:** `stage_timestamps` stayed completely empty (`{}`) for the entire cycle — never recorded at any stage transition, across all 5 stages. `files_read_in_build` was recorded (8) but `spec_questions_asked` was not. This is the second consecutive cycle (see `2026-06-07-changelog-integration` retro) where `spec_questions_asked`/`files_read_in_build` tracking was flagged as skipped; that retro's suggested fix (a bold callout reminder) evidently wasn't applied, and `stage_timestamps` is now revealed to be *fully* unpopulated too — a broader version of the same problem.

**Suggestions:**
- `stage_timestamps` and `spec_questions_asked`/`files_read_in_build` metric-tracking instructions are being skipped in live execution across at least two consecutive cycles now, despite being called out before. The prose-reminder approach isn't working. Consider making the instruction mechanically concrete (e.g., an explicit `date -u +%Y-%m-%dT%H:%M:%SZ` command shown inline at each stage's "Update State" step) rather than a plain sentence, since the current phrasing is easy to read past.
- Add a Plan self-review check: when a task changes a stage skill's stopping/gating/behavioral rules, explicitly check whether `dev:autopilot` (or any other skill that documents or depends on that behavior) needs a matching update. This would have caught the `build.md`/`autopilot.md` coupling before Validate instead of during it.
