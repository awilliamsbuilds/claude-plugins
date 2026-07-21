# Depersonalize Writing
*Branch: feature/depersonalize-writing · Confidence: 95% — Ready · 2026-07-21*
*Cycle type: feature · Tier: standard*

## Intent
The `writing` plugin is meant to be installable by anyone, but it currently ships Adam's
personal voice and Adam-specific skills baked in, and its components are tangled: `voice`
contains Adam's profile; `email`/`linkedin`/`web-copy` hardcode `../voice/references/...`; and
`humanize` reaches into `~/.claude/skills/voice-*/references/...`, which other users won't have.

This cycle turns `writing` into a shareable, voice-neutral toolkit built from **clean,
single-purpose components** that compose:
- **`humanize`** — strips AI-writing patterns into a natural default voice. Nothing about a
  specific person; it no longer resolves or reads voice skills.
- **A personal voice** — a self-contained `voice-*` skill (produced by `voice-extractor`),
  resolvable from anywhere via a lightweight pointer + naming convention.
- **Shared channel best-practices** — current, voice-neutral guidance for each channel, shipped
  in the plugin.
- **Platform skills (`email`, `linkedin`)** — the composers: they pull best-practices + a
  `humanize` de-AI pass + the resolved voice.

Adam's personal material (`voice`, `web-copy`) moves out to local skills so his own setup keeps
working. It's Milestone 2 of the writing-plugin-voice product plan and depends on the completed
`voice-extractor` convention.

## Scope
- **Decouple `humanize` from voice.** Remove the `~/.claude/skills/voice-*/references/...`
  lookups from `humanize`'s Voice Calibration step. `humanize`'s job narrows to de-AI'ing text
  into a natural, varied human default voice; it no longer reads or resolves personal voice
  skills. (Voice is composed on top by the platform skills or by the user combining skills.)
- **Composition in the platform skills.** `email` and `linkedin` produce output by composing:
  (1) the shared channel best-practices for the relevant channel/format, (2) a `humanize` de-AI
  pass, and (3) the resolved personal voice (or a clean default if none).
- **Voice resolution (location- and layout-independent)** in `email` and `linkedin`, replacing
  the hardcoded `../voice/references/voice-profile.md`, in this order:
  1. **Registered pointer** — if `~/.claude/CLAUDE.md` declares `Writing voice: <skill-name-or-path>`, use it.
  2. **Convention** — otherwise use an installed `voice-*` skill, resolved via Claude's own skill
     discovery (not a filesystem glob): 0 → clean best-practice default; 1 → use it; 2+ → ask which.
  3. **Load at the skill level** — load the resolved voice *skill* itself (a single self-contained
     `SKILL.md`), never a hardcoded reference-file path. Option A's wording changes from "Adam's
     personal voice" to "your installed personal voice."
- **Registration pointer support.** Document a lightweight convention: an optional
  `Writing voice: <skill-name-or-path>` entry in `~/.claude/CLAUDE.md` that the writing skills
  honor first. It may name an installed skill or point to a voice anywhere. No new file format.
- **voice-extractor pointer hook (small addition, no layout change).** When `voice-extractor`
  creates a voice skill, it offers to write/refresh the `Writing voice: <name>` pointer in
  `~/.claude/CLAUDE.md`. Offer only — never write silently. `voice-extractor`'s single-file
  `SKILL.md` output is unchanged; no `references/` folder is added (not needed — see Out of Scope).
- **Shared channel best-practices (the retained value):** a voice-neutral, in-plugin reference of
  *current best practices* per channel that `email` and `linkedin` always load, regardless of the
  resolved voice. Content is **researched and refreshed to reflect current best practice**,
  reusing existing skills/plugins where they cover a channel, and seeded by the voice-neutral
  portions of today's `platform-guide.md` (Adam-specific voice and examples stripped).
- **LinkedIn format distinction:** `linkedin` distinguishes and gives best-practice guidance for
  three formats, chosen up front:
  - **Message** — 1:1 DM / InMail / connection note. Short, purposeful; no feed-post hook mechanics.
  - **Post** — native feed post. Hook-driven, one idea (today's default; existing post types + hooks).
  - **Article** — long-form native article. Titled, sectioned, evergreen; distinct from a feed post.
- **Migrate Adam out (local, no-gap):**
  - `voice` → `~/.claude/skills/voice-adam/` as a **single self-contained `SKILL.md`**
    consolidating Adam's voice profile and his personal platform notes (matching `voice-extractor`'s
    convention), created before the in-plugin `voice` skill is removed. Add
    `Writing voice: voice-adam` to Adam's `~/.claude/CLAUDE.md`.
  - `web-copy` → `~/.claude/skills/web-copy/` (local personal skill), created before the in-plugin
    `web-copy` skill is removed. Its voice reference is repointed to the same resolution logic.
- **Delete from the plugin** once the local copies + pointer + shared best-practices file exist:
  the `voice` skill and the `web-copy` skill.
- **Registry/marketplace hygiene:** update the CLAUDE.md Component Registry and marketplace/plugin
  metadata to drop `voice` and `web-copy` and reflect the new shared reference.

## Out of Scope
- **A `references/` folder for `voice-extractor` (the "Milestone 3" question): not needed.** Its
  single-file `SKILL.md` is a robust, self-contained voice profile, and every consumer now loads
  voice at the skill level, so no split-out reference files are required anywhere.
- Re-running extraction to build `voice-adam`; it is assembled by consolidating Adam's existing
  curated `voice-profile.md` + `platform-guide.md` content into one `SKILL.md`.
- The `trm-brand-voice` skill referenced in `voice/SKILL.md` (separate company-voice concern).
- Web-copy channel best practices in the *shared* plugin reference. Web-copy leaves the plugin
  this cycle; the shared file covers email + the three LinkedIn formats only.
- A structured registry file (e.g. `voice-registry.json`) — the pointer lives in CLAUDE.md.
- Publishing/enabling the shareable plugin for other users, or full installer documentation beyond
  a minimal note on registering/pointing at your own voice.

## Success Criteria
- **`humanize` contains no voice-skill coupling** — `grep -n "voice-" plugins/writing/skills/humanize/SKILL.md`
  returns nothing pointing at `voice-*/references/...`; it runs standalone for any user with no
  voice installed and never errors on a missing references path.
- A fresh installer with no voice skill and no pointer can use `email` and `linkedin` and gets
  clean output = current channel best practices + de-AI'd (via `humanize`) + a natural default
  voice, with **zero** references to Adam anywhere in the plugin.
- Voice resolution honors pointer → convention → default and loads a **single self-contained
  voice `SKILL.md`** at the skill level, wherever it is installed.
- A voice outside the `voice-*` convention (different name/location) is picked up via the
  `Writing voice:` pointer.
- The `writing` plugin source contains no personal voice profile and no Adam-specific skill —
  `grep -ri "Adam"` across `plugins/writing/skills/{email,linkedin,humanize}` and the shared
  best-practices file returns no personal-voice content; `voice/` and `web-copy/` no longer exist
  in the plugin.
- `linkedin` routes to message / post / article guidance from an up-front format choice.
- On Adam's machine: `email`/`linkedin` resolve `voice-adam` via his CLAUDE.md pointer and produce
  output materially identical to today's; local `web-copy` still works.
- No window exists in which Adam's voice or web-copy is unavailable: `voice-adam`, its pointer, and
  local `web-copy` are created and verified before their in-plugin counterparts are deleted.

## Happy Path
1. User invokes `email` or `linkedin`.
2. **linkedin only:** skill asks which format — message / post / article.
3. Skill loads the shared channel best-practices for that channel/format.
4. Skill resolves the personal voice: CLAUDE.md `Writing voice:` pointer → else installed `voice-*`
   (0 → clean default, 1 → use it, 2+ → ask) → load the resolved voice `SKILL.md`.
5. Skill drafts, applying best-practices + a `humanize` de-AI pass + the resolved voice.
6. Output is current-best-practice, human-sounding, and on-voice — no hardcoded path, no Adam
   assumption.

## Edge Cases
- **`humanize` invoked directly with no voice installed:** works fully — de-AI into a default
  human voice; no voice lookup, no error.
- **Zero voices, no pointer:** clean best-practice default; still apply shared best-practices.
- **Multiple voices, no pointer:** enumerate and ask; don't silently pick one.
- **Voice outside the convention:** resolved only via the CLAUDE.md pointer; else fall through to
  "ask / describe your voice."
- **Pointer references a missing/renamed skill:** don't hard-fail — note it, fall back to the
  convention or default.
- **Best-practice regression:** a fresh installer must not lose today's structural guidance — it
  moves into (and is refreshed within) the shared file.
- **Deletion ordering:** deleting an in-plugin skill before its local copy (and, for `voice-adam`,
  the pointer) exists would strand Adam — ordering is load-bearing. (No longer a `humanize` risk,
  since `humanize` no longer depends on the voice skill.)
- **LinkedIn message vs post confusion:** a message must not use feed-post hook mechanics; the
  format gate prevents this.

## Audience
Two audiences: (1) new installers of the shared `writing` plugin — with their own voice anywhere,
a `voice-*` voice, or none — who want current best practices per channel; (2) Adam, whose voice
and web-copy setup must keep working via local skills and a CLAUDE.md pointer.

## Technical Constraints
- `~/.claude/skills/voice-adam/`, `~/.claude/skills/web-copy/`, and the `~/.claude/CLAUDE.md`
  pointer line are **outside** the git repo; creating them is a local action, not part of the PR.
  The PR contains the plugin decoupling (`email`, `linkedin`, `humanize`), the shared
  best-practices file, the LinkedIn format work, the pointer-reading logic, the `voice-extractor`
  pointer offer, deletions, and registry updates.
- No skill reads a hardcoded voice reference-file path. Voice is loaded at the skill level; voice
  skills are single self-contained `SKILL.md` files. `humanize` reads no voice at all.
- The shared best-practices file must be reachable by relative path from both `email` and
  `linkedin` after the `voice` skill is gone.
- Best-practices content should be sourced from current guidance (research and/or reusable
  existing skills), not merely copied from the year-stamped current file.

## Dependencies
- Depends on the completed `voice-extractor` cycle and its single-file `~/.claude/skills/voice-<name>/SKILL.md`
  convention; `voice-extractor` gains only the optional CLAUDE.md-pointer offer this cycle.
- `email` and `linkedin` depend on the shared best-practices file existing before the `voice` skill
  is deleted, and compose the `humanize` skill at draft time.
- Research into current channel best practices (and reusable existing skills/plugins) is a
  Plan/Build activity feeding the shared file and the LinkedIn format guidance.

## UI Needed
No. This is a skill-file refactor — Shape stage is skipped; next stage is Plan.

---
*Auto-filled dimensions: none*
