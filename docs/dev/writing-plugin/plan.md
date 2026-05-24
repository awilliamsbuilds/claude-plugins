# Writing Plugin — Implementation Plan
*Branch: feature/writing-plugin · 2026-05-22*

## Research Findings

Prior to building, we surveyed existing Claude Code writing plugins to avoid reinventing solved problems:

| Plugin | Key insight adopted |
|--------|-------------------|
| [great-web-copy](https://github.com/makash/great-web-copy) | 4 copywriting frameworks (PAS, AIDA, BAB, StoryBrand); always output 3 headline variants + 2 CTA variants; banned jargon list |
| [linkedin-skills](https://github.com/sergebulaev/linkedin-skills) | 2026 hook formula library (anaphora, R.I.P. obituary, curiosity gap, year-over-year pivot, etc.); built-in AI-pattern enforcement; length guidance |
| [marketingskills](https://github.com/coreyhaines31/marketingskills) | Skill dependency model: check voice/positioning context before writing anything |
| [ai-co-writing-claude-skills](https://github.com/az9713/ai-co-writing-claude-skills) | `voice-dna` structure for the voice skill: tone + signature phrases + things-never-said + audience context |

**What changed vs. original plan:** `voice` SKILL.md is now structured as a voice-dna document (not freeform). `web-copy` embeds framework selection. `linkedin` embeds the 2026 hook formula library. `email` uses B2B sequence model with subject variants.

---

## Files

| File | Action | Purpose |
|------|--------|---------|
| `plugins/humanize/` → `plugins/writing/` | Rename (git mv) | Preserve history while renaming plugin |
| `plugins/writing/.claude-plugin/plugin.json` | Modify | Update plugin name and description |
| `.claude-plugin/marketplace.json` | Modify | Update source path from `./plugins/humanize` to `./plugins/writing` |
| `README.md` | Modify | Update plugin table and all `humanize` plugin references |
| `CLAUDE.md` | Modify | Update Component Registry entries |
| `plugins/plugin-manager/skills/add-plugin/SKILL.md` | Modify | Update the "Existing Plugins" table inside the skill |
| `plugins/writing/skills/voice/SKILL.md` | Create | Adam's personal voice-dna reference |
| `plugins/writing/skills/web-copy/SKILL.md` | Create | Web copy writing skill with framework selection |
| `plugins/writing/skills/linkedin/SKILL.md` | Create | LinkedIn post writing with 2026 hook formulas |
| `plugins/writing/skills/email/SKILL.md` | Create | Email writing with sequence model and subject variants |

---

## Tasks

### Task 1: Rename plugin folder
What: Move `plugins/humanize/` to `plugins/writing/` using `git mv` to preserve history.
Used by: All subsequent tasks — this is the foundation.
Depends on: nothing — first task
Files: `plugins/humanize/` → `plugins/writing/` (rename)

Implementation steps:
1. `git mv plugins/humanize plugins/writing`
2. Verify the move: `ls plugins/writing/`
3. Confirm `plugins/writing/skills/humanize/SKILL.md` still exists and is unchanged

---

### Task 2: Update plugin.json
What: Update the plugin name and description inside the renamed folder.
Used by: Claude Code's plugin registry when loading the plugin.
Depends on: Task 1
Files: `plugins/writing/.claude-plugin/plugin.json` (modify)

Implementation steps:
1. Change `"name"` from `"humanize"` to `"writing"`
2. Update `"description"` to: "Multi-context writing toolkit — humanize AI text, write in your voice, web copy, LinkedIn posts, and email"

---

### Task 3: Update marketplace.json
What: Point the marketplace entry at `./plugins/writing` instead of `./plugins/humanize`.
Used by: Claude Code when resolving plugin sources.
Depends on: Task 1
Files: `.claude-plugin/marketplace.json` (modify)

Implementation steps:
1. Find the `humanize` entry in `plugins[]`
2. Change `"name"` to `"writing"`
3. Change `"description"` to match the updated plugin description
4. Change `"source"` from `"./plugins/humanize"` to `"./plugins/writing"`

---

### Task 4: Update reference files
What: Fix all remaining `humanize` plugin references in README.md, CLAUDE.md, and the add-plugin skill.
Used by: Documentation and the plugin-manager skill's self-knowledge.
Depends on: Task 1
Files: `README.md` (modify), `CLAUDE.md` (modify), `plugins/plugin-manager/skills/add-plugin/SKILL.md` (modify)

Implementation steps:
1. In `README.md`: update the plugins table row — change `humanize` to `writing`, update skills list to include all five skills, update description
2. In `CLAUDE.md` Component Registry: remove `humanize:humanize` row, add `writing:humanize`, `writing:voice`, `writing:web-copy`, `writing:linkedin`, `writing:email` rows with updated paths
3. In `add-plugin/SKILL.md`: find the "Existing Plugins" table and update the `humanize` row to `writing` with the full skill list

*Tasks 2, 3, and 4 have no dependency on each other — only on Task 1. Can be done in sequence.*

---

### Task 5: Create voice SKILL.md
What: Scaffold the voice skill as a voice-dna document; Adam fills in the personal content.
Used by: Invoked when user wants Claude to write in Adam's specific voice; referenced by web-copy, linkedin, email as an optional voice source.
Depends on: Task 1 (folder exists)
Files: `plugins/writing/skills/voice/SKILL.md` (create)

Implementation steps:
1. Create directory: `plugins/writing/skills/voice/`
2. Write SKILL.md with frontmatter: name `voice`, rich description triggering on "write in my voice", "use my voice", "sound like me", "personal voice", "my writing style", "voice and tone"
3. Structure skill body as a voice-dna document (borrowed from az9713 pattern) with these sections:
   - **Purpose**: Adam's personal voice reference — not a generic adapter
   - **Tone** `<!-- ADAM: e.g. direct, warm, no fluff -->` (placeholder)
   - **Signature phrases** `<!-- ADAM: phrases you use regularly -->` (placeholder)
   - **Things I never say** `<!-- ADAM: banned words/patterns — e.g. "leverage", "synergy" -->` (placeholder)
   - **Audience context** `<!-- ADAM: who you're usually writing for -->` (placeholder)
   - **Example writing** `<!-- ADAM: paste 2-3 samples of your best writing -->` (placeholder)
   - **What this is not**: clarify it's Adam's persona, not a project-voice adapter
4. Adam completes all placeholder sections before Task 9

---

### Task 6: Create web-copy SKILL.md
What: Web copy writing skill with framework selection, always outputs headline and CTA variants.
Used by: Invoked when user wants to write or edit website copy — landing pages, hero text, CTAs, about pages, product descriptions.
Depends on: Task 1 (folder exists)
Files: `plugins/writing/skills/web-copy/SKILL.md` (create)

Implementation steps:
1. Create directory: `plugins/writing/skills/web-copy/`
2. Write SKILL.md frontmatter: name `web-copy`, rich description triggering on "web copy", "landing page", "website copy", "hero text", "CTA", "about page", "homepage copy", "product description", "write copy for"
3. Skill body structure:
   - **Step 1 — Voice context** (borrowed from marketingskills dependency model): ask "Which voice? (A) My personal voice (voice skill)  (B) This project's voice — describe it or point me to context  (C) Start fresh — I'll ask as we go." If B and no context found, run 3-question voice elicitation (brand personality / audience / tone).
   - **Step 2 — Framework selection** (borrowed from great-web-copy): select from PAS / AIDA / BAB / StoryBrand based on page type and audience temperature. Show which framework was chosen and why.
   - **Copy types with guidance**: landing pages, hero/subhero, CTAs, about/team pages, product descriptions, nav copy
   - **Output format** (borrowed from great-web-copy): copy draft + 3 headline variants + 2 CTA variants + one-line rationale for each variant
   - **Banned patterns**: "innovative", "cutting-edge", "world-class", "leverage", "seamless", "game-changing" — replace with specifics
   - **Iteration**: invite feedback, revise inline

---

### Task 7: Create linkedin SKILL.md
What: LinkedIn post writing with 2026 hook formulas, AI-pattern enforcement, and voice context.
Used by: Invoked when user wants to write a LinkedIn post.
Depends on: Task 1 (folder exists)
Files: `plugins/writing/skills/linkedin/SKILL.md` (create)

Implementation steps:
1. Create directory: `plugins/writing/skills/linkedin/`
2. Write SKILL.md frontmatter: name `linkedin`, rich description triggering on "LinkedIn post", "LinkedIn update", "write for LinkedIn", "LinkedIn content", "post for LinkedIn"
3. Skill body structure:
   - **Step 1 — Voice context**: same A/B/C prompt as web-copy
   - **Step 2 — Post type**: thought leadership / personal story / achievement / industry take / how-to — user picks or Claude infers from topic
   - **Hook formula library** (borrowed from linkedin-skills 2026 formulas): anaphora, R.I.P. obituary format, year-over-year pivot, curiosity gap, contrarian take, "I was wrong about X" — present 2 hook options using different formulas
   - **AI-pattern enforcement** (synthesized from humanize skill's known markers): no "In today's fast-paced world", no em dashes for rhythm, no excessive single-line paragraphs for padding, no fake dialogue, no "Read that again." closers, no achievement post formula (context → struggle → result → lesson)
   - **Output format**: full post (hook + body + CTA) with 2 hook variants labeled by formula name
   - **Length guidance**: 150–300 words standard; 600–1200 for deep takes; always state word count

---

### Task 8: Create email SKILL.md
What: Email writing with sequence model, subject line variants, and relationship-context calibration.
Used by: Invoked when user wants to write an email — cold outreach, follow-up, internal comms, newsletters.
Depends on: Task 1 (folder exists)
Files: `plugins/writing/skills/email/SKILL.md` (create)

Implementation steps:
1. Create directory: `plugins/writing/skills/email/`
2. Write SKILL.md frontmatter: name `email`, rich description triggering on "write an email", "email draft", "cold email", "follow-up email", "outreach email", "email copy", "draft an email"
3. Skill body structure:
   - **Step 1 — Voice context**: same A/B/C prompt as web-copy
   - **Step 2 — Relationship calibration**: ask "Who is this to? (A) Stranger/cold  (B) Warm lead — we've interacted  (C) Existing relationship  (D) Internal/colleague" — adjusts formality and opener approach
   - **Email types with guidance** (borrowed from marketingskills cold-email model): cold outreach, follow-up, internal update, newsletter, re-engagement — each with structural template
   - **Hard rules**: subject line always required; output 3 subject variants; opening line must not be "I hope this email finds you well", "Hope you're doing well", or "I wanted to reach out"; no more than 3 sentences in first paragraph
   - **Output format**: 3 subject variants (with rationale) + full email body + optional PS line
   - **Iteration**: invite feedback, offer to adjust tone or length

*Tasks 5, 6, 7, 8 have no dependency on each other — only on Task 1. Can be done in any order.*

---

### Task 9: Test and tune all skills
What: Invoke each new skill with real content and refine SKILL.md based on output quality.
Used by: Validation against spec success criterion 5 — "skills produce quality output when tested with real content samples."
Depends on: Tasks 5–8 complete; Adam's voice-dna content added to voice SKILL.md
Files: Any SKILL.md that needs tuning (modify)

Implementation steps:
1. Adam completes voice SKILL.md placeholder sections before this task
2. Test `voice` skill: invoke it, verify it loads and presents the voice-dna correctly
3. Test `web-copy` skill: invoke with a real page type, verify framework selection appears, verify headline + CTA variants in output
4. Test `linkedin` skill: invoke with a real post topic, verify hook formula library is used, verify no AI-pattern openers in output
5. Test `email` skill: invoke with a real email scenario, verify relationship calibration prompt appears, verify 3 subject variants in output
6. For each skill: note gaps or awkward flows → edit SKILL.md inline → re-test
7. Commit tuning changes: `build: tune <skill-name> SKILL.md`

---

## Edge Cases

| Edge case | Handled in | Approach |
|-----------|-----------|----------|
| Project has no voice context | Tasks 6, 7, 8 | Option C in voice prompt triggers 3-question voice elicitation |
| `voice` skill used outside Adam's projects | Task 5 | Skill body notes it's Adam's personal reference, not a generic adapter |
| `humanize` skill path breaks after rename | Task 1 | `git mv` preserves history; skill invocation key is skill name, not folder path |

## Out of Scope
- General "write this for me" skill
- Twitter/X, blog posts, or other formats
- Changes to `humanize` skill behavior
