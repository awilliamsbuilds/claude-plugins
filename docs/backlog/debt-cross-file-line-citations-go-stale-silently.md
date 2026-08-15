---
type: debt
scope: repo
status: open
severity: P3
first_recorded: 2026-08-15
cycles: [entry-adapters]
recurrence: 1
files:
  - plugins/dev/skills/autopilot/SKILL.md
  - plugins/dev/skills/fix/SKILL.md
  - plugins/dev/skills/migrate-tracker/SKILL.md
---

**What's wrong:** `/dev` skills cite each other by `file:line`, and nothing keeps those citations
true. Editing any cited file silently invalidates every pointer into it from every other file. This
cycle broke **eight** such citations merely by inserting lines into `spec/SKILL.md`, `pr/SKILL.md`,
and `debt/SKILL.md`; seven were repaired, one could not be. The repo treats these citations as
load-bearing — the spec for this very cycle argued that leaving one pointing at a deleted file "turns
a checkable claim into an unverifiable one" — so a silently-drifting pointer is the same defect the
repo already says it cares about, arriving by a different route.

**The one that could not be repaired is the useful part of this item.**
`autopilot/SKILL.md:139` cites `spec/SKILL.md:478`, which this cycle shifted to roughly 533. Repairing
it would edit `dev:autopilot`, and this cycle's SC10 requires that file byte-identical except for
`dev:linear` rename references. So a **success criterion and a correctness fix were in direct
conflict**, and the criterion won. That conflict is structural, not a one-off: any cycle that both
edits a cited file and freezes a citing file will hit it again.

**Why deferred:** The repair is mechanical but the *design* question is not, and it is the kind that
wants its own cycle: either citations stop carrying line numbers (cite by step or section name, which
is what this cycle's repairs in `migrate-tracker` actually did), or something checks them. Choosing
between those is a contract decision across a dozen skills.

**Done looks like:** Either `/dev` skills cite each other by stable anchor (step number, section
heading) rather than by line number, and the remaining `file:line` forms are converted; or a check
exists that resolves every `file:line` citation and fails when one no longer points at what it claims.
Editing a cited file then cannot silently falsify a citation in a file the editing cycle never opened.
