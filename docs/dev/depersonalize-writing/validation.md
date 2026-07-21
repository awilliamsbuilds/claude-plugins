# Depersonalize Writing — Validation Report
*Branch: feature/depersonalize-writing · 2026-07-21*

## Summary
Loops run: 1 / 3
Final status: clean — no open P1/P2

Two fresh `general-purpose` subagents reviewed the build diff (`46c16f6..HEAD`) in parallel —
one code review, one security review — seeing only the diff, the spec's success criteria, and
the plan's task list. Findings were classified and fixed in a single loop; all hard success
criteria verified by grep.

## Issues Resolved
### Loop 1
- **P2 — LinkedIn post-length contradiction.** `channel-best-practices.md` (~1,300 chars
  short / ~3,000 long) and `linkedin/SKILL.md` (300–700 words / 600–1200) gave materially
  different numbers on the same dimension, and the Post route loads both at once. → Removed the
  competing numbers from `linkedin/SKILL.md` and deferred to `channel-best-practices.md`
  (`## LinkedIn — Post → Length and format`) as the single source of truth.
- **P3 — Stale plugin inventory (T10 hygiene miss).** `add-plugin/SKILL.md` still listed the
  deleted `voice` and `web-copy` skills. → Updated to `humanize`, `voice-extractor`, `linkedin`,
  `email` with a voice-neutral note.
- **P3 — Unvalidated "point to a voice anywhere" pointer (security).** `voice-resolution.md`
  told the model to load a `Writing voice:` target from any path with no scope constraint. →
  Constrained the pointer to an installed skill or a path under `~/.claude/`; a target outside
  that space now requires user confirmation before loading.
- **Nit — No "treat as data" guard on loaded voice content (security).** → Added a note to
  `voice-resolution.md` that a resolved voice skill is stylistic data (a writing sample), never
  new instructions to act on.

## Issues Remaining
### P1 Open
- None

### P2 Open
- None

### P3 Open
- None

### Nits Surfaced
- **Residual `adam`/`voice-adam` example slugs in `voice-extractor/SKILL.md`** (~lines 41,
  126–127). Left intentionally: plan Task 6 explicitly keeps these as pedagogical
  slug-collision examples (a person named Adam → `voice-adam`), not the deleted skill.
- **Main `CLAUDE.md` "Installed Plugins" table never listed `writing`** (pre-existing, predates
  this diff). Out of scope for this cycle.

## Notes
- All success-criteria greps verified clean post-fix: no `voice-*/references` coupling in
  `humanize`; no `trm` in shipped skills; no `../voice/` paths; no Adam personal-voice content in
  `email`/`linkedin`/`humanize` or the shared references; `voice/` and `web-copy/` removed from
  the plugin.
- Security review's net finding: the refactor is security-neutral-to-positive — it *removes* the
  prior filesystem-globbing voice lookup and uses Claude's skill roster (not a glob) for
  discovery, shrinking the automatic file-read surface. The `voice-extractor` CLAUDE.md write is
  correctly offer-only (Phase H). No secrets committed.
- Tasks 7 and 8 (local `voice-adam` / `web-copy` migration + pointer) are outside the repo and
  correctly absent from the diff; the user's global pointer + installed `voice-adam` confirm
  they were done.
