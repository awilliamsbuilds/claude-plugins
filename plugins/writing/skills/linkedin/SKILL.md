---
name: linkedin
description: >
  Write or rewrite LinkedIn content — a feed post, a long-form article, or a 1:1 message / connection note / InMail. Use this skill when the user wants to: write a LinkedIn post, draft a LinkedIn update, write a LinkedIn article, write a LinkedIn message or DM, write a connection request note, write an InMail, announce something on LinkedIn, share a win on LinkedIn, write a thought leadership post, write a personal story for LinkedIn. Also trigger on: "help me post this on LinkedIn", "write this as a LinkedIn post", "turn this into a LinkedIn post", "make this LinkedIn-ready", "write my LinkedIn announcement", "reach out to someone on LinkedIn", "write a LinkedIn article".
---

# LinkedIn

Write LinkedIn content in the right voice and the right format — structured, direct, one idea
developed fully.

## Step 1 — Voice context

> "Which voice should I write in?
> A) Your installed personal voice — I'll resolve and load it
> B) This project/company's voice — describe it or point me to context
> C) Start fresh — tell me about the voice and audience"

**If A:** Resolve the voice by following `../../references/voice-resolution.md` (registered
pointer → installed `voice-*` convention → default). Load the resolved voice skill *at the
skill level* and apply it. If resolution yields no voice, fall through to a clean default —
never error, never assume a specific person's voice.

**If B or C:** Establish tone (opinionated/neutral, personal/brand, formal/casual) and
audience before proceeding.

---

## Step 2 — Format gate

Ask up front which format this is — the answer routes the rest of the flow. Load the matching
section of `../../references/channel-best-practices.md` and apply it.

| Format | What it is | Route |
|--------|-----------|-------|
| **Message** | A 1:1 DM, InMail, or connection note — private, person-to-person | Load `## LinkedIn — Message`. **Skip Steps 3–4 (post type and hook) entirely.** Go to Step 5. |
| **Post** | A native feed post — public, hook-driven, one idea | Load `## LinkedIn — Post`. Continue with Steps 3–4. |
| **Article** | A long-form native article — titled, sectioned, evergreen | Load `## LinkedIn — Article`. **Skip Steps 3–4 (no feed-post hook mechanics).** Go to Step 5. |

**Message path (guard):** a message must NOT use feed-post hook mechanics, curiosity gaps, or
engagement bait ("Thoughts?", "Agree?"), and no hashtags. The recipient already opened it —
there's nothing to hook. Keep it short and purposeful: one clear reason for reaching out.

**Article path:** open by earning the read through substance, not a scroll-stop hook. Give it
a real title and subheads; frame it to hold up over time.

---

## Step 3 — Post type *(Post format only)*

Identify or ask which type this is:

| Type | What it is |
|------|-----------|
| **Thought leadership** | A position on something in your field. Built around one contrarian or non-obvious claim. |
| **Personal story** | Something that happened. Leads with the moment, not the lesson. |
| **Achievement / milestone** | Announcing something real. Opens with the announcement, not "I'm excited to share..." |
| **How-to / instructional** | Step-by-step or lesson-based. Label takeaways explicitly. |
| **Industry take** | Reaction to something happening in the space. Names the thing, takes a position. |

---

## Step 4 — Hook *(Post format only)*

The first line is everything. It must stop the scroll.

Choose from these proven structures — offer 2 options using different formulas:

| Formula | Structure | Example |
|---------|-----------|---------|
| **Opens with the point** | State your claim. Full stop. | "Most product managers ship the wrong thing." |
| **Curiosity gap** | Imply something surprising without giving it away | "I made a decision last year that I thought would hurt us. It didn't." |
| **Contrarian** | Name the accepted view and reject it in one beat | "Everyone says hire for culture fit. I stopped doing that." |
| **Year-over-year pivot** | Sharp before/after with a time anchor | "A year ago I would have disagreed with this completely." |
| **The admission** | Open with a specific honest confession | "I was wrong about this for most of my career." |
| **The one-thing** | Name the single hinge everything turns on | "The word that was killing our apologies: 'if.'" |

---

## Step 5 — Body and close

**Post — body:**
- One idea, developed through a specific story, example, or observation
- Personal experience over vague generalities
- Paragraphs vary in length — some one sentence, some three
- Short standalone sentence for emphasis, used at most once

**Post — close:**
- A principle, question, or challenge — never a summary of what was just written
- If instructional: label the takeaway ("Take-away:" or "Lesson:")
- Do not end with "Follow me for more" or "What do you think?" as the whole close

**Post — length:** 300–700 words for most posts. Long-form (600–1200) only if the idea
genuinely requires it.

**Article — body:** a real title, then a few titled sections that each carry one part of the
argument. Develop the idea fully; vary paragraph length; use firsthand experience and named
sources. Close on a principle or a forward-looking point, not a summary.

**Message — body:** short and purposeful. Lead with the reason for reaching out and what
you're asking for. Match register to the relationship. No hook mechanics, no engagement bait,
no hashtags.

**Humanize de-AI pass (all formats):** after drafting, run the draft through the `humanize`
skill's LinkedIn rules to strip AI tells (one-line-per-paragraph formatting, engagement bait
closers, arrow chains, ALL-CAPS emphasis, "Read that again." padding) before delivering. Apply
`humanize` to the output — don't re-derive its rules here. Order: best-practices + resolved
voice → draft → humanize pass.

---

## Step 6 — Output format

**Post:**
- **Full post** with the chosen hook, body, and close
- **2 hook variants** using different formulas, labeled by name
- **One-line note** on the structural choice made

**Article:**
- **Full article** with title, subheads, and sections
- **1 alternate title** and a one-line note on the framing

**Message:**
- **The message**, tight and ready to send
- **1 alternate opening line** if it helps

Then invite feedback.

---

## Hard rules

Never:
- Open with "I'm excited to share," "Thrilled to announce," "Humbled to..."
- Open with a rhetorical question ("Have you ever wondered...")
- Use "In today's fast-paced world" or any variant
- Em dashes — use periods or colons instead
- Stacked fragment punchlines ("Fast. Simple. Effective.")
- Hashtags as content (fine at the end of a post if needed, not in the writing; never in a message)
- Emoji in the body of professional posts
- Summarize at the end — the close should land something new, not restate what was said
- "Read that again." / "Let that sink in." / "And honestly?" as rhetorical padding
- The achievement post formula: context → struggle → result → lesson (it's overused and reads as AI)
- Feed-post hook mechanics or engagement bait in a **message** — it's a private note, not a broadcast
