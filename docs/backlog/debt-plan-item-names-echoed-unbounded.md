---
type: debt
scope: repo
status: open
first_recorded: 2026-09-06
cycles: [plan-order-near-miss]
recurrence: 1
files:
  - plugins/dev/references/product-plans.md
---

**What's wrong:** `references/product-plans.md` §L1 defines a plan item name as "the first
whitespace-delimited token after the checkbox" and places **no charset constraint** on it — unlike the
plan file's stem, which §L1 allowlists at the trust boundary. Three §L4 arms then echo
`next-item-name` verbatim: `already-done`, `mismatch`, and the `switch` answer, which interpolates it
into a pasteable `/dev:spec "<next-item-name>"` command. Item text is external-origin — a milestone
can be seeded from a `docs/backlog/` item whose body came from a Linear issue — so this is
externally-authored text reaching agent-visible output, and in the `switch` case reaching a command
the file invites a human to paste.

**Why deferred:** The gap predates the near-miss arm and sits on three arms that cycle did not touch.
Bounding `next-item-name` is a change to §L1's output contract with four call sites to re-check,
which is more than a fast-path change should carry. (`dev:spec` Step 6 and `dev:fix` Step 2b are the
callers; `dev:autopilot` Step 2 cites the behaviour; Milestone 4b will consume §L1.)

**The cost, measured:** the `plan-order-near-miss` cycle added a *fourth* echo and bounded it, then
wrote a sentence claiming it was "the one place a name is echoed without having been matched against
a normalized input." A cold reviewer caught that the claim was false. Left standing, it would have
told the next author the other three arms were already safe — the exact reading that keeps a gap open
across cycles.

**Done looks like:** §L1 constrains `item-name` and `next-item-name` to `^[a-z0-9][a-z0-9-]*$` the
way it already constrains the filename stem, and an item failing it is skipped as though it did not
exist — matching the stem rule's shape. The `switch` arm's pasteable command is the priority: an
unbounded value reaching a command line is a different class from one reaching prose.
