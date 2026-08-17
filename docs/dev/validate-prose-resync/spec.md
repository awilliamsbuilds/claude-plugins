# Validate Prose Re-sync
*Branch: feature/validate-prose-resync · Confidence: 70% — High · 2026-08-17*
*Cycle type: feature · Tier: standard*

## Intent

When a fix loop edits a block of code, the English around it that *describes* that code silently goes
stale, and nothing makes the loop check. The next reviewer catches it, which costs a whole extra loop
— a full cold subagent dispatch — to correct a sentence.

Measured on the cycle that produced this item: loop 2 added a third guard to a shell block; loop 3
existed only to fix "**Two** `case` statements" (there were now three); loop 4 existed only to fix
"**Three** branches:" above a list that now had four bullets. **Two of four loops were English
catching up to one code change.**

The cost asymmetry is the whole argument. Re-reading the subsection that contains the edited block is
**~1,060 tokens**; the reviewer dispatch it avoids measured **60,000–170,000 tokens** in this
repo's cold reviews. Roughly a 1:60 trade at worst.

This is not a rare shape. Across 28 completed cycles, **10 (36%) reached loop 3 or deeper**, and five
reached loop 5+, one running to loop 9. Not all of those are prose desync — that attribution is only
directly evidenced on one cycle — but deep loops are routine rather than exceptional, and this is one
confirmed contributor.

## Scope

**1. A re-sync rule in `dev:validate` Step 4's fix loop.**

When a fix in this loop edits a fenced code block, **re-read the prose inside the smallest enclosing
heading before the loop may exit**, and reconcile any statement that no longer describes the block.

Three properties are load-bearing, and each was chosen against a rejected alternative:

- **It is about English matching code, not about numbers.** Counts and ordinals are what went stale in
  the observed cases, but a number-hunting rule would miss every non-numeric staleness. The rule is
  stated as "does this prose still describe the block," which subsumes the numeric case.
- **It is bounded to the smallest enclosing heading**, not the file and not a fixed line radius.
  Measured on the observed failure: the edited fence was at lines 152–172 of `review/SKILL.md`, and
  **both** stale sentences (lines 174 and 192) sat inside the same `###` subsection (line 146
  onward). That subsection is 80 lines / ~1,060 tokens against a 479-line / ~5,825-token file — **16%**.
  A whole-file re-read would cost 5.5× more for no additional catch on the evidence available.
- **It does not extend to other files.** Step 4 **step 3a** already propagates a fix to declared
  canonical/mirror counterparts, which is how `dev:secure` received the same edits on the observed
  cycle. Cross-file is covered; the uncovered case is intra-file, and that is what this rule adds.

**2. The rule composes with Step 4's existing prose rule, and the spec must say how.**

Step 4 step 4 already says: *"do not rewrite correct prose during the fix loop"* — deliberately, so
polish edits do not reopen loops. Read carelessly, the new rule contradicts it.

They compose through Step 4's own existing classification. Step 4 already sorts a P3 into
**defect-class** ("a statement that is wrong, self-contradictory, or ambiguous") versus **polish**
("better phrasing for prose that is already correct"). Prose that this loop's own code edit just made
**wrong** is defect-class by that definition and is fixed inline. Prose that is merely improvable
stays deferred to Step 5a exactly as today. **The new rule adds a trigger for finding defect-class
prose; it does not widen what counts as defect-class**, and it grants no licence to polish.

**3. The fix-diff re-review checklist gains one line, which is what makes the rule enforceable.**

"Re-read the subsection" leaves no artifact — nothing distinguishes a loop that did it from one that
skipped it, and unenforceable steps in this workflow are the ones that get skipped. Step 4 step 8's
re-reviewer already reads every fix diff, and it is the party that actually caught both misses on the
observed cycle. It gains a question:

> Did this fix change a code block whose surrounding prose no longer describes it?

This is the cheapest available enforcement: no new dispatch, no new artifact, and the check runs
where it has already been demonstrated to work.

**4. The same-region recurrence rule learns to tell converging from circling.**

Step 4 step 8's **same-region recurrence** rule stops the loop when two consecutive rounds produce
findings in the same region, on the reasoning that the loop is "circling one unsettled decision
rather than converging on it." A prose-resync cascade trips it mechanically while being the opposite
of circling.

This is not hypothetical: on the observed cycle the rule triggered from loop 3 onward and was
**overridden by documented human judgment**, with the override recorded in `validation.md`. A rule
that requires a written override to behave correctly is itself a defect.

The rule gains a **converging-cascade exemption** distinguishing the two shapes. The signals that
separated them on the observed cycle, and which the exemption is built from:

- **severity is monotonically falling** across the rounds (P2 → P3 → P3), versus flat or rising;
- **no code changed after the first round** — subsequent rounds edited only prose;
- the findings are **consequences of the same earlier edit** rather than competing answers to one
  unsettled question.

Where the exemption applies, the loop continues rather than routing to Step 4a; where it does not,
today's behavior is unchanged.

## Out of Scope

- **No change to `dev:fix`'s mirrored one-round bound.** Its cap is pinned to 1, so it cannot produce a
  multi-loop cascade — the failure this cycle addresses is structurally unreachable there. Whether its
  single round should still carry the re-read is a real question, and deliberately deferred: the
  canonical/mirror relationship means it can be added later in one edit, and adding it now would widen
  a cycle whose whole premise is being small and compounding.
- **No change to `loops_max`, tier derivation, or the loop's P1/P2 fix ordering.**
- **No change to Step 5a's carrying-cost buffer or Step 5b's build check.**
- **No new `state.json` key, no new `validation.md` section.** Enforcement rides the existing
  re-review checklist rather than a new artifact — see Scope 3's rejected alternative.
- **No attempt to fix `debt-artifact-path-rule-artifact-component-unconstrained` or
  `debt-primary-cd-failure-unchecked`**, which also name `validate/SKILL.md`. Both are adjacent files,
  neither is this clause.
- **`backlog-reflect-before-pr-merge-retire-legacy-commands` stays open** — it is Milestone 3 of this
  plan and edits the stage *tail* (`done`, `reflect`, and Step 5/6), where this cycle edits Step 4's
  *loop*. Different regions of the same file, sequenced after this cycle by the plan for that reason.

## Success Criteria

1. `dev:validate` Step 4 states the re-sync rule: a fix that edits a fenced code block cannot exit the
   loop until the prose within the smallest enclosing heading has been reconciled against it. The rule
   is stated in terms of **prose describing code**, and a grep of the rule's text contains no
   number-specific trigger list.
2. The rule names its boundary explicitly as the **smallest enclosing heading**, and says why —
   both observed misses fell inside it, and a whole-file re-read costs ~5.5× for no evidenced gain.
3. Step 4 states how the new rule composes with the existing *"do not rewrite correct prose"* rule,
   in terms of the **defect-class vs polish** classification Step 4 already defines. A reader
   following both rules is never in contradiction, and the new rule demonstrably does not widen what
   counts as defect-class.
4. The **fix-diff re-review checklist** carries a question about prose no longer describing changed
   code. It is a question in that existing checklist — no new dispatch and no new artifact.
5. The **same-region recurrence** rule distinguishes a converging cascade from a circling loop, naming
   at least the falling-severity and no-code-changed-after-the-first-round signals, and states which
   behavior each shape gets. Today's behavior is unchanged for the circling shape.
6. **No `state.json` key is added**, no `validation.md` section is added, and `dev:fix` is not edited —
   verified by the diff touching only `plugins/dev/skills/validate/SKILL.md`.
7. The cycle's own Validate stage is an honest test of criterion 1: this cycle edits prose in a file
   that contains code blocks, so if the rule as written is unworkable, its own fix loop should reveal
   that.

## Happy Path

1. A fix loop iteration fixes a P1/P2 that edits a fenced code block in a skill file.
2. Before the loop's commit, the fixer re-reads the prose under the smallest heading enclosing that
   block, and reconciles any statement that no longer describes it — counts, ordinals, enumerations,
   and any other description alike.
3. Reconciliation edits ride the **same** loop commit, so no additional loop is spent on them.
4. Step 8's cold re-reviewer reads the fix diff and applies its checklist, which now asks whether
   changed code left its surrounding prose behind. On a loop that did the re-read, this returns clean.
5. The loop exits at step 9 with no open P1/P2 — one loop instead of three.

## Edge Cases

- **The fix edits prose only, no code.** The rule does not fire. Its trigger is a changed fenced block.
- **The edited block sits under no heading** (top of file, or a file with no headings). Fall back to
  the whole file — a file small enough to have no headings is cheap to re-read, so the fallback costs
  little and needs no second boundary rule.
- **The enclosing heading is very large.** The boundary is stated as the *smallest enclosing* heading,
  so a deeply nested `####` binds tighter than its parent `##`. The observed case resolved to an
  80-line `###`.
- **Reconciliation reveals a genuine defect rather than stale English** — the code is right and the
  prose describes intended behavior the code does not implement. That is a normal P1/P2 finding, fixed
  through the loop as usual, not a re-sync edit.
- **The re-read finds prose that is stale but only improvable, not wrong.** Deferred to Step 5a under
  the existing polish rule. The new rule finds it; it does not licence fixing it.
- **A cascade that is genuinely circling, not converging** — severity flat or rising, or code still
  changing each round. The recurrence exemption does not apply and today's routing to Step 4a stands.
- **Cross-file staleness** — a declared canonical/mirror counterpart in another file. Already handled
  by step 3a; the re-sync rule does not duplicate it.

## Audience

Solo developer running `/dev` across several repos, dogfooding the plugin in the repo that defines it.
Every reader of these skills is either the author or an agent executing them.

## Technical Constraints

- **Markdown-only change**, to one file. Skills are prose; there is no build system. Verification is
  the 89-test `dev:debt` viewer suite (untouched by this cycle) as a regression check, plus manual
  walkthrough of the amended loop against the observed failure.
- **The rule must cost less than the loop it prevents**, or it is not worth having. Measured margin is
  ~1,060 tokens against 60,000–170,000 — roughly 1:60. Any drafting that widens the boundary toward a
  whole-file or whole-repo re-read erodes the only reason this change pays.
- **This cycle's own Validate stage runs under the pre-merge rules**, not the new ones — the plugin
  cache reflects `main` until merge plus `/plugin update`. The rule cannot be dogfooded within the
  cycle that writes it.

## Dependencies

None external. Blocks `retro-inside-pr` (Milestone 3), which edits the same file's stage tail.
Independent of `autopilot-resume-stage`, the other Milestone 1 cycle — disjoint files, so the two may
run concurrently.

## UI Needed

No.

---
*Auto-filled dimensions: none*
*Grounding inventory: (1) "Step 4 has no rule about prose" → `grep -n "prose" validate/SKILL.md` → **false, 2 hits** (`:176`, `:177`), and they run the opposite way — "do not rewrite correct prose during the fix loop." The claim was inverted, and Scope 2 exists because of this correction. (2) "step 3a covers only cross-task counterparts, not intra-file prose" → read `:162` in full → confirmed; it keys on `plan.md`'s `Interfaces:` blocks, a registry the plan cannot hold intra-file prose adjacency in. (3) "the stale prose sat several paragraphs from the edited fence, so an adjacency rule would miss it" → **false, and I asserted it before measuring.** Measured: fence at `review/SKILL.md:152-172`, stale sentences at `:174` (two lines after) and `:192`, both under the same `###` at `:146`. This inverted the recommendation — the bounded-subsection rule became viable *because* of the measurement, having been ruled out on an unmeasured claim. (4) Subsection cost → computed: 80 lines / ~759 words / ~1,062 tokens vs 479 lines / ~5,825 tokens whole-file = 16%. (5) Reviewer dispatch cost → measured from this session's four cold reviews: 62k–173k subagent tokens. (6) "36% of cycles reach loop 3+" → `git log --grep="^validate: loop"` over `main`, loop-number distribution → 28 cycles at loop 1, 10 at loop 3+, 5 at loop 5+, max 9. Deliberately **not** claimed as all prose-desync — only one cycle is directly evidenced. (7) "`dev:fix` mirrors Step 4 step 8 and may need the same rule" → `fix/SKILL.md:700-701` → confirmed mirror, and its cap is "pinned to 1", so the cascade is structurally unreachable there; Out of Scope records the deferral rather than assuming it away. (8) Open debt intersecting `validate/SKILL.md` by front-matter `files:` sweep over the P5 corpus → **4 items**: the source item (in scope), `backlog-reflect-before-pr-merge-retire-legacy-commands` (Milestone 3, different region), and two adjacent-only (`debt-artifact-path-rule-artifact-component-unconstrained`, `debt-primary-cd-failure-unchecked`). None folded in beyond the source.*
