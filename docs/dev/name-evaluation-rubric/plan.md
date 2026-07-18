# Name Evaluation Rubric — Implementation Plan
*Branch: feature/name-evaluation-rubric · 2026-07-18*

Single-file change to `plugins/naming/skills/craft-name/SKILL.md`. Four tasks, edited in order because they touch one file; only Task 4 has a true logical dependency on the others. The governing constraint (from spec) is **method, not answer key**: fold in the rubric's phoneme→sensation mapping, onset–center–coda test, three gates, and balanced-sheet verdict — expressed *neutrally* and bound to the project's own Step 1 target feeling — while dropping the rubric's fixed "hard = good" verdicts, its target-attribute checklist, Diamond framing, 0–3 scoring sheet, and hard Kill/Hold/Advance table.

## Files

| File | Action | Purpose |
|------|--------|---------|
| `plugins/naming/skills/craft-name/SKILL.md` | Modify | Fold rubric's meaning/sound evaluation method into the skill, reconciled with existing sound guidance |
| `docs/dev/name-evaluation-rubric/state.json` | Modify | Reconcile workflow state (spec completed, shape skipped) + record plan artifact/timestamps |

## Tasks

### Task 1: Reconcile "Quick Phonetic Heuristics" into a neutral phoneme→sensation section
What: Replace the existing `## Quick Phonetic Heuristics` section (currently lines 547–601: softer/stronger/futuristic sounds + smooth/crisp endings) with a single upgraded `## Sound Symbolism: Phoneme → Sensation` section carrying a phoneme-class table, the onset–center–coda test, and explicit neutral framing tied to the Step 1 target feeling.
Used by: The Generation Process evaluation steps (wired in Task 4) and anyone reading the skill for sound guidance.
Depends on: nothing — first task.
Files: `plugins/naming/skills/craft-name/SKILL.md`
Interfaces:
- Consumes: nothing.
- Produces: A section titled `## Sound Symbolism: Phoneme → Sensation` (this exact heading is referenced by Task 4). The old `## Quick Phonetic Heuristics` heading no longer exists after this task.

Implementation steps:
1. Delete the entire `## Quick Phonetic Heuristics` section (heading through the last "Crisp endings" bullet, current lines 547–601).
2. In its place, write `## Sound Symbolism: Phoneme → Sensation` with a lead paragraph establishing the neutral principle: each sound class maps to a *neutral sensation*, not a verdict; whether a sensation is a strength or a defect is decided entirely by the 3–5 target adjectives chosen in Step 1. State the acid-test example both directions: hard clipped edges suit a name that wants command/speed and fight a name that wants calm/warmth; a soft nasal or open ending is on-target for a wellness or playful brand and off-target for a security platform. Explicitly: "Read every row as a signal, not a good/bad rating."
3. Add the phoneme table with a single neutral "Reads as" column (no "good/bad", no illustration verdicts):
   | Phoneme class | Reads as (neutral signal) |
   - Voiceless stops /t/ /k/ /p/ → sharp, fast, precise, clipped
   - Voiced stops /d/ /b/ /g/ → grounded, weighty, solid
   - /s/ fricative → precise, clean, technical
   - /v/ fricative → active, energetic, modern
   - Nasals /m/ /n/ & liquids /l/ /r/ → soft, smooth, slow, diffuse
   - Soft / open endings (-a, -o, -er, final /l/ or /n/) → gentle, unresolved, open
   - Crisp stop endings (-t, -k, -p, -d) → decisive, closed, punchy
   - Consonant clusters (e.g. -rth-, -str-) → friction, effort, slowness
   - Front vowels /i/ /e/ → small, fast, light, bright
   - Back vowels /o/ /u/ /a/ → large, slow, heavy, expansive
4. Add the **onset–center–coda test**: score the opening consonant, the middle, and the ending *separately* against the target feeling. Frame the classic failure as a *mismatch with the target*, not "soft ending = weak": a crisp onset undercut by a soft open ending is a defect only when the target wants decisiveness; a hard clipped ending fighting a smooth onset is the defect when the target wants warmth. The test is coherence with the chosen feeling.
5. Fold the deleted lists in without reintroducing bias: preserve the futuristic-letters caution as one neutral line — X / Z / K / V add a "techy/futuristic" edge that is on-target for some feelings and reads artificial or dated in excess.
6. Add a one-line cross-reference: the per-vowel qualities in the "Open vowel sounds" subsection (under "What Makes a Name Feel Good to Say") still apply and are consistent with the front/back vowel rows here — do not restate them.

### Task 2: Add the meaning-fit read and the three soft gates
What: Add a new `## Meaning & Strategic Fit: the Read and the Three Gates` section covering (a) a brief meaning-fit read and (b) the off-category-pull, scale, and ownability gates — all as soft flags the human weighs, generalized away from the rubric's hardwired categories.
Used by: The evaluation/presentation steps wired in Task 4; the balanced-sheet verdict (Task 3) references these flags.
Depends on: Task 1 (sequential edit to the same file; place this section immediately after the Task 1 section).
Files: `plugins/naming/skills/craft-name/SKILL.md`
Interfaces:
- Consumes: The Step 1 target feeling (existing) and Step 9 "Check marketplace friction" (existing) — the ownability gate interprets Step 9's signal, it does not re-list the checks.
- Produces: A section titled `## Meaning & Strategic Fit: the Read and the Three Gates` (exact heading referenced by Tasks 3 and 4), containing three named gates: **off-category pull**, **scale**, **ownability**.

Implementation steps:
1. Write a lead paragraph on the **meaning-fit read**: alongside sound, ask what the name's *meaning* signals and whether it matches the intended story and the Step 1 target feeling. A name can be phonetically excellent and semantically off. Advisory, not scored.
2. Write a framing sentence for the gates: these three are **soft flags a human weighs, not automatic disqualifiers**. A phonetically excellent name that trips a gate is still presented as a finalist with the flag called out — this preserves the skill's advisory "here are the trade-offs" tone. (Explicitly note this departs from the source rubric's hard two-gate model.)
3. **Off-category pull gate:** flag when the name's *meaning* drags toward the wrong category and overpowers this project's intended story. Give the rubric examples as *illustrations, not the universe*: medical/biology reads (e.g. Artery, Vital, Florence), or strong borrowed place-names (e.g. Cairo, Geneva) whose pre-existing identity swamps the brand. Generalize the rule: "any category-pull stronger than this project's intended story." Flag it; the human decides.
4. **Scale gate (conditional):** flag when a name sounds tool/feature-sized rather than platform-sized — a dimension distinct from sound quality. State the condition plainly: this is **only** a liability when the thing being named is meant to be a platform or master brand. For a single-purpose app or an intended sub-brand, tool-sized is correct — keep this gate quiet, or route a too-small-for-a-platform name to "good sub-brand," not "problem."
5. **Ownability gate:** a trademark + marketplace-clutter read in **the categories relevant to this project** (not a fixed AI/fintech/security list — generalize it). Apply it as a *modifier on an otherwise-strong name*, not a first-class score: a strong name with clutter routes to "advance only with real trademark review," never an automatic kill. State that this builds on **Step 9 (Check marketplace friction)** — Step 9 gathers the signal, this gate interprets it as a soft modifier — and do **not** duplicate Step 9's checklist here.

### Task 3: Add the balanced-sheet verdict format
What: Add a short subsection describing the optional presentation shape for a finalist — two genuine strengths → the governing liability → the gated recommendation.
Used by: Anyone presenting a finalist; referenced from the Final Decision Rule / Step 10 wiring in Task 4.
Depends on: Task 2 (references the three gate flags; place this as a subsection at the end of the Task 2 section).
Files: `plugins/naming/skills/craft-name/SKILL.md`
Interfaces:
- Consumes: The three gates from Task 2 (a gate flag can be the "governing liability").
- Produces: A subsection titled `### Balanced-sheet verdict (optional presentation format)` (exact heading referenced by Task 4).

Implementation steps:
1. Write `### Balanced-sheet verdict (optional presentation format)` as a subsection at the end of the Task 2 section.
2. Describe the three-part shape: **(1) two genuine strengths** — real and specific, drawn from sound and/or meaning; **(2) the governing liability** — the single thing most likely to sink the name (a gate flag, a colliding seam, a clutter risk); **(3) the gated recommendation** — advisory, one of: advance / advance only with trademark review / good sub-brand / reconsider, with the trade-off named rather than hidden.
3. State that this is **one option, not mandatory**, and that it pairs naturally with the three gates and the existing Scoring Template.

### Task 4: Wire the new content into the Generation Process and run the consistency sweep
What: Add references from the existing process steps so the new sound-symbolism read, meaning-fit read, three gates, and balanced-sheet verdict are actually invoked during evaluation — then verify no existing section (seam test, cluster guidance, Warning Signs, Open vowel sounds) now contradicts the neutral phoneme table or references the deleted heading.
Used by: The whole skill — this is what makes the additions part of the flow rather than orphaned sections.
Depends on: Tasks 1, 2, and 3 (references their exact headings).
Files: `plugins/naming/skills/craft-name/SKILL.md`
Interfaces:
- Consumes: `## Sound Symbolism: Phoneme → Sensation` (Task 1), `## Meaning & Strategic Fit: the Read and the Three Gates` (Task 2), `### Balanced-sheet verdict (optional presentation format)` (Task 3).
- Produces: nothing — terminal task.

Implementation steps:
1. In **Step 4 (Run the mouth-feel screen)**, after the scoring table and its weighting note, add a line directing the reader to also read each finalist's *sound* against the Step 1 target feeling using "Sound Symbolism: Phoneme → Sensation," and its *meaning* against the gates in "Meaning & Strategic Fit." Keep the mouth-feel table itself intact.
2. In **Step 9 (Check marketplace friction)**, add one line noting this pass feeds the **Ownability gate** as a soft modifier (link by name to the Meaning & Strategic Fit section) — do not move or rewrite the existing checklist.
3. In **Step 10 (Choose ...)** and/or the **Final Decision Rule** section, add a line that a finalist may be presented in **balanced-sheet verdict** form with any tripped gate flags named for the user to weigh. Do not delete the existing "Would someone enjoy saying this name?" rule — the sound side stays primary; this augments it.
4. Consistency sweep — read and confirm, adjusting wording only where an actual contradiction exists:
   - "Avoid awkward consonant clusters" (existing section 4) and the new table's "consonant clusters → friction/slowness" are both neutral and must not reintroduce "hard = good"; leave section 4's "sometimes heaviness is the point" framing intact.
   - The compound-word seam test (section 8), its Step 6 reference, and the Warning Signs bullets stay as-is — they are about seams/collisions, orthogonal to the phoneme table; confirm no wording conflict.
   - Grep the file for any remaining reference to "Quick Phonetic Heuristics" and update it to the new heading if found.
   - Confirm the "Open vowel sounds" subsection is not now duplicated by the front/back vowel rows (Task 1 added a cross-ref instead of restating).

## Edge Cases
| Edge case | Handled in | Approach |
|-----------|-----------|----------|
| Target feeling wants softness (calm/warm/premium) | Task 1 | Phoneme table + onset–center–coda framed neutrally; soft nasals/liquids/open endings read on-target, never as defects, when the target is soft |
| Naming a single-purpose app, not a platform | Task 2 | Scale gate is conditional — stays quiet or routes to "good sub-brand" when a platform is not the goal |
| A gate trips on an otherwise-excellent name | Task 2 | Soft-flag framing — name is still presented as a finalist with the flag called out, never auto-removed or auto-demoted |
| Overlap/contradiction with existing content | Task 4 | Consistency sweep reconciles seam test, cluster guidance, Warning Signs, Open vowel sounds, and removes the old heading |

## Out of Scope
- The rubric's Diamond / strategic-brief framing.
- The full per-candidate 0–3 numeric scoring sheet (`CANDIDATE / BLOCK Z / BLOCK S / STRATEGIC EXPRESSIVENESS` template).
- Hard disqualifying gates / the two-gate Kill/Hold/Advance decision table — replaced by soft flags.
- The rubric's fixed target-attribute list (speed/command/investigation/etc.) as skill canon.
- Any change to the frontmatter `description`, plugin registration, or other skills.
