---
type: debt
scope: repo
status: open
first_recorded: 2026-08-23
cycles: [retro-inside-pr]
recurrence: 1
files:
  - plugins/dev/skills/validate/SKILL.md
possibly_related_to: debt-validate-3b-partial-measurement-of-compound-claims
---

**What's wrong:** `dev:validate` Step 4 step 3b requires the **fixer** to measure any claim about
observable command behavior before committing it, but step 8's fix-diff re-review checklist asks the
**reviewer** only to read. On `retro-inside-pr` two independent cold reviewers passed a snippet using
`head -n "$((LAST - 1))"`; the defect — BSD `head` rejects `-n 0` (exit 1), breaking on a decision log
whose `## Retrospective` is line 1 — was found by the fixer running it under 3b, not by either review.

**Why deferred:** It is a checklist-scope question, not a defect in any existing rule, and it reaches
`dev:fix`'s mirrored re-review by inheritance — so changing it touches the canonical/mirror pair and
wants its own consideration rather than a fix-loop edit.

**Done looks like:** A decision, either way, recorded. Either step 8's checklist gains a "run any
shell snippet whose behavior the diff asserts" line — and `dev:fix`'s inheritance-by-reference is
confirmed to carry it — or the asymmetry is documented as deliberate, on the ground that 3b already
covers the same class one step earlier.

**Cost if not paid:** this repo's "code" is shell embedded in Markdown, so portability defects are a
live class rather than a hypothetical one, and they are invisible to reading. Every one that slips
past both reviewers ships in a skill that an unattended agent later executes, where the failure
surfaces as a stage that cannot run.
