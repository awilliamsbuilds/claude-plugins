# claude-plugins

Personal Claude Code plugin repo for awilliamsbuilds. Registered as the `local-plugins` marketplace via `github` source type in `~/.claude/settings.json`.

## Repo Structure

```
awilliamsbuilds/claude-plugins/
├── .claude-plugin/
│   └── marketplace.json           # Registry — lists all plugins
└── plugins/
    └── <plugin-name>/
        ├── .claude-plugin/
        │   └── plugin.json        # Plugin metadata
        └── skills/
            └── <skill-name>/
                └── SKILL.md       # Skill instructions and triggers
```

## Installed Plugins

| Plugin | Skills | Description |
|--------|--------|-------------|
| `ux-toolkit` | `ux-designer`, `ux-copywriter` | UX design strategy and interface copywriting |
| `humanize` | `humanize` | AI pattern detection and voice rewriting |
| `plugin-manager` | `add-plugin` | Create and manage plugins in this repo |
| `dev` | `dev`, `dev:init`, `dev:spec`, `dev:shape`, `dev:plan`, `dev:build`, `dev:validate`, `dev:pr`, `dev:done`, `dev:reflect`, `dev:fix`, `dev:autopilot` | Structured multi-stage development workflow (spec → shape → plan → build → validate → PR → done) |

## Adding a Plugin

1. Feature branch: `add-plugin/<name>`
2. Create `plugins/<name>/.claude-plugin/plugin.json`
3. Create `plugins/<name>/skills/<skill-name>/SKILL.md` with YAML frontmatter
4. Add entry to `.claude-plugin/marketplace.json` (read file first to get SHA before updating)
5. PR → merge → delete branch
6. Enable in `~/.claude/settings.json`: `"<name>@local-plugins": true`
7. Run `/plugin update` in Claude Code

Use the `add-plugin` skill — it knows the full workflow.

## Adding a Skill to an Existing Plugin

Same as above but skip steps 2 and 4. Only create SKILL.md and PR.

## Git Workflow

Feature branch → PR → merge to main → delete branch (remote and local). Never commit directly to main.

## Deploying Changes

Changes must be merged to `main`. After merging, run `/plugin update` in Claude Code.

## Important Notes

- The `directory` source type is broken in Claude Code. This repo uses `github` source — do not change it.
- The `description` field in SKILL.md frontmatter is what Claude Code uses to decide when to invoke a skill. Make it rich with trigger phrases.
- `GITHUB_PERSONAL_ACCESS_TOKEN` must be set in `~/.claude/settings.json` with `repo` scope for this repo.
