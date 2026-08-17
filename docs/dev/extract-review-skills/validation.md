# Extract Review Skills — Validation Report
*Branch: feature/extract-review-skills · 2026-08-17*

## Summary
Loops run: 4 / 5
Final status: clean

Both Step 2 reviews ran cold and in parallel against `92522c0..b2f688b`. Neither returned a P1. Four
fix loops followed, each closed by a cold re-review of only that loop's own fix diff; the final
re-review returned no P1 and no P2.

## Build
no build system detected

Detection ran B1–B5 in order inside `$WORKDIR`: no `package.json`, no `Makefile`, no `Cargo.toml`, no
`go.mod` → **B5 / outcome O3**. Recorded as detected-nothing, never as a pass.

The repo's only executable verification is the `dev:debt` viewer suite, which this cycle does not
touch. It was run as a regression check after Build and after every fix loop: **89 tests, OK
(skipped=2)** each time.

## Issues Resolved

### Loop 1
- **P2**: the dispatched review subagent was never told the run is read-only → added a **Read-only**
  instruction to `dev:review`'s `## Cold dispatch` (canonical) and `dev:secure`'s mirror. This was the
  one place the cycle *weakened* an existing property: `dev:secure` previously ran in-session, where
  `## Purpose`'s "writes nothing" bound the executing context; moving the work to a fresh
  `general-purpose` agent (which has write tools) lost that, and `dev:fix` runs both reviewers
  unattended immediately before opening a PR.
- **P2**: the `### Security` → `### Review` rename left **three** dangling references →
  `validate/SKILL.md:182` (the *canonical* half of the fix-once mirror pair), `fix/SKILL.md:522`, and
  `fix/SKILL.md:544` (a control-flow instruction on the lane's dominant path). All swept, plus the
  surrounding "before Security" prose.
- **P2**: four cross-file line citations newly written into `review/SKILL.md` resolved to unrelated
  text — they were computed against the pre-cycle `secure/SKILL.md`, which this same cycle grew by
  ~130 lines → converted to **section names**, which cannot drift.
- **P3**: `grep -Eq` allowlists are line-oriented. Measured: a value of `/tmp/ok` + newline +
  `rm -rf /` **passes** → replaced with whole-string `case` guards in both files (tree and base).
- **P3**: `git rev-parse --is-inside-work-tree` prints `false` and **exits 0** for a git dir or bare
  repo, so the exit-status check accepted non-worktrees → now compares the output to `true`.
- **P3**: the `<tree>` allowlist rejected any path containing a space, which would have failed
  `"$WORKDIR"` for a repo under e.g. `/Users/x/My Projects/` and escalated to a stage stop → charset
  widened to admit a literal space. Verified still rejecting `-`-leading, newline, `;`, `$(…)`, and
  backtick.
- **P3**: artifact paths were unconstrained absolute paths whose *contents* are read and forwarded to
  a subagent → containment check added, plus a stated rule for `docs` mode, which has no `$TREE`.
- **P3**: `dev:fix`'s terminal report named only the security outcome → names both.
- **P3**: the PR-body interpolation-safety rationale under-enumerated its own untrusted inputs →
  now cites both reviews' findings.
- **P3**: the reviewer-cannot-run stop sat after the architecture subsection, so the feature-cycle
  path flowed past it → pointer added at the end of the feature-cycle dispatch.
- **Nits**: `CLAUDE.md`'s `dev:fix` row still said "before the security review"; the whole-project
  report header named a `<branch>` the verb never derived (now derives `AUDIT_BRANCH`); the
  `INVOKED_IN` remediation line interpolated unquoted; the dispatch fence hardcoded `plan.md` on a
  tier that has none.

### Loop 2
- **P2**: the containment check added in loop 1 **did not contain**. `case "$ARTIFACT" in "$TREE"/*)`
  is a plain prefix test on the unnormalized path, and `.` and `/` are both in the permitted charset —
  measured, `"$TREE/../../../../etc/passwd"` passed all four checks. Worse, the prose I wrote claimed
  it "closes it as an invariant," which is the unmeasured-behavioral-claim class the same file forbids
  two paragraphs earlier → `..`-segment rejection added to artifact paths **and** `<tree>` in both
  files, trailing-slash strip added (an unstripped `/x/repo/` makes the pattern `/x/repo//*` and
  rejects every legitimate artifact), and the claim corrected to say what it actually does.
- **P3**: `TREE_SUPPLIED` was consulted nowhere else, so a lost binding would print "no tree was
  supplied" *during an audit of a supplied tree* — the exact mis-disclosure it was added to remove →
  guard now also tests `[ "$TREE" = "$PRIMARY" ]`, so failure is silent rather than wrong.
- **P3**: both mirror pairs had their divergence named at only one end → named at both.
- **Nits**: report-header placeholder inconsistency; `<AUDIT_BRANCH>` rendering empty on detached HEAD.

### Loop 3
- **P3**: the loop-2 guard addition left the surrounding prose saying "**two** `case` statements" where
  the block now had three, in four places across both files → corrected, and the enumeration extended
  to name the third.
- **P3**: `dev:secure` inherited loop 2's two new guards with no in-file rationale, in a file whose
  house style is to record rather than gloss → added the mirror-fidelity reason (it has no containment
  consumer; the guards are carried so the blocks stay byte-identical apart from one named divergence).

### Loop 4
- **P3**: "**Three** branches" sat above **four** bullets in both files — the same off-by-one class
  loop 3 existed to fix, one paragraph above the corrected text → counts and the stale ordinal fixed.
- **Nit**: `docs` mode still said "fails **either** check" for a four-check set → "any".
- **Nit**: the "no consumer" claim was imprecise about how `$TREE` is used → made specific.

## Issues Remaining

### P1 Open
None.

### P2 Open
None.

### P3 Open
- `secure/SKILL.md`'s "no consumer" sentence reads as a closed enumeration of `$TREE`'s uses but omits
  two display-only sites (the base-resolution refusal message and the empty-diff template). The
  load-bearing conclusion is correct and confirmed by the final re-review — both omitted sites are
  display-only, so neither is a consumer a `..` segment or trailing slash could defeat.

### Nits Surfaced
- The loop-4 rewrap in `secure/SKILL.md` is ragged (a 25-char line followed by a ~106-char line) in a
  file that otherwise holds ~95–102.

## Notes

**Why the loop exited at 4 rather than running the P3 down.** Step 4's rule is that defect-class P3s
are fixed inline and polish-class P3s go to Step 5a. The remaining P3's *claim* is correct — the final
cold re-review verified the conclusion holds — so what is left is completeness of an enumeration, not
a wrong statement. That is the polish class, and this region had already produced findings in three
consecutive rounds. Editing it a fourth time is the compounding Step 4 step 4 and the same-region
recurrence rule both exist to stop.

**Same-region recurrence: triggered, and deliberately not treated as recurrence.** Step 4 step 8's
mechanical condition was met from loop 3 onward — consecutive rounds produced findings in the
path-guard region. It was not applied, because the rule's own diagnostic is "the loop is circling one
unsettled decision," and no decision was unsettled here: severity fell monotonically (P2 → P3 → P3),
no shell was altered after loop 2, and each round's findings were finite and enumerated. Recorded
here rather than left implicit, since it is a judgment call against a stated rule.

**Success Criterion 8 — the template-injection question is settled, and this is the record.** Read
`secure/SKILL.md`'s Injection bullet and `validate/SKILL.md:75` side by side. `dev:secure`'s only
`template` hit was "template literals into queries" *under SQL* — a JS syntax feature interpolated
into a query, i.e. SQL injection. `dev:validate` listed `template` as an injection type in its own
right. **Settled as distinct**: a user-controlled template rendered server-side (Jinja2, ERB,
Handlebars, Twig) is a different class with a different impact, typically RCE. Pass C's Injection
bullet now names it explicitly, so the criterion is satisfied by the file rather than only by this
record. CSRF was confirmed absent from Pass C **and** from the "deliberately not covered" list before
being added — absent from both is what made it a coverage loss rather than a declared boundary.

**Plan Task 13 step 8 — which reading held for the three non-sweep citations.** All three survive
unedited, confirmed against the post-Task-8 files rather than assumed:
- `spec/SKILL.md:565` and `plan/SKILL.md:210` ("the same reason `dev:validate` withholds conversation
  history from its reviewers") — still true by two routes: Step 4 step 8's re-reviewer, and both Step 2
  reviewers via `## Cold dispatch`. Validate dispatches reviewer *skills* now instead of checklists,
  but the history exclusion is unchanged.
- `references/tech-debt.md:458` ("the same rule `dev:validate` and `dev:spec` already apply to review
  subagents") — still true; both injection guardrails are intact.
`references/tech-debt.md` therefore needed no edit, and the conditional row in the plan's Files table
resolved to no change.

**Success Criterion 4's carve-out was exceeded by one plan-authorized edit.** SC4 permits only the two
Step 4 step 8 citations as text edits outside Step 2, but plan Task 10 step 3 directed a third — the
note marking the fix-diff re-review checklist as the named exception to *an orchestrator never defines
a checklist*. Loop 1 added a fourth (`:182`'s `### Security` → `### Review`), without which the
canonical half of a declared mirror pair would have pointed at a section that no longer exists. Both
are spec/plan conflicts resolved in favour of not shipping a dangling reference. Named so a
criterion-by-criterion audit reads them as deliberate rather than as misses.

**One implementation detail diverges from the spec's stated pattern.** Spec Scope 2 and the plan name
the `<tree>` allowlist as the regex `^/[A-Za-z0-9._][A-Za-z0-9._/-]*$`. What shipped is three `case`
guards with the same accept/reject set **plus** a literal space and **minus** `..` segments. The regex
form was line-oriented (measurably bypassable) and would have rejected legitimate checkouts under a
path containing a space. The final re-review confirmed the accept/reject sets are otherwise identical
to the specified pattern, so no caller regresses.

**A residual the reviews scoped rather than closed.** Artifact containment defeats `..` traversal but
not symlink escape — a symlink under `$TREE` pointing outside it passes every check. The security
reviewer raised this explicitly as *not* a finding, because no current caller can reach it
(`dev:validate` builds every path from `$WORKDIR`; `dev:fix` passes none) and the shipped prose scopes
its claim to `..` rather than asserting general containment. Recorded here so a future cycle that
makes `dev:review` take untrusted paths knows the invariant it would need to strengthen.
