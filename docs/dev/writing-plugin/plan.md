# Writing Plugin — Implementation Plan
*Branch: feature/writing-plugin · 2026-05-22*

## Files

| File | Action | Purpose |
|------|--------|---------|
| `plugins/humanize/` → `plugins/writing/` | Rename (git mv) | Preserve history while renaming plugin |
| `plugins/writing/.claude-plugin/plugin.json` | Modify | Update plugin name and description |
| `.claude-plugin/marketplace.json` | Modify | Update source path from `./plugins/humanize` to `./plugins/writing` |
| `README.md` | Modify | Update plugin table and all `humanize` plugin references |
| `CLAUDE.md` | Modify | Update Component Registry entries |
| `plugins/plugin-manager/skills/add-plugin/SKILL.md` | Modify | Update the "Existing Plugins" table inside the skill |
| `plugins/writing/skills/voice/SKILL.md` | Create | Adam's personal voice and tone reference |
| `plugins/writing/skills/web-copy/SKILL.md` | Create | Web copy writing skill |
| `plugins/writing/skills/linkedin/SKILL.md` | Create | LinkedIn post writing skill |
| `plugins/writing/skills/email/SKILL.md` | Create | Email writing skill |

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
2. Update `"description"` to reflect the full writing plugin scope: "Multi-context writing toolkit — humanize AI text, write in your voice, web copy, LinkedIn posts, and email"

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

*Tasks 2, 3, and 4 have no dependency on each other — only on Task 1. Can be done in sequence or parallel.*

---

### Task 5: Create voice SKILL.md
What: Scaffold the voice skill file; Adam fills in the personal voice content.
Used by: Invoked when user wants Claude to write in Adam's specific voice; referenced by web-copy, linkedin, email as an optional voice source.
Depends on: Task 1 (folder exists)
Files: `plugins/writing/skills/voice/SKILL.md` (create)

Implementation steps:
1. Create directory: `plugins/writing/skills/voice/`
2. Write SKILL.md with frontmatter: name `voice`, rich description triggering on "write in my voice", "use my voice", "sound like me", "personal voice", "my writing style"
3. In the skill body: leave a clearly marked placeholder section (`## Voice and Tone` with `<!-- ADAM: Fill in your voice and tone guidelines here -->`) for Adam to complete
4. Include skill structure: Purpose, Voice and Tone (placeholder), What This Is Not (not a general adapter — it's Adam's persona)
5. Adam completes the voice content before or during testing

---

### Task 6: Create web-copy SKILL.md
What: Full web copy writing skill that asks for voice context on invocation.
Used by: Invoked when user wants to write or edit website copy — landing pages, hero text, CTAs, about pages, product descriptions.
Depends on: Task 1 (folder exists)
Files: `plugins/writing/skills/web-copy/SKILL.md` (create)

Implementation steps:
1. Create directory: `plugins/writing/skills/web-copy/`
2. Write SKILL.md frontmatter: name `web-copy`, rich description triggering on "web copy", "landing page", "website copy", "hero text", "CTA", "about page", "homepage copy", "product description"
3. Skill body structure:
   - **Voice Context Step**: On invocation, always ask: "Which voice should I write in? (A) Your personal voice — I'll use the voice skill  (B) This project's voice — describe it or point me to context  (C) Start fresh — I'll ask as we go"
   - **Edge case**: If no voice context exists in the project, option B triggers a brief voice elicitation (3 questions: brand personality, audience, tone)
   - **Copy Types**: landing pages, hero/subhero, CTAs, about/team pages, product descriptions, nav copy — each with specific guidance
   - **Output format**: always present copy variants (2–3 options) for key elements; explain the reasoning behind each
   - **Iteration**: invite feedback and revise inline

---

### Task 7: Create linkedin SKILL.md
What: LinkedIn post writing skill that asks for voice context on invocation.
Used by: Invoked when user wants to write a LinkedIn post.
Depends on: Task 1 (folder exists)
Files: `plugins/writing/skills/linkedin/SKILL.md` (create)

Implementation steps:
1. Create directory: `plugins/writing/skills/linkedin/`
2. Write SKILL.md frontmatter: name `linkedin`, rich description triggering on "LinkedIn post", "LinkedIn update", "write for LinkedIn", "LinkedIn content"
3. Skill body structure:
   - **Voice Context Step**: same voice-choice prompt as web-copy (A/B/C)
   - **Post Types**: thought leadership, personal story, achievement/milestone, industry take, how-to — each with structural guidance
   - **LinkedIn-specific rules**: no AI-sounding openers ("In today's fast-paced world..."), no excessive line breaks for padding, no fake dialogue, authentic hooks only — pull these patterns from the humanize skill's known AI markers
   - **Output format**: full post with hook, body, CTA; offer 2 hook variants
   - **Length guidance**: 150–300 words for most posts; long-form 600–1200 for deep takes

---

### Task 8: Create email SKILL.md
What: Email writing skill that asks for voice context on invocation.
Used by: Invoked when user wants to write an email — cold outreach, follow-up, internal comms, newsletters.
Depends on: Task 1 (folder exists)
Files: `plugins/writing/skills/email/SKILL.md` (create)

Implementation steps:
1. Create directory: `plugins/writing/skills/email/`
2. Write SKILL.md frontmatter: name `email`, rich description triggering on "write an email", "email draft", "cold email", "follow-up email", "outreach email", "email copy"
3. Skill body structure:
   - **Voice Context Step**: same voice-choice prompt as web-copy (A/B/C)
   - **Email Types**: cold outreach, follow-up, internal update, newsletter, re-engagement — each with structural guidance
   - **Email-specific rules**: subject line always included and presented as variants (3 options); opening line must not be "I hope this email finds you well" or similar
   - **Output format**: subject variants, full email body, optional PS line
   - **Tone calibration**: ask for relationship context (stranger / warm lead / existing relationship / internal) to calibrate formality

*Tasks 5, 6, 7, 8 have no dependency on each other — only on Task 1. Can be done in any order.*

---

### Task 9: Test and tune all skills
What: Invoke each new skill with real content and refine SKILL.md based on output quality.
Used by: Validation against spec success criterion 5 — "skills produce quality output when tested with real content samples."
Depends on: Tasks 5–8 complete, Adam's voice content added to voice SKILL.md
Files: Any SKILL.md that needs tuning (modify)

Implementation steps:
1. Test `voice` skill: invoke it, verify it loads and presents Adam's voice reference correctly
2. Test `web-copy` skill: invoke with a real page type, verify voice prompt appears, verify output quality
3. Test `linkedin` skill: invoke with a real post topic, verify voice prompt appears, verify no AI-pattern openers
4. Test `email` skill: invoke with a real email scenario, verify voice prompt appears, verify subject variants appear
5. For each skill: note any gaps or awkward flows → edit SKILL.md inline → re-test
6. Commit tuning changes with message `build: tune <skill-name> SKILL.md`

## Edge Cases

| Edge case | Handled in | Approach |
|-----------|-----------|----------|
| Project has no voice context | Tasks 6, 7, 8 | Option C in voice prompt triggers inline voice elicitation (3 questions) |
| `voice` skill used outside Adam's projects | Task 5 | Skill body notes it's Adam's personal reference, not a generic adapter |
| `humanize` skill path breaks after rename | Task 1 | `git mv` preserves history; skill invocation key is skill name, not folder path |

## Out of Scope
- General "write this for me" skill
- Twitter/X, blog posts, or other formats
- Changes to `humanize` skill behavior
