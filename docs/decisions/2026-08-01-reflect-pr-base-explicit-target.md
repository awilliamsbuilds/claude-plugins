# dev:reflect — Explicit PR Target — Decision Log
*2026-08-01 · Branch: feature/reflect-pr-base-explicit-target · PR #59*

## What was built

`dev:reflect`'s skill-edit path now resolves an explicit `owner/name` PR target and passes it to
`gh pr create --repo`, so a user working in their own fork of the plugin repo can no longer have a
skill edit proposed against the upstream by `gh`'s fork-parent rule.

## Key decisions

- **Name the target, never let `gh` infer it** → without `--repo`, `gh` resolves the repo from the git
  remotes and sends a fork's PR to the fork's parent. The dogfood check verifies the *checkout*; the PR
  *destination* was a separate question the skill never asked. This adopts Decision 5 of ADR
  `2026-07-28-backlog-debt-model.md` (read the target explicitly, never guess it from `origin`).
- **Dogfood route reuses step 1's already-derived slug** → step 1 traces the skill's cache path to the
  marketplace name to that marketplace's registry entry. §P9's *config read*
  (`enabledPlugins` → `extraKnownMarketplaces[…].source.repo`) is a **different** lookup and is
  deliberately **not** re-run, which would shadow step 1's derivation. Verified by its absence from the
  file.
- **Ask route derives from the named checkout's `origin`, then echoes and confirms** → a fork's own
  `origin` is its own slug, which is the correct home. The echo is what makes a wrong answer visible
  instead of silent. The skill states why this does not violate §P9's "never guessed from `origin`":
  that rule governs resolving a *foreign* cross-repo delivery target, where the current repo is by
  definition not the destination. Here the user has just named the destination.
- **§P9.target-resolution is cited, not copied** → the normalization + allowlist
  (`^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$`, rejecting leading-`-` argument injection) lives in one place.
  A second copy is the drift the contract itself names. One shared sentence in `reflect/SKILL.md`, both
  routes point at it.
- **`--head` explicit, `--base` deliberately omitted** → `--head` mirrors `dev:pr` Step 4's guard against
  `gh` inferring the head from whatever the shared tree is on. `--base` is unnecessary: with `--repo`
  explicit, `gh` bases on *that repo's* default branch — already correct for a fork whose default is not
  `main`. Pinning it would need a `gh repo view --json defaultBranchRef` round-trip and a new failure
  mode. The omission is annotated so a later reader doesn't "fix" it.
- **The invocation is wrapped in `( cd "<source-repo-path>" && gh … )`** → `gh` has no `-C` flag, and the
  resolved checkout is not necessarily the cwd. Same workaround, same reason, as `dev:pr` Step 4.
- **Refuse to branch when `<source-repo-path>` resolves to `$WORKDIR`** (surfaced in validation) → the
  cycle worktree sits on the integration branch, and `push_integration`'s `HEAD:$INTEGRATION` refspec is
  HEAD-agnostic, so a skill edit committed there would ride onto the integration branch unreviewed,
  bypassing the PR entirely. Promoted from a dogfood-route bullet to a route-independent stop condition,
  with both sides of the comparison normalized.
- **Resolution and confirmation moved ahead of the push** → downstream of the push, confirmation can no
  longer prevent publishing and an aborted stop leaves a pushed branch. `tech-debt.md` §P9.delivery sets
  the opposite norm for the analogous case.

## Design choices

Shape was skipped — CLI skill-instruction editing, no visual surface.

## Validation notes

- 4 loops run (tier: standard; limit was 3, reached at loop 3 with an open P2 — user chose to keep
  looping at Step 4a). Every loop's fix diff was cold re-reviewed by a fresh subagent before the loop
  could exit; three of four re-reviews returned new P1/P2 findings, which is what drove the extra loop.
- **P1s found and resolved:** `<source-repo-path>` was never bound on the dogfood route (step 1 resolves
  an *identity*, not a path); loop 1's own fix then asserted `$PRIMARY` is "never `$WORKDIR`", which is
  self-contradictory on a legacy in-place cycle where they are the same directory.
- **P2s found and resolved:** the "`gh` never resolves from the remotes" claim was factually false as
  written; no `git -C` discipline on the branch/commit/push half; echo/confirm and stop conditions sat
  downstream of the push; `--title`/`--body` shell-expansion exposure in a skill full of `$VAR` and
  backticks; no content discipline on the commit; `$PRIMARY` left parked on the skill branch; the
  `$WORKDIR` refusal scoped to one route; the stop condition normalizing only one side of its comparison.
- **P3s:** all resolved except one, deferred to the backlog — `primary-path-relative-in-dev-headers`
  (all eleven `/dev` stage skills derive `PRIMARY` relatively when run from the primary checkout; the
  correct fix spans eleven files, out of scope here, worked around locally by normalizing both sides).
- **Nits accepted as-is:** "several remotes and no unambiguous one" isn't reachable from
  `git remote get-url origin` alone — kept because it mirrors step 1's phrasing, which this cycle must
  not modify. The `( cd … && gh … )` subshell sits in a skill whose header says never `cd` — kept
  because `gh` has no `-C` flag and `pr/SKILL.md` Step 4 sets the precedent.
- **Process caveat:** the final two nit fixes were applied after loop 4's cold re-review returned, so
  they carry no cold pass of their own. Both are textual clarifications of prose this cycle wrote.
- **Scope held:** `plugins/dev/skills/pr/SKILL.md` and `plugins/dev/references/tech-debt.md` ended the
  cycle byte-identical (Success Criterion 7).

## Artifacts (archived)

Spec, plan, and validation committed at: `59f469bd6ef8a6cfcfdc34139f637e5dae21a96a` on branch
`feature/reflect-pr-base-explicit-target`.
