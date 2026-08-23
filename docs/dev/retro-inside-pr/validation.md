# Retro Inside PR — Validation Report
*Branch: feature/retro-inside-pr · 2026-08-23*

## Summary
Loops run: 3 / 5
Final status: clean

Both Stage-5 reviewers ran cold and were issued together against base `e755ec4`:
`/dev:review diff` and `/dev:secure diff`, each with `$WORKDIR` and both artifact paths, so all six
code bullets ran — none reported `not run`. Neither returned a P1. Security returned no P2 either;
the two P2s came from the code review.

## Build
no build system detected (B5 — no `package.json`, `Makefile`, `Cargo.toml`, or `go.mod`). This is a
prose/skill-definition repo with no build and no test suite, exactly as the spec's Technical
Constraints record. Verification was grep-based and by reading, plus four measured shell fixtures
(see Notes).

## Issues Resolved

### Loop 1
- **P2** (code review): the re-entry empty-commit guard was applied to `dev:pr` Step 5's state commit
  only, leaving Steps 5a, 5c and `dev:reflect` Step 5 unguarded — on re-entry each can stage nothing
  and exit non-zero, contradicting the cycle's own *idempotent resume, never a stop* property and
  spec SC3 → added the pathspec-scoped `git diff --cached --quiet -- <path> || git commit … -- <path>`
  shape at all three.
- **P2** (code review): `dev:pr`'s `## Purpose` was never extended, though plan Task 2 step 12
  required it — `done`'s was rewritten and `pr`'s was missed → clause added naming all four sub-steps.
- **P3** (security): `dev:reflect` Step 5's replace-if-present branch anchored on the **first**
  `## Retrospective`, and a decision log's earlier sections are drafted from spec/plan/validation
  prose that in this repo quotes skill text verbatim — a meta-cycle's log can carry a literal
  `## Retrospective` above the real one, so deleting from the first match would discard committed
  sections → re-anchored on the **last** heading.
- **P3** (security): `dev:reflect` Step 5's commit was not pathspec-scoped, unlike every sibling write
  site in the PR flow → scoped.
- **P3** (security): the four sub-steps' commits are seen by no automated reviewer, since
  `dev:validate` has already run → named explicitly in `dev:pr`, with why the alternative placement
  is unavailable (no PR number for `PR #N`, no `pr_created`).
- **P3** (code review): `fix/SKILL.md`'s two `done/SKILL.md:56-133` citations and
  `migrate-tracker/SKILL.md`'s two `done/SKILL.md:255` citations, all staled by this cycle's line
  shifts → converted to anchors.
- **P3** (code review): the producing-stage rosters did not name `dev:pr`, which now writes the
  buffer → added at three sites.
- **P3** (code review): the buffer-survival argument named two file states and omitted the one that
  actually occurs → third state added with its justification.
- **P3** (code review): "One push carries every commit Steps 5–5d made" was inaccurate, since
  `dev:reflect` pushes first → reworded.
- **Nit**: `dev:done`'s double blank line; the stale claim in the backlog item this cycle fixes.

### Loop 2
- **P3**: `dev:pr`'s replacement push justification named an architecture cycle as a run where Step 5d
  does not push. Measured false — `dev:reflect` has no architecture carve-out and does run there,
  while Steps 5a/5b are the ones that skip → example replaced.
- **P3**: `dev:reflect` Step 5 claimed the detached-HEAD push failure "belonged to the post-merge home
  it no longer has", contradicting the Step 6 rewrite in the same commit, which names a still-live
  detached route during `dev:done` → the bare-push claim scoped to the Step 5d route, and the
  standalone route's trigger widened from "`WORKDIR` undefined" to "absent, **or not on this cycle's
  feature branch**", which subsumes it.
- **P3**: a fourth producing-stage roster in `dev:debt` was missed → added.
- **Nit**: roster ordering; the re-entry display conditional moved to its own line in the
  established `[If <condition>: …]` form.

### Loop 3
- **P2**: loop 2's roster-**ordering** edit duplicated `dev:validate` in the canonical Mode-symmetry
  roster → duplicate removed. This is a new P2 attributable to a cosmetic fix, which is Step 4's
  **circuit breaker** trigger; it fired, and no further P3/Nit fixes were attempted this cycle.

## Issues Remaining

### P1 Open
None.

### P2 Open
None.

### P3 Open
Four prose defects, all deferred by the circuit breaker and buffered as
`retro-inside-pr-deferred-prose-p3s` with their fixes pre-drafted. Each was verified non-load-bearing
— none changes what any step *does*:
- `dev:reflect` Step 5's "the standalone route **below**" now points the wrong way (loop 2 moved that
  paragraph above it). **Cost to the next cycle:** a reader following the pointer looks in the wrong
  direction for the rule that governs the push they are about to run.
- `dev:pr`'s second push-justification example ("a stage resumed after reflect already ran") does not
  hold — reflect's push sits outside the commit guard and runs unconditionally on re-entry.
  **Cost:** the same false-justification class this cycle already paid a loop to fix twice.
- `dev:reflect` Step 5 shape (b)'s reason is worktree-only; on a legacy in-place cycle the bare push
  would *succeed* and land on the integration branch. Routing is already correct. **Cost:** the
  understated reason invites a later editor to conclude the skip is unnecessary, which would
  reintroduce an unreviewed write to `main`.
- Malformed punctuation `skip.):` in `dev:pr`. **Cost:** trivial on its own; it is bundled because it
  sits in the same paragraph as the second item, so one pass fixes both.

### Nits Surfaced
- `../..` passes the §P9 slug allowlist, since `[A-Za-z0-9._]` admits `.`. **Not recorded**: harmless
  at the only consumer (`gh --repo` treats it as a name, not a path), pre-existing in the `.`
  allowance rather than introduced here, and it cannot state a cost the next cycle pays — so it fails
  the carrying-cost test's second half rather than being recorded with a vague one.
- Column-wrap overruns on several edited lines. **Not recorded** — pure polish, no stated cost, and
  the circuit breaker exists precisely because cosmetic passes over this prose have a measured defect
  rate.
- Out-of-surface citations staled by this cycle's line shifts (`migrate-tracker`'s `tech-debt.md:417`
  and `:256`'s `tech-debt.md:408-415`). **Not recorded separately** — these belong to the already-open
  `debt-cross-file-line-citations-go-stale-silently`, whose follow-on sweep runs after this merges and
  will see final line numbers. Recording them again would duplicate that item.

## Notes

**Two files were edited outside the spec's stated 12-file surface, both deliberately.** The spec's
Technical Constraints defer `review`, `secure` and `migrate-tracker` *citations* to the follow-on
sweep. `migrate-tracker/SKILL.md` was edited twice anyway: once for its verbatim §P9 regex
restatement, which SC6 forbids across all of `plugins/dev/` and which is a property claim rather than
a citation; and once for two `done/SKILL.md:255` citations that *this cycle's* deletion staled, which
falls under change 5's principle. `debt/SKILL.md` was edited for the fourth producing-stage roster,
for the same reason — `dev:pr` became a producing stage in this cycle, so the list is wrong because of
it. Flagged here so the whole-cycle reviewer sees the divergence stated rather than has to infer it.

**Step 8's same-region recurrence rule was checked and the converging-cascade exemption applied.**
Loops 1–3 all produced findings in `dev:reflect` Step 5 and `dev:pr`'s push-and-display region. All
three exemption signals held: severity in that region ran P2 → P3 → P3 (non-increasing and strictly
below the first round there); loop 2 changed **zero** command lines in `reflect` — prose only; and
every finding descended from the same Step 5 rewrite rather than answering a competing question. So
the loop continued fixing in-region rather than buffering out, which is the exemption's intended
behavior in autopilot.

**Step 3b measurement caught a portability defect the reviewers had passed.** The first version of
`dev:reflect` Step 5's replace branch used `head -n "$((LAST - 1))"`. Measured: BSD `head` rejects
`-n 0` (`head: illegal line count -- 0`, exit 1), so a decision log whose `## Retrospective` is line 1
would have broken the block. Replaced with a single `awk` pass and re-measured across four fixtures —
trailing-blank, heading-on-line-1, quoted-heading-above-real, and no-heading — plus two consecutive
re-entries to confirm exactly one `## Retrospective` and no blank-line accumulation. All exit 0.

**The circuit breaker's cost is recorded rather than hidden.** It cost this cycle four unfixed prose
defects; it prevented an unknown number of further regressions, one of which had already materialized.
The evidence for firing it is in Loop 3 above, not in a judgment call.
