# Changelog Integration — Implementation Plan
*Branch: feature/changelog-integration · 2026-06-07*

## Files

| File | Action | Purpose |
|------|--------|---------|
| `plugins/dev/skills/init/SKILL.md` | Modify | Add changelog detection step to Phase 2 |
| `plugins/dev/skills/pr/SKILL.md` | Modify | Add changelog write + version bump step |

## Tasks

### Task 1: Update dev:init — Changelog Detection
What: Add a changelog detection step to Phase 2 that scans for common changelog files, asks the user if none is found, detects versioning, and writes the result to config.json.
Used by: Any repo running `/dev:init` for the first time or updating config.
Depends on: nothing — first task, modifies init/SKILL.md only.
Files: `plugins/dev/skills/init/SKILL.md`

Implementation steps:
1. Add a new "Changelog Detection" section to Phase 2 (after the Three Setup Questions, before Create Directories).
2. Scan for changelog file in this order: `CHANGELOG.md`, `CHANGES.md`, `HISTORY.md`, `docs/CHANGELOG.md`. If found, use it.
3. If not found: ask "Does this project have a changelog? If so, what's the path? (Enter path or 'none')"
4. If user says none or blank: record `"changelog": null`, `"changelog_versioned": false`, skip versioning detection.
5. If a file was found or provided: inspect its content for version patterns (`## v1.2.3`, `## [1.2.3]`, `# 1.2.3`, etc.). Set `changelog_versioned: true` if any version pattern is found, otherwise false.
6. Update the Write config.json section to include the two new fields:
   ```json
   {
     "autopilot": { ... },
     "changelog": "CHANGELOG.md",
     "changelog_versioned": true
   }
   ```
7. Update the `git add` commit line to include any changelog config changes (config.json already included).

---

### Task 2: Update dev:pr — Changelog Write + Version Bump
What: Add a post-PR-description step that reads the changelog config, collects qualifying changes from the artifact chain, infers a version bump, and appends a styled entry to the changelog file.
Used by: `dev:pr` after Step 2 (PR description built), before Step 3 (push + open PR).
Depends on: nothing — modifies pr/SKILL.md only, independent of Task 1.
Files: `plugins/dev/skills/pr/SKILL.md`

Implementation steps:
1. Add a new **Step 2b: Update Changelog** between existing Step 2 and Step 3.
2. Read `docs/dev/config.json`. If `changelog` key is absent or null → skip entirely.
3. Read the changelog file. Extract the last 2–3 entries to use as style reference (heading format, bullet style, date/version format).
4. Collect qualifying changes by reviewing `spec.md`, `design.md` (if exists), and `plan.md`. Include only:
   - New features or capabilities
   - Removed features
   - UI/UX improvements (layout, flow, clarity, navigation)
   - Exclude: bug fixes, invisible performance improvements, copy/label changes, config additions, internal refactors
5. If no qualifying changes found → skip changelog entry. Add one line to the PR description: `*No user-facing changes in this cycle — changelog not updated.*`
6. If qualifying changes exist and `changelog_versioned: true`:
   - New features present → infer **minor** bump
   - UX improvements only, no new features → infer **patch** bump
   - Changes appear major in scope (e.g., complete redesign, breaking behavior change, multiple major features) → ask: `"These changes look substantial — worth a major version bump? (yes / no, use minor)"`
   - Never auto-bump major; always require explicit yes.
   - Increment the version number accordingly (parse current version from top of changelog).
7. Write the changelog entry matching the style extracted in step 3. Write from the user's perspective — what changed about their experience. No technical jargon.
8. Prepend the new entry to the changelog file (newest entries at top, standard convention). Stage and commit:
   ```bash
   git add <changelog-path>
   git commit -m "chore: update changelog for <feature>"
   ```
9. Update the exit display to mention: `Changelog updated: <path> (version bumped to vX.Y.Z)` or `Changelog updated: <path>` if not versioned.

## Edge Cases

| Edge case | Handled in | Approach |
|-----------|------------|----------|
| No changelog found, user says none | Task 1, step 4 | Record null, pr skill skips silently |
| Changelog found but not versioned | Task 2, step 6 | Skip version bump logic, still write entry |
| No qualifying changes in cycle | Task 2, step 5 | Skip entry, note in PR description |
| Changes look major in scope | Task 2, step 6 | Prompt user — never auto-bump major |
| Config missing changelog key (old init) | Task 2, step 2 | Treat as null, skip |

## Out of Scope
- Creating a new changelog file if none exists
- Enforcing or converting to a specific changelog format
- Changelog entries for validate, build, or other non-PR stages
- Retroactively fixing existing entries
