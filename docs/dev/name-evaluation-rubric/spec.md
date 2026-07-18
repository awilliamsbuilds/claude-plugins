# Name Evaluation Rubric — craft-name enhancement
*Branch: feature/name-evaluation-rubric · Confidence: 88% — Ready · 2026-07-17*
*Cycle type: feature · Tier: standard*

## Intent

The `craft-name` skill is deliberately "mouth-feel first" (75% sound / 25% memorability) and comparatively light on *meaning* and *strategic fit*. Insights reverse-engineered from Lexicon's actual name-*evaluation* methodology (`/Users/adam/Downloads/name-evaluation-rubric.md`) offer a more rigorous evaluation model — a two-axis Meaning × Sound system with disqualifying gates and a precise phoneme→meaning mapping.

Fold the strongest, most reusable pieces of that model into `craft-name` so the skill weighs meaning and strategic fit alongside sound, and surfaces failure modes it currently misses (off-category pull, tool-vs-platform scale, ownability clutter) — without abandoning the skill's phonetic strengths or its advisory tone.

## Scope

Selective integration into `plugins/naming/skills/craft-name/SKILL.md` — pull in the high-value pieces and weave them into the existing structure:

1. **Phoneme→meaning table + onset–center–coda test.** Adopt the rubric's phoneme-class → sensory-quality mapping (voiceless stops = sharp/fast/precise; voiced stops = grounded/heavier; /s/ = precise/technical; /v/ = active/modern; nasals & liquids = soft/slow/diffuse; soft/open endings = gentle/unresolved; consonant clusters = friction/slowness; front vowels = small/fast, back vowels = large/slow). Add the onset–center–coda test (score opening, middle, and ending separately; the classic failure is a strong opening undone by a soft ending). **Reconcile** this with the existing "Quick Phonetic Heuristics" section rather than bolting a second, overlapping list beside it (exact merge/replace shape is a Plan decision).

2. **Off-category pull gate.** Flag when a name's *meaning* drags toward the wrong category — the rubric's examples (healthcare/biology; borrowed place-names) are illustrations, not the whole set. Generalize to "any category-pull that overpowers this project's intended story."

3. **Scale gate.** Flag when a name sounds tool/feature-sized rather than platform-sized — a dimension distinct from sound quality. **Conditional:** only a liability when the thing being named is meant to be a platform/master brand; tool-sized is fine for a single-purpose app or a sub-brand.

4. **Ownability gate.** Trademark + marketplace-clutter read, applied as a *modifier* on an otherwise-strong name, not a first-class score. Generalize the rubric's hardwired "AI / fintech / security" categories to "the relevant categories for this project."

5. **Balanced-sheet verdict format.** Offer the rubric's recommendation structure — *two genuine strengths → the governing liability → the gated recommendation* — as the shape for presenting a finalist.

### Generalization principle (critical — applies to all of the above)

The rubric ships with **one client's answer key stapled to it.** Its "target attributes" (speed, command, investigation, intelligence, scale, AI-native, disruption/enforcement) and its ownability categories (AI/fintech/security) are reverse-engineered from a single strategic brief — almost certainly an AI-driven security/investigation platform. Consequently its phoneme *verdicts* are biased: "hard stops = good, soft endings = weak" is only true **because that brief wanted command and speed.** For a calm wellness app or a playful consumer brand, a soft nasal ending is the target, not a defect.

`craft-name` names *anything*, so the integration must keep the rubric's **method** while stripping its **specific answers**:

- **Keep the phoneme→*sensation* mapping; drop the fixed good/bad verdicts.** Present each phoneme class as a *neutral* signal ("voiceless stops read sharp/fast/precise"; "soft open endings read gentle/unresolved") — not as inherently strong or weak.
- **Bind "good vs. bad" to the project's own target feeling.** The skill already collects 3–5 target adjectives in "Step 1: Define the target feeling." The sound-symbolism check becomes: *does the sound match the adjectives this project chose* — not *does it sound like a fast, commanding platform.*
- **Generalize the hardwired specifics:** off-category examples are examples, not the universe; the ownability gate checks "the relevant categories for this project"; the scale gate matters only when a platform is the goal.
- **Do NOT import** the rubric's fixed target-attribute checklist, its Diamond/strategic-brief framing, or its numeric 0–3 scoring sheet as the skill's canon.

### Gate strength: soft flags, not hard overrides

All three gates (off-category, scale, ownability) surface as **prominent warnings the human weighs**, not automatic disqualifiers. A phonetically excellent name that trips a gate is still presented as a finalist with the flag called out — the skill keeps its "here are the trade-offs" advisory tone rather than auto-killing or auto-demoting names. (This is a deliberate departure from the rubric's own hard two-gate model.)

## Out of Scope

- The rubric's **Diamond / strategic-brief framing** ("what winning looks like / what we have / what we need / what we need to say").
- The full per-candidate **0–3 numeric scoring sheet** (the `CANDIDATE: ____ / BLOCK Z / BLOCK S / STRATEGIC EXPRESSIVENESS` template).
- **Hard disqualifying gates / the two-gate Kill/Hold/Advance decision table** — replaced by soft flags per above.
- The rubric's **fixed target-attribute list** as skill canon (speed/command/investigation/etc.) — generalized away, not adopted.
- Any change to the skill's frontmatter `description` triggers, plugin registration, or other skills.

## Success Criteria

- A name run through `craft-name` now also receives a **meaning-fit read** and is checked against the three gates, presented as flags.
- The **sound-symbolism guidance is more precise** than today's softer/stronger-sounds heuristics (phoneme-class granularity + onset–center–coda), and is expressed *neutrally* — tied to the project's target feeling, not to a fixed "hard = good" bias.
- A finalist can be presented in the **balanced-sheet verdict** form.
- The existing **mouth-feel screen, repetition test, seam test, and sentence-fit tests remain intact** — the change augments the meaning/gate side without gutting the sound side.
- No duplicated/contradictory phonetic guidance: the new phoneme table and the old "Quick Phonetic Heuristics" are reconciled into one coherent treatment.
- The skill reads as one voice, not "original skill + pasted rubric."

## Happy Path

1. User invokes `craft-name` to name something and defines a target feeling (existing Step 1).
2. Generation proceeds as today (broad lists across directions).
3. During evaluation, each finalist is now assessed on **sound** (upgraded phoneme guidance, tied to the target feeling) **and meaning** (does it signal the intended qualities; any off-category pull).
4. The three gates run as flags: off-category pull, scale (if a platform is the goal), ownability clutter in the project's categories.
5. Finalists are presented — optionally in balanced-sheet verdict form — with any gate flags called out for the user to weigh.

## Edge Cases

- **Target feeling wants softness** (calm/warm/premium): the phoneme guidance must treat soft nasals/liquids/open endings as *on-target*, never as defects. This is the acid test that generalization worked.
- **Naming a single-purpose app, not a platform:** the scale gate must stay quiet (tool-sized is correct), or route to "fine as-is / good sub-brand," not flag a problem.
- **A gate trips on an otherwise-excellent name:** it is still shown as a finalist with the flag noted (soft-flag behavior), not removed.
- **Overlap with existing content:** the seam test, cluster guidance, and old phonetic heuristics must not now contradict the new phoneme table.

## Audience

Anyone using `craft-name` via Claude Code to name a business, brand, product, app, feature, or project — general-purpose, across any category or tone.

## Technical Constraints

- Single-file change: `plugins/naming/skills/craft-name/SKILL.md` (Markdown skill instructions).
- Preserve valid SKILL.md structure; do not alter the YAML frontmatter `description` (it drives skill triggering) unless a change is explicitly justified.
- Length discipline: the file is already ~680 lines. Prefer reconciling/merging over appending; avoid bloating the skill with a redundant second scoring system.

## Dependencies

- Source insights: `/Users/adam/Downloads/name-evaluation-rubric.md` (input only; not shipped into the repo).
- No code, build, or runtime dependencies.

## UI Needed

No — Markdown skill-content change. Shape stage skipped.

---
*Auto-filled dimensions: happy_path, dependencies (inferred from the skill's own process and the single-file nature of the change rather than asked directly)*
