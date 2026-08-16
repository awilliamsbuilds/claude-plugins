---
type: backlog
scope: repo
status: open
first_recorded: 2026-08-15
cycles: [retire-legacy-commands]
recurrence: 1
files:
  - plugins/dev/skills/dev/SKILL.md
  - plugins/dev/skills/spec/SKILL.md
  - plugins/dev/skills/done/SKILL.md
  - plugins/dev/skills/autopilot/SKILL.md
---

**What:** A multi-milestone project loses its context between cycles, so the human running it cannot
tell at a glance which milestone is current and what comes next. Raised by the user at `dev:reflect`
Step 4: *"I as a human forget what milestone we're at and what's next. And so I have redirected us or
skipped the order, not intentionally, but because I didn't remember at the end of a cycle what was
next."*

**Why:** The information is emitted exactly once, in the worst place for it. `dev:done` Step 8's
product-plan exit protocol prints the milestone map, what completed, and the exact
`/dev:spec "<next item>"` command — at the tail of a long completion display, in the session that is
ending. Nothing carries it into the next session, which is where it is needed. `dev:dev` Step 6 is
multi-plan-aware for continuation, but only once you are already running `/dev`.

  The ordering risk is not hypothetical. Milestone 2 of `dev-fast-path` was delivered as
  `entry-adapters`, which absorbed and superseded the item as written. That worked out, but it is
  exactly the shape of "the order drifted and nobody was tracking it." At the close of this cycle the
  repo has one live plan (`dev-observability`) and no surface that announces it.

**The user's preferred direction — one worktree per project, not per cycle.** Stated at the same
turn: create a single worktree for a multi-milestone project and run each cycle inside it, clearing
between cycles, so the plan and the accumulated context persist rather than being torn down and
rebuilt.

**Sizing — this is its own cycle, not a fix.** `dev:spec` Step 6 creates `.dev-worktrees/<feature>/`
per cycle and `dev:done` Step 7 removes it. Moving to a project-scoped worktree changes the identity
of that directory from `<feature>` to a plan slug, so every stage skill's `WORKDIR` resolution block
changes: **12 files** hardcode `.dev-worktrees/<feature>/` or `.dev-worktrees/*/` (build, debt, dev,
autopilot, done, fix, reflect, pr, plan, secure, shape, validate). That is the same coordinated-edit
shape `debt-primary-cd-failure-unchecked` was deferred for. Two design questions fall out and belong
in that cycle's spec rather than in flight: what happens when cycles in one shared worktree need
different branches checked out, and whether several cycles' `docs/dev/<feature>/` directories coexist
in the shared tree.

**Done looks like:** At the end of a cycle and at the start of the next, a human can see which
milestone is current, what is next, and the exact command to start it, without having to remember it
across a session boundary — and a multi-milestone project is not paying worktree setup and teardown
once per milestone.
