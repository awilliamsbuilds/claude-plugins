---
type: backlog
scope: repo
status: open
first_recorded: 2026-08-15
cycles: [retire-legacy-commands]
recurrence: 1
possibly_related_to: backlog-reflect-before-pr-merge
files:
  - plugins/dev/skills/done/SKILL.md
  - plugins/dev/skills/reflect/SKILL.md
  - plugins/dev/skills/validate/SKILL.md
---

**What:** Move the retrospective to the end of the Validate stage so it ships **inside** the cycle's
own PR, instead of running after the merge and landing on the integration branch. Raised by the user
at `dev:reflect` Step 4: *"the retro should happen at the end of the validate stage. So the retro is
actually included in the PR versus having to do a second PR or committing it locally."*

**Why this is a recurrence, and why the prior close does not settle it.**
`backlog-reflect-before-pr-merge` asked the same question and was closed on 2026-08-15 by the
`fast-path` cycle's flush (commit `3a78f4d`, one of four closes). But `fast-path` built `/dev:fix` —
a lane that produces no decision log and no retrospective at all. It closed the question by
sidestepping it, while the seven-stage pipeline the item was actually about still merges first and
reflects after. The close also carries no `closed_by:` field, which P3 requires. Recorded as a new
item rather than a P6 merge because the original is in `closed/` and outside the active corpus.

**This cycle demonstrated the problem.** `retire-legacy-commands` merged PR #82, then wrote its
decision log and appended its retrospective directly to `main` afterwards — so the cycle's own
reasoning is absent from the PR a reviewer would read, and those commits never went through review.

**The real tension, stated so the next cycle does not rediscover it.** `dev:reflect` reviews a
*completed* cycle, and at the end of Validate the PR and merge have not happened — so
`stage_timestamps.pr_created`, the merge outcome, and `dev:done` Step 4a's docs-prose reconciliation
are not yet available. Most of what the retro actually reads *is* available by then (spec churn, both
challengers' disposition, validate loops, tier fit, token efficiency), so the question is whether the
merge-tail dimensions are worth the split. Two knock-on orderings also move: the decision log is
currently created at `dev:done` Step 5, and `dev:reflect` Step 6's buffer write is what `dev:done`
Step 6a's flush depends on running last.

**Done looks like:** The retrospective and the decision log are part of the cycle's PR diff, no
`dev:*` stage commits them directly to the integration branch, and whichever dimensions genuinely
require post-merge data are either explicitly deferred or explicitly dropped with a reason.
