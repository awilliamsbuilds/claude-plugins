---
type: debt
scope: repo
status: closed
first_recorded: 2026-08-17
cycles: [extract-review-skills]
recurrence: 1
closed: 2026-08-19
closed_by: validate-prose-resync
files:
  - plugins/dev/skills/validate/SKILL.md
---

**What's wrong:** `dev:validate` Step 4's fix loop has no rule requiring that a fix which edits a code
or shell block also re-read the **prose that describes that block** in the same loop. Step 3a covers
plan-declared canonical/mirror pairs across *files*, but not the ordinary case of a paragraph sitting
three lines above the code it documents.

Measured this cycle: loop 2 added a third `case` guard and a trailing-slash strip to two skill files.
The surrounding prose kept saying "**two** `case` statements" and "**Three** branches." Loop 3 fixed
the first; its re-review then found the second; loop 4 fixed that. **Two of four loops existed only to
let prose catch up to one code change** — each costing a full cold subagent dispatch. The re-reviews
were correct every time; the loop simply had no way to converge in one pass.

This also mechanically trips Step 4 step 8's **same-region recurrence** rule, which then reads as a
loop "circling an unsettled decision" when it is actually converging monotonically (P2 → P3 → P3). This
cycle had to override that rule by judgment and record the override, which is a sign the rule and this
gap interact badly.

**Why deferred:** The cost is a full extra loop per code-touching fix in a prose-heavy repo — here,
half the cycle's validate budget. It compounds with the same-region recurrence rule, which will keep
misfiring on this pattern and forcing either a judgment override or a premature route to Step 4a.

Deferred rather than patched because the right form is not obvious: a blanket "re-read surrounding
prose" instruction is unfalsifiable and will be skipped, while a mechanical rule (e.g. re-read the
paragraph immediately above and below any edited fence, and any sentence containing a count or an
ordinal) may be too narrow to catch the "Three branches" case, which sat further away.

**Done looks like:** a fix that edits a fenced code block cannot exit its loop without the prose
describing that block having been re-checked in the same loop — with counts and ordinals called out
explicitly, since those are what actually went stale — and the same-region recurrence rule
distinguishes a converging prose-resync cascade from a genuine circling loop.
