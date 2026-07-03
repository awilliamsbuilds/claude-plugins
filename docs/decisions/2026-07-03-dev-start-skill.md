# dev:start Skill — Decision Log
*2026-07-03 · Branch: fix/dev-start-skill · PR #13*

## What was built
Added `dev:start` — a read-only reference skill that prints the `/dev` workflow's 7-stage pathway (which skill covers each stage, exact invocation command), tier-shortcut notes, and lists the non-pathway skills (`dev:init`, `dev:fix`, `dev:autopilot`, `dev:reflect`) as FYI.

## Key decisions

- **Static reference only, no session-state detection** → considered also having it check for and display in-progress session status, but that's already `dev:dev`'s Step 3 job; duplicating it would create two places that could drift apart. Kept `dev:start` purely informational.
- **Descriptions pulled live from `CLAUDE.md`'s Component Registry, not hardcoded** → the registry is already the single source of truth (maintained by `dev:done` Step 4 on every feature cycle); a second hardcoded copy inside `dev:start` would inevitably go stale relative to it.
- **Fallback to a small hardcoded minimal description list, only if the registry table is missing or malformed** → resilience without competing with the primary source; validated by code review as correctly framed as degraded-mode-only, not a parallel source of truth.
- **Micro tier** → single new file, no UI, no cross-cutting concerns — confirmed via the "adding a skill to an existing plugin" convention in this repo's own `CLAUDE.md` (skip plugin.json/marketplace.json steps, only create `SKILL.md`).

## Validation notes
- 1 loop run (tier: micro, max: 1)
- Nit fixed: the Component Registry's Purpose strings already carry their own "Stage N — " prefix, and the print template also numbers each line, so a literal substitution would have read redundantly ("1. Spec → dev:spec — Stage 1 — builds..."). Fixed by adding an explicit strip-the-prefix instruction to Step 2.
- No P1/P2/P3 issues found. Security review noted this as about as low-risk a diff as this plugin can produce — no shell commands, no path-traversal surface, no gate-weakening, purely additive prose.

## Artifacts (archived)
Spec and validation committed at: 03d4546979b137a3c692c16e39df4eb4a33d599e on branch fix/dev-start-skill
