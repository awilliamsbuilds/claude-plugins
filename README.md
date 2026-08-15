# claude-plugins

Personal Claude Code plugins for awilliamsbuilds.

## Plugins

| Plugin | Skills | Description |
|--------|--------|-------------|
| `ux-toolkit` | `ux-designer`, `ux-copywriter` | UX design strategy, visual craft, and interface copywriting |
| `writing` | `humanize`, `voice-extractor`, `linkedin`, `email` | Multi-context writing toolkit — humanize AI text, write LinkedIn messages/posts/articles and personal email, and extract a reusable personal voice |
| `naming` | `craft-name` | Business, brand, product, and feature naming |
| `plugin-manager` | `add-plugin` | Create and manage plugins in this repo |
| `dev` | `dev`, `dev:init`, `dev:start`, `dev:spec`, `dev:shape`, `dev:plan`, `dev:build`, `dev:validate`, `dev:pr`, `dev:done`, `dev:reflect`, `dev:fix`, `dev:autopilot`, `dev:debt`, `dev:secure`, `dev:migrate-tracker` | Structured multi-stage development workflow (spec → shape → plan → build → validate → PR → done), plus `dev:fix` — the fast path that goes straight to an open PR with no cycle artifacts — and `dev:secure`, an on-demand security review that reports and writes nothing |

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

## Retired commands

These four commands in `~/.claude/commands/` predate the `dev` plugin and are replaced by it. **They
live in your home directory, so no PR in this repo can delete them** — the keystroke is yours.

| Command | Replaced by | Remove with |
|---|---|---|
| `fix.md` | `/dev:fix linear <id>` | `rm ~/.claude/commands/fix.md` |
| `pr.md` | `dev:pr` and `/dev:fix`'s PR segment, plus its build check | `rm ~/.claude/commands/pr.md` |
| `security-review.md` | `/dev:secure` | `rm ~/.claude/commands/security-review.md` |
| `security-review-diff.md` | `/dev:secure diff` | `rm ~/.claude/commands/security-review-diff.md` |

**On `pr.md`:** its step 3 instructed running `/security-review-pr`, and no such command file exists —
the files on disk are `security-review.md` and `security-review-diff.md`. Its security gate had been
a dangling reference, so the flow it advertised was not running. `/dev:fix` now calls `/dev:secure
diff` before every PR, which is the check `pr.md` described but never performed.

**This retirement is documented, not enforced.** A command still on disk still runs. Until you delete
the files, both the old command and its `/dev` replacement are available, and nothing in this repo
can change that.

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
- `~/.claude/commands/branches.md` is **not** retired. It restarts a launchd service for a personal app and has nothing to do with `/dev`, so it is excluded from the table above rather than swept up with it.
- Skills are markdown-first, but may ship runtime files beside `SKILL.md`. `dev:debt`'s viewer needs `python3` (stdlib only) — the repo's only runtime dependency.
