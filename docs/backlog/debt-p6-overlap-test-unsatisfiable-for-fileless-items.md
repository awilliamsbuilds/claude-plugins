---
type: debt
scope: repo
status: open
first_recorded: 2026-08-15
cycles: [entry-adapters]
recurrence: 1
files:
  - plugins/dev/references/tech-debt.md
---

**What's wrong:** P6's clear-match test requires that "the `files:` sets overlap **and** the
described defect is the same defect — **both** conditions, never either." An item carrying
`files: []` can never satisfy the first condition, so it can never be recurrence-merged, no matter
how plainly it is the same item. The flush's only other branch is "when uncertain, create a new
file," so a genuine recurrence of a file-less item is forced into a duplicate that P2 uniqueness then
disambiguates to `<type>-<slug>-<first-cycle>.md`. Four of the store's active items carry
`files: []` today: `backlog-debt-backfill`, `backlog-dev-skill-test-harness`,
`backlog-stage-lifecycle-telemetry-app`, `backlog-verboseness-check`. These are exactly the
repo-wide "build a thing" backlog items rather than defects localized to files, so the field is empty
by nature and not by omission.

**Why deferred:** Found while recording a recurrence against `backlog-dev-skill-test-harness` during
this cycle's Build, which is well past the point where editing the shared contract is in scope — P6
governs every producing stage and `dev:done`'s flush, so changing it is its own cycle with its own
review. The recurrence was recorded by hand instead, which is correct but does not generalize: the
next cycle to hit this will silently produce a duplicate rather than notice the rule failed.

**Done looks like:** P6's clear-match test states what an empty `files:` set means — most likely that
an empty set on **either** side makes the overlap condition inapplicable rather than false, leaving
the same-defect condition to decide alone, with the existing "never merge on topic or keyword
similarity alone" caution doing the work it already does. Recording a recurrence against a
`files: []` item then follows the documented path rather than requiring a hand edit.
