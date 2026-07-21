# Voice Extractor
*Branch: feature/voice-extractor · Confidence: 90% — Ready · 2026-07-21*
*Cycle type: feature · Tier: standard*

## Intent
People want their writing — cover letters, outreach, posts, emails — to sound like
*them*, not like a template. Today that voice lives only in scattered samples and in the
way a person writes to Claude. This skill gives anyone a repeatable way to capture how a
specific person actually writes and turn it into a reusable **per-person voice skill** that
other writing work can adopt. It packages the proven prompt in
`/Users/adam/Downloads/voice-skill-instructions.md` into an invocable skill, and adds an
iterative refine loop so the profile sharpens as more samples accumulate.

## Scope
- A new skill, `voice-extractor`, in the `writing` plugin
  (`plugins/writing/skills/voice-extractor/SKILL.md`), registered in `marketplace.json`
  like any other skill in this repo.
- The skill gathers voice evidence from multiple source types:
  - **Claude past chats** — the person's own messages (ignore Claude's replies); the primary
    source. Requires "Search and reference past chats" enabled.
  - **Pasted writing samples** — real prose written for other humans (weighted heavily).
  - **Files / folders** — local documents, exported posts, transcripts read from disk.
  - **Public web / URLs** — a person's published writing fetched from URLs.
- Full interactive extraction flow: gather → sort signal vs. artifact → note register
  shifts → show evidence and **wait** for confirmation → write skill → test-draft one sample.
- Writes the generated voice skill to **`~/.claude/skills/voice-<name>/SKILL.md`** (a
  personal skill, invocable anywhere, untouched by plugin updates). The destination path is
  confirmed with the user before writing.
- **Refine/update mode:** on invocation, if a voice skill for that person already exists,
  offer to improve it — fold in new samples/chats, revise Do/Don't and calibration, update
  the evidence-confidence note — rather than overwrite from scratch.

## Out of Scope
- Registering generated per-person voice skills in the plugin marketplace or editing the
  `writing` plugin's `marketplace.json` for outputs. Outputs are local personal skills only.
- Auto-applying an extracted voice to any downstream writing task (that's the job of the
  generated skill once it exists, plus existing writing skills).
- Building voice profiles from sources the environment can't reach (e.g. gated/private URLs,
  binary formats the Read tool can't parse).
- Modifying or replacing the existing `writing:voice` (Adam's personal voice) or
  `writing:humanize` skills.

## Success Criteria
- Running the skill on a person with reasonable source material produces a
  `~/.claude/skills/voice-<name>/SKILL.md` that another Claude with no access to that
  person's history could use to draft in their voice.
- The generated file follows a consistent structure: prose voice description · **Do**
  (traits, each with a real excerpt) · **Don't** (generic-AI tics *and* this person's
  specific non-traits, named concretely) · **Calibration** (how the voice flexes across
  contexts) · **Before/after** (2-3 default-AI passages rewritten in the person's voice).
- The evidence gate works: the skill shows 5-8 characteristic excerpts and does not write
  the final skill until the user confirms which sound right.
- Re-invoking on someone who already has a voice file improves the existing file rather than
  clobbering it.
- The skill is invocable as `/writing:voice-extractor` after `/plugin update`.

## Happy Path
1. User invokes the skill (e.g. "extract my voice" / `/writing:voice-extractor`).
2. Skill establishes whose voice and checks for an existing
   `~/.claude/skills/voice-<name>/SKILL.md` → new build or refine mode.
3. Gather: 8-10 past-chat searches across topics/time, plus any pasted samples, named
   files/folders, and URLs the user provides.
4. Sort real voice from chat-window artifact; note casual-vs-careful register, targeting the
   careful end.
5. Show 5-8 characteristic excerpts with what each demonstrates; **wait** for the user to
   confirm/reject.
6. Confirm the output path (default `~/.claude/skills/voice-<name>/SKILL.md`).
7. Write (or, in refine mode, update) the voice `SKILL.md` in the agreed structure.
8. Test-draft one short sample in the new voice so the user can sanity-check it; iterate if
   it's off.

## Edge Cases
- **Thin / unavailable input:** if "Search and reference past chats" is off or returns
  little, or the only material is clipped chat messages, the skill stops and asks the user to
  enable past chats and/or paste real human-directed prose — explaining that chat-only
  samples produce curt profiles. It does not silently proceed on weak input.
- **Flattery drift:** the skill self-checks that every "Do" trait cites a real excerpt and
  reads like the person rather than a sharper/more charming version; if the user says a line
  doesn't sound like them, it cuts and retries (2-3 rounds normal).
- **Evidence provenance in output:** the generated skill records how thin or rich its
  evidence was (e.g. "built from N chats + 2 samples — weight the careful register
  cautiously") so downstream use knows how much to trust it.
- **Unreachable sources:** URLs that fail to fetch or unparseable files are reported and
  skipped, not fatal.
- **Refine collision:** in refine mode, preserve confirmed traits from the prior file unless
  new evidence contradicts them; surface what changed.

## Audience
awilliamsbuilds (Adam) and anyone he shares the plugin with — technical users comfortable
with Claude Code skills. The *subject* of a voice profile can be any person with source
material.

## Technical Constraints
- SKILL.md with YAML frontmatter (`name`, `description`); `description` must be rich with
  trigger phrases (project convention — it drives skill invocation).
- Marketplace uses the `github` source type — do not change it. Register the new skill in
  `.claude-plugin/marketplace.json` (read for SHA first per repo convention).
- The generated output must be a valid personal skill: `~/.claude/skills/<name>/SKILL.md`
  with valid frontmatter, so Claude can invoke it directly.
- Tools the flow relies on: past-chat search, WebFetch (URLs), Read (files), Write (output).

## Dependencies
- "Search and reference past chats" enabled for the past-chats source.
- WebFetch available for URL sources; Read for file sources.
- Existing repo plugin wiring (`writing` plugin, `marketplace.json`) for registering the
  extractor skill itself.

## UI Needed
No. This is a skill (markdown instructions); no interface to design. Shape stage is skipped.

---
*Auto-filled dimensions: dependencies (inferred from source-type and tooling answers)*
