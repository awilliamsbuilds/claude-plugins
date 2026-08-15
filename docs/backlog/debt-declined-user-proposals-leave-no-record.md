---
type: debt
scope: repo
status: open
severity: P3
first_recorded: 2026-08-15
cycles: [entry-adapters]
recurrence: 1
files:
  - plugins/dev/skills/spec/SKILL.md
  - plugins/dev/skills/done/SKILL.md
---

**What's wrong:** When a user proposes scope and `/dev` declines it, nothing requires the proposal or
the reason to be recorded, and nothing distinguishes agent-authored scope cuts from overruled user
requests. `dev:spec` Step 4's YAGNI gate asks "Is [requirement] in scope for this cycle?" and
defaults to out; the spec's `## Out of Scope` is a bare bullet list with no provenance; `dev:done`
Step 5's decision-log template has a `## Key decisions` section (Decision → reason) that would be the
right home but is never required to carry a declined user proposal. The result is a record in which
dissent is invisible and every decision reads as unanimous.

**Concrete instance this was found from.** In the `fast-path` cycle the user proposed deleting the
`dev:linear` skill. It was declined on the stated ground that it was not needed, and the decision log
records only the outcome — "Today's `dev:fix` becomes `/dev:linear`. … Linear support retained." —
with no rationale for retention over removal and **no mention that removal was proposed at all**. The
next cycle (`entry-adapters`) then deleted it, which is what the user had asked for. Worse, the same
`fast-path` log already recorded under Consequences that the cycle "Enables Milestone 2
(`fast-path-backlog`, an entry adapter onto this lane)" — so the cycle that declined removal had
already written down that a superseding adapter was coming. The decline was wrong on the cycle's own
terms, and the record cannot show that anyone disagreed.

**Why this is worth carrying rather than treating as a one-off.** The cost is not the wrong call; a
dedicated cycle for the deletion was arguably the better sequencing, and `entry-adapters` found three
load-bearing things inside `dev:linear` that a rushed removal would have broken. The cost is that the
user received an unargued assertion instead of that sequencing rationale, and that no artifact
preserves the exchange — so the same proposal can be re-declined next cycle by an agent with no way
of knowing it was ever raised. That recurs by construction.

**Why deferred:** Found at `dev:reflect` Step 4 on a handed-off cycle, after the PR merged. The fix
spans two skills and touches the spec artifact's section contract, so it is a scope decision rather
than a retrospective edit.

**Done looks like:** A user proposal that `/dev` declines is recorded with attribution and reasoning
— most likely by having `dev:spec` Step 4 mark user-originated `## Out of Scope` entries as such with
a one-line reason, and `dev:done` Step 5 requiring any declined user proposal to appear under
`## Key decisions` as "Declined: <proposal> → <reason>". A declining rationale of the form "this is
not needed", with no argument attached, is explicitly named as insufficient: the reason must say
either why the thing is unnecessary or when it will be revisited.
