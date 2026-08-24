---
type: debt
scope: repo
status: open
first_recorded: 2026-08-24
cycles: [plan-linkage]
recurrence: 1
possibly_related_to: debt-plan-task-trust-boundaries
files:
  - plugins/dev/skills/plan/SKILL.md
---

**What's wrong:** `dev:plan` Step 3's task format requires `Consumes:` / `Produces:` to name what
crosses a task boundary, but not to state its **type or shape**. Step 7a's interface lens then checks
that names "align across tasks," which a pair of tasks can satisfy while disagreeing about what the
value actually is.

**Why deferred:** Surfaced at this cycle's Reflect, after the evidence accumulated across two stages
— it is a change to the plan contract, not a fix to this cycle's plan.

**The cost, measured on this cycle:** every finding that survived plan-challenger round 1 was an
untyped-boundary defect — `plan-path` returned absolute where it was consumed repo-relative; one
Linear-sourced name derived by two incompatible constructions at two call sites; the lookup's declared
output missing two fields its own output templates render. Two of those escaped Plan entirely and came
back as **P2s** at Validate, where a fix costs a full loop plus a cold re-review. Interfaces was the
only lens that never went clean.

**Done looks like:** `Produces:` (and the `State keys:` line) name a type or shape alongside each
name — absolute vs repo-relative for a path, the allowlist a slug satisfies, the fields an object
carries — and Step 7a's interface lens flags a produced value with no stated shape, the way it already
flags an undeclared `(writes: …)` mode.
