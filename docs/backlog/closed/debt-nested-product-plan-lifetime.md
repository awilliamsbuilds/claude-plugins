---
type: debt
scope: repo
status: closed
closed: 2026-07-29
closed_by: product-plan-correction
first_recorded: 2026-07-22
cycles: [tech-debt-tracking]
recurrence: 1
files:
  - plugins/dev/skills/spec/SKILL.md
  - plugins/dev/skills/done/SKILL.md
---

**What's wrong:** A nested product plan lives at `docs/dev/<parent>/product-plan.md` — inside
the parent's own cycle directory. `dev:done` Step 7 runs `rm -rf "$WORKDIR/docs/dev/<feature>/"`,
so the moment the parent cycle completes, its nested plan is deleted along with everything else
in that directory. A nested plan structurally cannot outlive the parent it decomposes. This is
the same disease the tech-debt tracker was built to treat: a record meant to be durable, stored
inside a directory designed to be destroyed.
**Why deferred:** Found by the tech-debt-tracking cycle's grounding sweep and explicitly placed
out of scope in its spec. Best fixed by a later cycle already working in those files — which is
the behavior this tracker exists to enable.
**Done looks like:** A nested product plan survives its parent's `dev:done`, either by living
one level up (as `docs/dev/tech-debt.md` does) or by being archived into `docs/decisions/`
before Step 7's cleanup.
