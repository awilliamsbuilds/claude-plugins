---
type: debt
scope: repo
status: open
first_recorded: 2026-10-28
cycles: [fix/skill-positional-arg-substitution]
recurrence: 1
files:
  - plugins/ux-toolkit/skills/ux-copywriter/SKILL.md
---

**What's wrong:** The Notification example reads "Your payment of $450 was declined". Claude Code substitutes `$N` positional references in a skill body with the invocation's arguments, so when the skill is invoked with arguments the example renders with an argument spliced in where the amount was.
**Why deferred:** Found by the cold code review of the reviewer arg-binding fix; it belongs to a different plugin than that change.
**Done looks like:** The example uses no dollar-digit sequence (e.g. "Your payment of 450 dollars was declined" or a different amount format), and `grep -rnE '\$[0-9]' plugins/*/skills/*/SKILL.md` returns nothing.
