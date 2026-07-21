---
name: email
description: >
  Write or rewrite a personal email. Use this skill when the user wants to: write an email, draft an email, help me email someone, write a follow-up email, help me respond to this email, write a thank you email, write a difficult email, reconnect with someone over email, write an email to a friend, write an email to a colleague. Also trigger on: "how should I phrase this email", "write this email for me", "help me say this in an email", "rewrite this email", "make this email sound better".
  
  This skill is for personal email — reaching out to people you know, following up, making asks, navigating difficult conversations. Not for marketing emails, newsletters, or cold B2B outreach.
---

# Email

Write personal emails that sound like a person wrote them.

## Step 1 — Load email best-practices

Always load `../../references/channel-best-practices.md` and apply its **`## Email`** section —
regardless of which voice is resolved below. These govern subject line, structure, one-ask
discipline, length, and the avoid-list. A fresh installer with no voice still gets current
email best-practices from here.

## Step 2 — Voice context

> "Which voice should I write in?
> A) Your installed personal voice — I'll resolve and load it
> B) Your own voice — describe how you typically write, or share an example
> C) Start fresh — I'll keep it clean and direct"

**If A:** Resolve the voice by following `../../references/voice-resolution.md` (registered
pointer → installed `voice-*` convention → default). Load the resolved voice skill *at the
skill level* and apply it. If resolution yields no voice, fall through to a clean default —
never error, never assume a specific person's voice.

**If B:** Ask for one example of how they typically write. Calibrate to that.

**If C:** Write clean and direct — professional register, human voice, no filler.

---

## Step 3 — Relationship calibration

Ask if it's not clear from context:

> "Who is this to?
> A) Friend or family
> B) Acquaintance — you've met or interacted before
> C) Professional contact you know well
> D) Someone you're reaching out to for the first time"

This determines warmth, formality, and how much context-setting is appropriate. A email to a friend can skip the opener framing entirely. A first-contact email needs a one-line anchor ("We met at...") or a clear reason for the outreach.

---

## Step 4 — Email type

| Type | Notes |
|------|-------|
| **Making an ask or request** | State the ask clearly in the first paragraph. Don't bury it. Give them exactly what they need to say yes. |
| **Difficult or sensitive topic** | Lead with the relationship, not the issue. One paragraph per point. Don't hedge into mush. |
| **Thank you / appreciation** | Specific over general. Name what they did and why it mattered. One paragraph is usually enough. |
| **Reconnecting** | Acknowledge the gap naturally, don't over-apologize for it. Lead with the reason you're reaching out now. |
| **Sharing news or an update** | The news first, then the context. Don't make them read three paragraphs to find out what happened. |
| **Casual catch-up** | Short. No formal structure needed. Write like a person. |
| **Follow-up** | Reference the prior interaction specifically ("Following up on what we discussed Tuesday..."). One clear ask or next step. |

---

## Step 5 — Write

Order: apply the email best-practices (Step 1) and the resolved voice (Step 2) → draft →
humanize pass.

**Structure:**
- One paragraph per purpose — don't combine context, the ask, and a question into one block
- Open with the point or the relationship anchor, not a pleasantry
- Close simply — a clear next step or a plain sign-off. No "Please don't hesitate to reach out if you have any questions."

**Length:**
- Match the relationship. Friends get short emails. Professional contacts get concise ones. Nobody needs three paragraphs for a simple ask.
- If it's getting long, that's usually a sign the ask isn't clear yet.

**Humanize de-AI pass:** after drafting, run the draft through the `humanize` skill's Email
rules to strip AI tells (greeting/closing formulas, corporate filler, buried ask, over-length,
stacked sign-offs) before delivering. Apply `humanize` to the output — don't re-derive its
rules here.

---

## Step 6 — Output format

Deliver:
- **Full email** with subject line
- **2 subject line variants** — different angle or framing, labeled briefly
- **Optional PS line** if there's something that fits better outside the main flow

Then invite feedback.

---

## Hard rules

Never open with:
- "I hope this email finds you well"
- "Hope you're doing well" / "Hope all is well"
- "I wanted to reach out because..."
- "Just following up..."
- "I'm writing to..."
- "Please feel free to..."
- "Don't hesitate to contact me if..."

Keep first paragraphs to 3 sentences max. The longer the opener, the less likely it gets read.
