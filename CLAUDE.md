# claude-plugins

Personal Claude Code plugin repo for awilliamsbuilds. Registered as the `local-plugins` marketplace via `github` source type in `~/.claude/settings.json`.

**This file is agent-facing configuration, auto-loaded every session.** The human-facing front door — what each plugin is, how to install and enable them, the plugin catalog, and the repo's directory layout — lives in [README.md](README.md); it is the single source of truth for those, so don't duplicate them here. Keep this file to the operational guardrails the agent needs in context and the `/dev` Component Registry below.

## Adding a Plugin or Skill

Use the `add-plugin` skill — it owns the full workflow (the human walkthrough is in [README.md](README.md#adding-a-plugin)). Two guardrails worth having in context:

- Adding a **plugin** touches `plugins/<name>/.claude-plugin/plugin.json`, one `skills/<skill>/SKILL.md`, and a new entry in `.claude-plugin/marketplace.json`. Adding a **skill** to an existing plugin only touches a new `SKILL.md` — skip the plugin.json and marketplace steps.
- Before updating `.claude-plugin/marketplace.json`, read it first (to get its current SHA if editing via the GitHub API) rather than blind-writing it.

## Git Workflow

Feature branch → PR → merge to main → delete branch (remote and local). Never commit directly to main.

## Deploying Changes

Changes must be merged to `main`. After merging, run `/plugin update` in Claude Code.

## Important Notes

- The `directory` source type is broken in Claude Code. This repo uses `github` source — do not change it.
- The `description` field in SKILL.md frontmatter is what Claude Code uses to decide when to invoke a skill. Make it rich with trigger phrases.
- `GITHUB_PERSONAL_ACCESS_TOKEN` must be set in `~/.claude/settings.json` with `repo` scope for this repo.

## Component Registry
*Last updated by /dev · 2026-07-21*

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
| `writing:humanize` | plugins/writing/skills/humanize/SKILL.md | AI pattern detection and human voice rewriting (voice-neutral; no personal-voice coupling) |
| `writing:voice-extractor` | plugins/writing/skills/voice-extractor/SKILL.md | Extracts a person's writing voice into a reusable per-person voice skill; offers a `Writing voice:` pointer |
| `writing:linkedin` | plugins/writing/skills/linkedin/SKILL.md | LinkedIn writing with an up-front message/post/article format gate |
| `writing:email` | plugins/writing/skills/email/SKILL.md | Personal email writing |
| `writing` shared refs | plugins/writing/references/channel-best-practices.md · voice-resolution.md | Voice-neutral channel best-practices + the pointer→convention→default voice-resolution procedure, loaded by `email` and `linkedin` |
| `plugin-manager:add-plugin` | plugins/plugin-manager/skills/add-plugin/SKILL.md | Create and manage plugins in this repo |
| `ux-toolkit:ux-copywriter` | plugins/ux-toolkit/skills/ux-copywriter/SKILL.md | Expert UX copywriting — write, review, audit copy |
| `ux-toolkit:ux-designer` | plugins/ux-toolkit/skills/ux-designer/SKILL.md | UX strategy and visual design craft |
| `naming:craft-name` | plugins/naming/skills/craft-name/SKILL.md | Generate and evaluate names by mouth-feel, meaning, and strategic fit |
