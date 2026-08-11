---
type: debt
scope: repo
status: open
severity: Nit
first_recorded: 2026-08-11
cycles: [autopilot-handoff]
recurrence: 1
files:
  - plugins/dev/skills/autopilot/SKILL.md
  - plugins/dev/skills/build/SKILL.md
  - plugins/dev/skills/done/SKILL.md
  - plugins/dev/skills/plan/SKILL.md
  - plugins/dev/skills/pr/SKILL.md
  - plugins/dev/skills/shape/SKILL.md
  - plugins/dev/skills/validate/SKILL.md
---

**What's wrong:** The shared artifact-path validation rule constrains only `<feature>`
(`^[a-z0-9][a-z0-9-]*$`, no `..` segments). The `<artifact>` component is bounded only by the
whole-path `..` ban, so a value like `docs/dev/real-feature/~%2Fssh%2Fid_rsa.md` parses as valid.

**Why deferred:** Inert today — `dev:autopilot` derives only `<feature>` and never opens the
named artifact. Recorded because the rule is stated identically in seven skills, several of which
*do* read the artifact the path names, and because this cycle advertised the argument form to
users at two gates and in two reference surfaces, widening who types these paths.

**Done looks like:** The shared rule constrains `<artifact>` to the known set
(`spec|design|plan|validation`) alongside its `<feature>` regex, restated identically in all
seven skills — or the rule is factored so there is one statement of it to change.
