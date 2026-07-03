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

## Retrospective
*Reviewed by dev:reflect · 2026-07-03*

**Spec:** Confidence (100%, Ready) is Micro tier's expected auto-filled ceiling — the real locked-in signal was ~45% from intent+scope+pre-filled dimensions before auto-fill, and Build needed zero corrections, so it held up fine. `spec_questions_asked` shows 0 despite one substantive scope-clarifying question (delivered via AskUserQuestion) — third consecutive cycle this counter hasn't moved. Notably, this cycle's `dev:spec` invocation loaded from the plugin *cache*, not the just-merged PR #11 fix (the user hadn't run `/plugin update` yet), so PR #11's concrete-instruction fix hasn't actually been exercised yet — this isn't evidence the fix failed, just that it hasn't been tested live.

**Shape:** Skipped (Micro tier, no UI). Correct call.

**Plan:** No separate plan.md — Micro tier's Implementation Note served as the plan and was followed exactly (code review confirmed no scope creep, nothing missing, no mid-build corrections).

**Validate:** 1/1 loop (Micro max) — clean after one Nit fix. No P1/P2 slipped through, consistent with the low-risk nature of a single static-reference file.

**Flow:** Tier (Micro) correctly detected — single file, no UI, bounded, matching this repo's own "adding a skill to an existing plugin" convention. No unnecessary stages. Full cycle (spec_start → pr_created) took ~32 minutes including two full subagent reviews — reasonable for Micro tier.

**Token efficiency:** `files_read_in_build` = 1, no outlier. `stage_timestamps` was fully populated this cycle (spec_start/end, build_start/end, validate_end, pr_created) — no gaps, unlike the prior two cycles. Caveat: since this session's `dev:spec`/`dev:build` invocations were still running from the stale cache (pre-PR #11), this completeness is more likely attributable to habit carried over within this same long session than to the shipped fix actually taking effect — worth re-checking once `/plugin update` runs and a fresh session tries a cycle cold.

**Suggestions:**
- No skill-file changes proposed this cycle — nothing surfaced that wasn't already addressed by the prior cycle's reflect fixes (PR #11). One follow-up worth tracking outside a skill edit: once `/plugin update` is run, verify in a fresh session that `stage_timestamps` and `spec_questions_asked` actually get recorded without the benefit of an already-warmed-up session's habits.
