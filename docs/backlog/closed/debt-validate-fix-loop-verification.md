---
type: debt
scope: repo
status: closed
first_recorded: 2026-07-22
cycles: [harden-validate]
recurrence: 1
files:
  - plugins/dev/skills/validate/SKILL.md
closed: 2026-07-25
closed_by: harden-validate
---

**What's wrong:** `dev:validate` Step 4 fixes issues, commits, and closes the loop. Nothing
verifies the fix itself — a defect introduced by a fix is caught only if another loop happens to
run and re-review the whole diff. In the tech-debt-tracking cycle this fired twice in a row:
loop 1's renumbering left a dangling cross-reference and put a guard after the operation it
guarded; loop 2's guard rewrite shipped `git rebase --show-current-patch … && { … }`, which
**exits 128 on the healthy path**, as the first command of `dev:done` Step 7 — every normal
cycle's teardown would have read as a failure. Loop 3 caught it by running the snippet. On a
`micro` tier (1 loop) or any cycle that goes clean early, neither would have been caught at all.

Two distinct gaps sit underneath. **(a)** There is no self-check step: the loop's exit condition
is "no open P1/P2," which says nothing about the fixes just written. **(b)** The specific rule
that would have caught the concrete defect — *a shell snippet written into a skill must exit 0 on
its healthy path, so `&&` chains and bare guard blocks don't read as failure* — **exists nowhere
in the plugin.** Verified by grep across all `dev:*` skills on merged `main`: zero hits. That
cycle's own `validation.md` asserted the rule was "already codified in `dev:validate` Step 6";
that claim was false and is recorded here so the next reader doesn't inherit it.

**Why deferred:** The user chose to record rather than patch. The concrete defect was already
fixed in-cycle; what remains is the missing mechanism, and this plugin's own history argues the
prevention is worth designing once rather than bolting a single rule onto Step 4 — see
*Sweep for gate-path state writes that are dead in autopilot*, which reaches the same conclusion
about a different recurring shape. Note that a diff of executable prose has no test harness, so
"verify the fix" cannot mean "run the tests"; it needs its own definition.
**Done looks like:** `dev:validate` Step 4 cannot close a loop without checking the fixes it just
wrote, and the healthy-path exit-code rule for shell snippets is stated once somewhere a fix
author will read it. A fix that breaks a sibling skill's happy path is caught by the loop that
wrote it, not by the next one.
