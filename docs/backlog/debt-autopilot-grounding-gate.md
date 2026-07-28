---
type: debt
scope: repo
status: open
first_recorded: 2026-07-21
cycles: [spec-grounding-and-clock]
recurrence: 1
files:
  - plugins/dev/skills/autopilot/SKILL.md
---

**What's wrong:** `plugins/dev/skills/autopilot/SKILL.md` (~lines 45–48) describes its own
confidence / auto-fill / stop logic but never mentions the grounding gate added to `dev:spec`
Step 7 / Step 8. Its "auto-fill remaining dimensions" line reads as if inference can clear the
path to proceed — which the gate forbids. **Behavior is safe:** autopilot delegates to
`dev:spec`, so an unverified as-is claim still surfaces through autopilot's existing "confidence
too low even after auto-fill → STOP" path. The gate is simply invisible in autopilot's own text.
**Why deferred:** Raised as issue #2 in that cycle's code review; judged a documentation gap,
not a blocker.
**Done looks like:** A one-line cross-note in autopilot's Step 2 pointing at the `dev:spec`
grounding gate.
