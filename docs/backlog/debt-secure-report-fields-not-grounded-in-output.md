---
type: debt
scope: repo
status: open
severity: P3
first_recorded: 2026-08-15
cycles: [retire-legacy-commands]
recurrence: 1
files:
  - plugins/dev/skills/secure/SKILL.md
---

**What's wrong:** Two places in `dev:secure`'s `diff` verb ask an agent to fill a report field from
shell state it never observes. `AUDIT_BRANCH` is assigned but only ever echoed inside the divergence
notice, which stays silent on the primary checkout — the exact `dev:fix` path — so the report's
`**Branch audited:**` field gets interpolated from recall rather than from output. Relatedly,
`BASE="$2"` is the only positional-parameter notation in any `dev` skill and has no script or
function context to bind in; executed verbatim it yields an empty value. That one fails loudly (the
next guard stops on it), but both share a root: shell written into a skill that is not runnable as
written, feeding a value a later step reports as fact.

**Why deferred:** Part of the same circling region the `same-region recurrence` rule closed off, so
no further fixes were attempted there this cycle. The fix is small but wants doing once across the
verb rather than patched per-field, and it is adjacent to the tree-scoping decision in
[[debt-secure-tree-scoping-unsettled]] — that decision may change which values the report carries at
all.

**Done looks like:** Every value `dev:secure` reports is either printed by a command the skill runs
or derived in the same step that reports it, and no shell snippet in the skill depends on a binding
the surrounding context does not provide. `dev:validate` Step 4 step 3b's measured-claims rule
applied to the skill's own report fields.
