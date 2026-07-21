---
name: voice-extractor
description: |
  Extract how a specific person actually writes and turn it into a reusable, invocable
  per-person voice skill saved to ~/.claude/skills/voice-<name>/SKILL.md.

  Use when:
  - User says "extract my voice", "build a voice profile", "capture how I write",
    "clone my writing style", "turn my past chats into a voice"
  - User asks to "make a voice skill for <person>" or capture how someone else writes
  - User wants a repeatable, sharable skill that other writing work can adopt so drafts
    (cover letters, outreach, posts, emails) sound like a real person, not a template
  - User has accumulated more samples and wants to refine/sharpen an existing voice profile

  This skill BUILDS a voice skill through an interactive extraction flow (gather → sort
  signal from artifact → show evidence and wait for confirmation → write → test-draft).
  It is distinct from writing:voice (Adam's fixed personal voice, used to write in that
  one voice) and from writing:humanize (which strips generic-AI patterns from text).
  Reach for this when the goal is to CAPTURE a person's voice into a new reusable skill.
user-invocable: true
---

# Voice Extractor

Capture how one specific person actually writes and package it as a reusable **per-person
voice skill** — a `SKILL.md` written to `~/.claude/skills/voice-<name>/SKILL.md` that any
later Claude can invoke to draft in that person's voice. This skill packages a proven
extraction prompt into a repeatable, interactive flow and adds a refine loop so the profile
sharpens as more samples accumulate.

The flow runs in phases. Phases A–D gather and analyze evidence and end at a hard stop where
the user confirms which excerpts sound right. Only after confirmation do Phases E–G write and
test the output skill. Do not skip ahead — the evidence gate is non-negotiable.

## Phase A — Identify subject & mode

1. Establish **whose** voice this profiles. Default to the user ("my voice"); allow naming
   another person ("make a voice skill for Jordan"). The *subject* is whoever the source
   material belongs to — it need not be the user.
2. Derive a `<name>` slug: lowercase, kebab-case, from the subject's name or "me" if the user
   declines to name themselves (e.g. `adam`, `jordan-lee`, `me`).
3. **Check for an existing profile.** Use the Read tool on
   `~/.claude/skills/voice-<name>/SKILL.md`.
   - If it exists → this is a **refine/update** run. Announce that a profile already exists
     and that you'll improve it rather than overwrite it (Refine mode, Phase F/Refine below).
   - If it does not exist → this is a **new build**. Continue to Phase B.

## Phase B — Gather

Cast wide before analyzing anything. Pull from all four source types the subject can offer:

1. **Claude past chats (primary source).** Run **8–10 separate searches** across different
   topics and time periods — mix topic searches (work, technical, casual, frustrated,
   long explanations) with recent-conversation lookups. Use **only the subject's own
   messages**; ignore Claude's replies entirely when building the profile.
   - Past-chat search requires **"Search and reference past chats"** enabled (Settings →
     profile menu). If it's off, say so — you have nothing to analyze from this source.
2. **Pasted writing samples.** Real prose the subject wrote for other humans — cover
   letters, long emails, LinkedIn posts, a strong Slack message. **Weight these heavily**;
   a few pieces of real human-directed prose beat dozens of chat messages.
3. **Files / folders.** Local documents, exported posts, transcripts. Read them from disk
   with the Read tool when the user names a path.
4. **Public web / URLs.** The subject's published writing. Fetch with WebFetch.

Collect broadly from whatever sources are available before moving on.

## Phase C — Sort signal from artifact

Not everything you gather is voice. Explicitly separate the two:

- **Real voice — keep:** sentence rhythm and length; how they structure an argument;
  vocabulary level; whether they hedge or state flatly; how they use humor; analogies they
  reach for; how they open and close; words and constructions they repeat; how direct they
  are when they disagree.
- **Chat-window artifact — discard:** typos, dictation errors, dropped punctuation, extreme
  terseness, mid-sentence self-corrections, and the imperative "bossing Claude around" tone.
  People don't write to other humans that way.

**Note the register shift.** Compare how the subject writes casually versus when they're
careful or explaining themselves to someone without context. Most target writing (cover
letters, outreach) lives at the **careful** end. Describe the voice at that end
specifically — not an average of everything.

## Phase D — Evidence gate (STOP here)

Before writing anything, show the user **5–8 short, characteristic excerpts** drawn from the
**subject's own messages/samples**, each with a one-line note on what it demonstrates
(e.g. "opens mid-thought, no throat-clearing"; "hedges with 'I think' before a strong claim").

Then **STOP and wait.** Ask the user to tell you which excerpts actually sound like the
subject and which are you pattern-matching. **Do not write the output skill before the user
responds.** This gate is non-skippable — a confirmed excerpt set is the input to Phase F.
