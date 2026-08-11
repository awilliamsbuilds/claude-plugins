# Autopilot Handoff at Pre-Execution Gates — Validation Report
*Branch: feature/autopilot-handoff · 2026-08-10*

## Summary
Loops run: 9 / 3 (limit reached at loop 3 with an open P2; user chose "keep looping" at the Step 4a gate)
Final status: clean — no open P1/P2

Every loop's fix diff was cold re-reviewed by a fresh subagent per Step 4 step 8, as were the
two initial reviews (code + security) per Step 2. The loop count is high because the fix-diff
re-review kept finding defects *in the fixes themselves* — loops 4 through 9 were entirely
self-correction of issues introduced during loops 3 through 8, all confined to one paragraph
of `dev:autopilot` Step 1.

## Issues Resolved

### Loop 1 — from the two Step 2 cold reviews
- **P2:** `handoff_at` branch conditions overlapped on the cold-start case — a bare
  `/dev:autopilot` on a new feature would let `dev:spec` Step 6 write `"mode": "standard"`,
  then read it back and record a handoff on a cycle that was autopilot end-to-end. → Anchored the
  branch decision to the `state.json` that existed *when the invocation began*. This was the
  cycle's most valuable fix: without it Success Criterion 8 failed outright.
- **P2:** `reflect/SKILL.md` still carried prose asserting `PRIMARY` is "absolute only sometimes"
  and warning about matching against a bare `.` — both invalidated by Task 1, and both named in
  the folded-in debt item's own *Done looks like*. → Replaced with the post-Task-1 truth.
- **P2:** Nothing on the orchestrator side acknowledged that a handed-off cycle now pauses at
  `dev:reflect` Step 4; autopilot's blanket "No approval gates" would have suppressed it, failing
  Success Criterion 6 at runtime. → Added the carve-out to autopilot Step 2.
- **P3:** Artifact-path form fell through to "begin from Spec" when a validated slug matched no
  cycle — a typo would silently launch a new unattended cycle. → Made it a STOP.
- **P3:** No-argument path had no defined scan roots. → Named the two globs.
- **P3:** Spec gate's offer held an unresolved inline alternation
  (`<Plan → … , or Build → … for micro>`) that could leak literally into terminal output.
  → Split into two mutually-exclusive bracketed branches.
- **P3:** `done`'s conditional template line mixed emitted output with authoring commentary.
  → Separated.
- **P3:** autopilot's "never `spec`/`shape`" invariant contradicted the early-paste path both
  gates bless. → Scoped to the approved path.
- **Nit:** second dangling "canonical block" citation at `dev/SKILL.md:71`. → Repointed.

### Loop 2 — from loop 1's fix-diff re-review
- **P2:** Loop 1's autopilot carve-out contradicted itself inside four sentences, and its closing
  claim was false against the `reflect` Step 6 edit made in the same loop. Re-review also flagged
  that extending Step 6's gate to handed-off cycles widened the feature past spec §Scope 4, which
  names exactly two marker readers. → **Reverted the Step 6 change** rather than widening scope
  during Validate; reconciled the carve-out to say Step 6 is not a second carve-out.
- **P3:** New STOP conditions were not added to autopilot's own "When autopilot stops" enumeration
  — the exact cross-skill ripple `plan/SKILL.md:177` requires closing. → Enumerated.
- **P3:** The scan borrowed `dev:dev` Step 3's procedure by reference, but that procedure *asks*
  which session to continue, which autopilot Step 2 forbids. → Borrowed the globs only, added an
  explicit multi-hit STOP.
- **Nit:** `done`'s "at Plan, not at Shape" prose could read a legitimate early-paste value as
  corruption. → Added the caveat.

### Loops 3–9 — self-correction of the multi-hit STOP paragraph
Loop 3's P3 cleanup introduced a P2 (escape hatch pointed at bare `/dev`, which lands on
`dev:dev` Step 3's resume/restart/abandon menu — whose *Restart* force-removes a worktree —
in exactly the state the STOP fires). Fixing that introduced a `no-ui` exemption that wrongly
removed single-hit resume. Each subsequent loop closed the previous loop's defect:

- **Loop 4:** escape retargeted to `/dev spec` (the documented new-session jump, parsed before
  `dev:dev`'s own scan); `no-ui` exemption added.
- **Loop 5:** `no-ui` exemption removed as over-reaching — it would have started a brand-new
  unattended cycle instead of resuming a single in-flight one. Replaced with `/dev spec no-ui`.
- **Loop 6:** carried the `no-ui` flag into the printed message so the user's intent isn't dropped.
- **Loop 7:** rewrote the STOP block to the file's own `[If cond: text]` convention and resolved a
  `<feature>` placeholder collision that would have handed the user a *pre-picked* cycle — the very
  thing the STOP exists to prevent. Added Step 3's **UI vs no-ui detection** rule, closing the same
  gap Task 2 step 5 closed for `tier` (Step 3 named a source for tier but none for the UI branch).
- **Loop 8:** scoped that new rule to Standard/Deep — a Micro cycle carries
  `skipped: ["shape","plan"]` and would otherwise have matched `+ no-ui` and queued a Plan stage.
  Stated the cold-start ordering.
- **Loop 9:** corrected the guard's justifying clause, which named a hazard that wasn't real and so
  invited a future editor to delete a correct guard.

## Issues Remaining

### P1 Open
None.

### P2 Open
None.

### P3 Open
- `PRIMARY=$(cd "$(dirname "$GIT_COMMON")" && pwd)` has no failure check on its second line across
  all 13 sites. If the `cd` fails the substitution yields the empty string and the assignment still
  succeeds, making every downstream path root-absolute — `dev:spec`'s
  `git -C "$PRIMARY" worktree add …` would then attempt a write at filesystem root. Not a
  regression (the pre-cycle form was equally unchecked), but this cycle deliberately added a
  failure branch to line 1 and stopped one line short.
- `dev:dev` Step 5a's stage-jump procedure describes *resumption* ("Read state.json to find the
  current feature") and has no `spec` row in its requirements table, so `/dev spec` as a
  new-session path is documented only in the Invocation Reference. This cycle's multi-hit STOP now
  points users at that route, which makes the gap load-bearing.
- `dev/SKILL.md:23`, `dev/SKILL.md:171` and `start/SKILL.md:41` still state flatly that `no-ui`
  skips Shape, while `dev/SKILL.md:86–89` and `spec/SKILL.md:478` make the spec's `## UI Needed`
  authoritative. Pre-existing; `dev:autopilot` was brought into line with the authority this cycle,
  so the three stale statements are now the odd ones out.

### Nits Surfaced
- The `<artifact>` component of the shared artifact-path validation rule carries no allowlist —
  only `<feature>` is regex-constrained. Inert in `dev:autopilot` (it derives only `<feature>`),
  but the rule is shared with six sibling skills that do read the named artifact.
- `autopilot/SKILL.md`'s "Check for in-progress session. If found: … Resuming from <current-stage>"
  is unconditioned for the multi-hit case; reading order saves it, since the STOP precedes it.
- `[Otherwise: …]` is a bracket form used nowhere else in `plugins/dev/`; siblings spell out both
  conditions.

## Notes

The two initial reviews and all nine fix-diff re-reviews ran as fresh `general-purpose` subagents
denied this session's conversation history, per the standing pre-authorization in
`~/.claude/CLAUDE.md` § /dev Subagent Reviews.

**Process observation for the retrospective.** `plan.md` Task 6 step 4 instructed "Do not touch
Step 6's skill-update gate — a user observation raised here already flows into it unchanged."
The instruction was followed at Build, but its stated premise was false: Step 6's gate is
standard-mode-only, so on a handed-off cycle it does not run. Loop 1 discovered the gap, loop 1's
own fix over-corrected past spec §Scope 4, and loop 2 reverted it. A plan rationale that asserts a
fact worth checking is worth checking at Plan time.

**Loop economics.** Six of nine loops were spent on one paragraph, each fixing the prior loop's
cosmetic fix. The P3s that triggered loops 3–9 were low-value; the fix-diff re-review that caught
each regression was high-value. Worth considering whether P3 fixes to already-clean prose should
be deferred to the buffer rather than attempted inline once P1/P2 are closed.
