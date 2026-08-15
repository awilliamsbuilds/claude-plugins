# Debt Pending — entry-adapters

Buffered backlog/debt items for this cycle. `dev:done` Step 6a flushes `## To Record` into
`docs/backlog/` and executes each `## To Close` close-intent, then Step 7 deletes this file. Nothing
else reads it.

## To Record

### p6-overlap-test-unsatisfiable-for-fileless-items
````markdown
---
type: debt
scope: repo
status: open
first_recorded: 2026-08-15
cycles: [entry-adapters]
recurrence: 1
files:
  - plugins/dev/references/tech-debt.md
---

**What's wrong:** P6's clear-match test requires that "the `files:` sets overlap **and** the
described defect is the same defect — **both** conditions, never either." An item carrying
`files: []` can never satisfy the first condition, so it can never be recurrence-merged, no matter
how plainly it is the same item. The flush's only other branch is "when uncertain, create a new
file," so a genuine recurrence of a file-less item is forced into a duplicate that P2 uniqueness then
disambiguates to `<type>-<slug>-<first-cycle>.md`. Four of the store's active items carry
`files: []` today: `backlog-debt-backfill`, `backlog-dev-skill-test-harness`,
`backlog-stage-lifecycle-telemetry-app`, `backlog-verboseness-check`. These are exactly the
repo-wide "build a thing" backlog items rather than defects localized to files, so the field is empty
by nature and not by omission.

**Why deferred:** Found while recording a recurrence against `backlog-dev-skill-test-harness` during
this cycle's Build, which is well past the point where editing the shared contract is in scope — P6
governs every producing stage and `dev:done`'s flush, so changing it is its own cycle with its own
review. The recurrence was recorded by hand instead, which is correct but does not generalize: the
next cycle to hit this will silently produce a duplicate rather than notice the rule failed.

**Done looks like:** P6's clear-match test states what an empty `files:` set means — most likely that
an empty set on **either** side makes the overlap condition inapplicable rather than false, leaving
the same-defect condition to decide alone, with the existing "never merge on topic or keyword
similarity alone" caution doing the work it already does. Recording a recurrence against a
`files: []` item then follows the documented path rather than requiring a hand edit.
````

### vercel-plugin-injects-into-unrelated-work
````markdown
---
type: backlog
scope: repo
status: open
first_recorded: 2026-08-15
cycles: [entry-adapters]
recurrence: 1
files: []
---

**What:** Decide how to stop the Vercel plugin injecting skill directives and platform
documentation into sessions that have nothing to do with Vercel. Options are to disable it, constrain
it, or report the matcher bug upstream — the decision has not been made, which is why this is a
backlog item rather than a fix.

**Why:** Two independent problems compound, and both were observed in this repo — a markdown plugin
repo with no Vercel surface of any kind, no `package.json`, no deployment, and no Vercel account
linkage.

1. **The prompt matcher rescues its own below-threshold matches.** A prompt about recording a tech
debt item produced: `"verification" matched: below threshold: score 4 < 6 (allOf [test, end, end]
+4); lexical recall (raw 1968.6, capped +4.0, source: lexical)`. The matcher scored 4 against its own
`minScore` of 6, correctly declined, and then a lexical-recall boost added +4 and injected anyway.
The trigger terms are the giveaway: `test`, `end`, `end` — `end` matching as a fragment inside
ordinary English (`append`, `depend`, `recommend`). The injected text then reads
`You must run the Skill(verification) tool.` and `MANDATORY: Your training data for these libraries
is OUTDATED and UNRELIABLE`, which is imperative framing over a match the plugin itself rated
insufficient.

2. **Two Vercel plugins are enabled at once** — `vercel-plugin@vercel` and
`vercel@claude-plugins-official`. This is visible as doubled skills in the session listing
(`vercel-plugin:ai-sdk` alongside `vercel:ai-sdk`, and so on for ~30 skills) and doubled SessionStart
hooks. `vercel-plugin@vercel` registers hooks on eight events including `UserPromptSubmit`,
`PreToolUse`, and six `PostToolUse` entries.

The cost is not only noise. Injected imperatives compete with the actual task's instructions, and a
`/dev` cycle running unattended in autopilot is exactly where an unrelated "you must run this tool"
directive is least likely to be caught by a human.

**Note on `files:`.** Empty by nature — nothing in this repo is at fault; the remedy is local plugin
configuration or an upstream fix. That empty list makes this item unmergeable by the recurrence
procedure, which is the defect recorded separately as
`p6-overlap-test-unsatisfiable-for-fileless-items`. Expect to record any recurrence of this by hand.

**Done looks like:** A decision is made and acted on — one of: both Vercel plugins disabled; exactly
one kept and the duplicate removed; or the matcher behavior reported upstream with the score line
above as the reproduction. Sessions in repos with no Vercel surface no longer receive Vercel skill
directives or knowledge-update documents.
````

## To Close

- debt-fix-tail-guard-stale-when-offline — this cycle rewrites `skills/fix/SKILL.md`'s argument parse and is already in the merge tail; capturing the fetch exit status is a few lines with a pre-written fix
- debt-fix-tail-multiple-open-prs-unchecked — same file, same edit session; the tail's prose already promises the multiple-open-PR stop that the snippet does not implement
