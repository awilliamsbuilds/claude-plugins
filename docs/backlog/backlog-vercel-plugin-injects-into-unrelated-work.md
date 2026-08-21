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

**Progress (2026-08-17).** Clause (1) is half done and clause (2) is drafted:

- **Located the actual registration.** The `vercel` marketplace is **not** in `~/.claude/settings.json`
  — that file held only the disabled plugin entry. The marketplace is registered in
  `~/.claude/plugins/known_marketplaces.json` (`source: github`, `repo: vercel/vercel-plugin`,
  `lastUpdated: 2026-04-12`), with state mirrored across `installed_plugins.json` and two cache
  directories holding **18.6M** (`marketplaces/vercel` 6.6M + `cache/vercel` 12M).
- **Done:** the orphaned `"vercel-plugin@vercel": false` entry was removed from
  `~/.claude/settings.json`'s `enabledPlugins`. Safe because plugins require an explicit `true` —
  absence never enables. Validated: 22 entries remain, `vercel@claude-plugins-official: true` intact.
- **Then open in (1):** unregistering the marketplace itself. Deliberately **not** hand-edited: the
  registry, `installed_plugins.json`, and the two cache dirs are coupled state Claude Code owns, and
  editing them by hand risks desync. The supported action is `/plugin marketplace remove vercel`.
- **(2) drafted, not filed.** Full bug report written, covering both defects — the lexical-recall boost
  being applied *after* the `minScore` check (so `minScore` bounds nothing), and trigger terms matching
  as substrings (`end` inside `append`/`depend`/`recommend`). Also flags the unnormalized `raw 1968.6`
  pre-cap score and the duplicated term in `allOf [test, end, end]`. Needs filing at
  `github.com/vercel/vercel-plugin`.

**Clause (1) complete — verified 2026-08-20.** `/plugin marketplace remove vercel` was run, and the
coupled state is clean on all four surfaces: `known_marketplaces.json` holds five marketplaces with no
`vercel` among them; `marketplaces/vercel` and `cache/vercel` (the 18.6M) are both gone;
`installed_plugins.json`'s only vercel-related key is `vercel@claude-plugins-official`; and
`settings.json` carries `vercel@claude-plugins-official: true` across 22 entries. The `vercel:*` skills
still listed in a session are served from `cache/claude-plugins-official/vercel` — the wanted copy —
so their presence is not evidence the removal failed.

  Recorded because the check is not obvious: the 2026-08-17 progress note above was written before the
  removal and read as still-open for three days afterwards, and was committed on 2026-08-20 without
  being re-verified against the actual state.

**Done looks like:** one thing still open. (2) The matcher bug is reported upstream — the score line above is the reproduction, and the
substantive complaint is that a lexical-recall boost can override the matcher's own `minScore`, and
that trigger terms match as fragments inside unrelated English. Reporting it matters beyond this
machine: 0.45.1 unhooked the injector but the scoring code is still shipped, so anything that
re-registers it inherits the same behavior. Optionally (3): if the SessionStart Vercel
knowledge-update document is still unwanted in repos with no Vercel surface,
`vercel@claude-plugins-official` goes too — that is a preference call, not a defect.
