# claude-plugins — Product Plan
*Created: 2026-07-21 · Cycles completed: 3/5*

Repo-level backlog of planned `/dev` cycles. Milestones are appended by `dev:spec` when a
request decomposes into more than one cycle; items are checked off by `dev:done`.

## Milestone 1: Voice tooling
- [x] voice-extractor (feature) — a skill that extracts a person's voice from Claude
  chats, pasted samples, files, and URLs, and writes a per-person voice skill to
  `~/.claude/skills/voice-<name>/SKILL.md` (local, survives plugin updates). Supports a
  refine/update mode on re-invocation.

## Milestone 2: Depersonalize writing plugin
- [x] depersonalize-writing (feature) — make the `writing` plugin shareable: migrate
  Adam's `voice` skill out to a local skill (`~/.claude/skills/voice-adam/`, produced via
  voice-extractor's convention), decouple `email`/`linkedin`/`web-copy` from the hardcoded
  `../voice/references/voice-profile.md` path so they accept any named voice, and ship a
  generic default. Depends on voice-extractor.

## Milestone 3: Tech debt tracking
- [x] tech-debt-tracking (feature) — a durable, per-repo tech debt tracker for the `/dev`
  plugin. Adds `docs/dev/tech-debt.md` (created by `dev:init`), a carrying-cost write rule
  applied by `validate`/`build`/`reflect` with recurrence-merge, a flush at `done` before
  the cycle directory is deleted, spec-time surfacing of debt touching the current cycle,
  and a new `dev:debt` skill for reading and closing entries.
- [ ] debt-backfill (feature) — mine existing `docs/decisions/*.md` on init to seed the
  tracker from past cycles. Deferred from tech-debt-tracking: measured yield was ~3 items
  across 10 cycles with 2 of them cosmetic, and parsing ten unstructured log formats is far
  easier once real entries exist to define the target shape. Depends on tech-debt-tracking.
- [ ] debt-linear-promotion (feature) — `/dev:debt promote <id>` turns a tracker entry into
  a Linear issue with link-back. The Linear seam already exists via `dev:fix`. Deferred from
  tech-debt-tracking as an independent second deliverable. Depends on tech-debt-tracking.
