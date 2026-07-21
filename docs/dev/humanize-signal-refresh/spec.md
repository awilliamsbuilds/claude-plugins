# Humanize Signal Refresh
*Branch: feature/humanize-signal-refresh · Confidence: 90% — Ready · 2026-07-21*
*Cycle type: feature · Tier: standard*

## Intent
The `humanize` skill's pattern library is derived from [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing). That article has grown new signal since the skill was last synced. Fold the in-scope deltas back in so the skill keeps catching current AI tells — most importantly the copy-paste markup artifacts that are near-certain "pasted straight from a chatbot" giveaways and aren't covered at all today.

## Scope
Four groups of additions, all confirmed absent from the current skill by grounding this stage:

1. **LLM copy-paste markup artifacts** — the render/citation tokens that leak when text is pasted from a chatbot UI: `oaicite`, `contentReference`, `oai_citation`, `turn0search0`, `+1` (ChatGPT); `[cite: 1]`, `[span_1]`, `[start_span]` (Gemini); `grok_card`, `grok_render_citation_card_json` (Grok); `ppl-ai-file-upload`, `attached_file` (Perplexity); `:::writing`; and `utm_source=` / tracking params left in pasted URLs. These are the highest-confidence tells in the whole library — treat as "remove on sight."
2. **AI-vocab additions + era-awareness** — add missing high-signal words (`meticulous`/`meticulously`, `bolstered`) and Grok's pseudo-scientific cluster (`causal`, `empirical`, `correlate`); add a short note that the AI-vocab set shifts over time (current-era emphasis: `emphasizing`, `enhance`, `highlighting`, `showcasing`) so the list reads as evolving rather than fixed. **Additive only** — no existing words are removed.
3. **"X rather than Y" reversed-emphasis parallelism** — a third negative-parallelism variant beyond the "not only…but also" and "not X, but Y" the skill already covers (e.g. "prioritizing empirical consolidation rather than ideological purity").
4. **Encyclopedic tells** — (a) title-as-proper-noun leads that define the piece's own title as a standalone entity ("X refers to…", "'List of…' is a curated compilation"); (b) tables used where prose belongs.

## Out of Scope
- **Signs-of-human-writing calibration note** (age-of-text, ability to explain editorial choices, idiosyncratic human syntax) — decided out; the skill flags AI patterns, and negative calibration indicators are a different concern.
- **Wikipedia-editing-only tells** — wikitext-vs-markdown markup, broken/invalid DOIs & ISBNs, page-number-less book citations, named-refs-declared-but-unused, edit-summary tells ("preserved/retained", "adherence to policies"), non-existent categories/templates, AfC submission statements, pre-placed maintenance templates, skipping heading levels, thematic breaks before headings. None of these apply to the channels the skill serves (blog, email, Slack, LinkedIn, marketing collateral).
- Any change to the auto-improvement loop, scoring rubric, channel auto-detection, or voice calibration.
- Rewriting or reorganizing existing patterns beyond what's needed to slot the additions in.

## Success Criteria
- `references/ai-patterns.md` documents all four in-scope groups, each with the reference's before/after (or watch-list) format consistent with the surrounding entries.
- The copy-paste markup artifacts are added to the **Chatbot Artifacts** area (pattern #20) — the natural home for "pasted from a chatbot" tells — flagged as remove-on-sight / highest-confidence.
- New vocab words are merged into the existing AI-vocabulary lists (SKILL.md quick-ref + ai-patterns.md #7) without dropping any current word; the era-awareness note is present.
- "X rather than Y" is added to the negative-parallelism coverage (#9 and/or #43).
- Encyclopedic tells are documented (title-as-proper-noun lead; prose-over-tables).
- SKILL.md's **Quick-Reference: Most Common Patterns** table reflects the new tells so they surface without opening the reference file.
- The skill's license/attribution line remains accurate (still Wikipedia-derived, CC BY-SA 4.0).
- No regression: existing pattern numbering/anchors and the table of contents stay internally consistent after edits.

## Happy Path
1. A user pastes text drafted in ChatGPT/Gemini/Grok/Perplexity — leftover `oaicite`/`[cite: 1]`/`utm_source=` tokens ride along — and runs `/humanize`.
2. The skill loads the refreshed `references/ai-patterns.md`.
3. The phrase-level scan flags the markup artifacts as highest-confidence tells, catches the newly-added vocab (`meticulous`, `bolstered`, etc.), the "X rather than Y" parallelism, and any title-as-proper-noun lead.
4. The review report lists them; the rewrite strips them.

## Edge Cases
- **Additive vocab, not replacement:** era-awareness must not read as "stop flagging older words" — older-era words still cluster in AI text. Keep them; frame the note as "the set grows."
- **Artifact placement:** the copy-paste tokens are channel-agnostic (a Slack paste and a blog paste leak the same tokens), so they belong in the universal Chatbot Artifacts section, not any channel-specific block.
- **False positives on legitimate use:** `utm_source=` can be intentional in a real marketing link; the rule should target it as a *pasted-and-forgotten* tell, not ban tracking params outright. Same nuance for tables — tables are fine when the data is genuinely tabular; flag only tables standing in for prose.
- **Anchor/TOC integrity:** inserting entries must not orphan existing `#pattern-anchor` links referenced elsewhere in the skill.

## Audience
Anyone drafting prose (blogs, emails, Slack, LinkedIn, marketing collateral) who runs `/humanize`; and maintainers of this plugin repo. (From skill frontmatter + repo CLAUDE.md.)

## Technical Constraints
- Additions go in the **canonical** `plugins/writing/skills/humanize/references/ai-patterns.md` and `SKILL.md` — **not** `~/.claude/humanize/ai-patterns-local.md`, which the auto-improvement loop reserves for runtime-discovered patterns. This is a deliberate maintainer sync, so canonical is correct.
- Markdown-only changes; no code, no build step. Two files touched (`SKILL.md`, `references/ai-patterns.md`).
- Preserve the existing document structure, numbering scheme, and the CC BY-SA 4.0 attribution.

## Dependencies
None. Self-contained edits to two markdown files.

## UI Needed
No. (Shape stage skipped.)

---
*Auto-filled dimensions: none — scope confirmed by user; success/happy-path/edge-cases derived from the grounding inventory below.*
*Grounding inventory (checked this stage against the live files, not memory): read `plugins/writing/skills/humanize/SKILL.md` and `references/ai-patterns.md` in full and diffed against a fresh fetch of the Wikipedia article. Verified absent: (a) copy-paste markup tokens — pattern #20 Chatbot Artifacts covers "I hope this helps" phrasing only, no citation/render tokens; (b) `meticulous`/`bolstered`/`causal`/`empirical`/`correlate` — not in the #7 or SKILL.md vocab lists; (c) "X rather than Y" — patterns #9 and #43 cover "not only…but"/"not X but Y"/"It's not X. It's Y." but not the reversed "rather than" form; (d) title-as-proper-noun lead and prose-over-tables — no matching entry. Canonical-vs-local file convention verified from SKILL.md Auto-Improvement Loop (writes local) vs. Process step 1 (loads canonical).*
