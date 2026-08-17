---
type: debt
scope: repo
status: open
first_recorded: 2026-08-16
cycles: [extract-review-skills]
recurrence: 1
possibly_related_to: debt-spec-grounding-citation-unverified
files:
  - plugins/dev/skills/spec/SKILL.md
---

**What's wrong:** `dev:spec` Step 7's grounding inventory records a sweep's *result* but nothing
re-derives its *input set* when scope later grows. Step 7 runs once, early; Step 12a's revisions then
add files to the cycle. The recorded count keeps looking authoritative — it was produced by a real
command — while having been computed over a file set that no longer matches the spec.

Measured in this cycle, the open-debt `files:` sweep was restated three times and was wrong at every
step before the last: **6** items, then **8** once Scope 9 added `dev/SKILL.md`, then **12** once
`spec/SKILL.md` and `plan/SKILL.md` were recognized as edited by item 7, then **17** once
`references/tech-debt.md` was included. Each correction came from a *cold reviewer re-running the
sweep*, never from the spec noticing its own input had changed.

Note the shape, which is the same one `debt-spec-grounding-citation-unverified` records for a
different reason: neither `spec_revisions` (0) nor `confidence.final_score` (100 / Ready) can see
this class. Both measure internal coherence, and a spec that consistently reasons over a stale set is
perfectly coherent with itself.

**User observation at Reflect (this cycle) sharpens the diagnosis and the fix.** The recurrence is
partly the review loop *chasing its own tail*: item 7's own edits added `spec/SKILL.md` and
`plan/SKILL.md` to the cycle's file set, which is what created the 8 → 12 gap. So a fourth spec
review would not converge — each round can enlarge the set the next round must sweep. The user's
conclusion, recorded verbatim in substance: **a build-time check would catch this class better than
another spec review.** That reframes the fix from "re-run the sweep on revision" to "verify the sweep
at the stage that knows the final file set."

**Why deferred:** Three of this cycle's sixteen challenger blockers were stale enumerations, each
costing a full cold-review round — roughly one round in three spent re-deriving a set the spec had
already claimed to have swept. The `files:` sweep gates which open debt gets named in Out of Scope, so
a stale set silently drops items from a cycle's declared surface; here it omitted eleven of seventeen
at the first pass. Left alone, every multi-revision cycle re-pays this, and the cost scales with how
much Step 12a improves the spec — the better the challenger works, the staler Step 7's sweeps get.

Deferred rather than patched because the right form is not obvious and touches two places, and the
Reflect observation adds a third candidate location (Build or Validate rather than Spec). A blanket
"re-run every sweep each revision" would be expensive, would still miss the pattern-too-narrow
variant, and — per the tail-chasing note above — would not terminate.

**Done looks like:** a grounding-inventory entry whose claim depends on a file set records that set,
and the claim is verified against the cycle's *final* file set at a stage that knows it, rather than
re-swept at each spec revision. A Scope edit that adds a file cannot leave an earlier count standing
as authoritative.
