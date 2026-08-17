---
type: debt
scope: repo
status: closed
severity: P3
first_recorded: 2026-08-15
closed: 2026-08-17
closed_by: extract-review-skills
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
