# Remove Superpowers Convention

*Branch: feature/remove-superpowers-convention · Confidence: 100% — Ready · 2026-07-02*
*Cycle type: feature · Tier: standard*

## Intent

`/dev`-managed cycles should never spawn competing `superpowers`-branded artifacts (`docs/superpowers/`, `.superpowers/`) in the target repo. Today the risk is real but indirect: no `dev:*` skill references `superpowers` directly (confirmed by repo grep), but the global `using-superpowers` meta-instruction tells Claude to invoke a `superpowers` skill "if there's even a 1% chance it applies." Mid-`/dev`-cycle, that can fire `superpowers:brainstorming` during Spec, `superpowers:writing-plans` during Plan, `superpowers:test-driven-development` during Build, or `superpowers:requesting-code-review` during Validate — each of which writes to its own folder convention, fragmenting the artifact trail that `/dev` is supposed to own. This was confirmed empirically: `~/Workspaces/dev-plugin-design-archive` (used to design `/dev` itself, before `/dev` existed) contains only `docs/superpowers/plans/` and `docs/superpowers/specs/` — no `docs/dev/` at all.

`/dev`'s stage skills already contain equivalent guidance inline (e.g. `dev:build` Step 2 has its own TDD instructions, `dev:plan` has its own task-list method) — they just don't say so explicitly, leaving the door open for the global meta-instruction to layer a redundant skill invocation on top.

## Scope

- Add a short, explicit guard note to each stage-entry skill stating that it supersedes its `superpowers` equivalent for the duration of a `/dev` session, and that the equivalent skill should not be separately invoked:
  - `dev/SKILL.md` (entry point) — supersedes `superpowers:brainstorming` (any creative/design decision) and `superpowers:writing-plans`
  - `spec/SKILL.md` — supersedes `superpowers:brainstorming`
  - `shape/SKILL.md` — supersedes `superpowers:brainstorming`
  - `plan/SKILL.md` — supersedes `superpowers:writing-plans`
  - `build/SKILL.md` — supersedes `superpowers:test-driven-development`, `superpowers:systematic-debugging`
  - `validate/SKILL.md` — supersedes `superpowers:requesting-code-review`
- Guard note applies only while a `/dev` session is active (i.e., `docs/dev/<feature>/state.json` exists for the current feature) — it is not a blanket suppression of `superpowers` outside `/dev`.
- Verify `dev:init`'s generated scaffold doesn't reference `superpowers` (already confirmed clean by grep).

## Out of Scope

- Changing the global `superpowers` plugin itself — not this repo's responsibility.
- Cycle #3 (context-clearing between stages / worktree vs. branch decision) — separate `/dev` cycle.
- Cycle B (new `dev:start` skill) — separate `/dev` cycle.
- Retroactively cleaning up existing `docs/superpowers/` folders in other repos (e.g. `dev-plugin-design-archive`) — historical artifact, not this plugin's job to remediate.
- Any change to the actual stage logic (TDD steps, planning method, review criteria) — this is a guardrail addition only, not a behavior rewrite.

## Success Criteria

- Every stage-entry skill listed above states explicitly which `superpowers` skill(s) it supersedes and that they should not be separately invoked during an active `/dev` session.
- A fresh `/dev` run end-to-end on a test repo produces artifacts only under `docs/dev/<feature>/` — no `docs/superpowers/` or `.superpowers/` folder appears.
- No change to any stage's actual functional behavior (TDD steps, planning method, etc.) — diff is additive guard notes only.

## Happy Path

1. Developer runs `/dev` (or invokes a `dev:<stage>` skill directly).
2. Claude reads the stage skill and sees the explicit "supersedes `superpowers:X`" note.
3. When the global meta-instruction nudges toward invoking a matching `superpowers` skill, Claude recognizes the current stage already covers it and does not invoke it separately.
4. All artifacts for the cycle land under `docs/dev/<feature>/` only.

## Edge Cases

| Case | Handling |
|------|----------|
| User explicitly invokes a `superpowers` skill directly (e.g. types `/brainstorm`) outside any `/dev` context | Fine — guard only applies while a `/dev` session is active for the current feature. |
| `dev:build`'s existing "When to deviate from TDD" section | Guard note must not contradict it — it's about *when* to skip strict TDD, not *which* skill governs TDD. |
| Skill invoked standalone (e.g. `/dev:plan` without going through `/dev` orchestrator) | Guard note lives in each stage skill individually, not just the entry point, so it applies regardless of invocation path. |

## Audience

Personal, single-user plugin repo (Adam only) — `awilliamsbuilds/claude-plugins`.

## Technical Constraints

- Repo uses `github` marketplace source type (not `directory` — broken in Claude Code). Changes must be pushed and merged to `main`, then `/plugin update` run to take effect.
- Pure Markdown/YAML-frontmatter edits to existing `SKILL.md` files — no code, no new dependencies.

## Dependencies

None external. No dependency on Cycle B (`dev:start`) or Cycle #3 (context-clearing) — this cycle is fully independent and can ship first.

---
*Auto-filled dimensions: none — all filled from direct investigation (repo grep, design-archive inspection) and confirmed via user's scale/sequencing decisions above.*
