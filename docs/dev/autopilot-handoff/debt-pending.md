# Debt Pending — autopilot-handoff

Buffered backlog/debt items for this cycle. `dev:done` Step 6a flushes `## To Record` into
`docs/backlog/` and executes each `## To Close` close-intent, then Step 7 deletes this file. Nothing
else reads it.

## To Record

### debt-primary-cd-failure-unchecked

````markdown
---
type: debt
scope: repo
status: open
severity: P3
first_recorded: 2026-08-11
cycles: [autopilot-handoff]
recurrence: 1
files: [plugins/dev/skills/autopilot/SKILL.md, plugins/dev/skills/build/SKILL.md, plugins/dev/skills/debt/SKILL.md, plugins/dev/skills/dev/SKILL.md, plugins/dev/skills/done/SKILL.md, plugins/dev/skills/fix/SKILL.md, plugins/dev/skills/migrate-tracker/SKILL.md, plugins/dev/skills/plan/SKILL.md, plugins/dev/skills/pr/SKILL.md, plugins/dev/skills/reflect/SKILL.md, plugins/dev/skills/shape/SKILL.md, plugins/dev/skills/spec/SKILL.md, plugins/dev/skills/validate/SKILL.md]
---

**What's wrong:** The canonical `PRIMARY` snippet checks only its first line. Line 2 —
`PRIMARY=$(cd "$(dirname "$GIT_COMMON")" && pwd)` — has no failure branch: if the `cd` fails
(git dir deleted between the two commands, a stale `--git-common-dir` in a pruned worktree,
a permissions change), the command substitution yields the empty string and the assignment
still succeeds. Every downstream path then becomes root-absolute: `$PRIMARY/.dev-worktrees/…`
→ `/.dev-worktrees/…`. Reads miss harmlessly, but `dev:spec` Step 6's
`git -C "$PRIMARY" worktree add "$PRIMARY/.dev-worktrees/<feature>"` would attempt a write at
filesystem root.

**Why deferred:** Not a regression — the pre-cycle one-liner was equally unchecked, and the
autopilot-handoff cycle strictly improved it by adding the `||` branch to line 1. Closing it
means a coordinated edit across 13 files, which is its own cycle rather than a Validate fix.

**Done looks like:** All 13 sites carry a non-empty check after the derivation — e.g.
`if [ -z "$PRIMARY" ]; then echo "Could not resolve the primary checkout."; exit 1; fi` —
and `grep -rn 'PRIMARY=' plugins/dev/skills/*/SKILL.md` shows every hit followed by that guard.
Keep the healthy path exiting 0 (`if`, not `[ … ] && …`).
````

### debt-dev-stage-jump-has-no-new-session-path

````markdown
---
type: debt
scope: repo
status: open
severity: P3
first_recorded: 2026-08-11
cycles: [autopilot-handoff]
recurrence: 1
files: [plugins/dev/skills/dev/SKILL.md, plugins/dev/skills/autopilot/SKILL.md]
---

**What's wrong:** `dev:dev`'s Invocation Reference documents `/dev spec` as "Jump to Spec
(new session)", but the Step 5a handler it routes to is written for *resuming*: its step 1 is
"Read state.json to find the current feature," and its requirements table has rows for
build/validate/pr/done only — no `spec` row and no new-session path. With two or more cycles
in flight, "find the current feature" is ambiguous.

**Why deferred:** The gap predates this cycle. It became load-bearing here because
`dev:autopilot`'s new multi-hit STOP points users at `/dev spec` as the way to start a fresh
cycle while others are in flight — but fixing `dev:dev`'s stage-jump procedure is outside the
autopilot-handoff spec's scope.

**Done looks like:** `dev:dev` Step 5a states a `spec` path explicitly — it creates a new
session rather than reading an existing `state.json`, and says so for the multi-cycle case —
or the Invocation Reference stops advertising `/dev spec` as a new-session route. Either way
`dev:autopilot`'s multi-hit STOP resolves to a procedure that works.
````

### debt-no-ui-flag-stated-as-authoritative

````markdown
---
type: debt
scope: repo
status: open
severity: P3
first_recorded: 2026-08-11
cycles: [autopilot-handoff]
recurrence: 1
files: [plugins/dev/skills/dev/SKILL.md, plugins/dev/skills/start/SKILL.md]
---

**What's wrong:** Three reference lines state flatly that the `no-ui` launch flag skips Shape —
`dev/SKILL.md:23` ("set mode to no-ui; Shape stage will be skipped"), the `/dev no-ui` row in
`dev/SKILL.md`'s Invocation Reference, and `start/SKILL.md`'s "no-ui mode: Shape is skipped, for
any tier". But `spec/SKILL.md` Step 12 makes the spec's own `## UI Needed` authoritative "whether
or not the cycle was launched with the `no-ui` flag," and `dev/SKILL.md`'s own next-stage logic
already reads `skipped[]` rather than the flag. A user whose spec resolves `UI Needed: Yes` gets
Shape despite having passed `no-ui`.

**Why deferred:** Pre-existing contradiction. The autopilot-handoff cycle brought `dev:autopilot`
into line with the authority (Step 3 now reads `skipped[]`, and its Invocation entry is hedged),
which leaves these three as the remaining stale statements — but editing reference surfaces for
a flag this cycle doesn't otherwise touch is scope creep.

**Done looks like:** All three lines describe `no-ui` as a request that Spec's `## UI Needed`
adjudicates, matching `spec/SKILL.md:478` and `dev:autopilot`'s hedged Invocation entry. A reader
comparing `/dev no-ui` against `/dev:autopilot no-ui` gets one promise, not two.
````

### debt-artifact-path-rule-artifact-component-unconstrained

````markdown
---
type: debt
scope: repo
status: open
severity: Nit
first_recorded: 2026-08-11
cycles: [autopilot-handoff]
recurrence: 1
files: [plugins/dev/skills/autopilot/SKILL.md, plugins/dev/skills/build/SKILL.md, plugins/dev/skills/done/SKILL.md, plugins/dev/skills/plan/SKILL.md, plugins/dev/skills/pr/SKILL.md, plugins/dev/skills/shape/SKILL.md, plugins/dev/skills/validate/SKILL.md]
---

**What's wrong:** The shared artifact-path validation rule constrains only `<feature>`
(`^[a-z0-9][a-z0-9-]*$`, no `..` segments). The `<artifact>` component is bounded only by the
whole-path `..` ban, so a value like `docs/dev/real-feature/~%2Fssh%2Fid_rsa.md` parses as valid.

**Why deferred:** Inert today — `dev:autopilot` derives only `<feature>` and never opens the
named artifact. Recorded because the rule is stated identically in seven skills, several of which
*do* read the artifact the path names, and because this cycle advertised the argument form to
users at two gates and in two reference surfaces, widening who types these paths.

**Done looks like:** The shared rule constrains `<artifact>` to the known set
(`spec|design|plan|validation`) alongside its `<feature>` regex, restated identically in all
seven skills — or the rule is factored so there is one statement of it to change.
````

## To Close

- debt-primary-path-relative-in-dev-headers — this cycle's whole premise is a resume command pasted into a cleared session running from the primary checkout, so `PRIMARY`/`WORKDIR` resolution is already the load-bearing path being edited; the relative-`PRIMARY` bug reproduced live during this cycle's own Spec stage.
- debt-autopilot-grounding-gate — the cycle is already rewriting `autopilot/SKILL.md` Step 1 and Step 2 to accept the artifact-path form, so adding the one-line cross-note to the `dev:spec` grounding gate is free while that file is open.
