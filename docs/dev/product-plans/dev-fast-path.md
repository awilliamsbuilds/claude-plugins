# Dev Fast Path — Product Plan
*Created: 2026-08-15 · Cycles completed: 0/3*

Promoted from `backlog-fix-as-short-bug-round-trip`, which asked a narrower question — what becomes
of `/fix` — and is answered here as one part of a larger one.

The premise: `/dev`'s seven stages are correctly weighted for a feature like `backlog-viewer` and
absurdly heavy for a one-line frontmatter fix. `dev:autopilot` does not close that gap — it removes
the *gates*, not the *ceremony*, still producing a worktree, `spec.md`, `state.json`, two
challengers, a validate fix loop, `validation.md`, a decision log, and a retrospective. The
governing question for this project is which of `/dev`'s guarantees are load-bearing at small scale
and which are ceremony, and how a request gets routed to the right weight.

The worked example is the session that produced this plan: five PRs merged in one sitting with zero
`/dev` artifacts, where rigor came from grounding before acting, running the suite, verifying in a
browser where the suite could not reach, capturing what was deferred, and reporting honestly.

## Milestone 1: The fast path
- [ ] fast-path (feature)

The compressed lane and the escalation rule that refuses it. Triage and lane ship together: a lane
without triage is dangerous, and triage without a lane has nowhere to route. Expected to absorb the
standalone "open a PR" and "merge and clean up" verbs as segments of the same lane rather than as
separate skills. Also settles the `/fix` vs `/dev:fix` naming collision, since whatever this
produces competes for that name.

Deliberately not split into an architecture cycle plus a feature cycle. "Which rigor is
load-bearing" is decision-shaped, but spending a full architecture cycle to decide how to be less
ceremonious undermines its own premise; the decision is small enough to settle in this cycle's Scope
and Success Criteria. If the spec challenger's scope lens disagrees, split then.

## Milestone 2: Backlog-driven invocation
- [ ] fast-path-backlog (feature)

Point the lane at a `docs/backlog/` item and let it run with as little interaction as possible,
closing the item on merge. Touches `dev:debt` and the tech-debt contract's lifecycle rules. Depends
on Milestone 1 defining what the lane guarantees.

## Milestone 3: Retire the legacy commands
- [ ] retire-legacy-commands (feature)

`~/.claude/commands/{fix,merge,pr,security-review,security-review-diff}.md` predate the `dev`
plugin and overlap it. Partly consolidation, partly deletion — and **partly outside this repo**: the
commands live in the user's home directory, so no PR here can remove them. This cycle decides their
fate and documents the manual step; the keystroke is the user's.
