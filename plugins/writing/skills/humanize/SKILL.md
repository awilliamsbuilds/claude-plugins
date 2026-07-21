---
name: humanize
description: |
  Remove signs of AI-generated writing and make text sound natural and human.
  Auto-detects content type (Blog, LinkedIn, Email, Slack, Marketing Collateral) and applies channel-specific rules.
  Use when the user asks to humanize, de-AI, or edit text to remove AI writing patterns, or asks to score / review / check text for AI tells.
  **Audience:** For anyone drafting prose — blogs, emails, Slack posts, LinkedIn posts.
user-invocable: true
license: "Based on Wikipedia:Signs_of_AI_writing (CC BY-SA 4.0). Adapted from blader/humanizer (MIT) and blog-post-humanizer."
---

# Humanize: Remove AI Writing Patterns

Edit text to remove signs of AI generation and make it sound like a real person wrote it.

## Process

0. **Auto-detect content type** — classify as Blog, LinkedIn, Email, Slack, or Marketing Collateral (see Auto-Detect section below); state the detected type at the top of your review before continuing
1. Load [references/ai-patterns.md](references/ai-patterns.md) (canonical patterns). Also check for `~/.claude/humanize/ai-patterns-local.md` — if it exists, read it too and apply those patterns alongside the canonical ones
2. Calibrate voice (see below) — ask for a writing sample if none was provided
3. **Phrase-level scan** — flag every AI vocabulary word, filler phrase, and pattern instance; apply universal markers plus channel-specific markers for the detected type
4. **Structural scan** — flag structural AI tells: paragraph rhythm monotony, stacked fragment punchlines, generic opening/closing, intro→list→conclusion template, runway sentences
5. **Originality check** — flag advice anyone could write, recycled framing, no firsthand evidence, "the future of X is Y" claims
6. **Hook vs. Value Calibration** — for LinkedIn only (see section below)
7. **Score the post** using channel-specific dimensions (see scoring rubric below)
8. Produce a **structured review report** (see output format below)
9. **Rewrite** following the rewrite rules below
10. **Auto-improvement loop** — check for new patterns and update the skill (see below)

---

## Auto-Detect Content Type

Before running the review, classify the content. State the detected type at the top of your review.

**Email** — Detect if the content has ANY of:
- A subject line, "To:", "From:", or "CC:" headers
- A greeting formula ("Hi [Name]", "Hey [Name]", "Dear [Name]")
- A formal sign-off ("Best", "Regards", "Thanks", "Cheers", followed by a name)
- "I wanted to reach out", "Following up on", "Per our conversation"
- Explicit ask + sign-off structure

**LinkedIn** — Detect if the content has ANY of:
- One-sentence-per-line paragraph formatting throughout
- Hashtags (#marketing, #leadership, etc.)
- Engagement CTA at the end ("Thoughts?", "Agree?", "What would you add?")
- @mentions of people or companies
- Under 3,000 characters with no headings/subheadings
- Emoji used as section markers or attention breaks
- LinkedIn-style story hook opening (vulnerability bait, credential stacking)

**Slack** — Detect if the content has ANY of:
- Channel references (#channel-name)
- @mentions without full names (@here, @channel, @username)
- Thread-style short messages
- Very casual tone with no greeting or sign-off
- Under 500 characters, conversational fragments
- Emoji reactions referenced or inline emoji shortcodes (:thumbsup:, :rocket:)

**Marketing Collateral** — Detect if the content has ANY of:
- "FOR IMMEDIATE RELEASE" or dateline format ("City, Date —")
- "We are thrilled/excited/pleased to announce"
- Hero headline + subheadline structure with no body prose between them
- CTA phrases: "Get started", "Request a demo", "Sign up free", "Learn more", "Contact sales"
- Feature/benefit bullet lists with no surrounding paragraphs
- "Introducing [Product]" or "Announcing [Product/Partnership]"
- Social proof blocks: "Join X companies", "Trusted by", logo mentions
- "Industry-leading", "best-in-class", "end-to-end solution", "comprehensive platform"
- Section headers like "Key Benefits", "How It Works", "Why [Company]", "Overview"
- Executive quote in quote marks attributed to a named title (CEO, VP, etc.)

**Blog Post** — Detect if the content has ANY of:
- Headings or subheadings (##, ###, or formatted headers)
- More than 3,000 characters of structured prose
- Multiple paragraphs with developed arguments
- "In this article", "Key takeaways", or other meta-commentary
- SEO-style structure

If ambiguous, default to **Blog Post** and note: "Detected as: Blog post. If this is a different format, let me know and I'll re-run with channel-specific rules."

When the content looks like marketing collateral, identify the specific sub-format — webpage, one-pager, press release, or sales deck — and apply the relevant sub-rules.

---

## Voice Calibration

Voice calibration is **optional and sample-based**. `humanize` does not read or resolve any
voice skill — its job is to strip AI patterns and de-AI text into a natural, varied human
voice. If a sample is provided, calibrate to it; if not, use a clean default voice. Never look
up, load, or depend on a personal voice profile — a user with no voice installed gets full
functionality and no errors.

Try to establish the user's voice using the following priority order:

1. **Use a provided writing sample** — if the user has included one inline or referenced a file path, read it and extract:
   - Sentence length patterns (short and punchy? long and flowing? mixed?)
   - Word choice register (casual? academic? somewhere between?)
   - How they open paragraphs and posts
   - How they end (principle, challenge, open question, summary, CTA?)
   - Punctuation habits (dashes? asides? semicolons?)
   - Phrases they would never use

2. **Ask for a sample** — if no sample is available, ask:
   > "To match your voice, paste a short sample of your own writing (a few sentences is enough), or share a file path. Or say 'skip' to proceed with a natural default voice."

3. **Proceed with default voice** — if the user declines or says skip, rewrite in a natural, varied, human voice and note: "No voice sample provided — using a default human voice. Sharing a sample would improve the match."

### How to provide a sample
- Inline: "Humanize this. Here's a sample of my writing: [sample]"
- File: "Humanize this. Use my style from [file path] as a reference."

---

## Channel-Specific Markers

Apply the universal markers in `references/ai-patterns.md` to all content types, then apply the relevant channel-specific markers below.

### LinkedIn-Specific Markers

**Phrase-level:**
- LinkedIn pivot transitions: "But here's the thing", "And here's the kicker", "Here's what most people miss", "Let me explain", "Here's why that matters"
- Engagement bait closers: "Agree?", "Thoughts?", "What would you add?", "Drop a comment if you've experienced this", "Repost if this resonates" — if the post is worth engaging with, people will. Don't beg for it.
- Vulnerability performance phrases: "I'll be honest", "Can I be real for a second?", "I'll be vulnerable here", "I wasn't going to share this but..." — real vulnerability doesn't announce itself.
- Fake humility: "I'm no expert, but...", "I don't have all the answers, but...", "This might be controversial, but..." — these always precede confident claims. Skip the disclaimer.
- Tag-and-thank: tagging 5+ people at the end with "Shoutout to..." — one or two genuine tags are fine. A list is reach-farming.
- Arrow chain format: using → arrows to show a process/flow. This reads as a slide deck. Write it as a sentence.
- ALL-CAPS single-word injection: capitalizing individual words mid-sentence to simulate spoken intensity (e.g., "Generated MILLIONS in ARR", "Woke up to a VERY exciting email"). Earn the emphasis through specificity — use the actual number or thing instead of a shouted word.
- "What if I told you..." curiosity hook: recognized ghostwriter/AI template. Only valid when followed by a specific, non-obvious insight the author genuinely has. If the post could have been written by anyone with a search engine, cut the hook.
- "Here's what nobody tells you about..." insider framing: AI uses this formula constantly without actual insider knowledge to follow. Flag when the content underneath is generic enough that anyone could have written it.
- "Read that again." / "Let that sink in." permission phrases: dropped after an unremarkable observation to manufacture gravity. Found at 22x normal frequency in AI-generated posts. Example: "Your habits shape your identity. Read that again." — the insight doesn't earn the dramatic pause. Cut both.
- "And honestly?" fake candor opener: AI drops this before a non-controversial claim to simulate real-talk authenticity. Example: "And honestly? That's what separates the good from the great." Just state the opinion directly.

**Structural:**
- One-line paragraph formatting: every sentence is its own paragraph. This is LinkedIn's #1 AI/ghostwriter tell. Group related sentences into real paragraphs.
- Hook > 3-point list > mic-drop closer template
- Explaining the algorithm: telling people why to comment or share. Just ask.
- Vulnerability bait hook: opening with a personal failure story designed primarily to hook readers, then pivoting to a tidy lesson. If the story is real, let it be messy.
- "We didn't just build X. We built Y" negation upgrade: just say what you built.
- Hyperbole opener: "X will never be the same." or "Everything changed." Start with the specific thing that happened.
- Common-belief-then-counter opener: three-sentence setup that states a common belief as fact, attributes it to "most people," then knocks it down. This is a ghostwriter/AI template. Rewrite by starting with the actual insight directly.
- Period-separated word emphasis: "every. single. day." — reads as performative. Rewrite to earn the emphasis.
- Self-intro paragraph at post bottom: ending with a formal self-introduction paragraph. An AI/ghostwriter template habit. Cut or weave the relevant credential into the post body.
- Information-withheld hook: opening sentences that deliberately omit the post's actual subject to force the "...more" click. Pure curiosity-gap manipulation — rewrite by opening with the actual insight.
- "X is [positive]. [X variant] is a whole different game" contrast formula: collapse into a single direct sentence about the actual challenge.
- Cliché proverb opener: starting with a well-worn business maxim. Replace with the specific observation or experience that prompted the post.
- External link CTA ending: closing a post with an external URL in the body or "link in comments 👇" kills ~60% of reach. LinkedIn's algorithm treats both as off-platform signals. Add the link in the first comment after engagement begins — or describe what's there and let people find it.
- Achievement post formula: AI-generated milestone posts follow a 4-beat template: (1) emotion word + announcement, (2) team/supporter thanks, (3) generic universal lesson, (4) emoji-closed enthusiasm sign-off. Flag when all four beats appear in sequence with generic language. Replace with a specific story about what made this milestone hard or meaningful.
- Fake dialogue/conversation format: framing an opinion piece as a fabricated back-and-forth between two roles (CEO/CMO, Founder/Investor, etc.). AI uses this to simulate authority without firsthand evidence. Rewrite as direct prose with the actual argument stated up front.

### Email-Specific Markers

**Phrase-level:**
- AI greeting formulas: "I hope this email finds you well", "I trust this message finds you in good spirits", "Hope you had a great weekend" (when the sender doesn't know the recipient)
- AI closings: "Please don't hesitate to reach out", "I look forward to hearing from you", "Thank you for your time and consideration", "Warmest regards", "With gratitude"
- Corporate filler: "I wanted to reach out because...", "I'm writing to inform you that...", "Per our previous conversation", "As per my last email", "Going forward", "At your earliest convenience", "Please be advised"
- Fake personalization: "I noticed your company is doing great things in [industry]", "I was impressed by your recent [post/talk/article]" — if you can't cite something specific, delete the flattery
- Hedge language: "I was wondering if perhaps...", "Would it be possible to maybe...", "I just wanted to quickly check if..."
- Email AI vocabulary: "circle back", "loop in", "touch base", "sync up", "deep dive", "bandwidth", "on my radar", "double-click on", "unpack"
- Over-politeness stacking: multiple politeness phrases in one email. One "thanks" is enough.
- Rhetorical throat-clearing: "I'd be remiss if I didn't mention...", "It goes without saying that..."
- Subject line AI patterns: "Quick question", "Following up", "Checking in", "A thought", "[First name], quick thought" — be specific about what the email is about

**Structural:**
- More than one ask in the email. Good emails have one clear ask.
- Ask buried at the bottom. Lead with what you need.
- Email is 2-3x longer than it needs to be for its purpose.
- Opens with context the recipient already knows.
- Greeting mismatched to the relationship ("Dear Mr. Smith" for someone you've emailed 20 times).
- Vague CTA instead of specific ("Let me know if you'd like to chat sometime" vs "Free Tuesday at 2pm?").
- Email reads like a template with blanks filled in.
- Multiple sign-off phrases stacked.

### Marketing Collateral-Specific Markers

Identify the sub-format first (webpage, one-pager, press release, sales deck), then apply the relevant sub-rules below in addition to the universal markers.

**Phrase-level (all collateral):**
- Hero headline padding: "Transform your X", "Revolutionize your Y", "The future of Z is here", "Unlock the power of", "Experience the difference" — state what the product actually does
- Feature-as-benefit fraud: listing what the product does instead of what the user gets. "Real-time monitoring" is a feature. "Catch issues before customers do" is a benefit. If a bullet describes a capability rather than an outcome the reader cares about, it's a feature masquerading as a benefit.
- Vague social proof: "thousands of customers", "leading organizations", "trusted by industry leaders" — use real numbers and named customers; if you can't, cut the claim
- "Industry-leading", "best-in-class", "world-class", "cutting-edge" without evidence — every company says this; none of it is a claim
- "Comprehensive solution", "end-to-end platform", "holistic approach" — specify what's comprehensive and what the two ends are
- "We help [audience] [verb] [vague outcome]" as the entire value proposition — name the specific problem, the specific mechanism, and a specific result
- Pain-solution without naming the pain: "Struggling with compliance? We can help." — what specifically? What does struggling look like for this customer?

**Structural (all collateral):**
- Every section ends with a CTA button — choose one primary CTA per page; the rest is friction
- Hero claim unsupported anywhere in the body — if the headline makes a claim, the body needs to substantiate it with evidence
- All benefits are outcomes with no mechanism: "save time", "reduce risk", "increase revenue" — how? the mechanism is the differentiator
- No specificity anywhere: no named customers, no numbers, no named problems — if everything is generic, nothing is credible
- Benefit bullet overload: 6-8 bullets all at the same weight with no hierarchy — readers scan and retain nothing; cut to 3 and order by what the ICP cares most about

**Press release sub-rules:**
- "We are thrilled/excited/delighted/pleased to announce" — state the news directly in the first sentence without an emotion qualifier
- Executive quote that says nothing: any quote where a different executive at a different company could have said the same thing ("We are excited about the opportunities this presents"). The quote should say something only this person, about this thing, at this moment could say.
- "This partnership/acquisition/launch represents a significant milestone" — significant for whom, and how? Specify.
- Buried news: most press releases bury the actual announcement in paragraph 2 or 3 after context-setting. The first sentence should be the news.
- Wire service filler: "announced today that", "is pleased to announce", "has entered into an agreement to" — say the thing directly
- No actual news: if nothing changed for the customer, the press release shouldn't exist

**One-pager sub-rules:**
- More features than benefits — a one-pager should answer "why should I care?" not "what does it do?"
- No named ICP — if it's for everyone, it's for no one; the one-pager should make a specific person feel seen
- No differentiation: what does this do that an alternative doesn't? If the answer isn't on the page, readers will default to the incumbent
- Stat bomb without context: "10x faster", "50% reduction" — faster than what? Reduction from what baseline? Over what time period?

**Webpage sub-rules:**
- CTA inflation: more than two distinct CTAs competing for attention on the same page
- Hero-body mismatch: the hero makes a claim the body doesn't support or even address
- Section headers as filler: "Why [Company]?", "How It Works", "The [Company] Difference" — these are placeholders, not communication
- Social proof logos with no context: a row of logos without a quote, metric, or outcome attached is decoration, not evidence

**Sales deck sub-rules:**
- Problem slide that's too abstract: the problem should make the target buyer feel seen and slightly uncomfortable — if it could describe any company in any industry, rewrite it
- Solution slide that leads with features: lead with the outcome the buyer cares about, then explain how the product delivers it
- "Our team has X years of combined experience" — irrelevant credential; replace with what that experience produced
- Generic competitive positioning: "we're the only platform that..." claims require evidence; vague differentiation is worse than no differentiation

### Slack-Specific Markers

**Phrase-level:**
- Over-formal language for Slack: "I wanted to reach out regarding...", "Please be advised that...", "At your earliest convenience" — Slack is casual. Write like you talk.
- Corporate Slack filler: "Just wanted to flag...", "Wanted to surface this...", "Looping in [name] for visibility" — be direct about what you need.
- Unnecessary hedging: "Sorry to bother you, but...", "I might be wrong, but...", "Not sure if this is the right channel, but..." — just say it.
- Emoji overload: 3+ emoji in a short message to manufacture enthusiasm or soften a request.

**Structural:**
- Message is too long for Slack. If it needs more than 4-5 sentences, it should probably be an email, a doc, or a thread with a TL;DR at the top.
- Buries the ask or action item in a long message. Lead with the ask, then provide context.
- Uses formal structure (greeting + body + sign-off) in a Slack message. Just say the thing.
- Over-explains context that the channel audience already has.

---

## Personality and Soul

Removing AI patterns is only half the job. Clean but voiceless writing is just as obvious as slop.

- **Have opinions.** Don't just report — react.
- **Vary rhythm.** Short punchy sentences. Then longer ones that take their time. Mix it up.
- **Acknowledge complexity.** "Impressive but kind of unsettling" beats "impressive."
- **Use "I" when it fits.** First person is honest, not unprofessional.
- **Be specific.** If you can't picture it happening in real life, rewrite it.
- **Let some mess in.** Perfect structure feels algorithmic.

---

## Scoring Rubric

Score on four dimensions (1–10). **Dimensions vary by content type.**

**Blog Post & LinkedIn:**

| Dimension | Measures | Target |
|---|---|---|
| AI-Likeness | How much AI texture (lower is better) | 1–3 |
| Authenticity | How unmistakably it sounds like a specific human | 8–10 |
| Reader Value | Would the target audience find this non-obvious? | 7–10 |
| Domain Credibility | Could only someone with this background write this? | 7–10 |

**Email:**

| Dimension | Measures | Target |
|---|---|---|
| AI-Likeness | How much AI texture (lower is better) | 1–3 |
| Authenticity | How much it sounds like a real person writing to this specific recipient | 8–10 |
| Clarity | Is the purpose clear and the ask unambiguous? | 8–10 |
| Appropriate Tone | Is the formality level right for this relationship and context? | 8–10 |

**Slack:**

| Dimension | Measures | Target |
|---|---|---|
| AI-Likeness | How much AI texture (lower is better) | 1–2 |
| Naturalness | Does it sound like how this person would actually type in Slack? | 8–10 |
| Clarity | Is the point/ask immediately clear? | 8–10 |
| Brevity | Is it the right length for a Slack message? | 8–10 |

**Marketing Collateral:**

| Dimension | Measures | Target |
|---|---|---|
| AI-Likeness | How much AI texture (lower is better) | 1–3 |
| Specificity | Named customers, real numbers, named problems — or generic claims? | 7–10 |
| Persuasion | Does it make a target reader want to act, or just describe features? | 7–10 |
| Differentiation | Does it say something a competitor couldn't also say? | 7–10 |

**Important:** If AI-Likeness is low but Domain Credibility (blog/LinkedIn), Clarity (email/Slack), or Specificity (collateral) is also low, call it out explicitly. The post is clean but hollow — clean but voiceless is as damaging as slop.

---

## Hook vs. Value Calibration (LinkedIn Only)

LinkedIn's algorithm operates in two stages. AI content often games Stage 1 and dies at Stage 2.

**Stage 1 — Distribution (first 30–60 min):** Hook quality determines whether the algorithm distributes broadly. A good hook forces a "see more" click.

**Stage 2 — Continued distribution (ongoing):** Dwell time, saves, and substantive comments determine whether the algorithm keeps distributing. AI content collapses here — generic content has low dwell time, low saves, and shallow comments.

One save = 5x a like in reach value. Substantive comments = 2.4x reach boost vs. surface reactions.

**Hooks that clear Stage 1 AND earn Stage 2:**
- Specific consequence opener: a named result, not a lesson ("I lost my best employee yesterday," not "Here's why retention matters")
- Data point with personal stakes: one number + what it meant to the author
- Contrarian claim with named evidence: a direct challenge to a common belief, backed by something only this author could have observed
- Story that ends unresolved: a real situation with no tidy lesson

**Hooks that game Stage 1 but kill Stage 2:**
- Information-withheld hook: manufactures curiosity, delivers nothing specific; reader clicks and is gone in 8 seconds
- "What if I told you..." / "Here's what nobody tells you...": recognized templates; when the payoff is generic, reader feels cheated
- Triple rhetorical question: reader already knows this pattern, skims for the answer
- ALL-CAPS intensity signals: gets scroll-stop, but collapses if content underneath is hollow
- Cliché proverb opener: no curiosity gap, no reason to click

**The saves-worthiness test:** Is there one specific, referenceable piece of information — a named tool, a concrete step, a number with context, a named decision the author actually made — that someone would save to return to? If not, it won't compound in distribution.

**The comment-quality test:** Does the post contain a claim specific enough to disagree with, a tradeoff with no obvious right answer, or a story that ends without a lesson? Those generate substantive comments. Generic takeaways generate "So true!" — which the algorithm now treats as weak engagement signal.

---

## Rewrite Rules

1. **Never add ideas that weren't in the original.** Never remove substance. Preserve every argument — only change delivery.
2. Replace every flagged AI phrase with natural language.
3. Vary sentence length — mix short punchy lines with longer analytical ones.
4. Replace generic openings with a specific hook (story, data, contrarian claim).
5. Replace summary conclusions with a challenge, principle, or open question.
6. Break paragraph rhythm monotony — some short, some long.
7. Add voice texture: incomplete sentences where appropriate, direct address, occasional bluntness.
8. If the post lacks a concrete example, **do not invent one** — insert `[ADD SPECIFIC EXAMPLE FROM YOUR EXPERIENCE]` as a placeholder.

**Channel-specific rewrite rules:**

**Blog Post:**
- Preserve heading structure but improve heading copy if generic
- Ensure prose paragraphs vary in length
- Replace "In this article" or "Let's dive in" meta-commentary

**LinkedIn:**
- Keep under 1,300 characters (short-form) or 3,000 characters (long-form). LinkedIn rewards density.
- Don't stack hashtags at the bottom. Weave 1-3 naturally or drop them.
- Remove engagement bait closers entirely.
- Replace arrow-chain formats with real sentences.
- Replace one-line-per-paragraph with actual paragraph structure (2-4 sentences per paragraph).
- Remove emoji used as decoration. Keep only emoji that carry genuine meaning.

**Email:**
- Lead with the ask or purpose, not context.
- Cut to minimum length. Most AI emails are 2-3x too long.
- Match formality to the relationship.
- Use a specific CTA ("Free Tuesday at 2?" not "Let's chat sometime").
- One ask per email.
- Remove performative politeness. One "thanks" is enough.
- Subject line: make it specific to the content.
- Opening: skip "I hope this finds you well." Start with the point.
- Closing: pick one sign-off. Not a stack of three.

**Slack:**
- Maximum 4-5 sentences. If longer, suggest moving to email/doc.
- Lead with the ask or action item.
- No formal greeting or sign-off.
- Match the casual tone of the channel.
- If sharing a link, add one sentence of context, not a summary.

**Marketing Collateral:**
- Every generic claim needs either evidence or a rewrite. Flag ones that can't be substantiated without more information from the author using `[NEEDS: specific customer/metric/example]`.
- Convert features to benefits: what does the reader get, not what the product does.
- Cut to one primary CTA per section.
- The hero or opening must state the specific problem solved and for whom — not a transformation promise.
- Executive quotes must say something specific to this moment, product, or outcome. If the quote could be said by any executive about anything, flag it as `[QUOTE NEEDS SPECIFICITY]`.
- Press releases: the first sentence is the news. Everything else is context.
- One-pagers: if the ICP isn't clear by the end of the first paragraph, name them explicitly.
- Replace vague differentiation ("only platform that...") with a named, verifiable claim — or remove it.

Tell the user at the end: "Your edits on top of this rewrite are often the best version."

---

## Output Format

```
## [Content Type] Review

**Detected as:** [Blog Post / LinkedIn Post / Email / Slack Message / Marketing Collateral]

### Overall Assessment
[2–3 sentence summary of strengths and biggest issues]

### Scores
| Dimension | Score | Note |
|---|---|---|
| AI-Likeness | X/10 | [one line] |
| [Dim 2] | X/10 | [one line] |
| [Dim 3] | X/10 | [one line] |
| [Dim 4] | X/10 | [one line] |

### AI Pattern Flags
[List every flagged phrase/structure with exact quote and suggestion]

### Structural Flags
[Generic opening? Paragraph rhythm monotony? Stacked fragments? Template structure?]

### [Originality Flags / Clarity & Effectiveness Flags]
[List every concern]

### Top 3 Changes That Would Most Improve This
1. [Specific, actionable]
2. [Specific, actionable]
3. [Specific, actionable]
```

Then provide the full rewrite.

See [references/example.md](references/example.md) for a complete worked example.

---

## Auto-Improvement Loop

Run this step after every review and rewrite. Do not skip. Do not wait for the user to ask.

1. Compare every pattern you flagged against the patterns already documented in [references/ai-patterns.md](references/ai-patterns.md)
2. For each flag, ask: "Is this pattern already documented? If not, is it specific and repeatable enough to add?"
   - Only consider patterns that are clearly general and recurring — not anything specific to the content just reviewed
   - Do not add vague rules — if you can't give a concrete, channel-neutral example, don't propose it
3. Report proposed additions to the user **before writing anything**:

**If new patterns are found:**
```
## Skill Update — Proposed Additions

Found [N] new pattern(s) worth adding to your local pattern library:

**[Pattern name]**
- Section: [which section]
- Rule: [one-line flaggable rule]
- Example before: [example]
- Example after: [example]

Reply "add them" to save to ~/.claude/humanize/ai-patterns-local.md, or "skip" to discard.
```

**If nothing new:**
```
## Skill Update
- No new patterns. The skill already covers everything flagged in this review.
```

4. Only write after the user explicitly confirms (e.g. "add them", "yes", "do it"). Never write automatically.
5. Write confirmed additions to `~/.claude/humanize/ai-patterns-local.md` — **never** to `references/ai-patterns.md`. This file is outside the plugin directory and will not be overwritten by plugin updates. Create it if it doesn't exist yet, with a short header comment explaining its purpose.

---

## Quick-Reference: Most Common Patterns

Full list with before/after examples in [references/ai-patterns.md](references/ai-patterns.md). Most frequent offenders:

| Pattern | Watch for |
|---|---|
| AI vocabulary | delve, tapestry, testament, pivotal, underscore, vibrant, intricate, landscape (abstract), foster, garner, crucial, showcasing, highlight (verb), align with, transformative, seamless, robust, leverage (as verb), empower, unlock, streamline, elevate, realm, essentially, certainly, overall, absolutely, typically, various, meticulous, bolstered, causal, empirical, correlate |
| Chatbot paste artifacts | oaicite, contentReference, oai_citation, turn0search0, [cite: N], [span_N], grok_card, ppl-ai-file-upload, :::writing — remove on sight; plus a stray utm_source= left in a pasted URL (a pasted-and-forgotten tell, not a ban on intentional tracking params) |
| Significance inflation | stands/serves as, marking a pivotal moment, underscores, reflects broader, indelible mark, shaping the, setting the stage for |
| Copula avoidance | "serves as," "stands as," "functions as," "represents" instead of "is/are" |
| Em dash overuse | — used where a comma or period would be cleaner |
| Filler openers | In order to, Due to the fact that, At this point in time, It is important to note that, In today's [noun], When it comes to, **The truth is** |
| Sycophancy | Great question!, Of course!, Certainly!, I hope this helps!, Let me know if... |
| Signposting | Let's dive in, Let's explore, Here's what you need to know, Without further ado, But here's the thing, Here's what most people miss |
| Rule of three | Forced triplets: "adjective, adjective, and adjective" |
| Persuasive authority | At its core, The real question is, What really matters, Fundamentally |
| Generic endings | The future looks bright, Exciting times lie ahead, A step in the right direction |
| Structural tells | **Paragraph rhythm monotony** (3+ consecutive body paragraphs in the same length band, 3+ consecutive paragraphs >100w with no shorter beat between, or a long piece with no <30w and no >100w paragraphs); stacked fragments "X. Y. Z."; intro→list→conclusion; runway sentences before the real point; reading complexity creep (3+ 3-syllable words per sentence) |
| Originality tells | No firsthand evidence; advice anyone could write; "the future of X is Y" |
| Promotional | nestled, breathtaking, boasts, vibrant, renowned, groundbreaking, must-visit |
| Excessive bold | **Bolded inline headers** followed by colons in every bullet |
| -ing phrase padding | "...symbolizing X, reflecting Y, contributing to Z" tacked onto sentences |
| Hyphenated word pairs | cross-functional, data-driven, client-facing, decision-making, high-quality, real-time |
| AI phrases | "brutal clarity", "here's a breakdown", "not only...but also", "X rather than Y", "a testament to", "Below is:", "The truth is", "Read that again.", "And honestly?" |
| Encyclopedic tells | title-as-proper-noun lead ("X refers to…"); a table used where prose belongs |
| LinkedIn tells | one-line-per-paragraph, ALL-CAPS words, "Read that again.", "And honestly?", achievement post formula, fake dialogue format, information-withheld hook, engagement bait closers |
| Email tells | "I hope this email finds you well", "Please don't hesitate to reach out", buried ask, 2-3x too long |
| Slack tells | over-formal language, corporate filler, emoji overload, too long for the medium |
| Collateral tells | hero headline padding, feature-as-benefit fraud, vague social proof, "industry-leading" without evidence, "We are thrilled to announce", executive quotes that say nothing, all benefits no mechanism |
