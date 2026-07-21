# Depersonalize Writing — Decision Log
*2026-07-21 · Branch: feature/depersonalize-writing · PR #33*

## What was built
Turned the `writing` plugin into a shareable, voice-neutral toolkit: `humanize`, `email`,
and `linkedin` were decoupled from Adam's baked-in personal voice, Adam's `voice` and
`web-copy` skills were migrated out to local skills, and voice is now resolved at runtime
via a pointer → convention → default procedure.

## Key decisions
- **Split into clean, single-purpose composable components** → `humanize` de-AIs text into a
  natural default voice and reads no voice at all; the platform skills (`email`, `linkedin`)
  compose shared best-practices + a `humanize` pass + a resolved voice on top. Keeps each piece
  installable and reusable by anyone.
- **Voice resolution order: registered pointer → `voice-*` convention → clean default** → a
  `Writing voice: <skill-name-or-path>` line in `~/.claude/CLAUDE.md` wins; otherwise Claude's
  own skill discovery finds installed `voice-*` skills (0 → default, 1 → use it, 2+ → ask). No
  hardcoded external reference-file path; the resolved voice is loaded at the skill level.
- **Discovery via Claude's skill roster, not a filesystem glob** → shrinks the automatic
  file-read surface and removes the prior `~/.claude/skills/voice-*/references/...` lookup.
- **Load the voice skill self-contained** → a voice is a single `SKILL.md` or one carrying its
  own `references/`; consumers never depend on its internal layout, so no `references/` split-out
  was needed for `voice-extractor` (the "Milestone 3" question — resolved as not needed).
- **Migrate Adam out locally with load-bearing ordering** → `voice-adam`, its CLAUDE.md pointer,
  and local `web-copy` are created and verified *before* the in-plugin `voice`/`web-copy` are
  deleted, so no window exists where Adam's setup breaks. Adam's genuine content (including
  incidental TRM examples in his own voice) stays; only the plugin is depersonalized.
- **`voice-extractor` offers, never silently writes, the pointer** → after creating a voice skill
  it presents the exact `Writing voice: voice-<name>` line and asks before touching CLAUDE.md.
- **Pointer scope constrained for safety** → a `Writing voice:` target must be an installed skill
  or a path under `~/.claude/`; anything outside requires user confirmation before loading, and a
  resolved voice skill is treated as stylistic data (a writing sample), never as instructions.

## Design choices
Shape stage was skipped — this was a skill-file refactor with no UI. Two shared references were
introduced instead of inlining logic: `channel-best-practices.md` (voice-neutral email + LinkedIn
message/post/article guidance, the retained structural value, refreshed from the old
`platform-guide.md` with all Adam/TRM examples stripped) and `voice-resolution.md` (the canonical
resolution procedure both platform skills point to). `linkedin` gained an up-front
message/post/article format gate; the Message path explicitly forbids feed-post hook mechanics and
engagement bait, guarding the message-vs-post confusion.

## Validation notes
- 1 loop run (tier: standard) — clean, no open P1/P2.
- Resolved in loop 1: P2 LinkedIn post-length contradiction (deferred to `channel-best-practices.md`
  as the single source of truth); P3 stale plugin inventory in `add-plugin/SKILL.md`; P3 unscoped
  pointer path (constrained to installed skill or `~/.claude/`); Nit "treat as data" guard added to
  `voice-resolution.md`.
- Accepted as-is: residual `adam`/`voice-adam` example slugs in `voice-extractor/SKILL.md`
  (intentional pedagogical slug-collision examples per plan Task 6); main `CLAUDE.md` "Installed
  Plugins" table never listed `writing` (pre-existing, out of scope).

## Artifacts (archived)
Spec, plan, and validation committed at: 8cf7fb68fc742aa569e86f973e311ce23476976a on branch
feature/depersonalize-writing.
