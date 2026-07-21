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
practices** — how to actually write well for each channel today — and resolve the writer's
personal voice through a **location-independent lookup** rather than a hardcoded path. Adam's
personal material (`voice`, `web-copy`) moves out to local skills so his own setup keeps working.
It's Milestone 2 of the writing-plugin-voice product plan and depends on the completed
`voice-extractor` convention.

## Scope
- **Voice resolution (location- and layout-independent).** Rewrite the "Option A" branch in the
  two remaining platform skills (`email`, `linkedin`) to resolve the user's personal voice in
  this order, instead of reading the hardcoded `../voice/references/voice-profile.md`:
  1. **Registered pointer** — if the user's `~/.claude/CLAUDE.md` declares a default (a line like
     `Writing voice: <skill-name-or-path>`), use it.
  2. **Convention** — otherwise use an installed `voice-*` skill (the `voice-extractor`
     convention), resolved via Claude's own skill discovery, not a filesystem path glob: 0 found →
     clean best-practice default; exactly 1 → use it; 2+ → ask which.
  3. **Load at the skill level** — load the *resolved voice skill itself* (let it pull its own
     references), so consumers don't depend on a specific internal layout (single `SKILL.md` vs a
     `references/` folder). Option A's wording changes from "Adam's personal voice" to "your
     installed personal voice."
- **Registration pointer support.** Document a lightweight convention: an optional
  `Writing voice: <skill-name-or-path>` entry in the user's `~/.claude/CLAUDE.md` that the writing
  skills honor first. It may name an installed skill or point to a voice living anywhere (even a
  bare file). No new file format — Claude already loads CLAUDE.md every session.
- **voice-extractor registration hook (small addition).** When `voice-extractor` creates a voice
  skill, it offers to write/refresh the `Writing voice: <name>` pointer in the user's
  `~/.claude/CLAUDE.md` so the writing skills pick it up automatically. Offer only — never write
  silently.
- **Shared channel best-practices (the retained value):** produce a voice-neutral, in-plugin
  reference of *current best practices* for each channel that `email` and `linkedin` always load,
  regardless of which personal voice (if any) is resolved. Content is **researched and refreshed
  to reflect current best practice**, reusing existing skills/plugins where they already cover a
  channel, and seeded by the voice-neutral portions of today's `platform-guide.md` (the
  Adam-specific voice and examples stripped). This — not Adam's personality — is what a fresh
  installer gets.
- **LinkedIn format distinction:** `linkedin` must clearly distinguish and give best-practice
  guidance for three formats, selected up front:
  - **Message** — a 1:1 direct message / InMail / connection note. Short, purposeful, personal;
    no feed-post hook mechanics.
  - **Post** — a native feed post. Hook-driven, one idea (today's default; the existing post
    types and hook formulas live here).
  - **Article** — a long-form native LinkedIn article. Titled, sectioned, evergreen, longer-form;
    different structure from a feed post.
- **Migrate Adam out (local, no-gap), for both Adam-specific pieces:**
  - `voice` → `~/.claude/skills/voice-adam/` with `SKILL.md` + `references/voice-profile.md` +
    `references/platform-guide.md` (keeping the reference-file layout `humanize` still reads
    directly), created before the in-plugin `voice` skill is removed. Add
    `Writing voice: voice-adam` to Adam's `~/.claude/CLAUDE.md` so resolution is unambiguous.
  - `web-copy` → `~/.claude/skills/web-copy/` (a local personal skill), created before the
    in-plugin `web-copy` skill is removed. Its Option-A voice reference is repointed to the same
    resolution logic so it keeps working locally.
- **Delete from the plugin** once the local copies exist and the shared best-practices file is in
  place: the `voice` skill and the `web-copy` skill.
- **Registry/marketplace hygiene:** update the CLAUDE.md Component Registry and any
  marketplace/plugin metadata to drop `voice` and `web-copy` and reflect the new shared reference.

## Out of Scope
- Re-running extraction to build `voice-adam`; it is populated by copying the existing curated
  reference files. (`voice-extractor`'s only change this cycle is the optional CLAUDE.md pointer
  offer above.)
- Migrating `humanize` off its direct `voice-*/references/...` read. It keeps working because
  `voice-adam` preserves the reference-file layout; converging `humanize` onto skill-level
  resolution is a possible future cleanup, not this cycle.
- The `trm-brand-voice` skill referenced in `voice/SKILL.md` (separate company-voice concern).
- Web-copy channel best practices in the *shared* plugin reference. Web-copy leaves the plugin
  entirely this cycle; the shared best-practices file covers email + the three LinkedIn formats
  only.
- A structured registry file (e.g. `voice-registry.json`). The pointer lives in CLAUDE.md by
  design; a dedicated registry format was considered and not adopted.
- Publishing/enabling the shareable plugin for other users, or full installer documentation
  beyond a minimal note on registering/pointing at your own voice.

## Success Criteria
- A fresh installer with **no** voice skill and no pointer can use `email` and `linkedin` and gets
  clean output grounded in **current channel best practices** (email; LinkedIn
  message/post/article), with **zero** references to Adam anywhere in the plugin.
- Voice resolution honors the order pointer → convention → default, and **loads a resolved voice
  at the skill level** (works whether the voice skill is a single `SKILL.md` or has a `references/`
  folder, and wherever it is installed).
- A user whose voice lives outside the `voice-*` convention (different name, different location, or
  a bare file) can be picked up via the `Writing voice:` pointer in their CLAUDE.md.
- The `writing` plugin source contains no personal voice profile and no Adam-specific skill —
  `grep -ri "Adam"` across `plugins/writing/skills/{email,linkedin}` and the shared
  best-practices file returns no personal-voice content; `voice/` and `web-copy/` no longer exist
  in the plugin.
- `linkedin` routes to message / post / article guidance from an up-front format choice, each
  reflecting current best practice for that format.
- On Adam's machine: `email`/`linkedin` resolve `voice-adam` (via his CLAUDE.md pointer) and
  produce output materially identical to today's; the local `web-copy` skill still works.
- No window exists in which Adam's voice or web-copy is unavailable: `voice-adam`, its CLAUDE.md
  pointer, and local `web-copy` are created and verified before their in-plugin counterparts are
  deleted.

## Happy Path
1. User (any installer) invokes `email` or `linkedin`.
2. **linkedin only:** skill first asks which format — message / post / article.
3. Skill resolves the personal voice: check CLAUDE.md `Writing voice:` pointer → else installed
   `voice-*` (0 → clean default, 1 → use it, 2+ → ask) → load the resolved voice at the skill
   level.
4. Skill always loads the shared channel best-practices for the relevant channel/format, then
   layers the resolved voice (or clean default) on top.
5. Output reflects current best practice for the channel + the chosen voice — no hardcoded path,
   no Adam assumption.

## Edge Cases
- **Zero voices, no pointer:** clean best-practice default; still apply shared best-practices.
  Resolution must not error on a missing `../voice/...` path (that path no longer exists).
- **Multiple voices, no pointer:** enumerate and ask; don't silently pick one.
- **Voice outside the convention:** resolved only if the CLAUDE.md pointer names it; otherwise it
  falls through to "ask / describe your voice."
- **Pointer references a missing/renamed skill:** don't hard-fail — note it, fall back to the
  convention scan or default.
- **Varied voice-skill layout:** a `voice-extractor` single-`SKILL.md` voice and a
  `references/`-style voice must both load — hence skill-level loading, not a fixed reference path.
- **Best-practice regression:** a fresh installer must not lose today's structural guidance — it
  moves into (and is refreshed within) the shared file, not away with Adam.
- **Deletion ordering:** deleting an in-plugin skill before its local copy (and, for `voice-adam`,
  the pointer) exists would strand Adam and break `humanize`'s example set — ordering is
  load-bearing.
- **LinkedIn message vs post confusion:** a message must not be written with feed-post hook
  mechanics; the format gate prevents this.

## Audience
Two audiences: (1) new installers of the shared `writing` plugin — with their own voice
(anywhere), a `voice-*` voice, or none — who want current best practices per channel; (2) Adam,
whose voice and web-copy setup must keep working via local skills and a CLAUDE.md pointer.

## Technical Constraints
- `~/.claude/skills/voice-adam/`, `~/.claude/skills/web-copy/`, and the `~/.claude/CLAUDE.md`
  pointer line are **outside** the git repo; creating them is a local action, not part of the PR
  diff. The PR contains only the plugin decoupling, the shared best-practices file, the LinkedIn
  format work, the pointer-reading logic, deletions, and registry updates.
- Voice resolution must not read a hardcoded reference-file path; it loads the resolved voice at
  the skill level and honors the CLAUDE.md pointer first. The pointer format
  (`Writing voice: <skill-name-or-path>`) must be documented where users will see it.
- The shared best-practices file must be reachable by relative path from both `email` and
  `linkedin` after the `voice` skill is gone.
- Best-practices content should be sourced from current guidance (research and/or reusable
  existing skills), not merely copied from the year-stamped current file.

## Dependencies
- Depends on the completed `voice-extractor` cycle and its `~/.claude/skills/voice-<name>/`
  convention; `voice-extractor` gains the optional CLAUDE.md-pointer offer this cycle.
- `email` and `linkedin` depend on the shared best-practices file existing before the `voice`
  skill is deleted.
- Research into current channel best practices (and any reusable existing skills/plugins) is a
  Plan/Build activity feeding the shared file and the LinkedIn format guidance.

## UI Needed
No. This is a skill-file refactor — Shape stage is skipped; next stage is Plan.

---
*Auto-filled dimensions: none*
