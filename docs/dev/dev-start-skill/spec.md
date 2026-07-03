# dev:start Skill

*Branch: fix/dev-start-skill · Confidence: 45% — Sufficient (Micro tier: intent + scope only) · 2026-07-03*
*Cycle type: feature · Tier: micro*

## Intent

Users forget how to get `/dev` started and what the stage sequence is. `dev:start` prints a static reference: the 7 workflow stages, which skill covers each, exactly how to invoke it, and — separately — the non-pathway skills (`dev:init`, `dev:fix`, `dev:autopilot`, `dev:reflect`) listed as FYI, so someone re-orienting to the plugin doesn't have to re-read every `SKILL.md` to remember the shape of the thing.

## Scope

- New skill: `plugins/dev/skills/start/SKILL.md`.
- On invocation (`/dev:start`), print:
  1. The stage sequence (Spec → Shape → Plan → Build → Validate → PR → Done) with which skill covers each stage and the exact invocation command, plus brief tier-variation notes (Micro skips Shape+Plan; no-ui mode skips Shape).
  2. A separate "FYI — other skills" section: `dev:init`, `dev:fix`, `dev:autopilot`, `dev:reflect` — not part of the linear pathway, so grouped apart from it.
- Skill descriptions are pulled live from `CLAUDE.md`'s `## Component Registry` table at invocation time — not hardcoded duplicate text — so the printout can't drift out of sync with the actual registry.
- Pure static reference. No session-state detection, no reads of `docs/dev/*/state.json`, no interaction — that's `dev:dev`'s Step 3 job, not this skill's.

## Out of Scope

- Detecting or displaying in-progress session status (explicitly deferred to `dev:dev`).
- Any interactive prompts or state.json writes — `dev:start` is read-only.
- Replacing or modifying `dev:dev`'s own orchestration logic.

## Success Criteria

- Running `/dev:start` prints the 7-stage pathway, the skill that covers each stage, and the exact command to invoke it.
- Tier variations (Micro, no-ui) are noted briefly.
- Non-pathway skills are listed separately as FYI, with one-line descriptions.
- All skill descriptions come from `CLAUDE.md`'s Component Registry, read at invocation time — confirmed by checking the skill's instructions don't contain a second, hardcoded copy of those descriptions.

## Happy Path

1. User forgets how `/dev` works and runs `/dev:start`.
2. Skill reads `CLAUDE.md`'s Component Registry table.
3. Skill prints the stage map with invocation commands, tier-variation notes, and the FYI skill list.
4. User picks the right command and continues.

## Edge Cases

| Case | Handling |
|------|----------|
| `CLAUDE.md` or the Component Registry table is missing/malformed | Fall back to a small hardcoded minimal skill list rather than erroring out. |
| Repo hasn't run `dev:init` yet (no `docs/dev/config.json`) | `dev:start` still works — it's pure reference and doesn't require init — but adds a one-line note: "Run `/dev:init` first if you haven't set up `/dev` in this repo yet." |

## Audience
Personal, single-user plugin repo (Adam only) — `awilliamsbuilds/claude-plugins`.

## UI Needed
No.

## Technical Constraints
Must read `CLAUDE.md`'s Component Registry live each invocation rather than hardcoding a second copy of the descriptions — avoids the two going stale relative to each other.

## Dependencies
None.

## Implementation Note
Files to touch: `plugins/dev/skills/start/SKILL.md` (new file).

Approach: Create a new skill with a static stage-order scaffold (the 7-stage sequence and its known tier variations, which are stable and don't need to be read from anywhere) combined with a live read of `CLAUDE.md`'s Component Registry table for each stage skill's one-line description. Cross-reference the registry rows for `dev:spec`, `dev:shape`, `dev:plan`, `dev:build`, `dev:validate`, `dev:pr`, `dev:done` against the hardcoded stage order to print: `Stage N: [Name] → [skill] — [description from registry] — Run: /dev:<skill> (or /dev to continue the guided flow)`. Follow with a short tier-variation note. Then print an "FYI — other skills" section using the registry rows for `dev:init`, `dev:fix`, `dev:autopilot`, `dev:reflect`. If the registry table is missing or a row can't be found, fall back to a small hardcoded description for that skill rather than failing.

---
*Auto-filled dimensions: success_criteria, happy_path, out_of_scope, edge_cases, ui_needed, dependencies — Micro tier skips guided questioning on these; filled directly from the clearly-scoped request and the one explicit scope-boundary answer (static reference only, no session-state check).*
