---
type: debt
scope: repo
status: open
first_recorded: 2026-08-23
cycles: [retro-inside-pr]
recurrence: 1
files:
  - plugins/dev/skills/plan/SKILL.md
possibly_related_to: debt-stage-metrics-blind-to-revisions-and-done
---

**What's wrong:** `dev:plan` Step 7 stamps `metrics.stage_timestamps.plan_end`, and Step 7a's cold
review plus its autopilot revision loop run **after** it. So `plan_end - plan_start` excludes the
challenger entirely. Measured on `retro-inside-pr`: Plan reported 6 minutes against roughly 34
actually spent, with the missing 28 minutes silently attributed to the gap before Build.

**Why deferred:** Surfaced at Reflect, after the stage that would carry the fix had already run, and
it is a measurement defect rather than a behavior one — no stage acts on the value. Recording it
costs the next cycle a one-line edit; leaving it unrecorded costs every future retrospective a
wrong number.

**Done looks like:** `plan_end` is re-stamped after Step 7a's loop settles, mirroring `dev:spec`
Step 13's existing `spec_end` re-stamp on revision — an established shape in this repo, not a new
design. `dev:reflect`'s stage-duration reading then attributes challenger time to Plan.

**Cost if not paid:** `dev:reflect` Step 2's stage-duration-outlier dimension is one of its few
quantitative signals, and it under-reports Plan by the whole challenger loop on every cycle. The
error scales with tier — deep permits 5 iterations — so it is largest exactly where the loop is most
expensive and most worth seeing. A future cycle tuning challenger economics would read Plan as cheap
and look elsewhere.
