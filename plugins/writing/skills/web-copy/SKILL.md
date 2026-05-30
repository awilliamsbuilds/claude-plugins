---
name: web-copy
description: >
  Write or rewrite website copy — landing pages, hero sections, CTAs, about pages, product descriptions, nav copy, pricing pages. Use this skill when the user wants to: write web copy, write a landing page, write homepage copy, write a hero section, write a CTA, write an about page, write product copy, write website content, improve a landing page, audit copy for a website, write copy for a SaaS product. Also trigger on: "write the copy for", "rewrite this page", "make this landing page better", "write our about page", "what should the hero say".
---

# Web Copy

Write high-converting website copy, grounded in proven frameworks and adapted to the right voice.

## Step 1 — Voice context

Before writing anything, ask:

> "Which voice should I write in?
> A) Adam's personal voice — I'll load your voice profile
> B) This project's voice — describe it or point me to context in this repo
> C) Start fresh — I'll ask a few quick questions"

**If A:** Load `../voice/references/voice-profile.md`. Web copy in Adam's voice should be direct, specific, and devoid of marketing clichés. Apply the vocabulary avoidance list from the voice profile to all copy.

**If B:** Ask for the brand's personality in one sentence, their audience, and their tone (e.g. "technical and dry", "warm and conversational", "bold and punchy"). If a brand doc, CLAUDE.md, or style guide exists in the project, read it first.

**If C:** Ask:
1. What does this product/company do? (one sentence)
2. Who is the primary audience?
3. What's the tone — formal, casual, bold, warm, technical?

---

## Step 2 — Framework selection

Choose the copywriting framework based on page type and audience temperature. State which one you're using and why.

| Framework | When to use |
|-----------|------------|
| **PAS** (Problem → Agitation → Solution) | Cold audiences who don't know the product yet; pain-first messaging |
| **AIDA** (Attention → Interest → Desire → Action) | Broad reach; brand-awareness pages; general landing pages |
| **BAB** (Before → After → Bridge) | Transformation narratives; the reader is aware of their pain and open to change |
| **StoryBrand** | Full brand messaging; homepage overhauls; when the product needs a clear hero/villain/guide structure |

For shorter elements (single CTAs, nav copy, microcopy): skip framework selection and apply the voice directly.

---

## Step 3 — Write

**Landing pages and hero sections:**
- Headline: the single most important job. Lead with the outcome or the problem — not the product name or a clever pun.
- Subheadline: one sentence that earns the headline; adds specificity.
- CTA: action verb + specific outcome. Not "Get Started" — "Start your free audit" or "See it in 60 seconds."
- No: "innovative," "cutting-edge," "world-class," "game-changing," "seamless," "robust," "leverage," "streamline," "holistic," "best-in-class," "next-level."

**About pages:**
- Start with what the company does or believes — not when it was founded.
- One moment of honesty or vulnerability earns more trust than three paragraphs of accomplishments.

**Product descriptions:**
- Lead with the outcome the user gets, not the feature that produces it.
- Features belong below the fold; benefits belong above.

**CTAs:**
- Always action verbs. Always specific. If the action has a concrete outcome, name it.

---

## Step 4 — Output format

Always deliver:
- **Copy draft** — full section or page as requested
- **3 headline variants** — different angles, labeled (e.g. "Outcome-led," "Problem-led," "Contrarian")
- **2 CTA variants** — different action + outcome combinations
- **One-line rationale** for each variant explaining the approach

Then invite feedback: "Which direction feels closest? I can push any of these further or try a different angle."

---

## Hard rules

Never write:
- Vague benefit statements ("We help teams work better together" — says nothing)
- Features as benefits ("Our platform has 200+ integrations" → "Connect the tools you already use — no manual exports")
- Performative urgency ("Act now!" / "Don't miss out!")
- Passive voice for key claims
- More than one exclamation point per page
