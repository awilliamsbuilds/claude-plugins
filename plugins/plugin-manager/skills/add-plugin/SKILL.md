---
name: add-plugin
description: >
  Create a new Claude Code plugin or add a new skill to an existing plugin in the awilliamsbuilds/claude-plugins repo. Use this skill when the user wants to: create a new plugin, add a skill to an existing plugin, understand the plugin file structure, register a plugin in the marketplace, enable a plugin in Claude Code settings, or troubleshoot a plugin that isn't loading. Also trigger on: "add a plugin", "create a plugin", "new skill", "plugin isn't loading", "update local plugins", "/plugin update", "add it to my plugins", "make a plugin for this".
---

# Add Plugin Skill

You are an expert on the `awilliamsbuilds/claude-plugins` GitHub repository and the Claude Code plugin system. You know exactly how to create, register, and enable plugins.

## Key Facts

- **Repo**: `awilliamsbuilds/claude-plugins` (private, GitHub)
- **Marketplace ID**: `local-plugins`
- **Settings file**: `~/.claude/settings.json`
- **Source type**: always `github` — the `directory` source type is broken in Claude Code

## Existing Plugins

| Plugin | Skills | Description |
|--------|--------|-------------|
| `ux-toolkit` | `ux-designer`, `ux-copywriter` | UX design strategy and interface copywriting |
| `writing` | `humanize`, `voice-extractor`, `linkedin`, `email` | Multi-context writing toolkit (voice-neutral; personal voice resolved via pointer/convention) |
| `plugin-manager` | `add-plugin` | This skill — manages plugins in this repo |
| `dev` | `dev`, `dev:init`, `dev:spec`, `dev:shape`, `dev:plan`, `dev:build`, `dev:validate`, `dev:pr`, `dev:done`, `dev:reflect`, `dev:fix`, `dev:linear`, `dev:autopilot` | Structured multi-stage development workflow, plus the `dev:fix` fast path |

## Repo Structure

```
awilliamsbuilds/claude-plugins/
├── .claude-plugin/
│   └── marketplace.json           # Registry of all plugins
└── plugins/
    └── <plugin-name>/
        ├── .claude-plugin/
        │   └── plugin.json        # Plugin metadata
        └── skills/
            └── <skill-name>/
                └── SKILL.md       # Skill content (one per skill)
```

## File Formats

### `.claude-plugin/marketplace.json` (repo root)

```json
{
  "name": "local-plugins",
  "description": "Personal Claude Code plugins",
  "owner": { "name": "Local" },
  "plugins": [
    {
      "name": "<plugin-name>",
      "description": "<one-line description>",
      "source": "./plugins/<plugin-name>"
    }
  ]
}
```

### `plugins/<name>/.claude-plugin/plugin.json`

```json
{
  "name": "<plugin-name>",
  "description": "<one-line description>",
  "author": { "name": "Local", "email": "" }
}
```

### `plugins/<name>/skills/<skill-name>/SKILL.md`

```markdown
---
name: <skill-name>
description: >
  Rich paragraph describing when to use this skill. Include explicit trigger
  phrases like "also trigger on: X, Y, Z" so Claude Code invokes it reliably.
---

# Skill content here
```

**The `description` field is the most important part.** Claude Code uses it to decide when to invoke the skill. Include explicit trigger phrases, alternate wordings, and "also trigger on:" examples.

## Workflow: Add a New Plugin

Follow the user's global git workflow (feature branch → PR → merge → delete branch).

### Step 1 — Create a feature branch

Use the GitHub MCP `create_branch` tool:
- Branch name: `add-plugin/<plugin-name>`
- Base: `main`

### Step 2 — Create plugin files

Use the GitHub MCP `create_or_update_file` tool for each file. **New files do not need a SHA.** Run steps 2a, 2b, and 2c in parallel since they're independent.

**2a.** `plugins/<name>/.claude-plugin/plugin.json`

**2b.** `plugins/<name>/skills/<skill-name>/SKILL.md`

**2c.** Update `.claude-plugin/marketplace.json` — read the file first to get its current SHA (required for updates), then add the new entry to the `plugins` array.

### Step 3 — Open and merge PR

Use GitHub MCP `create_pull_request`, then `merge_pull_request`. Delete the branch after merging (remote and local).

### Step 4 — Enable in `~/.claude/settings.json`

Add to `enabledPlugins`:
```json
"<plugin-name>@local-plugins": true
```

Use the Edit tool to modify `~/.claude/settings.json` directly.

### Step 5 — Reload

Tell the user to run `/plugin update` in Claude Code to pull the latest from GitHub. The skill will be available immediately after.

## Workflow: Add a Skill to an Existing Plugin

Same as above but:
- Skip step 2a (plugin.json already exists)
- Skip step 2c (marketplace.json already lists this plugin)
- Only create the new SKILL.md file
- No settings.json change needed (plugin is already enabled)

## Troubleshooting

**Skill doesn't trigger automatically**
The `description` frontmatter field needs explicit trigger phrases. Add "Also trigger on: [phrases]" and reload with `/plugin update`.

**`/plugin update` fails with auth error**
Check that `GITHUB_PERSONAL_ACCESS_TOKEN` is set in `~/.claude/settings.json` env block and has `repo` scope for `awilliamsbuilds/claude-plugins`.

**Plugin installed but not showing**
Check `enabledPlugins` in `~/.claude/settings.json` has `"<plugin-name>@local-plugins": true`. Then run `/plugin update`.

**Changes not appearing after `/plugin update`**
Make sure the PR was merged to `main` — Claude Code pulls from the default branch, not feature branches.

**`directory` source type doesn't work**
Known bug. Only `github` and `url` (with `file://`) work. The repo already uses `github` source — do not change it.
