---
name: voice
description: |
  Adam Williams's personal writing voice. Use this skill to write or rewrite
  content in Adam's voice — or load it as a reference to calibrate tone and style.
  
  Use when:
  - User asks to write something "in my voice", "for me", or "as me"
  - User asks to rewrite, clean up, or polish something they wrote
  - User is drafting a Slack message, LinkedIn post, blog post, executive update, or external email
  - Any skill generating first-person content from Adam (not TRM the company) should load this
  - Combined with /humanize: apply humanize first to strip AI patterns, then apply this voice
  
  This is Adam's personal voice for human-facing writing, not TRM's brand voice.
  For TRM company voice, use the trm-brand-voice skill instead.
user-invocable: true
---

# Voice: Adam Williams

Write or rewrite content in Adam's voice. Load [references/voice-profile.md](references/voice-profile.md) for the full voice analysis and [references/platform-guide.md](references/platform-guide.md) for platform-specific rules.

## How to use this skill

**Active rewrite:** User pastes draft → load both reference files → rewrite in Adam's voice → note key changes made.

**New draft:** User describes what they want to say → load both reference files → draft from scratch → confirm it lands.

**As a reference:** Other skills load `references/voice-profile.md` to calibrate tone without invoking the full skill.

## Process

1. Load [references/voice-profile.md](references/voice-profile.md)
2. Load [references/platform-guide.md](references/platform-guide.md) — check which platform applies
3. If editing existing text: identify what's off (too formal, sycophantic, padded, AI-textured, wrong structure)
4. Rewrite or draft, following the platform guide and voice profile
5. Never add ideas that weren't in the original — preserve substance, change only delivery
6. If a concrete example or specific detail is missing and needed, insert `[ADD SPECIFIC EXAMPLE]` — do not invent
7. Present the rewrite with a one-line note on the main changes made

## Quick rules

- Open with the point. Never with context-setting or "In today's..."
- One idea, fully developed. Don't pile on.
- Short standalone sentences for emphasis. Used deliberately, not constantly.
- End with a principle, question, or challenge — never a summary.
- Specific over general. "The company I work for had been understaffed" not "organizations often struggle."
- Honest first-person when appropriate. "I nearly cried." "I couldn't sleep."
- Qualifies when genuinely uncertain. Never hedges to avoid taking a position.
- Never: signposting, sycophancy, summary conclusions, stacked fragment punchlines, AI vocabulary.
