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

**1. Relocate four `dev:done` steps into `dev:pr` Step 5.**

| Moves from | To | Gains |
|---|---|---|
| `dev:done` Step 4 — Component Registry | `dev:pr` Step 5 | reviewed |
| `dev:done` Step 4a — Reconcile Docs Prose | `dev:pr` Step 5 | reviewed |
| `dev:done` Step 5 — Generate Decision Log | `dev:pr` Step 5 | reviewed; `PR #N` available |
| `dev:done` Step 6 — Run `dev:reflect` | `dev:pr` Step 5 | reviewed; `pr_created` readable |

Constraints on the relocation:

- **The relocated block sits inside `dev:pr` Step 5, between its state write and its push.** Step 5
  splits: immediately after `gh pr create`, update `state.json` (`pr_url`, `pr_number`,
  `completed[] += "pr"`, `stage = "done"`, `stage_timestamps.pr_created`) and commit it; then run the
  four relocated steps, each committing only; then Step 5's single
  `git -C "$WORKDIR" push` carries every one of those commits into PR #N. That ordering is what makes
  `pr_created` readable by `dev:reflect` Step 1 while still landing the whole block inside the
  reviewed diff. Placing the block before the state write would hide `pr_created` from the
  retrospective; placing it after the push would leave it out of the diff.
- **Each relocated step's post-merge premises are rewritten, not carried.** Step 4a's target rule
  drops "(present at the detached `$INTEGRATION` tip Step 2 left you on)" and reads `$WORKDIR`, on
  the feature branch; its detection input becomes *this cycle's diff against the PR base* rather than
  *this cycle's merged diff*; its reporting moves from `dev:done` Step 8's summary block to `dev:pr`
  Step 5's display, and `dev:done` Step 8's **Docs-prose reconciliation line** paragraph is deleted
  with it. Steps 4, 4a and 5 drop their `push_integration` calls and commit only — `push_integration`
  stays defined in, and used only by, `dev:done`.
- **Relative order 4 → 4a is preserved.** `dev:fix`'s D3 divergence rests on "`dev:done` Step 4a must
  never touch the table because Step 4 owns it two steps earlier." The reasoning survives only if the
  ordering does.
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
- `debt` → buffer entry with `type: debt`
- `fix now` → today's "yes" path verbatim, including both confirmations and every stop condition

The prompt must state that the first two act on nothing at the time.

The carrying-cost test gates **both** recording choices, per the contract's "It applies at **every**
capture site" — not `debt` alone. A `backlog` entry uses the contract's `**Why:**` body field in
place of `**Why deferred:**`; `dev:reflect` Step 6 currently hardcodes the debt body shape
(`**What's wrong:** / **Why deferred:** / **Done looks like:**`) and must branch on the chosen type.
The gate stays standard-mode-only: on any cycle that does not reach it, Step 6's unconditional
carrying-cost write records `type: debt`, exactly as today.

The existing rule that `$WORKDIR` is refused as `<source-repo-path>` stays, but its stated *reason*
changes: at PR stage `$WORKDIR` pushes to the feature branch, not `$INTEGRATION`, so the current
justification ("a skill edit committed there would land on `$INTEGRATION`") no longer describes the
hazard and must be rewritten to the one that now applies — the edit would land in this cycle's own
PR.

**3. Two pre-existing `dev:reflect` Step 5 defects.**

- **Path.** `cat >> docs/decisions/<file>.md` is cwd-relative while every sibling command in the file
  uses `$WORKDIR`. It silently appends in whatever directory the shell is in. Prefix `$WORKDIR/`.
- **Push.** `git -C "$WORKDIR" push` is a bare push, which fails on the detached HEAD `dev:done`
  Step 2 leaves behind; `dev:done` Step 6 separately claims this step uses `push_integration`, which
  it does not. The relocation fixes the command for free — at PR stage `$WORKDIR` is on the feature
  branch, where a bare push is correct. The stale `push_integration` claim must still be removed.

**4. `dev:pr` re-entry guard.** Closes `debt-autopilot-pr-re-entry-not-idempotent`.

The rule is **idempotent resume, never a stop**: on re-entry with `artifacts.pr_url` already set,
skip `gh pr create`, reuse the stored PR number, overwrite (not append to)
`docs/decisions/<file>.md`, and re-run `dev:reflect` such that its Step 5 replaces the existing
`## Retrospective` rather than adding a second. The branch push still runs, so every path reaching
`dev:done` has a pushed branch. `dev:autopilot`'s stop list is unchanged because this path never
stops — which is what keeps it consistent with autopilot's standing rule that from the resolved entry
point onward no stage is exempted, PR included.

**5. Repair the three citations this cycle breaks.**

Renumbering `dev:done` and adding steps to `dev:pr` invalidates the `file:line` citations at
`fix/SKILL.md:60`, `autopilot/SKILL.md:168`, and in
`docs/backlog/debt-p9-slug-regex-allows-leading-dash.md`. Convert **those three** to stable anchors
(step number or section heading).

`debt-cross-file-line-citations-go-stale-silently` stays **open**: the plugin-wide conversion is 35
citation-bearing lines across `fix` (11), `migrate-tracker` (7), `review` (6), `autopilot` (5),
`secure` (4) and `validate` (2), several carrying multiple citations and several pointing at line
*ranges* inside historical narrative that need per-site judgment. That is a cycle of its own, and it
must run **after** this one merges so the sweep sees final line numbers rather than being invalidated
by this cycle's renumbering.

**6. §P9 slug allowlist.** Closes `debt-p9-slug-regex-allows-leading-dash` (P2).

`^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$` places `-` inside the character class, so `-foo/bar` passes —
while both §P9 and `dev:reflect` Step 6's stop conditions claim the regex rejects a leading dash,
calling it an argument-injection vector into `gh --repo`. The stated security property is not the
delivered one. Adopt the anchored form already proven in `dev:fix`:

```
^[A-Za-z0-9._][A-Za-z0-9._-]*/[A-Za-z0-9._][A-Za-z0-9._-]*$
```

as canonical in §P9, correct the matching claim in `dev:reflect` Step 6's stop conditions, and have
`dev:fix` drop its local divergence note in favour of citing §P9 plainly.

## Out of Scope

- **`dev:done` Steps 3, 6a, 7 remain post-merge.** Each structurally requires the merge to have
  happened: Step 3 checks off a completed cycle, Step 6a's flush must not run before the work is
  merged, Step 7 tears down the worktree.
- **The plugin-wide `file:line` → anchor conversion**, per change 5. A follow-on cycle.
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
   `## Retrospective`, and leaves the branch pushed.
4. `dev:reflect` Step 6 offers three named choices; neither `backlog` nor `debt` edits a skill file
   or opens a PR, and a `backlog` entry carries `**Why:**` rather than `**Why deferred:**`.
5. No `file:line` citation remains in `fix/SKILL.md:60`, `autopilot/SKILL.md:168`, or
   `docs/backlog/debt-p9-slug-regex-allows-leading-dash.md`; each names a step number or heading
   instead.
6. §P9's regex rejects `-foo/bar`, and no prose in `plugins/dev/` claims a validation property its
   regex does not deliver.
7. `dev:done` Step 6a still flushes `dev:reflect`'s buffered items — a cycle where reflect records an
   item ends with that item in `docs/backlog/`.

## Happy Path

1. Validate completes; `dev:pr` runs.
2. `dev:pr` checks `artifacts.pr_url` — unset, so this is a first entry.
3. `gh pr create` opens PR #N.
4. Step 5 writes and commits `state.json`, stamping `pr_created`.
5. Component Registry updated, docs prose reconciled — commits only.
6. Decision log written to `docs/decisions/YYYY-MM-DD-<feature>.md` with `PR #N` — commit only.
7. `dev:reflect` runs: user observation turn, retrospective appended to that log, three-way gate on
   each suggestion, buffer written. Its Step 5 commits and pushes its own commit.
8. Step 5's final push carries the remaining commits — every step-4-through-7 commit is now in
   PR #N's diff.
9. Human reviews the PR, including the cycle's own reasoning.
10. `dev:done` merges, checks off the product plan, flushes the buffer, cleans up. It touches
    `docs/decisions/` at no point.

## Edge Cases

- **Architecture cycles.** Steps 4 and 4a are feature-only and stay so; the decision log and
  retrospective still run.
- **`dev:pr` re-entry.** Idempotent resume, per change 4. No new stop condition.
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
- The follow-on `file:line` → anchor sweep (change 5) is downstream of this cycle.

## Technical Constraints

- Prose-only repo; no build or test suite. Verification is grep-based and by reading.
- `dev:fix` mirrors `dev:done` Step 4a with three named divergences (D1/D2/D3) that cite it by
  section. Both ends must be updated together.
- `references/entry-adapters.md` and `validate/SKILL.md` (healthy-path shell exit-code rule) both
  cite `dev:done` Step 4a by name.
- Estimated surface, matching the scope above: `pr`, `done`, `reflect`, `fix`, `autopilot`,
  `validate`, `dev`, `references/entry-adapters.md`, `references/tech-debt.md`,
  `docs/backlog/debt-p9-slug-regex-allows-leading-dash.md`, `CLAUDE.md`, `README.md` — 12 files.
  `review`, `secure` and `migrate-tracker` are **not** in scope; their citations belong to the
  follow-on sweep.

## Audience

Solo maintainer of this plugin repo, dogfooding `/dev` on the repo that defines it.

## UI Needed

No.

---
*Auto-filled dimensions: none*
*Grounding inventory: `dev:pr` Step 5 commits + pushes after `gh pr create` (`pr/SKILL.md:201-214`) — verified, and it is what makes a post-create slot land inside the PR diff; `pr_created` is stamped only inside that step (`pr/SKILL.md:208`), which is what pins the relocated block between Step 5's state write and its push. Step 4's `push -u origin <branch-name>` (`pr/SKILL.md:142`) — verified, so the cycle pushes more than once. Decision log created at `dev:done` Step 5, committed via `push_integration` to `$INTEGRATION` post-merge (`done/SKILL.md:300-336`) — verified. `dev:reflect` invoked at `dev:done` Step 6; its Step 5 appends `## Retrospective`, then a **bare `git push`** (`reflect/SKILL.md:141-153`) — verified; `done/SKILL.md:340` claims `push_integration` for it, which is false, so the post-merge `push_integration` set is Steps 3, 4, 4a, 5, 6a and 7 — reflect is not in it. `dev:done` Step 2 leaves `$WORKDIR` on a detached HEAD for worktree cycles — verified, which is what makes that bare push a live defect. Step 4a's three post-merge premises read directly and confirmed false at PR stage: detached-`$INTEGRATION`-tip target (`done/SKILL.md:239`), "merged diff" detection input (`:241`), Step 8 summary-block reporting (`:289`, rendered by `done/SKILL.md:625-634`). `dev:done` Step 6a's position note and its read-from-disk rule — verified (`done/SKILL.md:353-375`). Post-merge commit set enumerated from the file, not memory: Steps 3, 4, 4a, 5, 6(reflect), 6a, 7 — six commit sites beyond cleanup, where the source item named two. Consumers of `dev:done` Step 4/4a enumerated by sweep: `fix/SKILL.md:518,561-597` (D1/D2/D3 mirror), `references/entry-adapters.md:9-10`, `validate/SKILL.md:256` — the source item's `files:` list named none of these. Citations this cycle's renumbering breaks, found by grep and each resolved before citing: `fix/SKILL.md:60` → `reflect/SKILL.md:213`, `autopilot/SKILL.md:168` → `done/SKILL.md:504`, and `debt-p9-slug-regex-allows-leading-dash.md` → `reflect/SKILL.md:208`. The latter two of those three targets are cited in the store as `:212` and `:205`, both **already stale today** (those lines are blank) — direct evidence for `debt-cross-file-line-citations-go-stale-silently`, which this cycle leaves open. Full plugin-wide citation count measured, not estimated: 35 citation-bearing lines across `fix` 11, `migrate-tracker` 7, `review` 6, `autopilot` 5, `secure` 4, `validate` 2. §P9 allowlist read directly (`references/tech-debt.md:378`): `-` is inside the character class, so the documented leading-dash rejection does not hold. Carrying-cost binding read directly (`references/tech-debt.md:59-62`): applies at every capture site, and the body field is `**Why deferred:**` for debt, `**Why:**` for backlog; `reflect/SKILL.md:170` hardcodes the debt shape. Open-debt intersection run against the P5 corpus: 16 items share a file, 3 intersect the change surface, 1 further folded in by the user.*
