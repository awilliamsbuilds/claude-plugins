# Debt Pending — validate-prose-resync

Buffer for items `dev:done` Step 6a flushes into `docs/backlog/`.

## To Record

### backlog-converging-cascade-third-signal-unaudited

````markdown
---
type: backlog
scope: plugin
status: open
first_recorded: 2026-08-19
cycles: [validate-prose-resync]
recurrence: 1
files: [plugins/dev/skills/validate/SKILL.md]
---

**What's wrong:** The converging-cascade exemption added to `dev:validate` Step 4 step 8 requires
three signals before the same-region recurrence stop may be bypassed. Two are mechanically
checkable — severity non-increasing and strictly below the first round in that region, and no code
changed after that round. The third is not: *the findings are consequences of the same earlier edit,
not competing answers to one unsettled question.* That is a judgment call, made by the same agent
that authored the edits being judged, and nothing records it. In autopilot no human is present to
catch a misclassification.

**Why deferred:** Closing it means requiring the judgment be written down before the exemption may
be taken — naming, per round, which earlier edit the finding descends from — and the natural place
to write it is `validation.md`. This cycle's spec puts a new `validation.md` section explicitly out
of scope, and the alternative (folding it into `## Notes`) changes what that field means. Both are
scope decisions rather than edits, which is what makes this a separate cycle rather than a fix here.

**Done looks like:** Step 8's exemption states that the third signal must be recorded in writing
before it may be relied on, naming the earlier edit each round descends from — the same discipline
step 3b already applies to claims about observable behavior — with a decided home for that record.

  Cost if left: the exemption is bounded (`loops_max` still caps the loop, step 10 still routes to
  Step 4a, and step 8's cold re-review still runs each loop), so a misfire costs extra loops rather
  than unbounded editing. What the next cycle pays is the debugging: an autopilot run that kept
  fixing in a region it should have handed to the user leaves no record of why it thought the
  cascade was converging, so reconstructing the decision means re-reading the whole loop's diffs.
````
