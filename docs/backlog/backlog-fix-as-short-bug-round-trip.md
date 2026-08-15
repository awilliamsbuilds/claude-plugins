---
type: backlog
scope: repo
status: promoted
promoted_to: docs/dev/product-plans/dev-fast-path.md
first_recorded: 2026-08-12
cycles: [manual]
recurrence: 1
files:
  - plugins/dev/skills/fix/SKILL.md
---

**What:** Make `/fix` a short round trip for bugs, and decide what becomes of `dev:fix`'s current
role as an entry point into the full seven-stage cycle.
**Why:** `dev:fix` today opens the *whole* workflow — someone typing `/fix` for a small bug gets
spec, shape, plan, build, validate, PR, done. The name promises close to the opposite of what it
delivers, and `/fix` is the scarce thing worth spending on the fast path. This was originally
captured tangled with a second question — how `/fix` and `/dev:debt` should divide the Linear seam —
but the decision to stop investing in Linear settles that half: `backlog-debt-linear-promotion` is
cancelled, `dev:debt` no longer reaches toward an external tracker, and the two skills no longer
compete for the same territory. What remains is a scope-and-naming question about `/fix` alone.
`/dev`'s Micro tier is the likely mechanism for the short path.
**Done looks like:** `/fix` runs a short bug round trip instead of opening the full cycle, and the
Linear-issue entry path is either retired or renamed to something that describes what it does.
