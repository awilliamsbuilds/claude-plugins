---
type: debt
scope: repo
status: closed
severity: P3
first_recorded: 2026-08-15
cycles: [fast-path]
recurrence: 1
closed: 2026-08-15
closed_by: entry-adapters
files:
  - plugins/dev/skills/fix/SKILL.md
---

**What's wrong:** `dev:fix`'s merge tail says in prose "if more than one **open** PR resolves for the
branch, stop and report rather than guessing," but the snippet implementing it uses
`gh pr list … --json number -q '.[0].number'`, which silently takes the first. The stated guard is not
the delivered one.

**Why deferred:** reachable only by manually opening a second PR from the same head branch to a
different base, which the lane itself never does. Non-blocking, and found after the cycle's Validate
loop budget was spent.

**Done looks like:** the count is read (`--json number -q 'length'`) and a result greater than 1 stops
with both PR numbers named, matching what the prose already promises.
