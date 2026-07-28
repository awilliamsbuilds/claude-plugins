---
type: debt
scope: repo
status: closed
first_recorded: 2026-07-22
cycles: [init-rerun-hardening]
recurrence: 1
files:
  - plugins/dev/skills/spec/SKILL.md
closed: 2026-07-23
closed_by: init-rerun-hardening
---

**What's wrong:** `dev:spec` Step 4's product-plan procedure mandates a direct push to
`origin/main`. That conflicts with the standing "never commit directly to `main`" convention —
a repo with branch protection on `main` will simply reject the push, and a repo without it gets
an unreviewed commit on its default branch.
**Why deferred:** Found by the tech-debt-tracking cycle's grounding sweep and explicitly placed
out of scope in its spec. Best fixed by a later cycle already working in that file — which is
the behavior this tracker exists to enable.
**Done looks like:** The product plan lands on `main` through the same branch-and-PR path every
other change uses, or the procedure documents explicitly why this one file is exempt.
