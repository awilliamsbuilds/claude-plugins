---
type: debt
scope: repo
status: open
severity: P3
first_recorded: 2026-08-23
cycles: [retro-inside-pr]
recurrence: 1
files:
  - plugins/dev/skills/pr/SKILL.md
  - plugins/dev/skills/reflect/SKILL.md
---

**What's wrong:** Four prose defects surfaced by the loop-2 fix-diff re-review, left unfixed when
Step 4's circuit breaker tripped. Each is a stale or inaccurate cross-reference, with its fix already
drafted:

  1. `reflect/SKILL.md` Step 5 — "It is **not** correct on the standalone route **below**" points the
     wrong way. Loop 2 moved the standalone-route paragraph *above* the bare-push paragraph. Change
     "below" to "above".
  2. `pr/SKILL.md` "Push and display" — the second justification example, "a stage resumed after
     reflect already ran", does not hold: on re-entry Step 5d re-invokes `dev:reflect`, whose Step 5
     `git push` sits outside the commit guard and runs unconditionally, so Step 5d *does* reach its
     push there. Drop the clause, or replace it with "a `dev:reflect` that takes its standalone route,
     which skips the push by design." The first example ("a `dev:reflect` that stops early") is sound
     and carries the justification alone.
  3. `reflect/SKILL.md` Step 5 standalone route, shape (b) — the stated reason is worktree-only. On a
     **legacy in-place cycle** `dev:done` Step 2 runs `checkout "$INTEGRATION"` (attached, with an
     upstream), so the bare push would *succeed* and land the commit straight on the integration
     branch. Routing is already correct (the trigger is the branch test), but the reason understates
     the hazard and invites a later editor to conclude the skip is unnecessary. Append: "on a legacy
     in-place cycle `$WORKDIR` is *on* `$INTEGRATION` instead, where the same bare push would silently
     land the commit on the integration branch. Either way the push must not run."
  4. `pr/SKILL.md` "Push and display" — malformed punctuation `skip.):`; the period belongs inside the
     parenthesis and the colon at the end of the preceding sentence.

**Why deferred:** Step 4's circuit breaker fired. Loop 2's cosmetic roster-ordering edit introduced a
duplicated `dev:validate` in the canonical Mode-symmetry roster, which loop 3's re-review caught as a
P2 — a new P2 attributed to a cosmetic fix, which is exactly the breaker's trigger. The next cycle
pays a small, bounded cost: four one-line edits with fixes already written out above, so the work is
re-reading rather than re-deriving. The cost of *not* deferring is the one just measured — each
further cosmetic pass over this prose has a demonstrated chance of introducing a defect worse than
the one it fixes, and items 1-4 are all non-load-bearing (a directional word, two justification
examples, and punctuation); none changes what any step does.

**Done looks like:** All four edits applied in one pass, with the whole enclosing section re-read once
afterwards rather than each line patched in isolation.
