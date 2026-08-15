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

2. **Two copies of the same plugin were enabled at once, at different versions** —
`vercel-plugin@vercel` at **0.32.6** and `vercel@claude-plugins-official` at **0.45.1**. Not two
plugins: the same plugin, same description, same tree shape. 0.45.1 is a strict superset — it carries
all 25 of 0.32.6's skills (19 byte-identical, 6 newer) plus five more (`cdn-caching`, `eve`,
`microfrontends`, `vercel-connect`, `vercel-firewall`). The stale copy contributed nothing but noise.

**The injection came entirely from the stale copy, and upstream appears to have already fixed it.**
0.32.6 registers **7 hook events / 16 entries** — SessionStart, PreToolUse, `UserPromptSubmit`,
`PostToolUse` ×6, SubagentStart, SubagentStop, SessionEnd. 0.45.1 registers **2 events / 4 entries**:
SessionStart and SessionEnd only. Decisively, 0.45.1 still *ships*
`hooks/user-prompt-submit-skill-inject.mjs` but no longer wires it in `hooks.json` — the file is
present and unregistered, which reads as a deliberate unhooking between the two versions rather than
an accident.

The cost is not only noise. Injected imperatives compete with the actual task's instructions, and a
`/dev` cycle running unattended in autopilot is exactly where an unrelated "you must run this tool"
directive is least likely to be caught by a human.

**Note on `files:`.** Empty by nature — nothing in this repo is at fault; the remedy is local plugin
configuration or an upstream fix. That empty list makes this item unmergeable by the recurrence
procedure, which is the defect recorded separately as
`p6-overlap-test-unsatisfiable-for-fileless-items`. Expect to record any recurrence of this by hand.

**Resolved for the mid-conversation case (2026-08-15).** `vercel-plugin@vercel` set to `false` in
`~/.claude/settings.json` (one-line change; backup written alongside). This removes every
`UserPromptSubmit`, `PreToolUse`, `PostToolUse`, and subagent hook, and the duplicate skill listings,
at **zero cost** — 0.45.1 retains all 30 skills. This is a machine-local config change, not a repo
change; a fresh machine will reproduce the problem until the stale marketplace entry is gone
everywhere.

**Done looks like:** two things still open. (1) The `vercel` marketplace entry that supplied 0.32.6 is
removed rather than left disabled, so it cannot be re-enabled by accident or reappear on another
machine. (2) The matcher bug is reported upstream — the score line above is the reproduction, and the
substantive complaint is that a lexical-recall boost can override the matcher's own `minScore`, and
that trigger terms match as fragments inside unrelated English. Reporting it matters beyond this
machine: 0.45.1 unhooked the injector but the scoring code is still shipped, so anything that
re-registers it inherits the same behavior. Optionally (3): if the SessionStart Vercel
knowledge-update document is still unwanted in repos with no Vercel surface,
`vercel@claude-plugins-official` goes too — that is a preference call, not a defect.
````

### cross-file-line-citations-go-stale-silently
````markdown
---
type: debt
scope: repo
status: open
severity: P3
first_recorded: 2026-08-15
cycles: [entry-adapters]
recurrence: 1
files:
  - plugins/dev/skills/autopilot/SKILL.md
  - plugins/dev/skills/fix/SKILL.md
  - plugins/dev/skills/migrate-tracker/SKILL.md
---

**What's wrong:** `/dev` skills cite each other by `file:line`, and nothing keeps those citations
true. Editing any cited file silently invalidates every pointer into it from every other file. This
cycle broke **eight** such citations merely by inserting lines into `spec/SKILL.md`, `pr/SKILL.md`,
and `debt/SKILL.md`; seven were repaired, one could not be. The repo treats these citations as
load-bearing — the spec for this very cycle argued that leaving one pointing at a deleted file "turns
a checkable claim into an unverifiable one" — so a silently-drifting pointer is the same defect the
repo already says it cares about, arriving by a different route.

**The one that could not be repaired is the useful part of this item.**
`autopilot/SKILL.md:139` cites `spec/SKILL.md:478`, which this cycle shifted to roughly 533. Repairing
it would edit `dev:autopilot`, and this cycle's SC10 requires that file byte-identical except for
`dev:linear` rename references. So a **success criterion and a correctness fix were in direct
conflict**, and the criterion won. That conflict is structural, not a one-off: any cycle that both
edits a cited file and freezes a citing file will hit it again.

**Why deferred:** The repair is mechanical but the *design* question is not, and it is the kind that
wants its own cycle: either citations stop carrying line numbers (cite by step or section name, which
is what this cycle's repairs in `migrate-tracker` actually did), or something checks them. Choosing
between those is a contract decision across a dozen skills.

**Done looks like:** Either `/dev` skills cite each other by stable anchor (step number, section
heading) rather than by line number, and the remaining `file:line` forms are converted; or a check
exists that resolves every `file:line` citation and fails when one no longer points at what it claims.
Editing a cited file then cannot silently falsify a citation in a file the editing cycle never opened.
````

### bare-reference-paths-do-not-resolve
````markdown
---
type: debt
scope: repo
status: open
severity: Nit
first_recorded: 2026-08-15
cycles: [entry-adapters]
recurrence: 1
files:
  - plugins/dev/skills/init/SKILL.md
  - plugins/dev/skills/done/SKILL.md
---

**What's wrong:** Skills live at `plugins/dev/skills/<name>/SKILL.md` and shared references at
`plugins/dev/references/`, so a reference must be cited as `../../references/<file>.md`. Several
sites instead write a bare `references/<file>.md`, which resolves to nothing from a skill directory.
This cycle found and fixed seven such paths (five in `migrate-tracker`, one in `done`, one in
`debt`); two remain at `init/SKILL.md:162` and `done/SKILL.md:264`.

**Why deferred:** Both remaining sites are pre-existing and neither file was otherwise in this
cycle's scope — and `done/SKILL.md` carried an additional constraint, since SC10 limited this cycle's
edits to that file to `dev:linear` rename references. Fixing them is a two-line change that belongs
with whatever next opens those files, not a reason to widen this cycle.

**Done looks like:** `grep -rn '](references/' plugins/dev/skills/` returns zero — every reference
citation from a skill directory carries the `../../` prefix that actually resolves.
````

## To Close

- debt-fix-tail-guard-stale-when-offline — this cycle rewrites `skills/fix/SKILL.md`'s argument parse and is already in the merge tail; capturing the fetch exit status is a few lines with a pre-written fix
- debt-fix-tail-multiple-open-prs-unchecked — same file, same edit session; the tail's prose already promises the multiple-open-PR stop that the snippet does not implement
