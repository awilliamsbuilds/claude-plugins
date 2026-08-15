# Fast Path — Validation
*Branch: feature/fast-path · 2026-08-15 · Standard tier*

## Result

**Clean.** Final cold review returned 0 P1 · 0 P2 and an explicit "safe to merge." Test suite green
throughout (89 tests, `plugins/dev/skills/debt/test_viewer.py`).

Five review rounds ran: parallel code + security review of the build diff, then three fix loops, an
extended auto-fix pass, and a final confirmation review. Each fix loop was cold-reviewed against its
own diff rather than self-assessed.

## Rounds

| Round | Reviewer | P1 | P2 | P3 | Nit |
|---|---|---|---|---|---|
| 1 | Code review (build diff) | 0 | 4 | 5 | 4 |
| 1 | Security review (build diff) | 0 | 2 | 3 | 2 |
| 2 | Cold review of fix loop 1 | 1 | 2 | 2 | 3 |
| 3 | Cold review of fix loop 2 | 0 | 2 | 2 | 3 |
| 4 | Cold review of extended auto-fix | 0 | 1 | 0 | 0 |
| 5 | Final confirmation | **0** | **0** | 1 | 1 |

No P1 existed in the original implementation. The single P1 was introduced by an *incomplete* fix in
loop 1 and caught by the loop-2 cold review — which is the case for cold-reviewing each fix diff
rather than trusting the fixer.

## What was fixed

**Command injection into `gh pr create` (security P2 → P1 on re-review).** The PR body carries three
inputs outside the author's control at call time: the user's free-text request, verbatim test-suite
output, and quoted repo file content from grounding. All were interpolated into a double-quoted
`--body`, where `$…`, backticks, and `$(…)` still expand. This repo's own files are dense with
`$WORKDIR`, `$PRIMARY`, and `$(git rev-parse …)`, so a grounding quote silently dropping a variable
was near-certain and a backticked payload was reachable — in a lane that runs unattended, so nobody
sees the command first. Fixed to `--body-file` with a single-quoted heredoc. The loop-2 review then
caught that `--title` still carried the same input in double quotes; fixed the same way, and the
commit-message rule was made unconditional (an agent judging whether its own message "carries quoted
text" is exactly the judgment that fails). The rule already existed at `reflect/SKILL.md:223` and
`migrate-tracker/SKILL.md:747`; it is now cited where it is mirrored.

**Missing `--repo` (security P2).** `gh` resolves a fork's base repo to the fork's *parent*, so the
lane run in anyone's fork would have opened a PR against an upstream they don't own — unattended,
branch already pushed. Now resolves an `owner/name` slug from `origin` and passes `--repo` on every
call that accepts it. The `sed` handles all four remote forms; `ssh://` was initially missed and would
have hard-failed the lane in such clones.

**Wrong duplication pointer (code P2).** `done/SKILL.md` Step 7's back-pointer claimed the
branch-deletion half was canonical. Step 7 contains no branch deletion — Step 2 does it. A future
editor of Step 7's reconciliation block would have read a pointer about branch deletion and correctly
concluded it did not apply: the exact silent miss the "both ends" requirement exists to prevent.

**Unanchored file operations (code P2).** The lane anchored git commands to `$PRIMARY` but not file
reads and edits, so invoking it from inside a worktree would ground and edit that worktree's files
while committing to `$PRIMARY`.

**Helper defined after use, and cross-fence bindings (code P2 + P3).** `delete_feature_branch` was
called before it was defined. Moving it was not sufficient: a shell function lives only in the
invocation that defined it, and the intervening step says "wait and re-query." Definition and call now
share one fence, which opens with a `: "${VAR:?}"` bind guard — because the same argument applies to
the values, and an unset one fails worse than a missing function: `[ "$ALREADY_MERGED" -eq 0 ]` errors
and evaluates false, *silently skipping the merge*, and `git -C ""` is not an error at all.

**Non-re-runnable merge tail (code P2), twice.** Once `gh pr merge` succeeds the PR is no longer open,
so any downstream failure left a re-run unable to find its own PR — making the guard's own "re-run
`/dev:fix merge`" advice impossible to follow. Fixed with a merged-PR fallback. The `BRANCH =
DEFAULT_BRANCH` guard added alongside it then made a legitimately-interrupted tail unrecoverable, so it
now detects a leftover merged `fix/*` branch and prints a resume command. That scan initially used the
**local** default-branch ref, which is stale in precisely the compound-failure state the guard exists
for — the local ref only advances via the `pull --ff-only` whose failure sets `RECONCILED=0`. Now scans
`origin/$DEFAULT_BRANCH`, verified empirically on both the hit and the exclusion path.

## Deliberate non-fixes

**§P9's slug allowlist does not do what it says.** `^[A-Za-z0-9._-]+/…$` is documented in
`references/tech-debt.md:354` and `reflect/SKILL.md:205` as rejecting a leading `-`, "an
argument-injection vector into the `gh --repo` invocation." It does not — `-` is inside the character
class, so `-foo/bar` passes. Verified empirically. `dev:fix` anchors the first character in its own
copy and says why, so the new site delivers the property; the shared contract is **not** rewritten
here, because §P9 is read by `dev:debt`, `dev:done`, and `dev:reflect`, and changing it is a scope
decision rather than an edit. Recorded as `debt-p9-slug-regex-allows-leading-dash`.

Two follow-ups from the final review are buffered rather than fixed, both non-blocking and both found
after the loop budget was spent: `debt-fix-tail-guard-stale-when-offline` (the guard can report
"already completed" from a stale remote-tracking ref when `fetch` fails — transient, and largely
fenced by Step 2's `gh auth status` check) and `debt-fix-tail-multiple-open-prs-unchecked` (prose
promises a multiple-open-PR stop the snippet does not implement).

## Success criteria

All nine verified mechanically at Build and re-confirmed at Validate: the rename resolves at all 12
sites plus the 2 path-only references a `dev:fix` grep cannot see; `shape`, `build`, and `autopilot`
show no diff at all; every other stage-skill hunk is a rename reference or an authorized carve-out;
`grep -rn '/Users/\|awilliamsbuilds\|adam' plugins/dev/` returns zero; the lane is listed at all five
discoverability sites.

**Not verifiable here, stated plainly:** the installed plugin is a snapshot of `main`, so the lane
could not be exercised through its own invocation. Verification was at the file level, by walking each
procedure manually against the real repo, and by running the shell constructs (slug normalization
across five remote forms, the `:?` bind guard across four shells, `for-each-ref --merged` against a
scratch repo reproducing the compound-failure state) in isolation. A manual walkthrough is not an
end-to-end run.
