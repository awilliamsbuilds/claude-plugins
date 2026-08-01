---
type: debt
scope: repo
status: open
severity: P3
first_recorded: 2026-08-01
cycles: [reflect-pr-base-explicit-target]
recurrence: 1
files:
  - plugins/dev/skills/build/SKILL.md
  - plugins/dev/skills/debt/SKILL.md
  - plugins/dev/skills/dev/SKILL.md
  - plugins/dev/skills/done/SKILL.md
  - plugins/dev/skills/fix/SKILL.md
  - plugins/dev/skills/plan/SKILL.md
  - plugins/dev/skills/pr/SKILL.md
  - plugins/dev/skills/reflect/SKILL.md
  - plugins/dev/skills/shape/SKILL.md
  - plugins/dev/skills/spec/SKILL.md
  - plugins/dev/skills/validate/SKILL.md
---

**What's wrong:** All eleven `/dev` stage skills open with the same working-directory block,
deriving `PRIMARY=$(dirname "$(git rev-parse --git-common-dir)")`. That is absolute only when run
from inside a linked worktree; from the primary checkout `git rev-parse --git-common-dir` returns a
*relative* path — `.git` at the root, `../../../.git` further down, depth-dependent — so `$PRIMARY`
becomes `.` or `../..`. `$WORKDIR` is built from `$PRIMARY` and inherits it. Every later use as a
`cd` or `git -C` target therefore silently resolves against whatever cwd the shell holds at that
moment, and any equality test between a normalized path and a raw `$PRIMARY`/`$WORKDIR` compares an
absolute string to a relative one and misses. Measured in this repo: primary root → `.`, three
levels down → `../../../.git`, worktree (root and subdir) → absolute.

**Why deferred:** `reflect-pr-base-explicit-target` was scoped to step 2 of one section of one
skill. The correct fix edits the shared header block — one line in each of eleven files — which is a
different surface with its own blast radius, and the cycle's spec put everything outside that step
out of scope. Step 2 works around it locally by normalizing both sides before comparing.

**Done looks like:** the header derives `PRIMARY` already absolute, in the single invocation that
computes it, e.g. `PRIMARY=$(cd "$(dirname "$(git rev-parse --git-common-dir)")" && pwd)`, applied
uniformly across the eleven skills. `$WORKDIR` is then absolute by construction, and per-site
normalization caveats (including the one added at `reflect/SKILL.md` step 2) can be dropped.
