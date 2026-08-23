---
type: debt
scope: repo
status: closed
closed: 2026-08-23
closed_by: challenger-loop-economics
first_recorded: 2026-08-17
cycles: [extract-review-skills]
recurrence: 1
files:
  - plugins/dev/skills/spec/SKILL.md
  - plugins/dev/skills/autopilot/SKILL.md
---

**What's wrong:** The spec challenger's autopilot loop is bounded only by a **count**
(`challenge.loops_max`, 5 on deep). Nothing tests whether the findings are still worth another round,
so the loop runs to its cap regardless of what it is finding, and three separate defects follow from
that:

1. **No blocker-kind exit.** The user's stated test at Reflect: a round earns its keep while blockers
   take the form *"a builder following this literally ships something broken."* Rounds 1 and 2 met
   that bar — round 1 caught the config-contract check being deleted out of existence and `dev:secure`'s
   parser refusing the three-token call the cycle depends on; round 2 caught `/dev:review docs` being
   declared with required paths but invoked argument-free at every call site, and Success Criteria 6
   and 9 being mutually unsatisfiable. But the **concern** stream decayed to bookkeeping by round 2 (a
   duplicate label, an off-by-one line range), which is the signal the count-based cap cannot read.
2. **Revision rationale is written into the spec.** Each round's fixes add prose explaining why the
   previous draft was wrong. Measured this cycle: 200 → 546 lines, a 2.7x growth, much of it
   retrospective justification rather than specification. The user's judgment, recorded: **that
   reasoning does not belong in the spec.** The builder pays to read it and every later reviewer pays
   to re-read it.
3. **An errored iteration still counts as a loop.** Iteration 3 returned an internal tool error rather
   than a verdict, so it produced no findings — but the counters advanced. `challenge.loops_run` reads
   `5` and `challenge.blockers` reads `1` on a spec that was approved after a later verification fix
   resolved that blocker; `blockers` is overwritten per dispatch, and the post-loop fix did not
   re-dispatch, so the counter is durably stale on a clean spec. `dev:reflect` reads these counters as
   its primary spec signal.

**Why deferred:** Each unnecessary round costs a full cold subagent dispatch plus the commit that
applies its fixes, and — unlike a validate loop — it permanently enlarges an artifact every downstream
stage must read. The stale-counter half corrupts the retrospective's own input, so the process cannot
see its own cost. Left alone, every deep-tier cycle pays five rounds whether or not rounds 3–5 find
anything load-bearing.

Deferred rather than patched because all three parts are judgment calls the user should set: where the
blocker-kind bar sits, whether the cap should drop from 5 to 3, and where revision rationale should
live instead (decision log, or nowhere).

**Done looks like:** the loop exits when a round's blockers stop meeting the "a builder following this
literally ships something broken" bar, rather than at a fixed count; revision rationale lands somewhere
other than `spec.md`; and a dispatch that errors instead of returning a verdict neither advances
`loops_run` nor leaves a stale `blockers` value behind.
