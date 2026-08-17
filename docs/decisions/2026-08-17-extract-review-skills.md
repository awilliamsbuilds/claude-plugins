# Extract Review Skills — Decision Log
*2026-08-17 · Branch: feature/extract-review-skills · PR #86*
*Handed off to autopilot at Spec*

## What was built

A separation of `dev:validate` Step 2 into a reviewer and an orchestrator: review checklists moved
into a new report-only `dev:review` skill with `diff` and `docs` modes, `dev:validate` Step 2 became a
dispatcher, and `dev:fix` gained the code review it had never run.

## Key decisions

- **Split by *what to look for* vs *what to do about it*, not by convenience.** `dev:validate` was
  both reviewer and orchestrator, and only the orchestrator half was stage-specific — knowing what to
  look for in a diff has nothing to do with `state.json`, fix loops, or stage advancement. Bolting a
  checklist onto `dev:fix` would have fixed the symptom and entrenched the cause.
- **One rule, one named exception.** *A reviewer never writes; an orchestrator never defines a
  checklist.* The exception is `dev:validate` Step 4 step 8's fix-diff re-review checklist, which stays
  with the orchestrator because it is the loop's own exit condition — four questions about whether
  *this loop's fix* regressed something — and is meaningless outside the loop that owns it. Named
  explicitly in both files so a later reader does not "finish the extraction" by moving it.
- **Two explicit modes, no inferred one.** A bare `/dev:review` is an error because `diff` mode's P1
  (a correctness blocker) and `docs` mode's P1 (an internally inconsistent decision) do not mean the
  same thing. Each mode carries its own severity table adjacent to its own checklist, since a reviewer
  that cannot classify its own findings is not report-complete.
- **Base first, tree second.** `dev:secure` already bound its second token to the base and was called
  that way by `dev:fix`; tree-first would have silently reparsed `main` as a path and broken every
  existing caller.
- **A bad tree stops; it never falls back.** A silent fallback to `$PRIMARY` would turn a caller's
  typo into a confident audit of the wrong tree — the precise failure the argument exists to prevent.
- **Artifact paths are caller-supplied, never discovered.** A reviewer resolving `spec.md` itself
  would resolve against its own `$PRIMARY`. Where none are passed — the `dev:fix` route — the two
  artifact-dependent bullets report `not run`, never clean and never by silent omission.
- **The whole-project `dev:secure` verb keeps `$PRIMARY` as a documented refusal**, not an oversight:
  it has no caller to hand it a tree, so it discloses which tree it audited instead. This is what let
  `debt-secure-tree-scoping-unsettled` close as paid rather than partly met — its *Why deferred*
  allowed "a caller-supplied tree, **or** a documented refusal."
- **`dev:secure` corrections were treated as preconditions, not extras.** Once `dev:validate` stopped
  carrying security bullets, CSRF would have existed nowhere in the repo. Server-side template
  injection was settled as distinct from the SQL-adjacent "template literals into queries." And the
  false "adds no new vector" claim was corrected because a later cycle reconciling the duplication on
  the strength of it would have deleted real coverage believing it redundant.

## Validation notes

- 4 loops run (tier: deep, cap 5). Final status clean — no open P1/P2.
- Build check: no build system detected (B5/O3). The 89-test `dev:debt` viewer suite, untouched by
  this cycle, stayed green after Build and after every loop.
- **P2 — the report-only contract did not survive the dispatch boundary.** `## Purpose`'s "writes
  nothing" binds the skill file, not the fresh `general-purpose` subagent it dispatches, which has
  write tools. This was the one place the cycle *weakened* an existing property: `dev:secure`
  previously ran in-session, where that invariant held implicitly. Fixed by instructing the subagent
  read-only at both dispatch sites.
- **P2 — the `### Security` → `### Review` rename orphaned three references**, one the *canonical*
  half of a declared canonical/mirror pair, one a control-flow instruction on the lane's dominant
  path. Swept.
- **P2 — a containment check that did not contain.** `case "$ARTIFACT" in "$TREE"/*)` is a prefix test
  on an unnormalized path, so `$TREE/../../../../etc/passwd` passed every gate — while the prose
  asserted the invariant held. Fixed by rejecting `..` segments and stripping trailing slashes. This
  was the most instructive failure of the cycle: it is exactly the unmeasured-behavioral-claim class
  the same file forbids two paragraphs earlier, and it was caught only because the re-review *ran* the
  traversal instead of reading the guard.
- **P3 — two measured guard bugs.** `grep -Eq` allowlists are line-oriented (a value with an embedded
  newline passes); `git rev-parse --is-inside-work-tree` prints `false` but **exits 0** for a git dir
  or bare repo, so the exit-status check accepted non-worktrees. Both replaced with whole-string
  `case` guards and an answer comparison.
- **P3 — the allowlist rejected paths containing a space**, which would have failed `"$WORKDIR"` for a
  repo under e.g. `/Users/x/My Projects/` and escalated to a stage stop. Widened rather than
  documented, since documenting would have made a legitimate setup predictably broken.
- **Accepted as-is:** one P3 and one Nit, both prose-polish in a single sentence whose load-bearing
  claim the final re-review confirmed correct. Both dropped by the carrying-cost test rather than
  recorded as debt.
- **Two deliberate departures, both recorded in `validation.md`:** the same-region recurrence rule
  triggered mechanically from loop 3 and was judged not to apply (severity fell monotonically, no
  shell changed after loop 2, no unsettled decision underneath); and Success Criterion 4's carve-out
  was exceeded by two text edits in `dev:validate` outside Step 2, one plan-authorized and one
  required to avoid shipping a dangling canonical marking.
- **A residual scoped rather than closed:** artifact containment defeats `..` traversal but not
  symlink escape. No current caller can reach it, and the shipped prose scopes its claim to `..`
  rather than asserting general containment.

## Artifacts (archived)

Spec, plan, and validation committed at: `7435483` on branch `feature/extract-review-skills`
