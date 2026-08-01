---
type: debt
scope: repo
status: open
severity: P3
first_recorded: 2026-08-01
cycles: [reflect-pr-base-explicit-target]
recurrence: 1
possibly_related_to: debt-autopilot-grounding-gate
files:
  - plugins/dev/skills/spec/SKILL.md
---

**What's wrong:** `dev:spec` Step 7's grounding inventory records what was read, but nothing requires
that a claim of the form *"X is read from Y"* cite the file and line it was actually read at, and
Step 12a's cold review has no lens that checks the footer's citations resolve. The result is that a
plausible-sounding mechanism can be asserted without ever being opened, and it then propagates into
Intent, Scope, and the success criteria, which read as grounded because the footer says so. In
`reflect-pr-base-explicit-target` this was the cycle's only challenger blocker: the grounding footer
stated that `dev:reflect` step 1 derived its marketplace slug "from `~/.claude/settings.json`". Step
1 in fact traces the running skill's own cache path → the marketplace name in that path → that
marketplace's registry entry — a different lookup entirely. Two success criteria had been written
against the fictional mechanism before Step 12a caught it.

Note the shape: `spec_revisions` was **0** and `confidence.final_score` was **88 / Ready**. Neither
instrument can see this class of error, because both measure internal coherence — a spec grounded on
a mechanism that does not exist is perfectly coherent with itself.

**Why deferred:** Surfaced at `dev:reflect` Step 6; the user chose to record rather than patch. It
touches two places in `dev:spec` (Step 7's inventory format and Step 12a's lens list) and the right
form of the requirement is not obvious — a blanket "cite a line for everything" would bloat the
footer, so it needs to be scoped to *mechanism* claims specifically.

**Done looks like:** a grounding-inventory claim asserting where a value comes from carries the
`file:line` it was read at, and Step 12a's brief includes checking that the footer's citations
resolve to what they claim. A mechanism that was never opened cannot reach the success criteria.
