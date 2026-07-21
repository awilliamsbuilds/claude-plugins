# Depersonalize Writing
*Branch: feature/depersonalize-writing · Confidence: 95% — Ready · 2026-07-21*
*Cycle type: feature · Tier: standard*

## Intent
The `writing` plugin is meant to be installable by anyone, but it currently ships Adam's
personal voice and Adam-specific skills baked in: the `voice` skill contains Adam's
`voice-profile.md` and `platform-guide.md`; `email`, `linkedin`, and `web-copy` hardcode the
path `../voice/references/voice-profile.md` as "Option A — Adam's personal voice"; and
`web-copy` is written specifically around Adam's preferences. A fresh installer inherits Adam's
personality and dead-ends on a path that assumes his profile is present.

This cycle turns `writing` into a genuinely shareable, voice-neutral writing toolkit. After
decoupling, the platform skills that remain (`email`, `linkedin`) carry **current channel best
practices** — how to actually write well for each channel today — rather than one person's
voice. Adam's personal material (`voice`, `web-copy`) moves out to local skills so his own setup
keeps working. It's Milestone 2 of the writing-plugin-voice product plan and depends on the
completed `voice-extractor` convention.

## Scope
- **Decouple voice discovery** in the two remaining platform skills (`email`, `linkedin`):
  rewrite their "Option A" branch to scan `~/.claude/skills/voice-*/` (the convention `humanize`
  already uses) instead of the hardcoded `../voice/...` path. Behavior: 0 voice skills found →
  clean/best-practice default; exactly 1 → use it; 2+ → ask which. Option A's wording changes
  from "Adam's personal voice" to "your installed personal voice."
- **Shared channel best-practices (the retained value):** produce a voice-neutral, in-plugin
  reference of *current best practices* for each channel that `email` and `linkedin` always load,
  regardless of which personal voice (if any) is selected. Content is **researched and refreshed
  to reflect current best practice**, reusing existing skills/plugins where they already cover a
  channel, and seeded by the voice-neutral portions of today's `platform-guide.md` (the
  Adam-specific voice and examples are stripped). This — not Adam's personality — is what a fresh
  installer gets.
- **LinkedIn format distinction:** `linkedin` must clearly distinguish and give best-practice
  guidance for three formats, selected up front:
  - **Message** — a 1:1 direct message / InMail / connection note. Short, purposeful, personal;
    no feed-post hook mechanics.
  - **Post** — a native feed post. Hook-driven, one idea, ~short–medium (today's default; the
    existing post types and hook formulas live here).
  - **Article** — a long-form native LinkedIn article. Titled, sectioned, evergreen, longer-form;
    different structure from a feed post.
- **Migrate Adam out (local, no-gap), for both Adam-specific pieces:**
  - `voice` → `~/.claude/skills/voice-adam/` with `SKILL.md` + `references/voice-profile.md` +
    `references/platform-guide.md` (reference-file layout the consumers load), created before the
    in-plugin `voice` skill is removed.
  - `web-copy` → `~/.claude/skills/web-copy/` (a local personal skill), created before the
    in-plugin `web-copy` skill is removed. Its Option-A voice reference is repointed to the
    voice-* scan so it keeps working locally.
- **Delete from the plugin** once the local copies exist and the shared best-practices file is in
  place: the `voice` skill and the `web-copy` skill.
- **Registry/marketplace hygiene:** update the CLAUDE.md Component Registry and any
  marketplace/plugin metadata to drop `voice` and `web-copy` and reflect the new shared reference.

## Out of Scope
- Changing `voice-extractor` itself, or making it emit `platform-guide.md`. Adam's local
  `voice-adam` is populated by copying the existing curated reference files, not by re-running
  extraction.
- Any change to `humanize`'s behavior beyond confirming it still resolves voice-* skills after
  the in-plugin `voice` skill is gone.
- The `trm-brand-voice` skill referenced in `voice/SKILL.md` (separate company-voice concern).
- Web-copy channel best practices in the *shared* plugin reference. Web-copy leaves the plugin
  entirely this cycle; the shared best-practices file covers email + the three LinkedIn formats
  only. (A future cycle could reintroduce a voice-neutral web-copy skill if desired.)
- Publishing/enabling the shareable plugin for other users, or full installer documentation
  beyond a minimal note on pointing the skills at your own voice.
- Reference-file layout for `voice-adam` is fixed (reference files, not a single SKILL.md).

## Success Criteria
- A fresh installer with **no** `~/.claude/skills/voice-*/` skill can use `email` and `linkedin`
  and gets clean output grounded in **current channel best practices** (email; LinkedIn
  message/post/article), with **zero** references to Adam anywhere in the plugin.
- The `writing` plugin source contains no personal voice profile and no Adam-specific skill —
  `grep -ri "Adam"` across `plugins/writing/skills/{email,linkedin}` and the shared
  best-practices file returns no personal-voice content; `voice/` and `web-copy/` no longer exist
  in the plugin.
- `linkedin` correctly routes to message / post / article guidance based on an up-front format
  choice, each reflecting current best practice for that format.
- On Adam's machine: `email`/`linkedin` Option A discovers `voice-adam` and produces output
  materially identical to today's; the local `web-copy` skill still works.
- No window exists in which Adam's voice or web-copy is unavailable: `voice-adam` and local
  `web-copy` are created and verified before their in-plugin counterparts are deleted.
- The two remaining skills behave sensibly for all three discovery cases (0 / 1 / 2+ installed
  voice skills).

## Happy Path
1. User (any installer) invokes `email` or `linkedin`.
2. **linkedin only:** skill first asks which format — message / post / article.
3. Skill presents Option A "your installed personal voice" / B project voice / C start fresh.
4. On A, the skill scans `~/.claude/skills/voice-*/`.
5. Skill always loads the shared channel best-practices for the relevant channel/format, then
   layers the discovered voice (or clean default if none) on top.
6. Output reflects current best practice for the channel + the chosen voice — no hardcoded path,
   no Adam assumption.

## Edge Cases
- **Zero voice skills installed:** fall back to clean/best-practice default; still apply the
  shared channel best-practices. Option A must not error on a missing `../voice/...` path.
- **Multiple voice skills installed:** enumerate and ask which; don't silently pick one.
- **Best-practice regression:** a fresh installer must not lose the structural guidance the
  skills give today — that guidance moves into (and is refreshed within) the shared file, not
  away with Adam.
- **Deletion ordering:** deleting the in-plugin `voice` or `web-copy` skill before its local copy
  exists would strand Adam and, for `voice`, break `humanize`'s example set — ordering is
  load-bearing.
- **Stale references:** any lingering `../voice/references/...` path in the plugin after the
  cutover is a broken reference; the success grep guards against this.
- **LinkedIn message vs post confusion:** a message must not be written with feed-post hook
  mechanics; the format gate exists to prevent this.

## Audience
Two audiences: (1) new installers of the shared `writing` plugin who have their own voice or
none and want current best practices per channel; (2) Adam, whose voice and web-copy setup must
keep working via local skills.

## Technical Constraints
- `~/.claude/skills/voice-adam/` and `~/.claude/skills/web-copy/` are **outside** the git repo;
  creating them is a local action, not part of the PR diff. The PR contains only the plugin
  decoupling, the shared best-practices file, the LinkedIn format work, deletions, and registry
  updates.
- The shared best-practices file must be reachable by relative path from both `email` and
  `linkedin` after the `voice` skill is gone.
- Voice discovery must mirror `humanize`'s `~/.claude/skills/voice-*/` convention so the repo
  converges on one mechanism.
- Best-practices content should be sourced from current guidance (research and/or reusable
  existing skills), not merely copied from the year-stamped current file.

## Dependencies
- Depends on the completed `voice-extractor` cycle and its `~/.claude/skills/voice-<name>/`
  convention.
- `email` and `linkedin` depend on the shared best-practices file existing before the `voice`
  skill is deleted.
- Research into current channel best practices (and any reusable existing skills/plugins) is a
  Plan/Build activity feeding the shared file and the LinkedIn format guidance.

## UI Needed
No. This is a skill-file refactor — Shape stage is skipped; next stage is Plan.

---
*Auto-filled dimensions: none*
