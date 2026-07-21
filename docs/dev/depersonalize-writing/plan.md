# Depersonalize Writing — Implementation Plan
*Branch: feature/depersonalize-writing · 2026-07-21*

## Files

| File | Action | Purpose |
|------|--------|---------|
| `plugins/writing/references/channel-best-practices.md` | Create | Voice-neutral, current channel best practices — email + LinkedIn message/post/article — loaded by `email` and `linkedin` |
| `plugins/writing/references/voice-resolution.md` | Create | Canonical pointer→convention→default voice-resolution procedure, loaded by `email` and `linkedin` |
| `plugins/writing/skills/humanize/SKILL.md` | Modify | Remove `voice-*/references/...` lookups; genericize TRMer audience line |
| `plugins/writing/skills/email/SKILL.md` | Modify | Replace hardcoded `../voice/...` with voice resolution; load shared best-practices; add humanize de-AI pass |
| `plugins/writing/skills/linkedin/SKILL.md` | Modify | Add up-front message/post/article format gate; voice resolution; shared best-practices; humanize pass |
| `plugins/writing/skills/voice-extractor/SKILL.md` | Modify | Add optional `~/.claude/CLAUDE.md` pointer offer; fix stale `writing:voice` references |
| `plugins/writing/skills/voice/` | Delete | Migrated to local `~/.claude/skills/voice-adam/` |
| `plugins/writing/skills/web-copy/` | Delete | Migrated to local `~/.claude/skills/web-copy/` |
| `plugins/writing/.claude-plugin/plugin.json` | Modify | Drop `web copy` / voice from description |
| `.claude-plugin/marketplace.json` | Modify | Update `writing` plugin description |
| `CLAUDE.md` | Modify | Component Registry — remove `voice`/`web-copy`, note shared references |
| `~/.claude/skills/voice-adam/` | Create (LOCAL, no commit) | Adam's migrated personal voice skill |
| `~/.claude/skills/web-copy/` | Create (LOCAL, no commit) | Adam's migrated web-copy skill |
| `~/.claude/CLAUDE.md` | Modify (LOCAL, no commit) | Add `Writing voice: voice-adam` pointer |

## Tasks

### Task 1: Create shared channel best-practices reference
What: A voice-neutral, in-plugin reference of current best practices for email and the three LinkedIn formats, loaded by both platform skills regardless of resolved voice.
Used by: `email` (email section) and `linkedin` (message/post/article sections), via relative path `../../references/channel-best-practices.md`.
Depends on: nothing — first task.
Files: create `plugins/writing/references/channel-best-practices.md`
Interfaces:
- Consumes: nothing (may read `plugins/writing/skills/voice/references/platform-guide.md` as a seed while it still exists, and the existing `linkedin` post-type/hook tables).
- Produces: file at `plugins/writing/references/channel-best-practices.md` with these named top-level sections, referenced by later tasks: `## Email`, `## LinkedIn — Message`, `## LinkedIn — Post`, `## LinkedIn — Article`.

Implementation steps:
1. Seed from the **voice-neutral** portions of `plugins/writing/skills/voice/references/platform-guide.md` (the External email section; the LinkedIn/Blog structure, tone, length, and "Do not" lists) and from the existing `linkedin/SKILL.md` post-type + hook tables. Strip every Adam/TRM-specific example (e.g. "It's a subtle difference…", "Cortex is TRM's…", "You still have 4+ years at TRM…"). Replace illustrative examples with neutral ones.
2. Refresh to current best practice, reusing existing guidance already in the repo: the email/LinkedIn channel markers in `humanize/SKILL.md` (structural + phrase-level tells, Hook vs. Value calibration) are current and voice-neutral — reference/summarize them rather than re-deriving. Do targeted web research only where a channel's best practice may have shifted (e.g. LinkedIn article length/format norms, link-in-comments reach behavior).
3. Write `## Email` — subject-line specificity, one ask, lead-with-the-point structure, length discipline, formality matching, one sign-off. (Voice-neutral distillation of the platform guide's External email section.)
4. Write `## LinkedIn — Message` — 1:1 DM / InMail / connection note. Short, purposeful, one clear reason for reaching out; **no feed-post hook mechanics, no engagement bait, no hashtags**. State explicitly that message format must NOT use post hooks (this is the guard for the message-vs-post edge case).
5. Write `## LinkedIn — Post` — native feed post: hook-driven, one idea developed, the existing hook formulas + post types, paragraph rhythm, close with a principle/question, no engagement bait. This preserves today's structural guidance (best-practice-regression edge case).
6. Write `## LinkedIn — Article` — long-form native article: a real title, sectioned body with subheads, evergreen framing, distinct from a feed post (no scroll-stop hook mechanics; opening earns the read through substance).
7. Keep the file voice-neutral end to end: no "Adam", no "TRM", no first-person-as-a-specific-person examples. Do not include web-copy (out of scope this cycle).

### Task 2: Create shared voice-resolution reference
What: The single canonical procedure for resolving which personal voice to write in, location- and layout-independent, replacing every hardcoded `../voice/references/...` path.
Used by: `email` Step 1 and `linkedin` Step 1, via relative path `../../references/voice-resolution.md`.
Depends on: nothing — independent of Task 1.
Files: create `plugins/writing/references/voice-resolution.md`
Interfaces:
- Consumes: nothing.
- Produces: file at `plugins/writing/references/voice-resolution.md` documenting a procedure later tasks invoke by reference (no code symbols; a prose procedure the skills point to).

Implementation steps:
1. Document the resolution order exactly:
   1. **Registered pointer** — if `~/.claude/CLAUDE.md` declares a line `Writing voice: <skill-name-or-path>`, use it. It may name an installed skill or a path to a voice anywhere.
   2. **Convention** — otherwise discover installed `voice-*` skills via Claude's own skill discovery (NOT a filesystem glob): 0 → clean best-practice default; 1 → use it; 2+ → enumerate and ask which.
   3. **Load at the skill level** — load the resolved voice *skill itself* (self-contained: a single `SKILL.md`, or one that carries its own `references/`). Never load a hardcoded external reference-file path.
2. Document the edge cases inline so both skills inherit them:
   - **Pointer references a missing/renamed skill:** do not hard-fail — note it, fall back to the convention, then default.
   - **Voice outside the `voice-*` convention:** resolved only via the pointer; if no pointer, fall through to "ask, or describe your voice," then default.
   - **Zero voices, no pointer:** clean best-practice default (still apply channel best-practices).
3. State the default explicitly: when resolution yields no voice, write in a natural, varied human default voice — never error, never assume Adam.
4. Keep it voice-neutral and installer-facing (no "Adam's personal voice" wording).

### Task 3: Decouple `humanize` from voice + genericize audience
What: Narrow `humanize` to de-AI'ing text into a natural default voice; remove all personal-voice-skill resolution and the company-specific audience line.
Used by: any user invoking `humanize` directly, and `email`/`linkedin` composing a de-AI pass.
Depends on: nothing — independent.
Files: modify `plugins/writing/skills/humanize/SKILL.md`
Interfaces:
- Consumes: nothing.
- Produces: a `humanize` skill with no `voice-*/references/...` reference and no `trm` reference — the grep-based success criteria.

Implementation steps:
1. In the `## Voice Calibration` section, **delete priority item 1** ("Check for a local voice skill" with the `~/.claude/skills/voice-*/references/voice-profile.md` and `platform-guide.md` bullets). Renumber the remaining priorities (provided sample → ask for sample → default voice) as 1–3.
2. Reword the section intro so calibration is optional and sample-based only: `humanize` no longer reads or resolves any voice skill; if no sample is provided it de-AIs into a natural, varied default human voice.
3. In the frontmatter `description`, change `**Audience:** For any TRMer drafting prose` → `**Audience:** For anyone drafting prose`.
4. Verify: `grep -n "voice-" plugins/writing/skills/humanize/SKILL.md` returns nothing pointing at `voice-*/references/...`; `grep -in "trm" plugins/writing/skills/humanize/SKILL.md` returns nothing.

### Task 4: Rewrite `email` — voice resolution + best-practices + humanize pass
What: Replace `email`'s hardcoded voice load with the shared resolution procedure, always load the shared email best-practices, and compose a `humanize` de-AI pass.
Used by: users invoking `email`.
Depends on: Task 1 (channel-best-practices.md), Task 2 (voice-resolution.md).
Files: modify `plugins/writing/skills/email/SKILL.md`
Interfaces:
- Consumes: `plugins/writing/references/channel-best-practices.md` (`## Email` section) and `plugins/writing/references/voice-resolution.md`, both via `../../references/...`.
- Produces: an `email` skill with no `../voice/...` path and no "Adam's personal voice" default assumption.

Implementation steps:
1. Rewrite **Step 1 — Voice context**: remove the hardcoded `Load ../voice/references/voice-profile.md and ../voice/references/platform-guide.md`. Change option A wording from "Adam's personal voice" to "**your installed personal voice**." Point the resolution at `../../references/voice-resolution.md` (follow that procedure: pointer → convention → default). Keep options for "describe your own voice" and "start clean."
2. Add a step to **always load** `../../references/channel-best-practices.md` (`## Email` section) regardless of resolved voice, so a fresh installer still gets current email best practices.
3. In **Step 4 — Write**, add an explicit **humanize de-AI pass**: after drafting, apply the `humanize` skill's email rules to the draft (compose, don't inline-duplicate — reference running `humanize` on the output). Order: best-practices + resolved voice → draft → humanize pass.
4. Preserve the existing relationship-calibration, email-type, and output-format steps.
5. Verify: `grep -n "\.\./voice/" plugins/writing/skills/email/SKILL.md` returns nothing; `grep -in "adam" plugins/writing/skills/email/SKILL.md` returns nothing.

### Task 5: Rewrite `linkedin` — format gate + resolution + humanize pass
What: Add an up-front message/post/article format choice that routes to the right best-practice guidance, plus the shared voice resolution and a `humanize` de-AI pass.
Used by: users invoking `linkedin`.
Depends on: Task 1 (channel-best-practices.md), Task 2 (voice-resolution.md).
Files: modify `plugins/writing/skills/linkedin/SKILL.md`
Interfaces:
- Consumes: `plugins/writing/references/channel-best-practices.md` (`## LinkedIn — Message`, `## LinkedIn — Post`, `## LinkedIn — Article`) and `plugins/writing/references/voice-resolution.md`, via `../../references/...`.
- Produces: a `linkedin` skill with an explicit format gate and no `../voice/...` path, no "Adam's personal voice" default.

Implementation steps:
1. Rewrite **Step 1 — Voice context** the same way as email: option A → "your installed personal voice," resolution via `../../references/voice-resolution.md`; keep project/company and clean options.
2. Insert a new **format gate before post-type selection**: ask up front which format —
   - **Message** — 1:1 DM / InMail / connection note → load `## LinkedIn — Message`; short, purposeful, no hook mechanics. Skip the hook and post-type steps entirely.
   - **Post** — native feed post → load `## LinkedIn — Post`; proceed with the existing post-type table + hook formulas + body/close (today's default behavior, preserved).
   - **Article** — long-form native article → load `## LinkedIn — Article`; titled, sectioned, evergreen; no feed-post hook mechanics.
3. Always load the relevant section of `../../references/channel-best-practices.md` for the chosen format.
4. In the write step, add an explicit **humanize de-AI pass** on the drafted output (compose `humanize`, LinkedIn rules), same ordering as email.
5. Ensure the Message path explicitly forbids feed-post hook mechanics and engagement bait (message-vs-post edge case guard).
6. Verify: `grep -n "\.\./voice/" plugins/writing/skills/linkedin/SKILL.md` returns nothing; `grep -in "adam" plugins/writing/skills/linkedin/SKILL.md` returns nothing.

### Task 6: Add `voice-extractor` pointer offer + fix stale references
What: When `voice-extractor` finishes creating a voice skill, it offers (never silently writes) to add/refresh a `Writing voice: <name>` pointer in `~/.claude/CLAUDE.md`; also correct references to the now-removed in-plugin `writing:voice`.
Used by: users running `voice-extractor`.
Depends on: nothing — independent.
Files: modify `plugins/writing/skills/voice-extractor/SKILL.md`
Interfaces:
- Consumes: nothing.
- Produces: a `voice-extractor` that documents the pointer convention (consumed conceptually by Task 2's resolution order; no code coupling).

Implementation steps:
1. In **Phase F** (or a short new step after the file is written in Phase F/G), add: offer to write or refresh a single line `Writing voice: voice-<name>` in `~/.claude/CLAUDE.md` so the writing skills resolve this voice first. **Offer only** — present the exact line and ask; never write it silently. If a `Writing voice:` line already exists, offer to update it and show the before/after.
2. Do not change the single-file `SKILL.md` output shape or add a `references/` folder (explicitly out of scope).
3. Fix stale cross-references to the deleted in-plugin skill: the mentions of `writing:voice` (lines ~17 and ~126–127) currently assume that skill ships in the plugin. Reword to reference the general `voice-*` convention / an installed personal voice skill (e.g. the slug-collision warning should read "an existing `voice-<name>` skill" rather than "the repo's `writing:voice`"). Keep the legitimate `adam`/`jordan-lee` slug examples — those are illustrative, not the deleted skill.

### Task 7: Migrate `voice` → local `voice-adam` + register pointer (LOCAL — no commit)
What: Create Adam's personal voice as a local skill and register it, before the in-plugin `voice` is deleted, so no window exists where his voice is unavailable.
Used by: Adam's local `email`/`linkedin`/`web-copy` via the CLAUDE.md pointer.
Depends on: nothing — reads the in-plugin `voice/` which still exists.
Files (all outside the repo — **no git commit**):
- create `~/.claude/skills/voice-adam/` (verbatim copy of `plugins/writing/skills/voice/`)
- modify `~/.claude/CLAUDE.md`
Interfaces:
- Consumes: `plugins/writing/skills/voice/` (source to copy verbatim, incl. `references/voice-profile.md` and `references/platform-guide.md`).
- Produces: a resolvable `voice-adam` skill + a `Writing voice: voice-adam` pointer — the prerequisite verified before Task 9 deletes the plugin copy.

Implementation steps:
1. Copy the entire `plugins/writing/skills/voice/` directory verbatim to `~/.claude/skills/voice-adam/` — `references/` preserved exactly (Adam's genuine content; TRM examples stay per Out of Scope).
2. Edit only the copied `SKILL.md` frontmatter/prose minimally: rename `name: voice` → `name: voice-adam`; remove the dangling `trm-brand-voice` pointer line ("For TRM company voice, use the trm-brand-voice skill instead.") and the frontmatter mention of it. Leave Adam's own voice content (including incidental TRM references in examples) intact.
3. Add the line `Writing voice: voice-adam` to `~/.claude/CLAUDE.md`.
4. **Verify** before proceeding: the `voice-adam` skill is discoverable and the pointer line reads correctly. This verification is the deliverable — it gates Task 9. No commit is produced (all paths are outside the repo).

### Task 8: Migrate `web-copy` → local `web-copy` (LOCAL — no commit)
What: Create Adam's `web-copy` as a local skill with its voice reference repointed, before the in-plugin `web-copy` is deleted.
Used by: Adam locally.
Depends on: nothing — reads the in-plugin `web-copy/` which still exists.
Files (outside the repo — **no git commit**):
- create `~/.claude/skills/web-copy/` (copy of `plugins/writing/skills/web-copy/`)
Interfaces:
- Consumes: `plugins/writing/skills/web-copy/` (source to copy).
- Produces: a working local `web-copy` — prerequisite verified before Task 9.

Implementation steps:
1. Copy `plugins/writing/skills/web-copy/` to `~/.claude/skills/web-copy/`.
2. Repoint Step 1's voice reference: replace `Load ../voice/references/voice-profile.md` (which won't exist at the local path) with an **inlined** copy of the resolution logic (pointer → convention → default, load the resolved voice skill at the skill level). The shared `voice-resolution.md` lives in the plugin and is not reachable from `~/.claude/skills/web-copy/`, so inline it here rather than referencing it. Change "Adam's personal voice" wording to "your installed personal voice."
3. **Verify** the local `web-copy` still works (Step 1 resolves via the pointer to `voice-adam`). Verification is the deliverable; no commit.

### Task 9: Delete in-plugin `voice` and `web-copy`
What: Remove the migrated skills from the plugin once the local copies + pointer + shared references exist and the platform skills no longer reference them.
Used by: nothing — terminal cleanup of the plugin surface.
Depends on: Task 1 (shared best-practices seeded from `platform-guide.md` before it's deleted), Task 4 + Task 5 (`email`/`linkedin` no longer reference `../voice/`), Task 7 + Task 8 (local copies + pointer verified).
Files: delete `plugins/writing/skills/voice/` and `plugins/writing/skills/web-copy/`
Interfaces:
- Consumes: verified outputs of Tasks 1, 4, 5, 7, 8.
- Produces: a plugin with no personal voice profile and no Adam-specific skill.

Implementation steps:
1. Confirm the prerequisites: `../../references/channel-best-practices.md` and `voice-resolution.md` exist; `grep -rn "\.\./voice/" plugins/writing/` returns nothing; local `voice-adam` + pointer + local `web-copy` verified (Tasks 7, 8).
2. `git rm -r plugins/writing/skills/voice plugins/writing/skills/web-copy`.
3. Verify the success-criteria greps: `grep -ri "Adam" plugins/writing/skills/{email,linkedin,humanize}` and the shared references return no personal-voice content; `grep -rin "trm" plugins/writing/skills/` returns nothing; `voice/` and `web-copy/` no longer exist in the plugin.

### Task 10: Registry, marketplace, and plugin metadata hygiene
What: Update the repo's registry and plugin metadata to drop `voice`/`web-copy` and reflect the new shared references.
Used by: the marketplace loader and repo documentation.
Depends on: Task 9 (deletions done).
Files: modify `CLAUDE.md`, `plugins/writing/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`
Interfaces:
- Consumes: the deletions from Task 9.
- Produces: nothing — terminal task.

Implementation steps:
1. `CLAUDE.md` Component Registry: remove the `writing:voice` and `writing:web-copy` rows; add a row/note for the shared references (`plugins/writing/references/channel-best-practices.md` and `voice-resolution.md`). Update the "Last updated" line.
2. `plugins/writing/.claude-plugin/plugin.json`: revise `description` to drop "web copy" and the "write in your voice" framing — e.g. "Multi-context writing toolkit — humanize AI text, write LinkedIn messages/posts/articles, and personal email, composing your installed voice."
3. `.claude-plugin/marketplace.json`: update the `writing` plugin `description` the same way (read the file first to preserve structure).

## Edge Cases
| Edge case | Handled in | Approach |
|-----------|-----------|----------|
| `humanize` invoked directly, no voice installed | Task 3 | Voice Calibration is sample-only; no lookup, no error; de-AI into default voice |
| Zero voices, no pointer | Task 2 | Resolution yields clean best-practice default; best-practices still applied (Task 4/5) |
| Multiple voices, no pointer | Task 2 | Enumerate and ask; never silently pick |
| Voice outside `voice-*` convention | Task 2 | Resolved only via the `Writing voice:` pointer; else ask/describe → default |
| Pointer references missing/renamed skill | Task 2 | No hard-fail — note it, fall back to convention/default |
| Best-practice regression for fresh installer | Task 1 | Today's structural guidance moves into (and is refreshed within) the shared file |
| Deletion ordering strands Adam | Task 9 deps | T9 gated on T7+T8 (local copies+pointer verified) and T4+T5 (repointed) |
| LinkedIn message vs post confusion | Task 5 + Task 1 | Up-front format gate; Message section forbids hook mechanics/engagement bait |

## Out of Scope
- A `references/` folder for `voice-extractor` — its single-file `SKILL.md` stays self-contained.
- Re-running extraction / reformatting to build `voice-adam` — the existing directory is copied verbatim.
- Authoring or managing a `trm-brand-voice` skill (only the dangling reference is removed); scrubbing TRM from Adam's personal `voice-adam` content.
- Web-copy in the shared best-practices file — web-copy leaves the plugin this cycle.
- A structured registry file (`voice-registry.json`) — the pointer lives in `~/.claude/CLAUDE.md`.
- Publishing/enabling the shareable plugin for other users, or full installer docs beyond the pointer note.
