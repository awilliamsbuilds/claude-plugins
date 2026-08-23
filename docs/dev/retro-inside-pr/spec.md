# Retro Inside PR
*Branch: feature/retro-inside-pr · Confidence: 100% — Ready · 2026-08-23*
*Cycle type: feature · Tier: deep*

## Intent

Every reviewable content edit a `/dev` cycle makes should be in the PR a human reviews. Today four of
them are not: `dev:done` merges the PR first, then commits the Component Registry update, the
docs-prose reconciliation, the decision log, and the retrospective **directly to the integration
branch**. The cycle's own reasoning is absent from the diff a reviewer reads, and those commits go
through no review at all.

`retire-legacy-commands` demonstrated it concretely — PR #82 merged, then its decision log and
retrospective landed on `main` afterwards.

Milestone 3 of `docs/dev/product-plans/dev-process-hardening.md`. Source item:
`docs/backlog/backlog-reflect-before-pr-merge-retire-legacy-commands.md`.

## Scope

**1. Relocate four `dev:done` steps into `dev:pr`, after `gh pr create`.**

`dev:pr` Step 5 already commits and pushes *after* the PR is opened, and a push to the PR's head
branch updates the PR. That existing push is the mechanism — the relocated steps need no new
plumbing to land inside the diff.

| Moves from | To | Gains |
|---|---|---|
| `dev:done` Step 4 — Component Registry | `dev:pr`, post-create | reviewed |
| `dev:done` Step 4a — Reconcile Docs Prose | `dev:pr`, post-create | reviewed |
| `dev:done` Step 5 — Generate Decision Log | `dev:pr`, post-create | reviewed; `PR #N` available |
| `dev:done` Step 6 — Run `dev:reflect` | `dev:pr`, post-create | reviewed; `pr_created` already stamped |

Constraints on the relocation:

- **Relative order 4 → 4a is preserved.** `dev:fix`'s D3 divergence rests on "`dev:done` Step 4a must
  never touch the table because Step 4 owns it two steps earlier" (`fix/SKILL.md:574`). The reasoning
  survives only if the ordering does.
- **The decision-log template is unchanged**, including its `PR #N` header field. That field is why
  this cycle places the work after `gh pr create` rather than at the end of Validate: at the end of
  Validate there is no PR number, and changing the header would break comparability with every
  existing decision log — a property `dev:done` Step 5 states explicitly.
- **`dev:reflect` is invoked as a whole**, steps 1–6, from its new home. It is not split across
  stages.
- **`dev:done` Steps 3, 6a and 7 stay post-merge** and are untouched. Step 6a's "position is
  load-bearing twice over… Do not move it" note still holds: it reads the buffer from disk in
  `$WORKDIR`, so `dev:reflect` writing that buffer one stage earlier only makes "reflect's items are
  included" more certain.
- **Both relocated feature-cycle guards survive.** Steps 4 and 4a are `feature cycles only`;
  architecture cycles still skip them.

**2. `dev:reflect` Step 6's skill-update gate becomes three-way.**

Today the gate is yes/no, where "yes" edits the SKILL.md and opens a **second PR in-session**. Run
that before the merge and the second PR branches from a `$PRIMARY` `main` that lacks this cycle's
edits — and this cycle edits `done`, `pr`, `reflect` and `fix`, the likeliest targets of such a
suggestion. Making the acting path opt-in by name removes the collision as a default:

```
dev:reflect found a suggestion: [suggestion].

  backlog  — record as work to do. Nothing happens now.
  debt     — record as an accepted cost. Nothing happens now.
  fix now  — edit the skill and open a separate PR immediately.
             This goes through no /dev stages: no spec, no plan,
             no validate. It is a direct edit under two confirmations.
```

- `backlog` → buffer entry with `type: backlog`
- `debt` → buffer entry with `type: debt`; the carrying-cost test still gates it, unchanged
- `fix now` → today's "yes" path verbatim, including both confirmations and every stop condition

The prompt must state that the first two act on nothing at the time. The existing rule that
`$WORKDIR` is refused as `<source-repo-path>` stays, but its stated *reason* changes: at PR stage
`$WORKDIR` pushes to the feature branch, not `$INTEGRATION`, so the current justification ("a skill
edit committed there would land on `$INTEGRATION`") no longer describes the hazard and must be
rewritten to the one that now applies — the edit would land in this cycle's own PR.

**3. Two pre-existing `dev:reflect` Step 5 defects.**

- **Path.** `cat >> docs/decisions/<file>.md` is cwd-relative while every sibling command in the file
  uses `$WORKDIR`. It silently appends in whatever directory the shell is in. Prefix `$WORKDIR/`.
- **Push.** `git -C "$WORKDIR" push` is a bare push, which fails on the detached HEAD `dev:done`
  Step 2 leaves behind; `done/SKILL.md` separately claims this step uses `push_integration`, which it
  does not. The relocation fixes the command for free — at PR stage `$WORKDIR` is on the feature
  branch, where a bare push is correct. The stale `push_integration` claim must still be removed.

**4. `dev:pr` re-entry guard.** Closes `debt-autopilot-pr-re-entry-not-idempotent`.

Re-entering `dev:pr` on a cycle whose `artifacts.pr_url` is already set is undefined today. After
change 1 a re-run would additionally rewrite `docs/decisions/<file>.md` and append a second
`## Retrospective` to it. `dev:pr` must state one re-entry rule, guarded on `artifacts.pr_url`, that
`dev:autopilot` agrees with — and the branch push must be preserved on every path that reaches
`dev:done`.

**5. Stable cross-file citations.** Closes `debt-cross-file-line-citations-go-stale-silently`
(recurrence 2).

Renumbering `dev:done` and adding steps to `dev:pr` breaks three live `file:line` citations
(`reflect/SKILL.md:205`, `reflect/SKILL.md:212`, `done/SKILL.md:504`). Repairing only those three
leaves the class intact, so convert `file:line` cross-references to stable anchors (step number or
section heading) across the `dev` plugin.

**6. §P9 slug allowlist.** Closes `debt-p9-slug-regex-allows-leading-dash` (P2).

`^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$` places `-` inside the character class, so `-foo/bar` passes —
while both §P9 and `reflect/SKILL.md:205` claim the regex rejects a leading dash, calling it an
argument-injection vector into `gh --repo`. The stated security property is not the delivered one.
Adopt the anchored form already proven in `dev:fix`:

```
^[A-Za-z0-9._][A-Za-z0-9._-]*/[A-Za-z0-9._][A-Za-z0-9._-]*$
```

as canonical in §P9, correct `reflect/SKILL.md:205`'s claim, and have `dev:fix` drop its local
divergence note in favour of citing §P9 plainly.

## Out of Scope

- **`dev:done` Steps 3, 6a, 7 remain post-merge.** Each structurally requires the merge to have
  happened: Step 3 checks off a completed cycle, Step 6a's flush must not run before the work is
  merged, Step 7 tears down the worktree.
- **Three retro inputs are dropped, not deferred.** Once `dev:reflect` runs pre-merge they do not
  exist, and none is worth a second write to a merged file:
  1. *Merge outcome* — binary and almost always clean; `dev:done` Step 2 already STOPs loudly and
     visibly when it is not.
  2. *Step 3 plan check-off result* — mechanical, and the product plan file itself is the record.
  3. *Step 6a flush result* — `dev:reflect` Step 3's `**Deferred to tech debt:**` line already lists
     the slugs it recorded.
- **The remaining thirteen open store items** that share a file with this cycle but not its change
  surface.
- **`dev:fix`'s lane is not restructured.** It gains only the edits changes 5 and 6 require.

## Success Criteria

1. No `dev:*` stage commits `docs/decisions/`, `CLAUDE.md`, or `README.md` to the integration branch.
   Verifiable: no `push_integration` call in `dev:done` remains on a path that stages those files.
2. A completed cycle's PR diff contains its decision log with a populated `PR #N`, and a
   `## Retrospective` section appended to it.
3. Running `dev:pr` twice on the same cycle produces exactly one decision log with exactly one
   `## Retrospective`.
4. `dev:reflect` Step 6 offers three named choices; neither `backlog` nor `debt` edits a skill file
   or opens a PR.
5. `grep -rn 'SKILL\.md:[0-9]' plugins/dev/` returns nothing, or every remaining hit resolves to what
   it claims.
6. §P9's regex rejects `-foo/bar`, and no prose in `plugins/dev/` claims a validation property its
   regex does not deliver.
7. `dev:done` Step 6a still flushes `dev:reflect`'s buffered items — a cycle where reflect records an
   item ends with that item in `docs/backlog/`.

## Happy Path

1. Validate completes; `dev:pr` runs.
2. `dev:pr` checks `artifacts.pr_url` — unset, so this is a first entry.
3. `gh pr create` opens PR #N; `pr_created` is stamped.
4. Component Registry updated, docs prose reconciled.
5. Decision log written to `docs/decisions/YYYY-MM-DD-<feature>.md` with `PR #N`.
6. `dev:reflect` runs: user observation turn, retrospective appended to that log, three-way gate on
   each suggestion, buffer written.
7. One push — every step-4-through-6 commit lands in PR #N's diff.
8. Human reviews the PR, including the cycle's own reasoning.
9. `dev:done` merges, checks off the product plan, flushes the buffer, cleans up. It touches
   `docs/decisions/` at no point.

## Edge Cases

- **Architecture cycles.** Steps 4 and 4a are feature-only and stay so; the decision log and
  retrospective still run.
- **`dev:pr` re-entry.** Guarded by criterion 3 — the rule is change 4's deliverable.
- **Autopilot.** `dev:reflect` Step 4's user-observation pause on a handed-off cycle now occurs at PR
  stage rather than Done. Still a pause, not a stop; `dev:autopilot`'s stop list is unchanged.
- **`fix now` chosen mid-cycle.** The second PR branches from a `$PRIMARY` `main` lacking this
  cycle's unmerged edits. Accepted: the choice is now explicit and named, and the outcome is an
  ordinary stale-branch conflict a reviewer resolves.
- **Legacy in-place cycles** (`worktreePath` null). `$WORKDIR` is the primary tree; the `$WORKDIR`
  path prefix in change 3 is correct there too, and `dev:reflect`'s existing stop condition for
  `<source-repo-path> == $WORKDIR` still fires.
- **A cycle abandoned after `dev:pr` but before `dev:done`.** Its decision log and retrospective exist
  only on the unmerged branch and die with it — strictly better than today, where they could only be
  written after a merge that never happened.

## Dependencies

- Milestone 1's `validate-prose-resync` — merged; both edit `validate/SKILL.md`.
- Milestone 4 `project-scoped-worktree` is **downstream** of this cycle and must merge after it.

## Technical Constraints

- Prose-only repo; no build or test suite. Verification is grep-based and by reading.
- `dev:fix` mirrors `dev:done` Step 4a with three named divergences (D1/D2/D3) that cite it by
  section. Both ends must be updated together.
- `references/entry-adapters.md:10` and `validate/SKILL.md` (healthy-path shell exit-code rule) both
  cite `dev:done` Step 4a by name.
- Estimated surface: `pr`, `done`, `reflect`, `fix`, `autopilot`, `validate`, `dev`,
  `references/entry-adapters.md`, `references/tech-debt.md`, `CLAUDE.md`, `README.md` — 11 files.

## Audience

Solo maintainer of this plugin repo, dogfooding `/dev` on the repo that defines it.

## UI Needed

No.

---
*Auto-filled dimensions: none*
*Grounding inventory: `dev:pr` Step 5 commits + pushes after `gh pr create` (`pr/SKILL.md:201-210`) — verified, and it is what makes a post-create slot land inside the PR diff. Decision log created at `dev:done` Step 5, committed via `push_integration` to `$INTEGRATION` post-merge (`done/SKILL.md:300-336`) — verified. `dev:reflect` invoked at `dev:done` Step 6; its Step 5 appends `## Retrospective`, then bare `git push` (`reflect/SKILL.md:141-153`) — verified, and contradicts `done/SKILL.md:340`'s `push_integration` claim. `dev:done` Step 2 leaves `$WORKDIR` on a detached HEAD for worktree cycles (`done/SKILL.md` Step 2) — verified, which is what makes that bare push a live defect. `dev:done` Step 6a's position note ("load-bearing twice over… Do not move it") and its read-from-disk rule — verified (`done/SKILL.md:353-375`). `pr_created` stamped only at `dev:pr` Step 5 — verified, so it is unavailable at end of Validate but available to a post-create `dev:reflect`. Post-merge `push_integration` commit set enumerated from the file, not memory: Steps 3, 4, 4a, 5, 6(via reflect), 6a, 7 — six commit sites beyond cleanup, where the source item named two. Consumers of `dev:done` Step 4/4a enumerated by sweep, not recall: `fix/SKILL.md:518,561-597` (D1/D2/D3 mirror), `references/entry-adapters.md:10`, `validate/SKILL.md:256` — the source item's `files:` list named none of these. Live `file:line` citations that this cycle's renumbering breaks, found by grep: `reflect/SKILL.md:205` (cited by `debt-p9-slug-regex-allows-leading-dash`), `reflect/SKILL.md:212` (cited by `fix/SKILL.md:60`), `done/SKILL.md:504` (cited by `autopilot/SKILL.md:168`). §P9 allowlist read directly (`references/tech-debt.md:378`): `-` is inside the character class, so the documented leading-dash rejection does not hold. Open-debt intersection run against the P5 corpus: 16 items share a file, 3 intersect the change surface, 1 further folded in by the user.*
