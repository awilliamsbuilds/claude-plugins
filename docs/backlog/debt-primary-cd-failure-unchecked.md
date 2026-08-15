---
type: debt
scope: repo
status: open
severity: P3
first_recorded: 2026-08-11
cycles: [autopilot-handoff]
recurrence: 1
possibly_related_to: debt-primary-path-relative-in-dev-headers
files:
  - plugins/dev/skills/autopilot/SKILL.md
  - plugins/dev/skills/build/SKILL.md
  - plugins/dev/skills/debt/SKILL.md
  - plugins/dev/skills/dev/SKILL.md
  - plugins/dev/skills/done/SKILL.md
  - plugins/dev/skills/linear/SKILL.md
  - plugins/dev/skills/migrate-tracker/SKILL.md
  - plugins/dev/skills/plan/SKILL.md
  - plugins/dev/skills/pr/SKILL.md
  - plugins/dev/skills/reflect/SKILL.md
  - plugins/dev/skills/shape/SKILL.md
  - plugins/dev/skills/spec/SKILL.md
  - plugins/dev/skills/validate/SKILL.md
---

**What's wrong:** The canonical `PRIMARY` snippet checks only its first line. Line 2 —
`PRIMARY=$(cd "$(dirname "$GIT_COMMON")" && pwd)` — has no failure branch: if the `cd` fails
(git dir deleted between the two commands, a stale `--git-common-dir` in a pruned worktree,
a permissions change), the command substitution yields the empty string and the assignment
still succeeds. Every downstream path then becomes root-absolute: `$PRIMARY/.dev-worktrees/…`
→ `/.dev-worktrees/…`. Reads miss harmlessly, but `dev:spec` Step 6's
`git -C "$PRIMARY" worktree add "$PRIMARY/.dev-worktrees/<feature>"` would attempt a write at
filesystem root.

**Why deferred:** Not a regression — the pre-cycle one-liner was equally unchecked, and the
autopilot-handoff cycle strictly improved it by adding the `||` branch to line 1. Closing it
means a coordinated edit across 13 files, which is its own cycle rather than a Validate fix.

**Done looks like:** All 13 sites carry a non-empty check after the derivation — e.g.
`if [ -z "$PRIMARY" ]; then echo "Could not resolve the primary checkout."; exit 1; fi` —
and `grep -rn 'PRIMARY=' plugins/dev/skills/*/SKILL.md` shows every hit followed by that guard.
Keep the healthy path exiting 0 (`if`, not `[ … ] && …`).
