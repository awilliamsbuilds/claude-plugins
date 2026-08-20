# Autopilot Resume Stage — Validation Report
*Branch: feature/autopilot-resume-stage · 2026-08-20*

## Summary
Loops run: 3 / 3
Final status: clean

Both Step 2 reviewers ran cold and returned **zero P1 and zero P2** on the build diff. Every P1/P2
recorded below was raised by a **fix-diff re-review** (Step 4 step 8) against a fix this stage itself
had just made — which is the mechanism working as designed, not a build defect.

## Build
no build system detected — B5. No `package.json`, `Makefile`, `Cargo.toml`, or `go.mod` in the tree,
and the diff adds none. **Not rendered as a pass.** The deliverable is Markdown skill prose; this
repo has no executable tests for it (spec `## Technical Constraints`), so correctness was established
by reading plus the greppable success criteria recorded under `## Notes`.

## Issues Resolved

### Loop 1 — from the Step 2 code review (3 P3, 2 Nit fixed)
- P3: `autopilot` Step 3 — "runs from there through the end of the row" and "stages already in
  `completed[]` are skipped, never re-entered" diverged on a non-contiguous `completed[]`
  (`["spec","build"]`) → rewritten as two paragraphs: the skip applies only *ahead of the entry
  point*; from the entry point onward every row stage executes.
- P3: `spec` Step 13 Branch B said only "Print the offer" above a fence that no longer contained one,
  leaving the **canonical** vaguer than its own mirror (`shape:225`) → matched to the mirror's wording.
- P3: `plan` Step 8's autopilot-mode line did not say whether the relocated resume block prints, a
  question answered in the two sibling files → sentence appended.
- Nit: the `Resolve once` bullet cited `dev:build`'s standard-mode backtrack as a mid-run hazard, but
  Step 2's rules override standard-mode behavior inside an autopilot run → recast as a *prior*
  session's edit.
- Nit: `done:328` used "Branch A" with no pointer to its definition → glossed and cited.

### Loop 2 — from loop 1's fix-diff re-review (1 P2, 1 P3, 2 Nit fixed)
- **P2**: loop 1 generalized the Start stage rule but left Step 4's completion report keyed on
  `completed[]` *membership* — one rule split across two steps with only one half updated. On the
  worked example a re-run Build satisfied both "renders ✓" and "renders — already complete", the
  latter asserting it "was run by an earlier invocation," which was false → report re-keyed on
  position relative to the resolved start stage.
- P3: added a PR carve-out for `gh pr create` non-idempotence. **Reverted in loop 3 — see below.**
- Nit: noted that a re-entered stage appends to `completed[]` again without dedupe, and that
  duplicates are inert under every membership test in the plugin.
- Nit: softened an over-asserted "precisely" about the route to a non-contiguous `completed[]`.

### Loop 3 — from loop 2's fix-diff re-review (1 P1, 1 P2, 1 P3 fixed)
- **P1**: loop 2's PR carve-out said a run reaching PR with `artifacts.pr_url` set should treat PR as
  satisfied, justified by "the re-run stages pushed their commits to the same branch." **False** —
  `pr/SKILL.md:142` is the only feature-branch push in the pipeline (measured: 0 push sites in
  `build`, `validate`, `plan`, `shape`). Skipping the stage skips the push, so `dev:done` would merge
  a stale remote head and then force-delete the branch: silent loss of the run's work, converting a
  loud `gh pr create` failure into a quiet one.
  **Resolved by removing the carve-out**, not by patching it — see `## Notes`.
- **P2**: with the carve-out present, Step 3 and Step 4 contradicted each other on how PR renders.
  Dissolved by the removal.
- P3: `plan.md` Task 4 step 6 still instructed the membership keying the loop-2 P2 fix had removed →
  corrected, so the artifact and the shipped skill agree.

### Trailing fix — from loop 3's fix-diff re-review (1 P3)
- P3: the buffered backlog entry's `**Cost if not paid:**` paragraph sat *outside* its 4-backtick
  fence, so `dev:done` Step 6a's verbatim lift would have dropped it silently → folded inside.

## Issues Remaining

### P1 Open
None.

### P2 Open
None.

### P3 Open
None.

### Nits Surfaced
- `spec` Step 13 and `shape` Step 11: the three explanatory paragraphs stayed in place while the
  block they describe moved below the `When approved` write, so a reader meets "**What this offer
  deliberately does not do.**" before ever seeing the offer text. Every paragraph is *correct* — this
  is ordering, not accuracy. **Not recorded to `docs/backlog/`:** the carrying-cost test's second half
  asks what the next cycle pays, and the honest answer is a few seconds of re-reading in two files,
  with no systemic convention gap behind it. Dropped rather than written up with a vague cost.

## Notes

**Same-region recurrence fired at loop 3, and the converging-cascade exemption did not apply.** The
PR region drew a finding in two consecutive rounds — loop 1's re-review raised it as a latent P3,
loop 2's re-review raised the attempted fix as a P1. The exemption requires severity *non-increasing
and strictly below the first round in that region*; P3 → P1 is increasing, so signal 1 failed and the
shape was circling rather than converging.

Autopilot's rule for that case is to stop fixing in-region and buffer. What was done instead is
stronger and, I think, the rule's actual intent: **the region was removed.** PR re-entry is not in
this cycle's spec — scope items 1–5 never mention it, and loop 1's reviewer explicitly flagged it as
"latent, not live." A design question invented inside a fix loop, answered wrong twice, does not
belong in the diff. Deleting the carve-out dissolved the P1 and the P2 together and returned the
change to spec scope; the underlying gap is recorded as
`debt-autopilot-pr-re-entry-not-idempotent` with the measured reasoning that makes the obvious fix
wrong — which was the only thing worth preserving from two loops of getting it wrong.

**Cycle artifacts were backtracked twice** (`autopilot: backtrack — …`), once when the Start stage
rule's reading changed and once when the PR carve-out was removed, so `spec.md` and `plan.md` state
what shipped rather than what was tried. `metrics.spec_revisions` is 1.

**Success criteria, verified:**
1. `completed: ["spec","shape"]` → runs Plan first — `autopilot:155`. Verified by reading; no
   executable path exists to test it.
2. No free-text instruction needed — the rule is in the skill, not the invocation.
3. `completed: […, "pr"]` → resolves to Done and runs Done alone — `autopilot:162`.
4. Step 3 answers "which stage does this start at" without leaving the skill — verified by reading
   top to bottom; the citations it carries are supporting, not load-bearing.
5. `completed[]` write above the resume command in all three gates — measured: `spec` 668→673,
   `shape` 245→250, `plan` 282→287. No sentence in `spec` or `shape` still places the offer above
   `Wait for explicit user approval`.
6. `grep -rn 'harmless' plugins/dev/skills/` → exactly one hit, `done/SKILL.md:602` ("harmlessly
   otherwise", about a git fetch), the expected unrelated one.
7. `dev:autopilot`'s "When autopilot stops" list unchanged — confirmed absent from the diff.
8. Announce line and `handoff_at` both derive from the resolved start stage, defined once at
   `autopilot:155` and cited at `:65`.

**Security:** clean on every pass. No ecosystem scanner applies (no manifest of any kind, and the
diff adds none — reported as *not applicable*, never as a passing audit). Secret scan clean across
all three checks. The reviewer noted the change is a net security *improvement*: it structurally
closes the window in which a handoff command could be pasted before approval and run a stage
unattended without the Design Status confirmation.
