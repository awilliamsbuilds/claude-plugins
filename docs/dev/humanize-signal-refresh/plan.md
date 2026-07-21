# Humanize Signal Refresh — Implementation Plan
*Branch: feature/humanize-signal-refresh · 2026-07-21*

Docs-only change. Two markdown files, no code, no build step. Tasks 1–4 edit
`references/ai-patterns.md` in place; Task 5 folds the same tells into `SKILL.md`'s
quick-reference; Task 6 verifies TOC/anchor/numbering/attribution integrity.

Tasks 1–4 touch different regions of the same file and are logically independent, but
are sequenced 1→4 so Build makes clean, non-overlapping edits and Task 5 can consume the
final wording. Task 5 depends on 1–4 (it mirrors their exact token/word lists). Task 6
depends on everything.

## Files

| File | Action | Purpose |
|------|--------|---------|
| plugins/writing/skills/humanize/references/ai-patterns.md | Modify | Add copy-paste markup artifacts (#20), vocab + era note (#7), "X rather than Y" (#9), and two new encyclopedic-tell entries (#53, #54) with TOC lines |
| plugins/writing/skills/humanize/SKILL.md | Modify | Reflect the new tells in the Quick-Reference: Most Common Patterns table and vocab row |

## Tasks

### Task 1: Copy-paste markup artifacts → ai-patterns.md #20 Chatbot Artifacts
What: Document the render/citation tokens that leak when text is pasted from a chatbot UI, as the highest-confidence "remove on sight" tells, inside the existing Chatbot Artifacts pattern.
Used by: The phrase-level scan (SKILL.md Process step 3) when a user pastes chatbot-drafted text; Task 5 mirrors this token list into the SKILL.md quick-ref.
Depends on: nothing — first task.
Files: Modify `plugins/writing/skills/humanize/references/ai-patterns.md` (section `### 20. Chatbot Artifacts`, lines ~328–338).
Interfaces:
- Consumes: nothing.
- Produces: the canonical copy-paste-token list (exact strings below) that Task 5 reuses verbatim. Pattern #20's anchor `#20-chatbot-artifacts` and title are unchanged.

Implementation steps:
1. Under `### 20. Chatbot Artifacts`, keep the existing "I hope this helps" content. Add a new subsection labeled **"Copy-paste markup artifacts (highest confidence — remove on sight):"** listing the leaked tokens grouped by source:
   - ChatGPT: `oaicite`, `contentReference`, `oai_citation`, `turn0search0`, trailing `+1`
   - Gemini: `[cite: 1]`, `[span_1]`, `[start_span]`
   - Grok: `grok_card`, `grok_render_citation_card_json`
   - Perplexity: `ppl-ai-file-upload`, `attached_file`
   - Generic: `:::writing`; `utm_source=` / tracking params left in a pasted URL
2. Add one line stating these are channel-agnostic — a Slack paste and a blog paste leak the same tokens — so they live in this universal section, not any channel-specific block (edge case: artifact placement).
3. Add the `utm_source=` nuance explicitly: flag it as a *pasted-and-forgotten* tell, not a ban on tracking params — a deliberately-built marketing link with `utm_source=` is legitimate (edge case: false positives on legitimate use).
4. Add a short Before/After consistent with the surrounding entries, e.g. Before: a sentence ending in `oaicite:0` / `[cite: 3]`; After: the same sentence with the token stripped.

### Task 2: AI-vocab additions + era-awareness note → ai-patterns.md #7
What: Add the missing high-signal vocab words and a note that the AI-vocab set shifts over time, without removing any existing word.
Used by: The phrase-level scan; Task 5 mirrors the added words into the SKILL.md vocab row.
Depends on: Task 1 (same file, sequential).
Files: Modify `references/ai-patterns.md` (section `### 7. AI Vocabulary Words`, lines ~158–169).
Interfaces:
- Consumes: nothing.
- Produces: six added words (`meticulous`, `meticulously`, `bolstered`, `causal`, `empirical`, `correlate`) merged into the `**High-frequency AI words:**` list, plus an era-awareness note. Task 5 reuses these exact words.

Implementation steps:
1. Append to the existing `**High-frequency AI words:**` list (line 160), preserving every current word: `meticulous`, `meticulously`, `bolstered`, and the Grok pseudo-scientific cluster `causal`, `empirical`, `correlate`.
2. Add a one- to two-sentence **era-awareness note** after the word list (before or after the existing `**Problem:**` line) stating the set grows over time — older-era words still cluster in AI text, so they stay; current-era emphasis includes `emphasizing`, `enhance`, `highlighting`, `showcasing` (already listed), and the Grok `causal`/`empirical`/`correlate` cluster is a recent addition (edge case: additive vocab, not replacement — the note must NOT read as "stop flagging older words").
3. Do not touch the existing Before/After example.

### Task 3: "X rather than Y" reversed-emphasis parallelism → ai-patterns.md #9
What: Add the third negative-parallelism variant (reversed "rather than" emphasis) alongside the "not only…but also" and "not X, but Y" forms the pattern already covers.
Used by: The phrase-level scan; Task 5 mirrors it into the quick-ref AI-phrases row.
Depends on: Task 2 (same file, sequential).
Files: Modify `references/ai-patterns.md` (section `### 9. Negative Parallelisms and Tailing Negations`, lines ~186–201).
Interfaces:
- Consumes: nothing.
- Produces: a "X rather than Y" entry within #9. Pattern #9's anchor and title are unchanged.

Implementation steps:
1. Extend the `**Problem:**` line (or add a short labeled note under it) to name the reversed-emphasis variant: "X rather than Y" that elevates X by demoting Y (e.g. "prioritizing empirical consolidation rather than ideological purity").
2. Add a Before/After pair consistent with the existing ones in #9. Before: a sentence using "…rather than…" for manufactured emphasis; After: a direct declarative rewrite.
3. Keep the entry in #9 only (its natural home). Do not renumber or add a duplicate in #43.

### Task 4: Encyclopedic tells → new ai-patterns.md entries #53 & #54 + TOC
What: Add two new numbered patterns — title-as-proper-noun leads and tables-where-prose-belongs — as an appended "Encyclopedic Tells" section, with matching TOC lines, without renumbering anything.
Used by: The phrase-level / structural scan; Task 5 mirrors them into a quick-ref row.
Depends on: Task 3 (same file, sequential).
Files: Modify `references/ai-patterns.md` (Table of Contents, lines ~5–66; append new section after `### 52.`, line ~961).
Interfaces:
- Consumes: nothing.
- Produces: new anchors `#53-title-as-proper-noun-lead` and `#54-tables-where-prose-belongs`, plus a section anchor `#encyclopedic-tells`. Task 5 references these two pattern names; Task 6 verifies the anchors resolve.

Implementation steps:
1. Append at the very END of the file (after `### 52. Webpage and Sales Deck AI Patterns`) a new top-level section `## Encyclopedic Tells` containing two entries — appending, not inserting, so no existing anchor or number changes (edge case: anchor/TOC integrity):
   - `### 53. Title-as-Proper-Noun Lead` — Problem: AI opens a piece by defining the piece's own title as a standalone encyclopedia entity. Words to watch: `X refers to…`, `'[Title]' is a curated compilation/list of…`. Before/After: Before "Remote Onboarding refers to the process by which…"; After a direct opening that starts with the actual point.
   - `### 54. Tables Where Prose Belongs` — Problem: AI reaches for a table to present material that reads better as prose. Include the nuance: tables are fine when the data is genuinely tabular; flag only tables standing in for a paragraph or two of connected reasoning (edge case: false positives on legitimate use). Before: a 2-column table restating a simple comparison; After: one or two sentences.
2. In the Table of Contents, add a new group after the `- [Platform-Specific Patterns](#platform-specific-patterns)` block (i.e. after the `#52` line at ~line 66):
   ```
   - [Encyclopedic Tells](#encyclopedic-tells)
     - [53. Title-as-Proper-Noun Lead](#53-title-as-proper-noun-lead)
     - [54. Tables Where Prose Belongs](#54-tables-where-prose-belongs)
   ```
3. Match the GitHub-anchor convention used throughout (drop the number's period, lowercase, spaces→hyphens) so `### 53. Title-as-Proper-Noun Lead` resolves to `#53-title-as-proper-noun-lead`.

### Task 5: Reflect new tells in SKILL.md Quick-Reference
What: Fold the four groups' tells into `SKILL.md`'s "Quick-Reference: Most Common Patterns" table and vocab row so they surface without opening the reference file.
Used by: A user/agent scanning the quick-ref during a review before loading ai-patterns.md.
Depends on: Tasks 1–4 (mirrors their exact token/word lists and pattern names).
Files: Modify `plugins/writing/skills/humanize/SKILL.md` (Quick-Reference table, lines ~458–481).
Interfaces:
- Consumes: Task 1's copy-paste-token list, Task 2's six added vocab words, Task 3's "X rather than Y" phrasing, Task 4's two encyclopedic-tell names.
- Produces: updated quick-ref rows. Terminal for content; Task 6 verifies consistency.

Implementation steps:
1. **Vocab row** (line 460, `| AI vocabulary | delve, tapestry, …`): append `meticulous`, `bolstered`, `causal`, `empirical`, `correlate` (keep every existing word).
2. **Add a new row** for the copy-paste artifacts, e.g. `| Chatbot paste artifacts | oaicite, contentReference, oai_citation, turn0search0, [cite: N], [span_N], grok_card, ppl-ai-file-upload, :::writing, stray utm_source= in a pasted URL — remove on sight |`.
3. **AI phrases row** (line 476): add `"X rather than Y"` alongside the existing `"not only...but also"`.
4. **Add a new row** for encyclopedic tells, e.g. `| Encyclopedic tells | title-as-proper-noun lead ("X refers to…"); a table used where prose belongs |`.
5. Leave the era-awareness note out of the compressed quick-ref (it lives in #7); the quick-ref carries only the words.

### Task 6: Integrity verification
What: Confirm no regression — TOC anchors resolve, numbering/existing anchors are untouched, and the CC BY-SA 4.0 attribution is still accurate in both files.
Used by: Final gate before Build is considered done.
Depends on: Tasks 1–5.
Files: Read-only verification of both edited files.
Interfaces:
- Consumes: the new anchors from Task 4 and the edits from Tasks 1–5.
- Produces: nothing — terminal task.

Implementation steps:
1. Confirm the two new TOC lines point at the exact anchors the `### 53.`/`### 54.` headings generate; confirm no existing TOC entry or `#pattern-anchor` was renumbered or moved.
2. Confirm `SKILL.md` frontmatter `license:` line (line 9) and `ai-patterns.md` line 3 still read as Wikipedia-derived / CC BY-SA 4.0 — unchanged and still accurate.
3. Confirm no existing vocab word, pattern, or example was removed (all additions are additive).

## Edge Cases
| Edge case | Handled in | Approach |
|-----------|-----------|----------|
| Additive vocab, not replacement | Task 2 | Era note frames the set as *growing*; older-era words kept and still flagged |
| Artifact placement (channel-agnostic) | Task 1 | Tokens go in universal #20 Chatbot Artifacts, not any channel block |
| False positives — `utm_source=` | Task 1 | Flag as *pasted-and-forgotten*, not a ban on tracking params |
| False positives — tables | Task 4 | Flag only tables standing in for prose; genuine tabular data is fine |
| Anchor/TOC integrity | Task 4 + Task 6 | Append #53/#54 at end (no renumber); Task 6 verifies anchors resolve |

## Out of Scope
- Signs-of-human-writing calibration note (decided out in spec).
- Wikipedia-editing-only tells (wikitext markup, DOIs/ISBNs, named-refs, edit-summary tells, etc.) — none apply to the skill's channels.
- Any change to the auto-improvement loop, scoring rubric, channel auto-detection, or voice calibration.
- Writing to `~/.claude/humanize/ai-patterns-local.md` — additions are a deliberate maintainer sync to the **canonical** files only.
- Rewriting or reorganizing existing patterns beyond slotting the additions in.
