---
type: debt
scope: repo
status: open
first_recorded: 2026-07-28
cycles: [tech-debt-migration]
recurrence: 1
files:
  - plugins/dev/skills/spec/SKILL.md
  - plugins/dev/skills/plan/SKILL.md
  - plugins/dev/skills/build/SKILL.md
  - plugins/dev/skills/validate/SKILL.md
---

**What's wrong:** Each `/dev` stage commits its artifact and its state advancement at two
different moments. Spec commits `spec.md` at write time but only advances `completed[]` += "spec"
/ `stage` -> "plan" at the Step 13 approval gate (spec `SKILL.md:560`). Plan commits `plan.md` at
Step 7 (`plan/SKILL.md:187`) but only advances `completed[]` += "plan" / `stage` -> "build" at the
Step 8 approval gate (`plan/SKILL.md:277`). The challenger steps in between (spec Step 12a, plan
Step 7a) write `state.json` in place, uncommitted, "carried by the next commit" (`plan/SKILL.md:245`,
spec `SKILL.md:520`). So between "artifact committed" and "approval committed," the working tree
holds an uncommitted challenge value and the committed `state.json` still points at the earlier
stage. If the gate is interrupted — a `/clear`, a session end, or any discard of working-tree
changes before the approval commit — committed `state.json` lags the artifacts and commits that
prove the stage was actually reached, and the maintainer must reconstruct the true sequence by hand
("state repair"). Observed recurring across cycles. Plan's resume-mid-approval check
(`plan/SKILL.md:49`) covers only the single-stage-lag case; Build and Validate trust committed
`state.json` on entry with no reconciliation.
**Why deferred:** Surfaced at the tech-debt-migration retrospective. The fix is cross-cutting —
it changes the state-commit model across spec/plan/build/validate — so it is too broad for a
minimal targeted skill edit and warrants its own `/dev` cycle with a proper spec/design, rather
than an inline patch during close-out.
**Done looks like:** State advancement survives an interrupted gate without manual repair — either
`completed[]`/`stage` is committed atomically with the stage artifact, or each stage's entry runs a
reconciliation step that repairs committed `state.json` when it lags the on-disk artifacts+commits
(generalizing plan's existing resume-mid-approval check to Build and Validate and to multi-stage
lag). The challenger's in-place `state.json` writes no longer leave advancement uncommitted at the
gate.
