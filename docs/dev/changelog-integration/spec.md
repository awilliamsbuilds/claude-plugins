# Changelog Integration for /dev
*Branch: feature/changelog-integration · Confidence: 87% — Ready · 2026-06-07*
*Cycle type: feature · Tier: standard*

## Intent
The `dev:pr` skill's changelog entries have degraded — too many minor/technical items, wrong visual style, and no version awareness. Fix this end-to-end: `dev:init` detects and records the changelog location and versioning scheme; `dev:pr` reads the file, infers an appropriate version bump, and writes a curated, human-readable entry that matches the existing style.

## Scope
- **`dev:init`**: Detect changelog file in the repo root and common locations. If not found, ask the user whether one exists and where. Record `"changelog"` path (or `null`) in `docs/dev/config.json`. Detect whether the changelog uses version numbers; record `"changelog_versioned": true/false`.
- **`dev:pr`**: Read changelog config → if path is null, skip changelog work entirely. If path exists: read recent entries to match style → collect qualifying changes from spec/design/plan artifacts → write a new changelog entry → append to file.
- **Version bumping** (only when `changelog_versioned: true`): Infer bump level from changes included in the entry:
  - New features added → minor bump
  - UX improvements only, no new features → patch bump
  - Changes look major in scope → ask: "These look significant — worth a major version bump? (yes / no, use minor)"
  - Major is never auto-bumped; always requires explicit confirmation.
- **Changelog entry content rules** — include only:
  - New features or capabilities
  - Removed features
  - UI/UX improvements (layout, flow, clarity)
- **Changelog entry content rules** — always exclude:
  - Bug fixes
  - Performance improvements invisible to the user
  - Copy or label changes
  - Config or settings additions
  - Internal refactors
- **Writing quality**: entries are human-readable prose/bullets — no technical jargon, written from the user's perspective, concise. Style (heading format, bullet style, date/version format) must match existing entries in the file.

## Out of Scope
- Creating a new changelog file if none exists (record null, skip)
- Enforcing a specific changelog format (match whatever exists)
- Changelog entries for non-PR workflows (validate, build, etc.)
- Retroactively fixing existing changelog entries

## Success Criteria
- A human reads the new changelog entry and immediately understands what changed about their experience
- The entry is visually indistinguishable in style from existing entries in the file
- Only user-facing improvements and feature changes appear — no noise
- Version number (when present) is incremented correctly with no false majors

## Happy Path
1. `dev:init` runs in a repo → scans for changelog → finds `CHANGELOG.md` with versioned entries → writes `"changelog": "CHANGELOG.md"` and `"changelog_versioned": true` to config
2. Developer completes a build cycle with new features and UX improvements
3. `dev:pr` runs → reads config → reads last 2–3 changelog entries for style reference → reviews spec and plan artifacts for qualifying changes → infers minor bump (new feature present) → writes entry → appends to `CHANGELOG.md` → reports what was added

## Edge Cases
- **No changelog found, user says none exists**: record `"changelog": null`, skip all changelog work in `dev:pr`
- **Changelog found but not versioned**: skip version bump logic, still write entry
- **No qualifying changes in the cycle** (e.g., pure bug fix): skip changelog entry entirely, note in PR description
- **Changes look major**: prompt user before bumping — do not auto-bump major
- **Config missing changelog key** (older init): treat as null, skip changelog work

## Technical Constraints
- Changes are to skill `.md` files (`dev:init/SKILL.md`, `dev:pr/SKILL.md`) and `docs/dev/config.json` schema
- No new dependencies; `dev:pr` reads artifacts already produced by prior stages
- Config changes must be backward-compatible (existing repos without `changelog` key in config behave as null)

## Dependencies
- `dev:init` SKILL.md — adds changelog detection step
- `dev:pr` SKILL.md — adds changelog write step, version bump logic
- `docs/dev/config.json` schema — adds `changelog` (string | null) and `changelog_versioned` (boolean) fields

## UI Needed
No.

---
*Auto-filled dimensions: edge cases (inferred from detection logic), dependencies (inferred from file list)*
