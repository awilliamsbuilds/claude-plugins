# Retire Legacy Commands — Validation Report
*Branch: feature/retire-legacy-commands · 2026-08-15*

## Summary
Loops run: 3 / 5
Final status: clean — no open P1/P2

## Build
no build system detected

Detected per `dev:validate` Step 5b's B1–B5: no `package.json`, `Makefile`, `Cargo.toml`, or
`go.mod` in this repo, so branch **B5** applies and outcome **O3** records it here. This is not a
pass — nothing was built. (Step 5b is itself shipped by this cycle; running it against its own diff
is deliberate dogfooding, and it correctly detected the absence rather than claiming success.)

## Issues Resolved

### Loop 1
- **P2:** three line-number citations the diff *added* were already stale, shifted by this same
  diff's earlier insertions. `secure`'s cite for the P1/P2/P3/Nit table pointed at
  `validate/SKILL.md:102-111`, which after Task 8's insertions is the **architecture** severity
  mapping — the very scheme the sentence says the skill does not use. → all three replaced with
  section names, the convention the plan mandated elsewhere for exactly this reason.
- **P2:** the security audit diffed against the **local** default branch while the lane cuts its
  branch from `origin/$DEFAULT_BRANCH` and the PR's base is the remote. A local ref behind origin is
  still an ancestor of HEAD, so the diff succeeds against a stale merge base and the audit covers
  unrelated commits — under this cycle's own stop rule, a finding in that extra code would block a
  PR that does not contain it. → resolves `AUDIT_BASE="origin/$DEFAULT_BRANCH"` with a fallback.
- **P2:** `dev:secure` used the explicit `<base>` token verbatim in `git diff`, so a `-`-leading
  value parses as an option. **Measured:** `git diff --output=FILE` creates the file and returns an
  empty diff — the skill would report examining nothing while writing outside the repo, breaking
  SC1's zero-write invariant. → anchored ref allowlist plus `--end-of-options` (measured: rejects it).
- **P3:** the subagent-unavailable fallback sat on the branch that never dispatches a subagent. →
  moved to the cold re-review, the section's only dispatch.
- **P3:** rung 2's `gh repo view` named no repo, so a fork resolves its parent. → anchored slug.
- **P3:** the "never clean" rule covered only a *missing* scanner; one that exits non-zero with no
  parsable report read as clean. → rule extended; `pip-audit`'s scope pinned (bare, it audits the
  active environment rather than the project).
- **Nit:** O-labels are build-only, so "a failing build or suite (Verify's O2)" mislabeled the suite.
- **Nit:** the untrusted-input enumeration did not name the security findings the body now renders.

### Loop 2
- **P1 — introduced by loop 1's own fix.** `git diff --end-of-options "$BASE"...HEAD --name-only`
  fatals: every other option must come **before** `--end-of-options`. **Measured:** exit 128 with
  `option '--name-only' must come before non-option arguments`, versus exit 0 for
  `--name-only --end-of-options`. The diff verb would have lost its changed-file list on every run,
  which via the `not run` rule stops `dev:fix` without a PR on a healthy repo. → reordered, with the
  constraint and its measurement stated inline so the next editor does not re-swap it. The guard
  still blocks `--output=` in the corrected order (verified: no file created).
- **P3:** the explicit-base path validated `$BASE` with nothing assigning it.
- **P3:** the rationale for the scanner rule claimed `npm audit --json` "prints nothing" without a
  lockfile. **Measured false:** exit 1 with a 239-byte `ENOLOCK` JSON object. Rule was right, reason
  was wrong — the exact claim class the `step 3b` rule *this cycle adds* requires measuring, caught
  in this cycle's own prose.
- **P3:** loop 1 replaced three stale line citations and introduced a new one (`fix/SKILL.md:70-84`,
  whose range excluded the regex it cited). → section name.

### Loop 3
- **P2 — found by executing the procedure rather than reading it.** The `diff` verb anchors every
  command to `$PRIMARY`, the primary checkout, which on a repo with active `/dev` worktrees is
  usually on the default branch while the work under review is on a worktree's branch. **Measured in
  this repo: 0 changed files where the worktree has 13.** Diffing the wrong tree does not error — it
  returns an *empty* diff, and the empty-diff branch then reports there was nothing to examine. A
  security gate confidently saying "nothing to audit" is the worst available failure shape. →
  `$PRIMARY` stays the audited tree (correct for `dev:fix`, which operates on it by contract), but
  the verb now **discloses**: a notice naming both trees, the audited branch in the report header,
  and the empty-diff message naming branch and base. Verified firing from the worktree and silent
  from the primary checkout.
- **P3:** `BASE="<the second token, verbatim>"` was an angle-bracket placeholder inside a bash fence.

## Issues Remaining

### P1 Open
- None.

### P2 Open
- None.

### P3 Open
- `AUDIT_BRANCH` is never printed on the healthy path, so the report's new `**Branch audited:**`
  field is interpolated from recall rather than from observed output.
- The notice's remediation line ("run from the primary checkout of it") is unactionable for a `/dev`
  worktree — all worktrees share one primary checkout, so following it reproduces the same audit.
- The **whole-project** verb has the same wrong-tree exposure with no disclosure at all, and unlike
  the diff verb it does not come back empty — it comes back looking like a completed clean audit of
  code the user is not looking at.

### Nits Surfaced
- `BASE="$2"` is the only positional-parameter notation in any `dev` skill, with no script or
  function context for it to bind in. It fails loudly and safely (the next guard stops on the empty
  value), so it does not gate.

## Notes

**Same-region recurrence — the loop was stopped deliberately, not by exhaustion.** Loop 2's
re-review found a P1 in `secure/SKILL.md`'s diff-verb region; loop 3's found P3s in that same region.
Two consecutive rounds in one region is `dev:validate` Step 4 step 8's signal that the loop is
circling an unsettled decision rather than converging on it. The unsettled question, stated plainly:
**which tree should `/dev:secure` audit when it is invoked from inside a worktree?** `dev:fix` needs
`$PRIMARY`; a human standing in a worktree means "what I am looking at." That is a design call, not a
fix-loop call. Per the autopilot branch of that rule the run continues, no further fixes were
attempted in that region, and its remaining findings are buffered rather than dropped. Budget was not
the constraint — 3 of 5 loops were used.

**What the cold re-reviews earned this cycle.** Loop 1's fix introduced a P1 that loop 2 caught; loop
2's fix was clean at the gate but loop 3's execution-based check found a P2 that three prior
reviews — two reading the diff, one reading the fix — had all missed. The distinguishing move was
running the procedure instead of reading it, which is precisely what this cycle's own new `step 3b`
requires. Two of this cycle's three P2s were found that way.

**SC9 is not yet satisfied and is not expected to be here.** Both debt items remain in
`docs/backlog/` with `status: open`; their close-intents are buffered in `debt-pending.md`'s
`## To Close`, and `dev:done` Step 6a executes the archive-and-close. Worth confirming at merge —
it is the criterion most easily missed there.
