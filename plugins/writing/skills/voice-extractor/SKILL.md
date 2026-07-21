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

## Phase E — Confirm output path

Default output path: **`~/.claude/skills/voice-<name>/SKILL.md`** — a personal skill,
invocable anywhere, untouched by plugin updates. State the path and confirm it with the user
before any write. Only write once the path is agreed.

## Phase F — Write the generated voice skill

Write the output file at the confirmed path, using only the **confirmed** excerpt set from
Phase D. The generated file must follow this exact structure:

1. **YAML frontmatter** — `name: voice-<name>` and a rich `description` (with trigger phrases
   like "write in <name>'s voice", "draft this as <name>") so it's an invocable personal
   skill. Include `user-invocable: true`.
2. **Prose voice description** — how you'd describe the subject's writing to another writer,
   in a short paragraph.
3. **Do:** specific, actionable traits — **each with a real excerpt** from the subject's own
   messages/samples. No trait without an example.
4. **Don't:** the generic-AI tics that make writing obvious *and* this person's specific
   non-traits, named concretely (actual phrases and constructions to avoid — not vague
   categories).
5. **Calibration:** how the voice flexes across contexts (e.g. cover letter vs. recruiter
   email vs. LinkedIn message; careful vs. casual register).
6. **Before/after:** 2–3 short passages in default AI-assistant voice, each rewritten in the
   subject's voice, so the difference is visible rather than described.
7. **Evidence-provenance note:** record how thin or rich the evidence was, e.g. "Built from
   9 chats + 2 writing samples — weight the careful register cautiously." This tells
   downstream use how much to trust the profile.

**The output must be self-sufficient.** Another Claude with no access to the subject's
history must be able to draft from it: every "Do" trait carries a concrete example, and vague
guidance like "conversational but professional" is banned.

## Phase G — Test-draft & iterate

After writing, draft **one short sample** in the new voice (ask the user for a quick scenario,
e.g. a cover letter for a role they describe) so they can sanity-check it. If it reads off,
cut and retry — 2–3 rounds is normal. Don't defend a draft the subject says isn't them.

## Refine / update mode

Entered from Phase A when `~/.claude/skills/voice-<name>/SKILL.md` already exists. Instead of
rebuilding from scratch:

1. Read the existing file. Gather the **new** samples/chats the user is adding (Phases B–C
   still apply to the new material).
2. Fold new evidence into the existing **Do / Don't / Calibration** sections; revise the
   **evidence-provenance note** to reflect the larger sample.
3. **Preserve confirmed traits** from the prior file unless new evidence contradicts them.
   Never overwrite the file wholesale.
4. **Surface what changed** — tell the user which traits were added, sharpened, or removed
   and why, so they can veto.
5. Run the Phase D evidence gate on materially new or changed traits, then Phase G test-draft.

## Edge cases

- **Thin / unavailable input.** If "Search and reference past chats" is off or returns
  little, or the only material is clipped chat messages, **stop and ask** the user to enable
  past chats and/or paste real human-directed prose. Explain that chat-only samples read
  curt — a profile built on them produces terse, throat-clearing-free drafts that misfire in
  careful contexts. **Do not silently proceed** on weak input.
- **Flattery drift.** The most common failure is describing a writer sharper and more
  charming than the person actually is. Self-check that every "Do" trait cites a real excerpt
  and reads like the subject, not a charmier version of them. If the user says a line doesn't
  sound like them, cut it and retry (2–3 rounds normal).
- **Unreachable sources.** URLs that fail to fetch and files the Read tool can't parse are
  **reported and skipped** — non-fatal. Continue with the remaining sources and note in the
  provenance line what couldn't be reached.

## Final self-check

Before declaring done, confirm the output is a **valid personal skill** at
`~/.claude/skills/voice-<name>/SKILL.md`: valid YAML frontmatter (`name`, `description`,
`user-invocable: true`), every "Do" trait backed by a real excerpt, and the
evidence-provenance note present.
