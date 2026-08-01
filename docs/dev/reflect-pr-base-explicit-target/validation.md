# dev:reflect — Explicit PR Target — Validation Report
*Branch: feature/reflect-pr-base-explicit-target · 2026-08-01*

## Summary
Loops run: 4 / 3 (limit reached at loop 3 with an open P2; user chose **A — keep looping** at Step 4a)
Final status: clean — no open P1/P2

Every loop's fix diff was cold re-reviewed by a fresh subagent before the loop could exit, per Step 4
step 8. Three of the four re-reviews returned new P1/P2 findings, which is what drove the extra loop.

## Issues Resolved

### Loop 1 — from the two parallel cold reviews (code + security)
- **P1:** `<source-repo-path>` was never bound on the dogfood route. Step 1 resolves an *identity*
  ("the current checkout **is** the source repo"), not a path, and `reflect/SKILL.md:25` states that
  under `dev:done` `$WORKDIR` is the cycle worktree on the integration branch — a live wrong answer.
  → Bound it explicitly.
- **P2:** "`gh` never resolves the repo from the git remotes" was factually false and contradicted the
  very next clause (which described that resolution). → Restated as the conditional truth: *without*
  `--repo`, `gh` resolves from the remotes and picks a fork's parent.
- **P2:** the branch/commit/push half of step 2 had no directory discipline while the `gh` half argued
  at length that the checkout is not the cwd. → `git -C "<source-repo-path>"` throughout.
- **P2:** echo/confirm and both stop conditions sat *downstream of the push*, so confirmation could no
  longer prevent publishing and an aborted stop left a pushed branch. `tech-debt.md` §P9.delivery sets
  the opposite norm for the analogous case. → Resolution and confirmation moved ahead of the push.
- **P2:** `--title`/`--body` interpolate into double-quoted shell args; skill prose is full of `$VAR`
  and backticks, and this skill's own line 169 flags backlog-store text as untrusted. → Added the
  expansion warning and the `--body-file` / single-quoted-heredoc guidance.
- **P3:** the dogfood route didn't point at the shared normalize-and-validate procedure, reading as
  though an already-derived slug were already trusted. → Both routes now run it.
- **P3:** no defined behavior when the user rejects the echoed slug. → Take a slug directly, revalidate,
  re-echo; stop if they can't name one.
- **P3:** step 1's `~/.claude/plugins/cache/` guard wasn't re-applied to the ask route's answer.
  → Reject and re-ask.
- **Nits:** `<branch-name>` was a dangling placeholder; the ask route named `git remote get-url origin`
  without the `git -C` form the rest of the file uses. → Both fixed.

### Loop 2 — from the loop 1 fix-diff cold re-review
- **P1:** loop 1's fix said "`<source-repo-path>` is `$PRIMARY`, never `$WORKDIR`" — self-contradictory
  on a legacy in-place cycle, where the header's second resolution case makes them the same directory.
  Verified: `push_integration` is `git -C "$WORKDIR" push origin "HEAD:$INTEGRATION"`, HEAD-agnostic, so
  a skill edit committed there rides onto the integration branch unreviewed, bypassing the PR.
  → Refuse to branch when they coincide; also corrected the stated hazard, which loop 1 had misattributed
  to the flush breaking rather than to the refspec being HEAD-agnostic.
- **P2:** no content discipline on the commit, in a checkout the user may have unrelated work in.
  → Pathspec-scoped commit, never `-a`/`add -A`; stop if the branch can't be created cleanly.
- **P2:** `$PRIMARY` was left parked on the skill branch, sending `dev:done` Step 7's reconcile down its
  "different branch" arm (`done/SKILL.md:553-567`) → `refadvanced` instead of a fast-forward.
  → Restore the original branch.
- **P3 / Nit:** `$PRIMARY` may be relative; "four `<…>` values" was five. → Both addressed.

### Loop 3 — from the loop 2 fix-diff cold re-review
- **P2:** the `$WORKDIR` refusal was scoped to the dogfood bullet, but the hazard belongs to the
  directory, not the route — the ask route could land on `$WORKDIR` too (a user asked where the source
  repo lives may name the checkout they're standing in). → Promoted to a route-independent stop condition.
- **P3:** loop 2's `$PRIMARY` rationale was backwards. Measured: `--git-common-dir` returns an *absolute*
  path from a linked worktree (the dominant case under `dev:done`) and a relative one only from the
  primary checkout. → Rationale corrected, depth-dependence included.
- **P3:** the restore was under-specified — nothing recorded the original ref, detached HEAD had no
  referent, and it was gated on the PR succeeding. → Record with
  `symbolic-ref --quiet --short HEAD || rev-parse HEAD` (exits 0 in both states), restore unconditionally.
- **Nit:** a commit in `$WORKDIR` was said to land on `main`; on a nested cycle `$INTEGRATION` is the
  parent's branch. → Corrected.

### Loop 4 — from the loop 3 fix-diff cold re-review
- **P2:** the new stop condition normalized only one side of its own comparison. `$WORKDIR` is derived
  from `$PRIMARY` and inherits its relativity, so matching an absolute `<source-repo-path>` against a
  bare `.` would miss exactly the legacy-in-place ask-route case the condition exists for.
  → Compare both sides normalized.
- **P3:** `cd "$PRIMARY" && pwd` at point-of-use inherits the cwd dependence the skill's header forbids.
  → Normalization tied to the shell that still holds the derivation cwd (see Notes — the full fix is
  deferred).
- **P3:** the restore was gated on "once the feature branch exists", so a failed commit would carry an
  uncommitted edit onto the restored branch. → Gated on the commit existing.
- **Nits:** the restore named no command and a bare-SHA restore re-detaches, unstated; `SRC` was
  introduced and never bound to `<source-repo-path>`; the no-commit clause misdescribed the
  branch-never-created case. → All three fixed.

## Issues Remaining

### P1 Open
None.

### P2 Open
None.

### P3 Open
None open against this cycle's scope. One P3 was **deferred to the backlog** rather than fixed here —
see Notes.

### Nits Surfaced
Two, both deliberate and left as-is:
- "several remotes and no unambiguous one" isn't reachable from `git remote get-url origin` alone.
  Kept because it mirrors step 1's existing phrasing, which this cycle must not modify.
- The `( cd … && gh … )` subshell sits in a skill whose header says never `cd`. Kept because
  `gh` has no `-C` flag and `pr/SKILL.md` Step 4 sets the same precedent for the same reason.

## Notes

**Deferred to backlog (Step 5a):** `primary-path-relative-in-dev-headers` — all eleven `/dev` stage
skills derive `PRIMARY=$(dirname "$(git rev-parse --git-common-dir)")`, which is relative when run from
the primary checkout, and `$WORKDIR` inherits it. The correct fix edits the shared header block across
eleven files; this cycle was scoped to step 2 of one section of one skill, and works around it locally
by normalizing both sides before comparing. Buffered in `debt-pending.md` for `dev:done` Step 6a.

**Also buffered:** the close-intent for `debt-reflect-dogfood-pr-base`, the item this cycle pays
(written at Build, unchanged here).

**Scope held throughout.** `plugins/dev/skills/pr/SKILL.md` and `plugins/dev/references/tech-debt.md`
are byte-identical to their pre-cycle state (Success Criterion 7). Step 1's discovery logic, steps 3
and 4, the "Ask fallback (the common case)" paragraph, and the two-confirmation gate are all unchanged.
All seven success criteria verified against the file on disk, including SC2's negative check — no
`enabledPlugins` or `extraKnownMarketplaces` lookup anywhere in the file — and SC4's, no second copy of
the §P9 allowlist regex.

**One caveat on process:** the final two nit fixes (the `SRC` binding and the no-commit-clause wording)
were applied *after* loop 4's cold re-review returned, so they carry no cold pass of their own. Both are
textual clarifications of prose this cycle wrote; neither changes the procedure.

**For the PR description:** the fix is behavioral for forks only. This repo is not a fork, so `gh`
already resolves correctly here — the cycle exists so the plugin is safe for anyone who forks it.
