---
name: dev:init
description: "Sets up the /dev workflow infrastructure in a repo. Detects stack, asks 1 setup question, creates docs/dev/ and docs/decisions/, writes CLAUDE.md Component Registry and config.json. Auto-triggered by /dev when config.json is missing."
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
- Infer the answer to the setup question from what you find
- Present the inference for confirmation: "Based on your README and project structure, here's what I think — correct anything off."
- Only ask the blank question when evidence is absent
- Then Phase 2

**Scenario D — Already initialized** (`docs/dev/config.json` exists):
- Read and display current config
- Ask: "Update config or keep it as-is?"
- If keep: before exiting, check for `docs/dev/tech-debt.md`. If it is absent, create it exactly
  as in **Create Directories** below and name it in the exit line — "Config unchanged. Created
  docs/dev/tech-debt.md (untracked — review, commit, and push when ready). Run /dev to start a
  feature cycle." Do **not** `git add` or commit it: this path runs outside a cycle, usually with the
  checkout on `main`, and staging a file the user didn't ask for means their next unrelated
  commit silently carries it. If it already exists, exit with "Config unchanged. Run /dev to
  start a feature cycle."
  This is the only automatic path by which a repo initialized before the tracker shipped ever
  gets the file: `dev:init` is auto-triggered only when `config.json` is missing, which is false
  for exactly those repos. (`dev:done`'s flush creates the file too, but only once a cycle there
  actually defers something.)
- If update: run a **safe migration** in place — never a fixed-template rewrite. This is the
  general mechanism by which an older/drifted repo gains new config keys and artifacts
  (generalizing the former `tech-debt.md`-only backfill above):
  1. Read and JSON-parse the existing `config.json`. **Malformed-config guard:** if the file does
     not parse as valid JSON, or `schema_version` is present but not a non-negative integer, do
     **not** rewrite it — STOP and report the file as malformed for manual repair. (Silently
     falling back to the fresh template here would clobber the user's tuned values, the exact
     outcome the migration exists to prevent.) Otherwise read its `schema_version` — absent ⇒ treat
     as legacy version `0`.
  2. **Future-version guard:** if `schema_version` > `SCHEMA_VERSION` (`1`), do **not** modify or
     downgrade the file — leave it untouched and report: "config schema vN is newer than this init
     knows (v1); left unchanged." (Edge: unknown/future `schema_version`.) Stop here.
  3. Otherwise **merge** against the current schema (see **Write config.json**). For each schema
     key: if it is **absent**, add it with its consumer-side default (`component_policy` →
     `can-propose`; `spec_max_questions` → `10`; `spec_min_confidence` → `85`; `changelog` →
     `null`; `changelog_versioned` → `false`). Migration backfills `changelog` to `null` and does
     **not** re-run changelog detection — a repo with an existing changelog enables it via a fresh
     init or a manual edit. If a key is **present**, **preserve the existing value** — never
     overwrite a present value with a template default. (Edge: tuned-value preservation — a
     customized `spec_max_questions` survives.)
  4. Leave any key the new template no longer emits (e.g. a pre-existing `worktree_root`) **in
     place** — do not strip it and do not error on encountering it. (Edge: `worktree_root` in an
     existing config.)
  5. Stamp `schema_version = SCHEMA_VERSION` (`1`).
  6. Ensure `docs/dev/tech-debt.md` exists — create it from the canonical header (as in **Create
     Directories**) if absent.
  7. **Leave the updated `config.json` and any newly created `tech-debt.md` unstaged** — no
     `git add`, no commit (same rule as **Do not commit — leave unstaged**). Report: "migrated
     config to schema v1; left unstaged — review, commit, and push when ready."

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

### Setup Question

Ask this question. If evidence exists (Scenario C), present the inferred answer for confirmation rather than asking cold.

**Component policy:**
"When building features, should I work within your existing components only, or can I propose new ones when existing components don't fit?"
- A) Existing components only → stored as `component_policy: "existing-only"`
- B) Can propose new components when justified → stored as `component_policy: "can-propose"`

This answer is persisted to `config.json` under `component_policy` (see **Write config.json**) and read by `dev:shape` and `dev:reflect`.

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

Then create the tech-debt tracker — **only when it is absent**, so re-running init never
clobbers real entries. Do not `touch` it: an empty file is not ready to receive its first entry.
Write the canonical header from `../../references/tech-debt.md` plus both section headings:

```bash
[ -f docs/dev/tech-debt.md ] || cat > docs/dev/tech-debt.md <<'EOF'
# Tech Debt

Deferred items discovered by `/dev` cycles — recorded rather than fixed, with enough context to
act on later without re-deriving the finding. Written automatically by `dev:done` when a cycle
completes; read, ranked, and closed via `/dev:debt`. Format and rules: the `/dev` plugin's
`references/tech-debt.md`.

## Open

## Closed
EOF
```

It lives at `docs/dev/`, beside `product-plan.md` and one level above the per-cycle directory
`dev:done` Step 7 deletes — which is why it survives cycles.

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

Write to `docs/dev/config.json` in the user's project. `SCHEMA_VERSION = 1` — the current
config schema version, the literal value init stamps and the migration (Scenario D) stamps:
```json
{
  "schema_version": 1,
  "autopilot": {
    "spec_max_questions": 10,
    "spec_min_confidence": 85
  },
  "component_policy": "<existing-only-or-can-propose>",
  "changelog": "<detected-path-or-null>",
  "changelog_versioned": "<true-or-false>"
}
```

- `schema_version`: the literal `1` (`SCHEMA_VERSION`).
- `component_policy`: `"existing-only"` or `"can-propose"` from the **Setup Question** answer.
- `changelog`: the detected path, or `null`.
- `changelog_versioned`: `true` or `false` from detection.

There is no `worktree_root` key — every skill hardcodes `.dev-worktrees`, so the key is dead and
init no longer emits it. (A pre-existing `worktree_root` in an already-initialized repo is left in
place by the migration, not stripped — see Scenario D.)

**Consumer-side defaults** (used by a reader when a key is absent, independent of migration; the
migration in Scenario D backfills these same values): `spec_max_questions` → `10`;
`spec_min_confidence` → `85`; `component_policy` → `"can-propose"`; `changelog` → absent/null ⇒
skip changelog; `changelog_versioned` → absent ⇒ `false`; `schema_version` → absent ⇒ legacy
(version `0`).

### Do not commit — leave unstaged

Do **not** `git add` and do **not** commit any file this skill created or modified. Leave every
one of them (`docs/dev/.gitkeep`, `docs/decisions/.gitkeep`, `docs/dev/config.json`,
`docs/dev/tech-debt.md`, `CLAUDE.md`, `.gitignore`) **unstaged** in the working tree. This mirrors
the "keep" path (Scenario D): init usually runs with the checkout on `main`, and a file the user
didn't explicitly ask to commit must not silently ride their next unrelated commit to `main`. The
developer reviews the scaffolding, then commits and pushes it themselves.

## Exit Display

```
✓ /dev workflow initialized

  Created: docs/dev/  docs/decisions/
  Created: docs/dev/tech-debt.md
  Written: docs/dev/config.json
  Updated: CLAUDE.md (Component Registry added)
  Changelog: [path detected] (versioned: yes/no) — or "No changelog configured"

These files are unstaged — review, commit, and push when ready. Until they are pushed, a cycle
worktree cut from origin/main won't see config.json / tech-debt.md.

Run /dev to start your first feature cycle.
```

Omit the `Created: docs/dev/tech-debt.md` line if the file already existed — the creation is
guarded by `[ -f … ] ||`, so on a re-init nothing was created.
