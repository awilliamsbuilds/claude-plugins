# Entry Adapters — Validation Report
*Branch: feature/entry-adapters · 2026-08-15*

## Summary
Loops run: 3 / 5
Final status: **clean** — no open P1 or P2

Reviews were dispatched as fresh subagents with no conversation history: a code review and a
security review over the full Build diff, then a cold re-review of **each loop's own fix diff**
before the loop was allowed to exit. The third re-review returned clean at every severity.

## Issues Resolved

### Loop 1 — from the two Build-diff reviews

- **P1** (`fix/SKILL.md`, mirrored in `entry-adapters.md` §A4) — the merge tail's Closeout block
  `:?`-asserted `BRANCH` and `ITEM`, whose recovery advice ("re-run the resolution block") cannot
  work: by that point the merge fence has deleted the feature branch and moved the checkout to
  `$DEFAULT_BRANCH`, so re-running binds `BRANCH` to the default branch and exits on its own guard.
  The section simultaneously claimed those variables were re-derivable *and* that the block runs in a
  different invocation — the two cannot both hold. **SC3 would have failed on the ordinary path.**
  → Fixed: `ITEM`/`BRANCH_MERGED` became agent-substituted literals (the idiom the skill already uses
  everywhere else); `:?` retained only for `PRIMARY`/`DEFAULT_BRANCH`, which have re-runnable
  derivations; `RECONCILED` still re-derived from observable state.

- **P2** (both reviewers, independently) — the Closeout's `status: open` check did not deliver what
  its own prose claimed. It catches an *already-closed* item and does nothing about an *unrelated but
  open* one, and `fix/` is not exclusive to the backlog dispatch. A Linear `gitBranchName` beginning
  `fix/`, or a free-text summary that kebabs into an item's basename, would have archived a real item
  — committed and pushed, reported as a legitimate close, for a merge that never paid it.
  → Fixed: a `^(debt|backlog)-[a-z0-9][a-z0-9-]*$` basename allowlist gates the Closeout, with both
  guards documented as required and non-redundant.

- **P2** (`fix/SKILL.md`) — `BRANCH_NAME` was consumed by five shell lines and assigned by none; it
  existed only in prose. An empty value would have made Step 5's collision check read `refs/heads/`
  and silently find nothing, missing a real collision before failing at the push.
  → Fixed: a documented re-derivation via `git branch --show-current`, exact after `checkout -b`.

- **P2** (security, `pr/SKILL.md`) — Step 4 built the PR body into a **double-quoted `--body`** while
  this cycle made Linear issue text a first-class input to it. An issue description containing
  `$(…)` would reach command substitution during an unattended cycle. The plan had deferred this as
  out of scope; the deferral did not survive review, because this cycle is what routes external
  content there and the fix is three lines in a file already being edited.
  → Fixed: single-quoted heredoc + `--body-file`, matching the discipline `dev:fix` already carried.

- **P3s fixed inline** — a `commit -F -` fence with no heredoc attached (would abort on EOF and leave
  `config.json` staged for the next commit to sweep up); the Linear Pre-lane side effect firing before
  Step 3's "nothing to change" exit with no report line; bare `references/…` paths that do not
  resolve from a skill directory; the prompt-injection guardrail restated twice on the backlog path
  and zero times on the higher-exposure Linear path; stale line-number citations this diff created;
  and a config cache committing workspace identifiers into a tracked file.

### Loop 2 — from the cold re-review of loop 1's fix diff

- **P1** (`pr/SKILL.md`) — **a regression introduced by loop 1's own fix.** The new body heredoc wrote
  to `$WORKDIR/.git/dev-pr-body.md`; in a worktree — which is every modern cycle — `.git` is a regular
  *file*, so the redirect fails with `Not a directory` and the stage opens no PR at all. Confirmed
  empirically in this worktree before and after.
  → Fixed, then re-fixed in loop 3 (below).

- **P2** (`entry-adapters.md` §A4) — loop 1's new allowlist was stated as running *before* resolution,
  contradicting §A4's own rule four paragraphs later that a bare slug is accepted and normalized.
  `/dev:fix backlog fix-tail-guard-stale-when-offline` would have read as a refusal.
  → Fixed: allowlist scoped to the *normalized* value, after resolution.

- **P3s** — the `BRANCH_NAME` derivation was documented *after* the fence consuming it; five bare
  `references/tech-debt.md` paths remained in `migrate-tracker`.

### Loop 3 — from the cold re-review of loop 2's fix diff

- **P3, fixed rather than deferred because it was a regression this cycle introduced.** Loop 2's
  `$GIT_COMMON` fix was correct only from a worktree: `git rev-parse --git-common-dir` returns `.git`
  from the primary checkout root and `../.git` from a subdirectory, and the fence later `cd`s, so a
  relative path would be re-resolved against a different directory on the legacy in-place lane.
  Verified by running the derivation from all three positions.
  → Fixed: `$PRIMARY/.git/…`, absolutized by the stage preamble and correct on both lanes. The
  supporting prose also corrected a false claim about `dev:fix` ("that lane never runs in a
  worktree") — `fix/SKILL.md:47` says the opposite; it is safe because it anchors on `$PRIMARY`.

- **P3** — §A4's justification prose still described the pre-fix ordering, which could have led a
  future reader to "tidy" the allowlist back before resolution and reintroduce the loop-2 P2.
  → Fixed, and the ordering constraint is now stated in **both** directions.

## Issues Remaining

### P1 Open
None.

### P2 Open
None.

### P3 Open
- `autopilot/SKILL.md:139` cites `spec/SKILL.md:478`; this cycle's spec edits shifted that target to
  ~533. **Deliberately not repaired** — SC10 requires `dev:autopilot` byte-identical, and a citation
  repair is not a `dev:linear` rename reference, so fixing it would break a stated success criterion
  to fix a P3. Recorded as debt instead (see below). The citation degrades gracefully: the
  surrounding prose names "Step 12 reconciles", so the target is still findable by name.

### Nits Surfaced
- `pr/SKILL.md` carries three pre-existing shell blocks whose `<placeholder>` arguments are unquoted,
  so `bash -n` rejects them. Not introduced by this diff and not executed literally.
- Bare `references/tech-debt.md` paths remain at `init/SKILL.md:162` and `done/SKILL.md:264`.
  Pre-existing and untouched; `done/` is additionally SC10-constrained this cycle.
- Both `pr/SKILL.md` and `fix/SKILL.md` hardcode the `.git` basename rather than using the resolved
  common-dir name, so a repo using `--separate-git-dir` would have no `$PRIMARY/.git`. Pre-existing
  across the repo — the `PRIMARY` derivation itself already assumes it.

## Notes

**All eleven success criteria were re-verified after the final loop.** SC6, SC8, SC10, and SC11 are
mechanical and were run as commands returning zero/expected counts. The regression suite
(`python3 -m unittest discover -s plugins/dev/skills/debt`) passes at 89 tests.

**SC1, SC2, SC3, SC4, SC5, SC7, and SC9 were not executed.** They assert behavior, and this repo has
no harness that can run a skill. They were verified by walking the edited procedures against the real
files, and by three independent cold reviewers tracing the same paths. That is the best available
substitute and it is not equivalent — the gap is recorded against
`docs/backlog/backlog-dev-skill-test-harness.md`, whose `recurrence` this cycle incremented with the
evidence.

**One out-of-repo change was made during Build and is not visible in this diff.** A reviewer correctly
flagged it: `~/.claude/settings.json` had `vercel-plugin@vercel` set to `false`, at the user's explicit
request, after a third-party plugin's `UserPromptSubmit` hook was observed injecting directives into
this cycle. A backup was written alongside. It is machine-local configuration, outside the spec's
scope, and is recorded in the debt buffer rather than hidden.

**The `Closes` line's end-to-end behavior remains unverified.** Whether Linear's GitHub integration
parses `Closes [<ID>](<url>)` from a PR body is Linear-side behavior no file in this repo can assert.
The design does not have a single point of failure here — the `gitBranchName` path also carries the
issue ID — but the criterion should not be reported as executed.
