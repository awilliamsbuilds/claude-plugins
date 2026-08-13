---
type: backlog
scope: repo
status: open
first_recorded: 2026-08-12
cycles: [manual]
recurrence: 1
files:
  - plugins/dev/skills/done/SKILL.md
  - plugins/dev/skills/reflect/SKILL.md
  - plugins/dev/skills/pr/SKILL.md
---

**What:** Decide whether `dev:reflect` should run before the PR merges, so the files it touches land
in the cycle's own PR instead of after it.
**Why:** `dev:done` merges the PR first, then invokes `dev:reflect`. Everything reflect produces —
the retrospective appended to the decision log, plus any skill-file edits it proposes and the user
confirms — therefore lands outside the PR the cycle is about. That splits one cycle's output across a
merged PR and a loose working tree, and the checkout it lands in is sitting on `main`, which the
standing convention says never to commit to directly. Reordering isn't free either: reflect reviews
the completed cycle, and "completed" currently includes the merge.
**Done looks like:** A decision is recorded on where reflect sits in the pipeline, and if it moves,
`dev:done`/`dev:pr`/`dev:reflect` are reordered so reflect's output ships inside the cycle's PR.
