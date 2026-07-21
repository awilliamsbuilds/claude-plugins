# Humanize Signal Refresh — Decision Log
*2026-07-21 · Branch: feature/humanize-signal-refresh · PR #36*

## What was built
Refreshed the `humanize` skill's pattern library with new AI-writing signal accumulated upstream in Wikipedia:Signs of AI writing since the last sync — most importantly the copy-paste markup artifacts that leak when text is pasted straight from a chatbot UI.

## Key decisions
- **Sync canonical files, not the runtime-local file** → Additions went into `plugins/writing/skills/humanize/references/ai-patterns.md` and `SKILL.md`, not `~/.claude/humanize/ai-patterns-local.md` (reserved by the auto-improvement loop for runtime-discovered patterns). This is a deliberate maintainer sync, so canonical is correct.
- **Copy-paste artifacts belong in the universal #20 Chatbot Artifacts section** → The leaked tokens are channel-agnostic (a Slack paste and a blog paste leak the same tokens), so they live in the universal section rather than any channel-specific block.
- **Additive vocab only, framed as a growing set** → New words (`meticulous`, `meticulously`, `bolstered`, `causal`, `empirical`, `correlate`) merged into #7 without removing any existing word; an era-awareness note frames the set as growing over time so older-era words keep being flagged.
- **`utm_source=` is a pasted-and-forgotten tell, not a blanket ban** → A deliberately built marketing link with `utm_source=` is legitimate; the rule targets the stray leftover, not tracking params outright. Same nuance for tables: flag only tables standing in for prose.
- **Append encyclopedic tells, never renumber** → #53 (title-as-proper-noun lead) and #54 (tables where prose belongs) were appended at the end with matching TOC lines, so no existing `#pattern-anchor` shifted.
- **Scoped out Wikipedia-editing-only tells** → wikitext markup, DOIs/ISBNs, named-refs, edit-summary tells, etc. don't apply to the channels the skill serves (blog, email, Slack, LinkedIn, marketing collateral).

## Validation notes
- 1 loop run (tier: standard). Code review and security review ran in parallel against the Build diff.
- No P1/P2/P3 found.
- Two nits found and both fixed in loop 1: aligned the #7 era-note word forms to the list (`highlight`/`showcase`); unbundled `utm_source=` from "remove on sight" in the SKILL.md quick-ref to preserve its nuance.
- Security review clean — added artifact tokens are inert detection targets, not live secrets or agent-steering directives.
- No regression: additive only, CC BY-SA 4.0 attribution intact, all three new TOC anchors resolve.

## Artifacts (archived)
Spec and plan committed at: e9677059e16e8765c5ba4567e6d116e06d982146 on branch feature/humanize-signal-refresh
