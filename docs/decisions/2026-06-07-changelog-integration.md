# Changelog Integration — Decision Log
*2026-06-07 · Branch: feature/changelog-integration · PR #9*

## What was built
Added end-to-end changelog awareness to the `/dev` workflow: `dev:init` detects and records the project's changelog location and versioning scheme; `dev:pr` writes a curated, human-readable entry with automatic version bumping.

## Key decisions

- **Path recorded as a string in config.json, not a format hint** → the PR skill reads existing entries to match style at write-time, making stored metadata minimal and self-correcting
- **Version bump inferred from change type, not prompted** → minor for new features, patch for UX-only, never auto-bumps major (asks when changes look substantial) — reduces friction while preventing false majors
- **Changelog entry content rules are strict exclusions** → bug fixes, performance improvements, copy changes, config additions, and refactors are always excluded — quality over completeness
- **Backward-compatible config schema** → missing `changelog` key treated as null; existing repos continue working without re-running init

## Validation notes
- 1 loop run (tier: standard)
- P2 fixed: `dev:pr` Step 1 artifact read list omitted `docs/dev/config.json`
- P3 fixed: `dev:init` config template used a literal path value that looked hardcoded
- Nit fixed: "last 2–3 entries" → "most recent 2–3 entries"

## Retrospective
*Reviewed by dev:reflect · 2026-06-07*

**Spec:** Confidence 87% matched actual clarity — no plan updates in build, auto-filled dimensions (edge cases, dependencies) were correct. `spec_questions_asked` metric showed 0 despite ~5 questions asked; counter wasn't incremented during the session.

**Shape:** Skipped (no UI). Correct call.

**Plan:** Accurate — no mid-build updates, sequence was right, task independence held (different files, no cross-dependencies).

**Validate:** 1 loop / 3. P2 caught: `dev:pr` Step 1 read list omitted `docs/dev/config.json`. Pattern: when a skill is updated to consume a new config key, other skills that read that same config need their read lists updated too — not obvious to catch in plan/build.

**Flow:** Tier correct, no unnecessary stages, no friction.

**Token efficiency:** `files_read_in_build` metric showed 0 despite reading 2 skill files during build; counter wasn't incremented.

**Suggestions:**
- Both `spec_questions_asked` and `files_read_in_build` metrics are consistently not being incremented during execution. Consider adding a visible reminder in the spec and build skills (e.g., bold callout) to update these counters — low-visibility instructions are being skipped.
- Add a validate checklist item: "if this cycle introduces a new config key, verify all skills that read config.json have it in their Step 1 read list." Catches the class of P2 found here.

## Artifacts (archived)
Spec, design, and plan committed at: f7cc71921a8284b4f911bcf59503fd5c9a2b12a9 on branch feature/changelog-integration
