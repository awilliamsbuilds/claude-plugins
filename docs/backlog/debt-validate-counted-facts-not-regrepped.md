---
type: debt
scope: repo
status: open
first_recorded: 2026-08-24
cycles: [plan-linkage]
recurrence: 1
files:
  - plugins/dev/skills/validate/SKILL.md
---

**What's wrong:** `dev:validate` Step 4's fix loop has a rule (step 3b) requiring a claim about
observable command behavior to be **measured** before the fix asserting it is committed, and one
(step 3c) re-syncing prose around an edited code block. Neither covers a third case: a fix that
changes a **counted fact** other files assert — "the 12 stage-header sites carry no guard", "the
repo's fourth guarded derivation", an item's `files:` list.

**Why deferred:** It is a new trigger in the fix loop's checklist, adjacent to but distinct from 3b
and 3c; adding it mid-cycle would have widened this cycle's own scope.

**The cost, measured on this cycle:** adding a non-empty `$PRIMARY` guard to `dev:spec` Step 6 — a
one-line fix — falsified counts asserted in `dev:fix`, `dev:secure`, `dev:review`, `CLAUDE.md`, and
`docs/backlog/debt-primary-cd-failure-unchecked.md`. Two of three validate loops went to chasing that
drift, each with its own cold re-review, and one loop's fix introduced a fresh miscount that the next
loop had to correct.

**Done looks like:** Step 4's loop carries a trigger of the form *did this fix change a number or an
enumeration that other files state?* — and where it did, a repo-wide grep for that count runs and its
hits are reconciled inside the same loop commit, the way step 3c reconciles prose inside its own.
