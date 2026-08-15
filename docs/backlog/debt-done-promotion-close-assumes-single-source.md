---
type: debt
scope: repo
status: open
first_recorded: 2026-08-15
cycles: [manual]
recurrence: 1
files:
  - plugins/dev/skills/done/SKILL.md
  - plugins/dev/references/tech-debt.md
---

**What's wrong:** `dev:done` Step 3b's reverse-lookup finds the backlog item whose front-matter
carries `promoted_to: <plan-path>` and closes it as the promotion terminus, asserting that "by the
one-way invariant there is at most one such match." That assertion does not hold. The
`dev-observability` plan was promoted from **two** items — `backlog-backlog-viewer-app` and
`backlog-stage-lifecycle-telemetry-app` — both carrying the same `promoted_to` and both
`status: promoted`, and the plan's own header states it was promoted from two items, so many-to-one
promotion is a supported input rather than a corrupted state. The step does not say whether to close
every match, the first, or none, and it runs exactly once, at project completion, in the same commit
that deletes the plan file. Whatever it does there is unrecoverable from the plan, which is gone.

A related gap sits one level up: a source item whose own `Done looks like:` is satisfied by an early
milestone stays `status: promoted` until the *whole* plan completes. `backlog-backlog-viewer-app` was
fully delivered by Milestone 1 but would have read `promoted` through Milestones 2–3, which are the
other item's scope — inverting the reason `dev:debt list` surfaces `promoted` at all.

**Why deferred:** Found by inspection while reviewing the store after the `backlog-viewer` cycle, not
by a failure — the plan is 1/4 complete, so Step 3b has not fired. `backlog-backlog-viewer-app` was
closed by hand at that point, which incidentally leaves this plan with a single `status: promoted`
match and defuses the case for this plan only. The defect stands for the next multi-source promotion.

**Done looks like:** Step 3b states its behavior when the reverse-lookup returns more than one match
— close every match, or stop and ask — and the "at most one" claim is either corrected or backed by a
rule in `references/tech-debt.md` that actually forbids many-to-one promotion. Ideally `dev:spec`'s
promotion step and `dev:done`'s terminus agree on which one they implement, since today spec can
create the many-to-one case that done assumes away.
