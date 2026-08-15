---
type: debt
scope: repo
status: open
severity: Nit
first_recorded: 2026-08-15
cycles: [entry-adapters]
recurrence: 1
files:
  - plugins/dev/skills/init/SKILL.md
  - plugins/dev/skills/done/SKILL.md
---

**What's wrong:** Skills live at `plugins/dev/skills/<name>/SKILL.md` and shared references at
`plugins/dev/references/`, so a reference must be cited as `../../references/<file>.md`. Several
sites instead write a bare `references/<file>.md`, which resolves to nothing from a skill directory.
This cycle found and fixed seven such paths (five in `migrate-tracker`, one in `done`, one in
`debt`); two remain at `init/SKILL.md:162` and `done/SKILL.md:264`.

**Why deferred:** Both remaining sites are pre-existing and neither file was otherwise in this
cycle's scope — and `done/SKILL.md` carried an additional constraint, since SC10 limited this cycle's
edits to that file to `dev:linear` rename references. Fixing them is a two-line change that belongs
with whatever next opens those files, not a reason to widen this cycle.

**Done looks like:** `grep -rn '](references/' plugins/dev/skills/` returns zero — every reference
citation from a skill directory carries the `../../` prefix that actually resolves.
