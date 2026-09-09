---
type: backlog
scope: repo
status: open
first_recorded: 2026-09-09
cycles: [dev-process-hardening-closeout]
recurrence: 1
files:
  - plugins/dev/references/tech-debt.md
  - plugins/dev/skills/done/SKILL.md
  - plugins/dev/skills/dev/SKILL.md
---

**What:** Give a product-plan milestone a third state — declined — and give `dev:done` a way to close
a plan whose remaining milestone was declined rather than built.

**Why:** Both gaps were hit closing `dev-process-hardening` and both had to be worked around by hand.

1. **No declined state.** Checkboxes are `- [ ]` or `- [x]`, and `dev:done` Step 3's completion
   detection is "every checkbox is `[x]`". Marking a declined milestone `[x]` reads as *shipped*;
   leaving it `[ ]` means the plan never completes, never deletes, and `/dev` Step 6 keeps offering
   it as the next item indefinitely. The closeout chose `[x]` plus an inline annotation, which is a
   convention no code enforces and no reader is told about.
2. **No path to close a plan outside a cycle.** Step 3b's deletion, its source-item close, and Step
   3's check-off all run only at a completing cycle's `dev:done`. Declining the last milestone is not
   a cycle, so the check-off, the plan deletion, the source-item close, and the project-level decision
   log were all done by hand.

**The cost, if unfixed:** every future multi-milestone project that declines anything repeats this by
hand, and the `[x]`-means-settled convention stays undocumented — so the next reader of a plan cannot
tell a shipped milestone from a declined one without opening the decision log.

**Done looks like:** The plan format carries a declined marker the completion test understands;
`dev:done` (or `dev:debt`) exposes a close-the-plan verb that performs the check-off, the deletion,
the source-item close, and the project-log write outside a cycle; and `/dev` Step 6 renders a declined
milestone as settled rather than as next up.
