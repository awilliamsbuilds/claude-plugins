# Absorb Superpowers Into Dev Plugin

*Branch: feature/remove-superpowers-convention · Confidence: 100% — Ready · 2026-07-02*
*Cycle type: feature · Tier: standard*

## Intent

`/dev` should be fully self-contained — it should never need to invoke, reference, or depend on the `superpowers` plugin, and it should never produce competing `superpowers`-branded artifacts (`docs/superpowers/`, `.superpowers/`) in the target repo.

Investigation confirmed the risk is real: no `dev:*` skill currently references `superpowers` directly, but the global `using-superpowers` meta-instruction tells Claude to invoke a `superpowers` skill "if there's even a 1% chance it applies." Mid-`/dev`-cycle, that can fire `superpowers:brainstorming` during Spec, `superpowers:writing-plans` during Plan, `superpowers:test-driven-development`/`systematic-debugging` during Build, or `superpowers:requesting-code-review` during Validate — each writing to its own folder convention. Confirmed empirically: `~/Workspaces/dev-plugin-design-archive` (used to design `/dev` itself, before `/dev` existed) contains only `docs/superpowers/plans/` and `docs/superpowers/specs/`, no `docs/dev/` at all.

Rather than just suppress the redundant invocation, the fix is to **absorb whatever `/dev` is actually relying on from `superpowers` directly into the corresponding `dev:*` skill**, so there's nothing left to invoke. Reviewed `brainstorming`, `writing-plans`, `systematic-debugging`, and `requesting-code-review` skill-by-skill against `/dev`'s current stages:

| Superpowers skill | Dev stage | Finding |
|---|---|---|
| `brainstorming` | `dev:spec` | No gap — confidence-meter-driven questioning already exceeds this. |
| `brainstorming` (design phase) | `dev:shape` | No gap — "2-3 approaches" step already present. |
| `writing-plans` | `dev:plan` | **Real gap.** Missing per-task `Interfaces: Consumes/Produces` block (exact signatures a task hands to later tasks), missing explicit "No Placeholders" rule, missing "type consistency" self-review check. |
| `test-driven-development` | `dev:build` | No gap — TDD steps already embedded (Step 2). |
| `systematic-debugging` | `dev:build` | **Real gap.** Build only backtracks when the *plan* is wrong (Step 4); nothing governs what to do when a test fails unexpectedly mid-implementation — the "root cause before fix" discipline is absent. |
| `requesting-code-review` | `dev:validate` | **Real design gap.** `dev:validate`'s review loop (P1-Nit classification, parallel code+security review) is already more structured, but it reviews in-session — the reviewer has watched the whole implementation and may be less objective. `requesting-code-review`'s core technique (dispatch a fresh subagent with only the diff + requirements, no session history) is worth adopting. |

## Scope

1. **`dev:plan`** — add to the Task Structure template (Step 3) and Self-Review (Step 6):
   - `Interfaces:` block per task — `Consumes:` (what it uses from earlier tasks, exact signatures) / `Produces:` (what later tasks rely on, exact names and types)
   - Explicit "No Placeholders" rule: no "TBD", "similar to Task N", "add appropriate error handling" — steps must show actual content
   - Self-review addition: type/signature consistency check across tasks (a function named differently in Task 3 vs. Task 7 is a plan bug)

2. **`dev:build`** — add a condensed root-cause-first rule for test failures discovered during implementation (distinct from the existing plan-is-wrong Backtrack Trigger): when a test fails unexpectedly, investigate why before patching — read the error completely, check what changed, form one hypothesis, test it minimally — rather than immediately altering code to make the test pass. Keep this condensed (a few lines), not the full four-phase process — `/dev`'s Build stage is meant to move fast within an already-approved plan.

3. **`dev:validate`** — change Step 2 (Feature Cycle reviews) to dispatch review as a fresh `general-purpose` subagent per review (code review, security review) rather than running inline in the current session. Subagent receives: the diff (`BASE_SHA..HEAD_SHA`), `spec.md` success criteria, `plan.md` tasks — explicitly NOT this session's conversation history. Main session receives the subagent's findings and continues the existing P1-Nit fix loop unchanged.

4. **Guard notes** — every stage-entry skill states explicitly that it supersedes its `superpowers` equivalent and that skill should not be separately invoked during an active `/dev` session:
   - `dev/SKILL.md` (entry) — supersedes `superpowers:brainstorming`, `superpowers:writing-plans`
   - `spec/SKILL.md`, `shape/SKILL.md` — supersede `superpowers:brainstorming`
   - `plan/SKILL.md` — supersedes `superpowers:writing-plans`
   - `build/SKILL.md` — supersedes `superpowers:test-driven-development`, `superpowers:systematic-debugging`
   - `validate/SKILL.md` — supersedes `superpowers:requesting-code-review`
   - Applies only while a `/dev` session is active (`docs/dev/<feature>/state.json` exists for the current feature) — not a blanket suppression of `superpowers` outside `/dev`.

5. Verify `dev:init`'s generated scaffold doesn't reference `superpowers` (already confirmed clean by grep).

## Out of Scope

- Changing the global `superpowers` plugin itself.
- Cycle #3 (context-clearing between stages / worktree vs. branch decision) — separate `/dev` cycle.
- Cycle B (new `dev:start` skill) — separate `/dev` cycle.
- Retroactively cleaning up existing `docs/superpowers/` folders in other repos (e.g. `dev-plugin-design-archive`) — historical, not this plugin's job.
- Adopting `writing-plans`' subagent-dispatch *execution* model (`subagent-driven-development`/`executing-plans`) for `dev:build` itself — `/dev` already has its own inline Build execution model; only the review-isolation technique from `requesting-code-review` is being adopted, not plan execution.
- Porting `systematic-debugging`'s full four-phase process, Red Flags table, or "3+ fixes = architectural problem" escalation verbatim — condensed to what fits `/dev:build`'s pace.

## Success Criteria

- `dev:plan`'s task template includes the `Interfaces` block, the "No Placeholders" rule, and the self-review type-consistency check.
- `dev:build` has an explicit root-cause-before-fix rule for unexpected test failures, distinct from the existing plan-correction Backtrack Trigger.
- `dev:validate`'s Step 2 dispatches a fresh subagent per review type, passing only diff + spec + plan — not session history — and the existing fix-loop logic (Step 4 onward) is otherwise unchanged.
- Every stage-entry skill listed in Scope item 4 states which `superpowers` skill(s) it supersedes.
- A fresh `/dev` run end-to-end on a test repo produces artifacts only under `docs/dev/<feature>/` — no `docs/superpowers/` or `.superpowers/` folder appears, and no `superpowers:*` skill is invoked.

## Happy Path

1. Developer runs `/dev` (or invokes a `dev:<stage>` skill directly).
2. Each stage now contains, inline, whatever `/dev` actually needs from the equivalent `superpowers` skill (plan's interface contracts, build's root-cause discipline, validate's review isolation) — plus an explicit note that it supersedes that skill.
3. The global meta-instruction has nothing left to add: `/dev`'s own content already covers the ground `superpowers` would have covered, so there's no reason for Claude to invoke it separately.
4. All artifacts for the cycle land under `docs/dev/<feature>/` only; no `superpowers:*` skill fires during an active `/dev` session.

## Edge Cases

| Case | Handling |
|------|----------|
| User explicitly invokes a `superpowers` skill directly (e.g. types `/brainstorm`) outside any `/dev` context | Fine — guard only applies while a `/dev` session is active for the current feature. |
| `dev:build`'s existing "When to deviate from TDD" section vs. new root-cause rule | New rule governs *test failures discovered mid-implementation*; existing TDD-deviation guidance governs *when to skip writing tests first* (config files, scaffolding). Different moments, no contradiction. |
| Subagent dispatch in `dev:validate` fails or is unavailable in a given harness | Fall back to in-session review (today's behavior) rather than blocking the loop — note this as a fallback, not a hard requirement. |
| Skill invoked standalone (e.g. `/dev:plan` without going through `/dev` orchestrator) | Guard note and absorbed content live in each stage skill individually, not just the entry point, so it applies regardless of invocation path. |

## Audience

Personal, single-user plugin repo (Adam only) — `awilliamsbuilds/claude-plugins`.

## Technical Constraints

- Repo uses `github` marketplace source type (not `directory` — broken in Claude Code). Changes must be pushed and merged to `main`, then `/plugin update` run to take effect.
- Markdown/YAML-frontmatter edits to existing `SKILL.md` files. The `dev:validate` subagent-dispatch change is the one behavioral (not purely additive) change — it alters *how* review runs, not just what's documented.

## Dependencies

None external. No dependency on Cycle B (`dev:start`) or Cycle #3 (context-clearing) — this cycle is fully independent and can ship first.

---
*Auto-filled dimensions: none — all filled from direct investigation (superpowers skill-by-skill review, repo grep, design-archive inspection) and confirmed via user's explicit answers above.*
