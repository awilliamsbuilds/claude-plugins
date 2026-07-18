---
name: dev:init
description: "Sets up the /dev workflow infrastructure in a repo. Detects stack, asks 3 setup questions, creates docs/dev/ and docs/decisions/, writes CLAUDE.md Component Registry and config.json. Auto-triggered by /dev when config.json is missing."
---

# dev:init — Workflow Setup

**Announce:** "I'm using dev:init to set up the /dev workflow for this project."

## Purpose

Set up /dev workflow infrastructure in this repo. Does not replace framework scaffolding tools. This skill runs automatically when `/dev` is invoked and `docs/dev/config.json` does not exist.

## Step 1: Detect Repo State

Check which scenario applies and follow that path:

**Scenario A — Empty repo** (no package.json, no framework files at all):
- Ask: "What are we building? I can scaffold the project first."
- Based on the answer, recommend the appropriate scaffolding tool (create-next-app, create-vite, etc.)
- For Vercel projects, offer: "I can delegate to vercel-plugin:bootstrap for this — want to?"
- Wait until the project exists (user confirms scaffolding is complete)
- Then proceed to Phase 2 below

**Scenario B — Scaffolded, no /dev config** (package.json exists, `docs/dev/config.json` does not):
- Skip to Phase 2 directly

**Scenario C — Existing project, first use** (significant codebase, no `docs/dev/config.json`):
- Scan for existing context before asking anything:
  - Read README.md if it exists
  - Read CLAUDE.md if it exists
  - Check for `components/`, `src/components/`, `app/`, `src/app/` directories
  - Check for `tailwind.config.*`, `tsconfig.json`, `package.json`
- Infer answers to the 3 setup questions from what you find
- Present inferences for confirmation: "Based on your README and project structure, here's what I think — correct anything off."
- Only ask blank questions when evidence is absent
- Then Phase 2

**Scenario D — Already initialized** (`docs/dev/config.json` exists):
- Read and display current config
- Ask: "Update config or keep it as-is?"
- If keep: exit with "Config unchanged. Run /dev to start a feature cycle."
- If update: re-run Phase 2

## Phase 2 — Plugin Setup

### Stack Detection

Auto-detect the following. Present as a numbered list before proceeding — do not assume they're correct:

- **Framework:** Next.js / React / Vue / Svelte / Node / Python / other (infer from package.json dependencies or project files)
- **Build command:** from package.json `scripts.build`, or `npm run build` if not found
- **Test command:** from package.json `scripts.test` or equivalent
- **Package manager:** check for `yarn.lock`, `pnpm-lock.yaml`, `bun.lockb` — default npm
- **TypeScript:** tsconfig.json exists?
- **Tailwind:** tailwind.config.* exists?
- **shadcn/ui:** components.json exists?
- **Git remote:** `git remote get-url origin`

Present as:
```
Here's what I detected about this project:
1. Framework: [detected]
2. Build: [detected]
3. Tests: [detected]
4. Package manager: [detected]
5. TypeScript: yes / no
6. Tailwind: yes / no
7. shadcn/ui: yes / no
8. Git remote: [detected]

Anything off? (Say "looks good" to continue, or correct what's wrong)
```

Wait for confirmation before continuing.

### Three Setup Questions

Ask these one at a time. If evidence exists (Scenario C), present the inferred answer for confirmation rather than asking cold.

**Question 1 — Design personality:**
"How would you describe the visual style of this project in a sentence? (This helps Shape stage stay consistent.)"
- For new projects: invite a forward-looking description of what you're building toward
- For existing: invite a descriptive sentence about what currently exists

**Question 2 — Component policy:**
"When building features, should I work within your existing components only, or can I propose new ones when existing components don't fit?"
- A) Existing components only
- B) Can propose new components when justified

**Question 3 — Primary audience:**
"Who primarily uses this? (One sentence — e.g., 'internal ops team', 'public end-users', 'developers integrating your API')"

### Changelog Detection

Scan for a changelog file in this order: `CHANGELOG.md`, `CHANGES.md`, `HISTORY.md`, `docs/CHANGELOG.md`.

**If found:** use that path. Inspect its content for version patterns (`## v1.2.3`, `## [1.2.3]`, `# 1.2.3`). Set `changelog_versioned: true` if any version pattern is found, otherwise `false`.

**If not found:** ask:
> "Does this project have a changelog? If so, what's the path? (Enter the path or 'none')"

- If the user provides a path: use it, run the same version detection above.
- If the user says 'none' or leaves it blank: record `"changelog": null`, `"changelog_versioned": false`.

### Create Directories

Create these in the project root (not the plugins repo — run these in the user's project):
```bash
mkdir -p docs/dev
mkdir -p docs/decisions
touch docs/dev/.gitkeep
touch docs/decisions/.gitkeep
# Ensure /dev worktrees are ignored (create .gitignore if absent; append only if missing)
grep -qxF '.dev-worktrees/' .gitignore 2>/dev/null || echo '.dev-worktrees/' >> .gitignore
```

### Create or Update CLAUDE.md

**If CLAUDE.md is absent:** Create it with this template:
```markdown
# [Project Name]

[Brief project description from README or user input]

## Stack
[Framework, language, key dependencies from stack detection]

## Commands
- Build: [build command]
- Test: [test command]
- Dev: [dev server command, if detected]

## Component Registry
*Last updated by /dev · [today's date]*

| Component | Path | Purpose |
|-----------|------|---------|
[populated from component directory scan]
```

**If CLAUDE.md exists:** Locate or append a `## Component Registry` section. Preserve all other content exactly. Format:
```markdown
## Component Registry
*Last updated by /dev · [today's date]*

| Component | Path | Purpose |
|-----------|------|---------|
| [Name] | [path/to/file] | [One-line purpose inferred from filename] |
```

Populate by scanning component directories (`components/`, `src/components/`, or equivalents found during stack detection). List each component file once. Infer purpose from filename and directory structure.

### Write config.json

Write to `docs/dev/config.json` in the user's project:
```json
{
  "autopilot": {
    "spec_max_questions": 10,
    "spec_min_confidence": 85
  },
  "worktree_root": ".dev-worktrees",
  "changelog": "<detected-path-or-null>",
  "changelog_versioned": "<true-or-false>"
}
```

Set `changelog` to the detected path or `null`. Set `changelog_versioned` to `true` or `false` based on detection.

### Commit

```bash
git add docs/dev/.gitkeep docs/decisions/.gitkeep docs/dev/config.json CLAUDE.md .gitignore
git commit -m "Initialize /dev workflow"
```

## Exit Display

```
✓ /dev workflow initialized

  Created: docs/dev/  docs/decisions/
  Written: docs/dev/config.json
  Updated: CLAUDE.md (Component Registry added)
  Changelog: [path detected] (versioned: yes/no) — or "No changelog configured"

Run /dev to start your first feature cycle.
```
