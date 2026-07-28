---
type: debt
scope: repo
status: closed
first_recorded: 2026-07-22
cycles: [done-doc-reconciliation]
recurrence: 1
files:
  - plugins/dev/skills/fix/SKILL.md
  - plugins/dev/skills/spec/SKILL.md
  - plugins/dev/skills/done/SKILL.md
closed: 2026-07-24
closed_by: done-doc-reconciliation
---

**What's wrong:** `dev:done` interpolates `<feature>` into five double-quoted
`git commit -m "… <feature>"` strings (Steps 3, 4, 5, 6a, 7), where `$(…)` and backticks
execute. The slug is only validated against `^[a-z0-9][a-z0-9-]*$` on the argument-derived path;
the common path takes it from conversation context, and `dev:fix` derives it by kebab-casing a
Linear issue title with no character allowlist stated. Other stages have the same shape.
**Why deferred:** Found by the tech-debt-tracking cycle's security review. The right fix is at
the source — one allowlist in `dev:fix` Step 3 and `dev:spec` Step 5 closes every call site at
once — which means editing skills this cycle's spec put out of scope. Patching only the one new
call site would leave four identical ones and imply the shape was reviewed and accepted.
**Done looks like:** Feature-name derivation strips everything outside `[a-z0-9-]` after
kebab-casing and rejects a result that doesn't match `^[a-z0-9][a-z0-9-]*$`, so every downstream
interpolation is safe by construction rather than by convention.
