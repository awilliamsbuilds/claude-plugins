# Voice Extractor — Implementation Plan
*Branch: feature/voice-extractor · 2026-07-21*

## Files

| File | Action | Purpose |
|------|--------|---------|
| plugins/writing/skills/voice-extractor/SKILL.md | Create | The voice-extractor skill: interactive extraction flow + generated-skill template + refine mode + edge-case handling |
| CLAUDE.md | Modify | Add `writing:voice-extractor` row to the Component Registry |

**Note on marketplace.json:** No edit needed. `marketplace.json` registers *plugins*, not skills — the `writing` plugin is already registered and skills are auto-discovered from its `skills/` dir (confirmed: `voice`, `email`, etc. have no marketplace entries). Per CLAUDE.md "Adding a Skill to an Existing Plugin," the marketplace step is skipped. The spec's Technical-Constraints line about registering the skill in marketplace.json is inaccurate and is intentionally not acted on. (See Out of Scope.)

## Tasks

### Task 1: Author SKILL.md — frontmatter + input & analysis half
What: Create the voice-extractor skill file with frontmatter and the first half of the interactive flow — identify subject, new-vs-refine detection, gather from all four sources, sort signal from artifact, note register shift, evidence gate.
Used by: A user invoking `/writing:voice-extractor` (or "extract my voice") after `/plugin update`.
Depends on: nothing — first task.
Files: create `plugins/writing/skills/voice-extractor/SKILL.md`
Interfaces:
- Consumes: nothing.
- Produces: the file `plugins/writing/skills/voice-extractor/SKILL.md` containing YAML frontmatter (`name: voice-extractor`, rich `description`) and the flow sections through the evidence gate. Establishes the section skeleton (Phases A–D present, Phases E–G + Refine + Edge Cases appended by Task 2). Establishes the `~/.claude/skills/voice-<name>/SKILL.md` output-path convention referenced by Task 2.

Implementation steps:
1. Write YAML frontmatter matching repo convention (block scalar `description`, like `plugins/writing/skills/voice/SKILL.md`). `name: voice-extractor`. `description` must be rich with trigger phrases so Claude Code invokes it: e.g. "extract my voice", "build a voice profile", "capture how I/someone writes", "make a voice skill for <person>", "clone my writing style", "turn my past chats into a voice", plus explicit note it produces a reusable per-person voice skill. Distinguish it from `writing:voice` (Adam's fixed personal voice) and `writing:humanize` (pattern stripping) so triggering doesn't collide.
2. Opening section: one-paragraph statement of what the skill does and its output — a per-person voice `SKILL.md` written to `~/.claude/skills/voice-<name>/SKILL.md`. Note it packages the proven prompt (from `/Users/adam/Downloads/voice-skill-instructions.md`) into an invocable, repeatable flow.
3. **Phase A — Identify subject & mode.** Establish whose voice (default: the user; allow naming another person). Derive a `<name>` slug (lowercase-kebab). Check whether `~/.claude/skills/voice-<name>/SKILL.md` already exists → if yes, announce refine mode (handled in Task 2); if no, new build. State the check explicitly so Build wires it to the Read tool.
4. **Phase B — Gather.** Instruct 8–10 separate past-chat searches across topics and time periods (topic + recent-conversation lookups), using ONLY the subject's own messages and ignoring Claude's replies. Also accept: pasted writing samples (weight heavily), named files/folders read from disk (Read tool), and URLs (WebFetch). List all four source types from spec Scope. Note past-chat search requires "Search and reference past chats" enabled.
5. **Phase C — Sort signal from artifact.** Real voice (sentence rhythm/length, argument structure, vocabulary, hedge-vs-flat, humor, analogies, openings/closings, repeated constructions, directness) vs. chat artifact to discard (typos, dictation errors, dropped punctuation, extreme terseness, self-corrections, imperative bossing-Claude tone). Note the register shift: casual vs. careful, and that the profile targets the careful end — describe the voice at that end specifically, not an average.
6. **Phase D — Evidence gate.** Show 5–8 characteristic excerpts from the subject's own messages, each with what it demonstrates, then **STOP and wait** for the user to confirm/reject which sound right. Make the wait explicit and non-skippable — do not write the output skill before confirmation.

### Task 2: Author SKILL.md — output, refine, and edge-case half
What: Append the second half of the flow — confirm output path, write the generated voice skill in the mandated structure, test-draft and iterate, refine/update mode, and all edge-case handling.
Used by: The same skill invocation, continuing after the Task 1 evidence gate is confirmed.
Depends on: Task 1.
Files: modify `plugins/writing/skills/voice-extractor/SKILL.md` (append sections).
Interfaces:
- Consumes: from Task 1 — the section skeleton, the confirmed excerpt set from the Phase D evidence gate, the `<name>` slug and existing-file check result from Phase A, and the `~/.claude/skills/voice-<name>/SKILL.md` output-path convention.
- Produces: nothing — terminal authoring task for the file.

Implementation steps:
1. **Phase E — Confirm output path.** Default `~/.claude/skills/voice-<name>/SKILL.md`; state that the path is confirmed with the user before any write (spec Scope + Technical Constraints).
2. **Phase F — Write the generated voice skill.** Specify the exact structure the *output* file must follow (spec Success Criteria):
   - Valid YAML frontmatter (`name: voice-<name>`, rich `description`) so it's an invocable personal skill.
   - Prose voice description (how you'd describe the writing to another writer).
   - **Do:** traits, each with a real excerpt from the subject's messages/samples.
   - **Don't:** generic-AI tics AND this person's specific non-traits, named concretely (actual phrases/constructions).
   - **Calibration:** how the voice flexes across contexts (e.g. cover letter vs. recruiter email vs. LinkedIn / careful vs. casual).
   - **Before/after:** 2–3 default-AI passages each rewritten in the person's voice.
   - **Evidence-provenance note** inside the output file (e.g. "built from N chats + M samples — weight the careful register cautiously") so downstream use knows how much to trust it.
   - State the file must be self-sufficient: usable by another Claude with no access to the subject's history; every "Do" trait carries an example; ban vague guidance like "conversational but professional."
3. **Phase G — Test-draft & iterate.** After writing, draft one short sample in the new voice for a sanity check; if the user says it's off, cut/retry (2–3 rounds normal).
4. **Refine / update mode** (branch from Phase A when the file already exists): fold in new samples/chats, revise Do/Don't and Calibration, update the evidence-provenance note. Preserve confirmed traits from the prior file unless new evidence contradicts them; surface what changed. Do not overwrite from scratch.
5. **Edge-case handling section** covering all spec edge cases (see Edge Cases table): thin/unavailable input (stop and ask to enable past chats / paste real human-directed prose; explain chat-only samples read curt — do not silently proceed), flattery drift self-check (every Do cites a real excerpt and reads like the person, not a charmier version; cut on user pushback), unreachable sources (report and skip failed URLs / unparseable files, non-fatal).
6. Final self-check line in the skill: confirm the output is a valid personal skill at `~/.claude/skills/voice-<name>/SKILL.md` with valid frontmatter.

### Task 3: Register in Component Registry
What: Add a row for the new skill to the CLAUDE.md Component Registry table.
Used by: Repo maintainers / future `/dev` cycles reading the registry; project convention.
Depends on: Task 1 (file must exist at the referenced path).
Files: modify `CLAUDE.md`.
Interfaces:
- Consumes: the file path produced by Task 1 (`plugins/writing/skills/voice-extractor/SKILL.md`).
- Produces: nothing — terminal task.

Implementation steps:
1. In the `## Component Registry` table, add a row under the other `writing:*` entries:
   `| \`writing:voice-extractor\` | plugins/writing/skills/voice-extractor/SKILL.md | Extracts a person's writing voice into a reusable per-person voice skill |`
2. Optionally bump the registry's "Last updated" date line to 2026-07-21.

## Edge Cases
| Edge case | Handled in | Approach |
|-----------|-----------|----------|
| Thin / unavailable past-chat input | Task 2 (Phase B note + edge section) | Stop; ask user to enable "Search and reference past chats" and/or paste real human-directed prose; explain chat-only samples read curt. No silent proceed. |
| Flattery drift (traits sound sharper than the person) | Task 2 (edge section) | Self-check every Do cites a real excerpt and reads like the person; cut and retry 2–3 rounds on user pushback. |
| Evidence provenance | Task 2 (Phase F) | Output file records how thin/rich its evidence was so downstream use is calibrated. |
| Unreachable URLs / unparseable files | Task 2 (edge section) | Report and skip; non-fatal; continue with remaining sources. |
| Refine collision (existing voice file) | Task 2 (Refine mode) | Preserve confirmed prior traits unless new evidence contradicts; surface what changed; never overwrite from scratch. |
| Subject is someone other than the user | Task 1 (Phase A) | Establish whose voice up front; derive `<name>` slug; drive path and searches from it. |

## Out of Scope
- Editing `.claude-plugin/marketplace.json` — not needed for a skill added to an already-registered plugin (marketplace lists plugins, not skills). The spec's constraint here is inaccurate and intentionally not acted on.
- Editing `plugins/writing/.claude-plugin/plugin.json` — its description already covers writing-voice work; no change required.
- Registering *generated* per-person voice skills in any marketplace (they are local personal skills).
- Auto-applying an extracted voice to downstream writing tasks (job of the generated skill + existing writing skills).
- Building profiles from unreachable sources (gated URLs, unparseable binaries).
- Modifying `writing:voice` or `writing:humanize`.
