# Writing Plugin
*Branch: feature/writing-plugin · Confidence: 92% — Ready · 2026-05-22*
*Cycle type: feature · Tier: standard*

## Intent
The existing `humanize` plugin is too narrow — it only detects AI patterns and rewrites for human voice. Expand it into a full `writing` plugin that covers multiple writing contexts (web copy, LinkedIn, email) while also housing a personal voice/tone reference skill. The expanded plugin should work in any project, adapting to that project's voice rather than assuming Adam's.

## Scope
- Rename the `humanize` plugin to `writing` end-to-end: folder, `plugin.json`, `marketplace.json`, `CLAUDE.md` Component Registry, `README.md`
- Retain the existing `humanize` skill unchanged inside the renamed plugin
- Add four new skills:
  - `voice` — Adam's personal voice and tone reference; content supplied by Adam
  - `web-copy` — writes and edits web copy; asks which voice to use on invocation
  - `linkedin` — writes LinkedIn posts; asks which voice to use on invocation
  - `email` — writes emails; asks which voice to use on invocation
- Each new skill's SKILL.md must have rich trigger phrases in the `description` frontmatter
- Skills are tuned and tested with real content before the cycle is considered done

## Out of Scope
- General "write this for me" skill (function and value unclear — defer to future cycle)
- Twitter/X, blog posts, or other formats
- Any changes to the `humanize` skill behavior

## Success Criteria
1. `plugins/writing/` exists with all five skill directories
2. `marketplace.json` references `writing`, not `humanize`
3. Each new SKILL.md invokes correctly in Claude Code
4. `web-copy`, `linkedin`, and `email` skills ask for voice context on first invocation
5. Skills produce quality output when tested with real content samples
6. All references to `humanize` as a plugin name are updated across the repo

## Happy Path
1. User invokes `/web-copy` in a project
2. Skill asks: "Write in your personal voice (voice skill) or this project's voice?"
3. User picks a voice context
4. Skill produces web copy in the chosen voice
5. User iterates or approves

Same flow applies to `linkedin` and `email`.

## Edge Cases
- Project has no voice context defined: skills fall back to asking the user to describe the target voice before proceeding
- `voice` skill invoked in a project that isn't Adam's: skill content is still Adam's personal reference — it's a stored persona, not a dynamic adapter

## Audience
Solo use — Adam's personal plugin repo.

## Technical Constraints
- Plugin folder rename must be a git `mv` to preserve history
- `marketplace.json` source path must update from `./plugins/humanize` to `./plugins/writing`
- `github` source type must not change
- All SKILL.md files follow existing frontmatter format (name, description, triggers)

## Dependencies
- Existing `humanize` skill SKILL.md (carry over unchanged)
- Adam supplies the `voice` skill content before or during Build

## UI Needed
No.

---
*Auto-filled dimensions: edge_cases (inferred from voice-context design), dependencies (inferred from existing plugin structure)*
