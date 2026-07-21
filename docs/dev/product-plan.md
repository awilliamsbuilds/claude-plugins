# Writing Plugin Voice — Product Plan
*Created: 2026-07-21 · Cycles completed: 0/2*

## Milestone 1: Voice tooling
- [ ] voice-extractor (feature) — a skill that extracts a person's voice from Claude
  chats, pasted samples, files, and URLs, and writes a per-person voice skill to
  `~/.claude/skills/voice-<name>/SKILL.md` (local, survives plugin updates). Supports a
  refine/update mode on re-invocation.

## Milestone 2: Depersonalize writing plugin
- [ ] depersonalize-writing (feature) — make the `writing` plugin shareable: migrate
  Adam's `voice` skill out to a local skill (`~/.claude/skills/voice-adam/`, produced via
  voice-extractor's convention), decouple `email`/`linkedin`/`web-copy` from the hardcoded
  `../voice/references/voice-profile.md` path so they accept any named voice, and ship a
  generic default. Depends on voice-extractor.
