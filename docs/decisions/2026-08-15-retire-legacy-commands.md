# Retire Legacy Commands — Decision Log
*2026-08-15 · Branch: feature/retire-legacy-commands · PR #82*
*Handed off to autopilot at Spec*

## What was built

A new report-only `dev:secure` skill with whole-project and `diff` verbs, plus a security review and
a build check on every route to a PR — closing the capability gaps that made four legacy
`~/.claude/commands/` files worth keeping, and then documenting their retirement.

## Key decisions

- **Close the capability gap before retiring anything** → grounding found `/dev:fix` opened PRs
  unattended with *zero* security review (`grep -i security fix/SKILL.md` → no hits), while the
  seven-stage pipeline was covered. Retiring `security-review-diff.md` against that gap would have
  been a loss, not a consolidation. So §1–§3 ship the capability and §4 documents the retirement.
- **Name it `secure`, and make the skill correct its own implication** → the spec author twice argued
  that `secure` names an outcome the skill does not deliver and proposed `risk` or `audit`. The user
  chose `secure` on the grounds that the namespace's convention is single-word and verb-shaped
  (`fix`, `validate`, `build`, `plan`, `shape`, `reflect`). The cost is carried by a hard requirement:
  the frontmatter description **and** the skill's opening line must both state that it reports and
  modifies nothing. The name may not be the only thing telling the user what happens.
- **Report only; write nothing** → chosen over offer-to-capture and auto-capture. Keeps the new
  skill's blast radius at zero and makes the retirement an exact trade. The boundary is explicit: the
  skill writing nothing is a property of *the skill*, not a licence for its **caller** to drop
  findings — the lane still captures declined P3/Nits under its rigor floor.
- **The lane calls the skill rather than growing its own checklist** → one canonical implementation,
  no mirror to drift. Checkable: the security checklist's vocabulary appears zero times inside
  `dev:fix`'s new section.
- **Bounded inline fixing over stop-on-any-finding** → the spec author recommended stopping before
  the PR on any finding, matching what `pr.md` did. The user chose one round with a cold re-review,
  on the grounds that it keeps the fast path fast without letting an unreviewed fix through. The
  bound is what carries that argument: without the one-round cap and the re-review, this would be an
  unattended lane making security decisions unchecked.
- **One rule for a failing build and a failing suite** → the lane previously ran the suite and said
  only "record each result verbatim," never stating what a failure meant. Adding a blocking build
  check beside a merely-reported suite would have read as an oversight, so one rule covers both.
  This deliberately changes existing suite behavior.
- **The suite half is `dev:fix`-only, and the asymmetry is stated** → verified that `dev:validate`
  runs no suite at all (Steps 1–6 contain no invocation; `dev:build` runs tests during TDD). Saying
  so beats implying a symmetry that does not exist.
- **Architecture cycles keep their security carve-out** → the user was shown that those cycles still
  reach `dev:pr` and open unreviewed PRs, and chose to keep it. This cycle records the reasoning in
  `dev:validate` so it reads as a decision rather than an oversight, and the spec says plainly that
  "every route to a PR" therefore carries one named exception.

## Design choices

*Shape was skipped — no UI. Terminal output only.*

## Validation notes

- **3 loops run** (tier: deep), stopped by the **same-region recurrence** rule rather than by
  exhaustion — 3 of 5 loops used.
- **P2 — stale line citations.** Three cross-file citations the diff *added* were already wrong,
  shifted by the same diff's own earlier insertions; one pointed at the *architecture* severity
  table, the very scheme the sentence said the skill does not use. → replaced with section names.
- **P2 — wrong audit base.** The review diffed against the *local* default branch while the lane
  cuts its branch from `origin/` and the PR's base is the remote. A stale local ref is still an
  ancestor of HEAD, so the diff succeeds against a stale merge base and the audit covers unrelated
  commits. → origin-qualified `AUDIT_BASE` with a fallback.
- **P2 — argument injection.** The explicit `<base>` token reached `git diff` unvalidated. Measured:
  `git diff --output=FILE` **creates the file** and returns an empty diff, so the skill would report
  examining nothing while writing outside the repo — breaking its own zero-write invariant. →
  anchored ref allowlist plus `--end-of-options`.
- **P1 — introduced by loop 1's own fix**, caught by loop 2's cold re-review: `--end-of-options`
  placed *before* `--name-only` fatals with exit 128, which would have broken the diff verb on every
  run. Every other option must precede it.
- **P2 — found by executing the procedure rather than reading it.** Run from a worktree, the diff
  verb audits `$PRIMARY` and returns **0 changed files where the worktree has 13** — coming back
  *empty* rather than erroring, so a security gate would have reported "nothing to examine." Three
  prior reviews missed it. → `$PRIMARY` stays the audited tree (correct for `dev:fix`), but the verb
  now discloses: a notice naming both trees, the audited branch in the report header, and an
  empty-diff message naming branch and base.
- **Accepted as-is:** 3 P3 + 1 Nit, all inside the circling region, buffered to `docs/backlog/` as
  `debt-secure-tree-scoping-unsettled` and `debt-secure-report-fields-not-grounded-in-output`.

**The unsettled question, recorded rather than guessed:** which tree should `/dev:secure` audit when
invoked from inside a worktree? `dev:fix` needs `$PRIMARY`; a human standing in a worktree means the
tree they are looking at. That is a design call, not a fix-loop call.

**Two spec backtracks during Plan**, both committed with their reasoning inline:
- **SC11** declared `dev:autopilot` byte-identical while Scope §3 created a Validate stop that
  autopilot must document. Behavior recorded in one place only is a gap even when that place is
  correct. SC13 was added alongside for the two skill-enumerating surfaces (`dev:start`, README's
  Plugins table) that `dev:done` reaches in *neither* mode on an autopilot cycle.
- **SC3** asserted a whole-file grep of zero that measures **1** today — `fix/SKILL.md:76`, the
  `owner/name` allowlist's "argument-injection vector" prose. Read literally it would have forced
  Build to delete a load-bearing sentence. Re-scoped to the new section.

## Artifacts (archived)
Spec, plan, and validation committed at: 0f11bb8 on branch feature/retire-legacy-commands
