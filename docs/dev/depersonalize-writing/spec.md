# Depersonalize Writing
*Branch: feature/depersonalize-writing · Confidence: 95% — Ready · 2026-07-21*
*Cycle type: feature · Tier: standard*

## Intent
The `writing` plugin is meant to be installable by anyone, but it currently ships Adam's
personal voice baked in: the `voice` skill contains Adam's `voice-profile.md` and
`platform-guide.md`, and `email`, `linkedin`, and `web-copy` hardcode the plugin-relative path
`../voice/references/voice-profile.md` as their "Option A — Adam's personal voice." A fresh
installer inherits Adam's personality and dead-ends on a path that assumes his profile is
present. This cycle decouples the plugin from any one person's voice so it can be shared, while
preserving (a) the generic writing craft for new installers and (b) Adam's own output on his
machine. It's Milestone 2 of the writing-plugin-voice product plan and depends on the
now-complete `voice-extractor` convention.

## Scope
- **Discovery mechanism:** rewrite the "Option A" branch in `email`, `linkedin`, and `web-copy`
  to scan `~/.claude/skills/voice-*/` (the convention `humanize` already uses) instead of the
  hardcoded `../voice/...` path. Behavior: 0 voice skills found → clean/direct default; exactly
  1 → use it; 2+ → ask which. Option A's wording changes from "Adam's personal voice" to "your
  installed personal voice."
- **Shared voice-neutral craft:** extract the voice-neutral structure rules from
  `voice/references/platform-guide.md` (LinkedIn/blog post structure, email rules — stripped of
  Adam-specific voice and example lines) into a shared, in-plugin reference file that all three
  skills always load, regardless of which personal voice (if any) is selected. Exact file
  location is a Plan/Build detail; it must be path-reachable from all three skill dirs.
- **Migrate Adam out (local, no-gap):** create `~/.claude/skills/voice-adam/` on this machine
  containing a `SKILL.md` plus `references/voice-profile.md` and `references/platform-guide.md`
  (the Adam-personal content), preserving the reference-file layout the consumers load. This is
  a local filesystem action outside the repo, sequenced *before* the in-plugin `voice` skill is
  removed so Adam is never without his voice.
- **Delete the in-plugin `voice` skill** (`plugins/writing/skills/voice/`) once Adam's local
  `voice-adam` exists and the shared craft file has absorbed the generic rules.
- **Registry/marketplace hygiene:** update the CLAUDE.md Component Registry and any
  marketplace/plugin metadata that references the removed `voice` skill.

## Out of Scope
- Changing `voice-extractor` itself, or making it emit `platform-guide.md`. Adam's local
  `voice-adam` is populated by copying the existing curated reference files, not by re-running
  extraction.
- Any change to `humanize`'s behavior beyond confirming it still resolves voice-* skills after
  the in-plugin `voice` skill is gone (it already scans `~/.claude/skills/voice-*/`).
- The `trm-brand-voice` skill referenced in `voice/SKILL.md` (company voice — separate concern,
  not part of this plugin).
- Publishing/enabling the shareable plugin for other users, or writing installer docs beyond the
  minimal note on how a new user points the skills at their own voice.
- Reference-file layout is fixed (reference files, not a single SKILL.md) — the single-file
  voice-extractor convention was considered and explicitly not adopted for the consumers.

## Success Criteria
- A fresh installer with **no** `~/.claude/skills/voice-*/` skill can use `email`, `linkedin`,
  and `web-copy` and gets clean, structurally-sound output (generic craft applied) with **zero**
  references to Adam anywhere in the plugin.
- The `writing` plugin source contains no personal voice profile — `grep -ri "Adam"` across
  `plugins/writing/skills/{email,linkedin,web-copy}` and the shared craft file returns no
  personal-voice content.
- On Adam's machine, invoking `email`/`linkedin`/`web-copy` → Option A discovers `voice-adam`
  and produces output materially identical to today's.
- No window exists in which Adam's voice is unavailable: `voice-adam` is created and verified
  before the in-plugin `voice` skill is deleted.
- The three skills produce sensible behavior for all three discovery cases (0 / 1 / 2+ installed
  voice skills).

## Happy Path
1. User invokes `email` (or `linkedin` / `web-copy`).
2. Skill presents Option A "your installed personal voice" / B project voice / C start fresh.
3. On A, the skill scans `~/.claude/skills/voice-*/`.
4. Exactly one voice skill found → it loads that skill's `references/` and always loads the
   shared voice-neutral craft file; writes in that voice.
5. Output reflects the discovered voice + generic craft — no hardcoded path, no Adam assumption.

## Edge Cases
- **Zero voice skills installed:** fall back to clean/direct default, still applying the shared
  craft file. Option A must not error on a missing `../voice/...` path.
- **Multiple voice skills installed:** enumerate and ask which; don't silently pick one.
- **Craft regression:** a fresh installer must not lose the structural guidance the skills give
  today — that guidance moves to the shared craft file, not away with Adam.
- **Deletion ordering:** deleting the in-plugin `voice` skill before `voice-adam` exists would
  strand Adam and break `humanize`'s example set — ordering is load-bearing.
- **Stale references:** any lingering `../voice/references/...` path in the plugin after the
  cutover is a broken reference; the success grep guards against this.

## Audience
Two audiences: (1) new installers of the shared `writing` plugin who have their own voice or
none, and (2) Adam, whose existing setup must keep working via a local `voice-adam` skill.

## Technical Constraints
- `~/.claude/skills/voice-adam/` is **outside** the git repo; creating it is a local action, not
  part of the PR diff. The PR contains only the plugin decoupling + shared craft file + deletions
  + registry updates.
- The shared craft file must be reachable by relative path from all three consumer skill
  directories after the `voice` skill is gone.
- Discovery must mirror `humanize`'s existing `~/.claude/skills/voice-*/` convention so the repo
  converges on one mechanism.

## Dependencies
- Depends on the completed `voice-extractor` cycle and its `~/.claude/skills/voice-<name>/`
  convention.
- Consumers depend on the shared craft file existing before the `voice` skill is deleted.

## UI Needed
No. This is a skill-file refactor — Shape stage is skipped; next stage is Plan.

---
*Auto-filled dimensions: none*
