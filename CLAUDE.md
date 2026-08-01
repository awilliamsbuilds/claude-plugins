# claude-plugins

Personal Claude Code plugin repo for awilliamsbuilds. Registered as the `local-plugins` marketplace via `github` source type in `~/.claude/settings.json`.

**This file is agent-facing configuration, auto-loaded every session.** The human-facing front door — what each plugin is, how to install and enable them, the plugin catalog, and the repo's directory layout — lives in [README.md](README.md); it is the single source of truth for those, so don't duplicate them here. Keep this file to the operational guardrails the agent needs in context and the `/dev` Component Registry below.

## Adding a Plugin or Skill

Use the `add-plugin` skill — it owns the full workflow (the human walkthrough is in [README.md](README.md#adding-a-plugin)). Two guardrails worth having in context:

- Adding a **plugin** touches `plugins/<name>/.claude-plugin/plugin.json`, one `skills/<skill>/SKILL.md`, and a new entry in `.claude-plugin/marketplace.json`. Adding a **skill** to an existing plugin only touches a new `SKILL.md` — skip the plugin.json and marketplace steps.
- Before updating `.claude-plugin/marketplace.json`, read it first (to get its current SHA if editing via the GitHub API) rather than blind-writing it.

## Deploying Changes

Changes must be merged to `main`. After merging, run `/plugin update` in Claude Code.

## Important Notes

- The `directory` source type is broken in Claude Code. This repo uses `github` source — do not change it.
- The `description` field in SKILL.md frontmatter is what Claude Code uses to decide when to invoke a skill. Make it rich with trigger phrases.
- `GITHUB_PERSONAL_ACCESS_TOKEN` must be set in `~/.claude/settings.json` with `repo` scope for this repo.

## Component Registry
*Last updated by /dev · 2026-08-01*

| Component | Path | Purpose |
|-----------|------|---------|
| `dev:autopilot` | plugins/dev/skills/autopilot/SKILL.md | No-gate orchestrator for the /dev workflow |
| `dev:build` | plugins/dev/skills/build/SKILL.md | Stage 4 — implements the plan |
| `dev:debt` | plugins/dev/skills/debt/SKILL.md | On-demand backlog + tech debt tracker — `list` (surfaces `promoted` + `routing: pending`, re-attempts stranded deliveries), `show`, `closed`, `close`, `add` (capture verb with `--debt`/`--plugin`/`--repo` overrides + P9 cross-repo routing), `inbox` (drain/convert routed `dev-backlog` issues into the local store; plugin repo only) |
| `dev:dev` | plugins/dev/skills/dev/SKILL.md | Main entry point for the /dev workflow; Step 6 product-plan continuation scopes to the governing plan, else scans `docs/dev/product-plans/` (multi-plan-aware) |
| `dev:done` | plugins/dev/skills/done/SKILL.md | Stage 7 — merges PR, generates decision record, reconciles README/CLAUDE.md prose (Step 4a) and the primary checkout post-merge; deletes the product-plan on project completion (all `[x]`) and closes the promoted source backlog item; Step 6a's flush re-attempts `routing: pending` items before writing new ones and carries the forward-defensive buffered plugin-scope routing branch |
| `dev:fix` | plugins/dev/skills/fix/SKILL.md | Linear-aware entry point into the /dev workflow |
| `dev:init` | plugins/dev/skills/init/SKILL.md | Sets up /dev workflow infrastructure in a repo |
| `dev:plan` | plugins/dev/skills/plan/SKILL.md | Stage 3 — transforms spec + design into a build plan; Step 7a cold-reviews the plan via a fresh subagent (spec-coverage / sequencing / interface lenses) before the gate |
| `dev:pr` | plugins/dev/skills/pr/SKILL.md | Stage 6 — opens a pull request with description |
| `dev:reflect` | plugins/dev/skills/reflect/SKILL.md | Retrospective — reviews the completed /dev cycle; skill-edit path discovers the plugin source repo portably (dogfood remote-match, else asks) with no hardcoded path/marketplace, then step 2 resolves an explicit `owner/name` PR target (§P9-validated, echo-confirmed on the ask route) and passes it as `gh pr create --repo`/`--head` so a fork's PR can never land upstream |
| `dev:shape` | plugins/dev/skills/shape/SKILL.md | Stage 2 — produces design.md with user flows |
| `dev:spec` | plugins/dev/skills/spec/SKILL.md | Stage 1 — builds the feature specification; Step 12a cold-reviews it via a fresh subagent before the gate; seeds `validate.loops_max` tier-correctly at state init; writes product-plans to the durable `docs/dev/product-plans/<slug>.md` and sets the `backlog → product-plan` promotion back-link (Steps 2/4) |
| `dev:start` | plugins/dev/skills/start/SKILL.md | Prints the /dev workflow reference — stages, skills, invocation commands |
| `dev:validate` | plugins/dev/skills/validate/SKILL.md | Stage 5 — code review and security check; the fix loop cold re-reviews each loop's own fix diff (Step 4 step 8) before it may exit, and states the healthy-path shell exit-code rule once for fix authors |
| `dev` shared refs | plugins/dev/references/tech-debt.md | Shared tech-debt contract — per-item `docs/backlog/` store (front-matter schema, file identity, lifecycle, redesigned buffer, carrying-cost test, recurrence-merge, silent-degrade); documents the live `promoted`/`promoted_to` fields + one-way `backlog → product-plan` promotion flow and ephemeral product-plan lifecycle; §P9 is the single source of truth for cross-repo routing of `scope: plugin` items (target resolution, dogfood-local, slug marker, intake dedup, degrade-to-local, retry seam, done-flush hook); loaded by `init`, `build`, `validate`, `reflect`, `done`, `debt`, `spec` |
| `writing:humanize` | plugins/writing/skills/humanize/SKILL.md | AI pattern detection and human voice rewriting (voice-neutral; no personal-voice coupling) |
| `writing:voice-extractor` | plugins/writing/skills/voice-extractor/SKILL.md | Extracts a person's writing voice into a reusable per-person voice skill; offers a `Writing voice:` pointer |
| `writing:linkedin` | plugins/writing/skills/linkedin/SKILL.md | LinkedIn writing with an up-front message/post/article format gate |
| `writing:email` | plugins/writing/skills/email/SKILL.md | Personal email writing |
| `writing` shared refs | plugins/writing/references/channel-best-practices.md · voice-resolution.md | Voice-neutral channel best-practices + the pointer→convention→default voice-resolution procedure, loaded by `email` and `linkedin` |
| `plugin-manager:add-plugin` | plugins/plugin-manager/skills/add-plugin/SKILL.md | Create and manage plugins in this repo |
| `ux-toolkit:ux-copywriter` | plugins/ux-toolkit/skills/ux-copywriter/SKILL.md | Expert UX copywriting — write, review, audit copy |
| `ux-toolkit:ux-designer` | plugins/ux-toolkit/skills/ux-designer/SKILL.md | UX strategy and visual design craft |
| `naming:craft-name` | plugins/naming/skills/craft-name/SKILL.md | Generate and evaluate names by mouth-feel, meaning, and strategic fit |
