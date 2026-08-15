# claude-plugins

Personal Claude Code plugins for awilliamsbuilds.

## Plugins

| Plugin | Skills | Description |
|--------|--------|-------------|
| `ux-toolkit` | `ux-designer`, `ux-copywriter` | UX design strategy, visual craft, and interface copywriting |
| `writing` | `humanize`, `voice-extractor`, `linkedin`, `email` | Multi-context writing toolkit — humanize AI text, write LinkedIn messages/posts/articles and personal email, and extract a reusable personal voice |
| `naming` | `craft-name` | Business, brand, product, and feature naming |
| `plugin-manager` | `add-plugin` | Create and manage plugins in this repo |
| `dev` | `dev`, `dev:init`, `dev:start`, `dev:spec`, `dev:shape`, `dev:plan`, `dev:build`, `dev:validate`, `dev:pr`, `dev:done`, `dev:reflect`, `dev:fix`, `dev:autopilot`, `dev:debt`, `dev:migrate-tracker` | Structured multi-stage development workflow (spec → shape → plan → build → validate → PR → done) |

## Setup

Add to `~/.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "local-plugins": {
      "source": {
        "source": "github",
        "repo": "awilliamsbuilds/claude-plugins"
      },
      "autoUpdate": true
    }
  },
  "enabledPlugins": {
    "ux-toolkit@local-plugins": true,
    "writing@local-plugins": true,
    "naming@local-plugins": true,
    "plugin-manager@local-plugins": true,
    "dev@local-plugins": true
  },
  "env": {
    "GITHUB_PERSONAL_ACCESS_TOKEN": "<your-token>"
  }
}
```

Then run `/plugin update` in Claude Code.

## Repo Structure

```
awilliamsbuilds/claude-plugins/
├── .claude-plugin/
│   └── marketplace.json           # Registry of all plugins
├── docs/
│   ├── decisions/                 # Architecture & /dev decision logs
│   ├── backlog/                   # Unified backlog + tech-debt store (one file per item)
│   └── dev/                       # /dev workflow state (config, in-flight cycle artifacts)
└── plugins/
    └── <plugin-name>/
        ├── .claude-plugin/
        │   └── plugin.json
        ├── references/            # Optional — shared refs loaded by the plugin's skills
        │   └── <reference>.md
        └── skills/
            └── <skill-name>/
                ├── SKILL.md
                ├── <runtime files>  # Optional — e.g. dev:debt's viewer.py
                └── references/      # Optional — refs scoped to a single skill
                    └── <reference>.md
```

## Adding a Plugin

Use the `add-plugin` skill — it walks through the full process. Or manually:

1. Create a feature branch: `add-plugin/<name>`
2. Create `plugins/<name>/.claude-plugin/plugin.json`
3. Create `plugins/<name>/skills/<skill-name>/SKILL.md`
4. Update `.claude-plugin/marketplace.json`
5. PR → merge → delete branch
6. Enable in `~/.claude/settings.json`: `"<name>@local-plugins": true`
7. Run `/plugin update`

## Notes

- Use `github` source type only. The `directory` source type is broken in Claude Code.
- The `description` field in SKILL.md frontmatter drives skill invocation — write rich trigger phrases.
- Skills are markdown-first, but may ship runtime files beside `SKILL.md`. `dev:debt`'s viewer needs `python3` (stdlib only) — the repo's only runtime dependency.
