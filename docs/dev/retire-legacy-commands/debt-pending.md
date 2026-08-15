# Debt Pending — retire-legacy-commands

Buffered backlog/debt items for this cycle. `dev:done` Step 6a flushes `## To Record` into
`docs/backlog/` and executes each `## To Close` close-intent, then Step 7 deletes this file. Nothing
else reads it.

## To Record

### debt-secure-tree-scoping-unsettled
````markdown
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

**What's wrong:** `dev:secure` anchors both verbs to `$PRIMARY`, the primary checkout. On a repo
with active `/dev` worktrees the primary is usually sitting on the default branch while the work a
user cares about is on a worktree's branch, so a standalone run audits the wrong tree. The `diff`
verb now *discloses* this (a notice, the audited branch in the report header, and an empty-diff
message naming branch and base), but two gaps remain. First, the notice's remediation line says to
"run from the primary checkout of it" — unactionable, because all worktrees of a repo share one
primary checkout, so following it reproduces the identical audit. Second, the **whole-project** verb
has the same exposure and no disclosure at all; unlike `diff` it does not come back empty, it comes
back looking like a completed clean audit of code the user is not looking at, which is the more
dangerous of the two shapes.

**Why deferred:** Surfaced by `dev:validate`'s **same-region recurrence** rule — two consecutive fix
loops produced findings in this region, which is the signal that the loop is circling an unsettled
decision rather than converging on it. The decision underneath is genuinely the user's: `dev:fix`
requires `$PRIMARY` (it operates there by contract and its PR opens from that tree), while a human
standing in a worktree means "audit what I am looking at." Serving both needs either a third
argument, a caller-supplied tree, or a documented refusal — a design choice, not a fix-loop edit.

**Done looks like:** `dev:secure` states one rule for which tree each verb audits that is correct for
both the `dev:fix` call path and standalone worktree use, the whole-project verb names the tree it
audited in its report exactly as the `diff` verb now does, and no remediation line instructs an
action that cannot change the outcome.
````

### debt-secure-report-fields-not-grounded-in-output
````markdown
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
````

## To Close

- debt-validate-fix-claims-unmeasured — this cycle writes build-detection shell (package.json scripts, Makefile targets, cargo/go) into two skills, which is exactly the claims-about-tools class the item names; the rule lands in `dev:validate` Step 4, a file this cycle already opens
- debt-bare-reference-paths-do-not-resolve — the two remaining bare `references/` paths in `init/SKILL.md` and `done/SKILL.md`; a two-line change folded in deliberately rather than opportunistically, since the cycle is already touching the reference-citation convention
