---
type: debt
scope: plugin
status: closed
closed: 2026-08-23
closed_by: retro-inside-pr
first_recorded: 2026-08-20
cycles: [autopilot-resume-stage]
recurrence: 1
files: [plugins/dev/skills/autopilot/SKILL.md, plugins/dev/skills/pr/SKILL.md]
severity: P3
---

**What's wrong:** `dev:autopilot` Step 3's Start stage rule executes every row stage from the
resolved entry point onward, including stages already in `completed[]`. PR is not safely
re-enterable under that rule: `dev:pr` Step 4 runs `gh pr create` unconditionally, which fails on a
second create against the same branch. Reaching PR with `artifacts.pr_url` already set therefore
stops an unattended run at its last step.

  Not currently reachable — producing it needs a `completed[]` holding `"pr"` while an earlier row
  stage is missing, and the only documented remover (`dev:build` Step 4, `build/SKILL.md:133`) removes
  `"plan"`, which sits before Build rather than after PR.

**Why deferred:** A fix attempted inside this cycle's validation loop asserted that the re-run
stages would have pushed their commits, so the open PR already carried them. That is false: the
feature branch is published in exactly one place, `pr/SKILL.md:142`, and skipping the stage skips
the push — so `dev:done` would merge a stale remote head and then force-delete the branch, silently
discarding the run's work. The reviewer caught it as a P1 and the exception was removed. Settling it
properly means deciding what a re-run owes an already-open PR (re-push and reuse the URL? re-target?
re-write the PR body's `## Validation` section, which describes the earlier loop?) — a design
question, not a clause.

**Done looks like:** `dev:autopilot` and `dev:pr` agree on one stated rule for re-entering PR on a
cycle whose `artifacts.pr_url` is already set, with the branch push preserved on every path that
reaches `dev:done`.

**Cost if not paid:** the next cycle that makes a non-contiguous `completed[]` reachable — any
change letting a stage after PR be removed, or a new backtrack path — turns a latent stop into a
live one. The obvious one-line fix is the one already measured to cause silent work loss, and the
next person will reach for it, because the reasoning that makes it wrong is recorded nowhere else.
