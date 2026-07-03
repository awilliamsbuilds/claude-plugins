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
