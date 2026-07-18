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
| `dev` | `dev`, `dev:init`, `dev:start`, `dev:spec`, `dev:shape`, `dev:plan`, `dev:build`, `dev:validate`, `dev:pr`, `dev:done`, `dev:reflect`, `dev:fix`, `dev:autopilot` | Structured multi-stage development workflow (spec → shape → plan → build → validate → PR → done) |

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

## Component Registry
*Last updated by /dev · 2026-07-18*

| Component | Path | Purpose |
|-----------|------|---------|
| `dev:autopilot` | plugins/dev/skills/autopilot/SKILL.md | No-gate orchestrator for the /dev workflow |
| `dev:build` | plugins/dev/skills/build/SKILL.md | Stage 4 — implements the plan |
| `dev:dev` | plugins/dev/skills/dev/SKILL.md | Main entry point for the /dev workflow |
| `dev:done` | plugins/dev/skills/done/SKILL.md | Stage 7 — merges PR, generates decision record |
| `dev:fix` | plugins/dev/skills/fix/SKILL.md | Linear-aware entry point into the /dev workflow |
| `dev:init` | plugins/dev/skills/init/SKILL.md | Sets up /dev workflow infrastructure in a repo |
| `dev:plan` | plugins/dev/skills/plan/SKILL.md | Stage 3 — transforms spec + design into a build plan |
| `dev:pr` | plugins/dev/skills/pr/SKILL.md | Stage 6 — opens a pull request with description |
| `dev:reflect` | plugins/dev/skills/reflect/SKILL.md | Retrospective — reviews the completed /dev cycle |
| `dev:shape` | plugins/dev/skills/shape/SKILL.md | Stage 2 — produces design.md with user flows |
| `dev:spec` | plugins/dev/skills/spec/SKILL.md | Stage 1 — builds the feature specification |
| `dev:start` | plugins/dev/skills/start/SKILL.md | Prints the /dev workflow reference — stages, skills, invocation commands |
| `dev:validate` | plugins/dev/skills/validate/SKILL.md | Stage 5 — code review and security check |
| `writing:humanize` | plugins/writing/skills/humanize/SKILL.md | AI pattern detection and human voice rewriting |
| `writing:voice` | plugins/writing/skills/voice/SKILL.md | Adam's personal voice-dna reference |
| `writing:web-copy` | plugins/writing/skills/web-copy/SKILL.md | Web copy writing with framework selection |
| `writing:linkedin` | plugins/writing/skills/linkedin/SKILL.md | LinkedIn post writing with 2026 hook formulas |
| `writing:email` | plugins/writing/skills/email/SKILL.md | Personal email writing |
| `plugin-manager:add-plugin` | plugins/plugin-manager/skills/add-plugin/SKILL.md | Create and manage plugins in this repo |
| `ux-toolkit:ux-copywriter` | plugins/ux-toolkit/skills/ux-copywriter/SKILL.md | Expert UX copywriting — write, review, audit copy |
| `ux-toolkit:ux-designer` | plugins/ux-toolkit/skills/ux-designer/SKILL.md | UX strategy and visual design craft |
| `naming:craft-name` | plugins/naming/skills/craft-name/SKILL.md | Generate and evaluate names by mouth-feel, meaning, and strategic fit |
