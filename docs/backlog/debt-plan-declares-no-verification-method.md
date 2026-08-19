---
type: debt
scope: plugin
status: open
first_recorded: 2026-08-19
cycles: [validate-prose-resync]
recurrence: 1
files: [plugins/dev/skills/plan/SKILL.md]
---

**What's wrong:** Nothing in `dev:plan` makes a plan say how its work will be verified. Step 5's
template has no verification section, Step 6's self-review never asks, and Step 7a's three cold
lenses — spec-coverage, sequencing, interface-consistency — are all structural and would pass a plan
with no verification story at all. But `dev:validate` Step 8a keys on precisely that: it re-runs
manual verification only for "a `plan.md` task that declared a **TDD deviation** — a task whose entry
states its layer has no test runner and names manual verification as its check." No declaration, no
re-verification.

**Why deferred:** Surfaced at Reflect, after the plan stage had already run. Fixing it means deciding
where the declaration belongs — a `## Verification` section in Step 5's template, a fourth lens in
Step 7a, or both — and a fourth lens is a real change to the challenger's brief, which Milestone 2
(`challenger-loop-economics`) is already scheduled to revisit. Folding it in there is cheaper than
editing the same rules twice.

**Done looks like:** A plan cannot pass Step 7a without stating how its work is checked — either the
suite that covers it, or an explicit TDD deviation naming the manual verification — so
`dev:validate` Step 8a always has something to key on.

  Cost if left: on any cycle whose layer has no test runner — every prose-only cycle in this repo,
  which is most of them — Step 8a silently does not fire. The fix loop then exits on a green suite
  that covers none of the changed files plus a clean diff review, which is exactly the evidence
  Step 8a says is missing rather than reassuring. This cycle paid it as a Build backtrack; a cycle
  that does not notice pays it as an unverified merge.
