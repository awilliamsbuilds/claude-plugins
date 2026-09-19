# Telemetry Schema — Validation Report
*Branch: feature/telemetry-schema · 2026-09-09*

## Summary
Loops run: 2 / 3
Final status: clean

The fix loop exited at 2/3 on the **same-region recurrence** rule with two P2s open, correctly
routing the unsettled question underneath them to a human rather than to a third iteration. **The
user settled it at the PR gate and directed that both be fixed before merge**, which is the outcome
that rule exists to produce. Both are now closed and verified; nothing ships open.

## Build
no build system detected (markdown + stdlib-Python repo). The one suite present passed on every
loop: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s plugins/dev/skills/debt -p 'test_*.py'`
→ `Ran 89 tests … OK (skipped=2)`.

## Issues Resolved

### Loop 1
- P1: ledger timestamps were mixed-format — `git log --format=%cI` emits the committer's local
  offset (`2026-09-09T00:10:07-05:00`, and `TZ` does not change it) while every other writer used
  `date -u` (`…Z`), so one file would have carried two formats and lexicographic compare across
  records would have been wrong → fixed: one format (`%Y-%m-%dT%H:%M:%SZ`) pinned in §T-envelope,
  git derivations switched to `TZ=UTC git log --date=format-local:… --format=%cd`, and a Python 3.9
  reader note added (measured: `fromisoformat('…Z')` raises on this repo's 3.9.6 floor).
- P2 (security): a git branch name reached a shell `-m` and a ledger field with no allowlist —
  refnames legally contain `$`, backticks, `;`, `&` → fixed: a re-validating `grep -Eq` against
  §A3's `^[A-Za-z0-9][A-Za-z0-9._/-]*$` in `### Resolve the branch and PR`, enforced rather than
  inherited, because the merge tail does not require the branch to have been created by the lane.
- P2: §T-append was self-contradictory about whether T4 runs on the already-recorded path, which
  would have made a re-entered `dev:done` hard-STOP on a cycle whose record was present and correct
  → fixed: control flow stated (T2 skips T3/T4, proceeds to T5's no-op guard), and "already
  recorded" declared a success at both the contract and `dev:done` Step 6b.
- P2: lane dedup keyed on the branch name, which is reusable across runs once the merge fence
  deletes both branches — two `/dev:fix` runs kebabing to the same summary would collide and the
  second would be silently dropped → fixed: keyed on `pr_number`, which is unique per run and known
  on all three arms.
- P2: `dev:pr`'s `### Push and display` prose became false once Step 5e commits after
  `dev:reflect`'s push — it told readers to expect `Everything up-to-date`, which is now the one
  symptom that matters → fixed, along with the four→five sub-step counts.
- P3 ×8: values passed to `python3` via `sys.argv` rather than inlined into program text;
  `MERGE_SHA` hex allowlist + `--end-of-options` on every new ref operand; three-dot range for
  churn; keep-both-lines conflict rule; `loops_max` on both challenge blocks; `dev:fix` Step 1
  Reads list; `dev:autopilot`'s `handoff_at` consumer enumeration; `dev:reflect`'s legacy-absence
  clause; mid-rebase reporting for the lane's new push.

### Loop 2
- P2: §T-lane's *field table* still carried the two-dot churn command that loop 1 had corrected in
  the derivation block eleven lines below — the file contradicted itself, and its own prose calls
  the table the parser's source → fixed.
- P2: §T-append T3's argv snippet could not express `null` — it wrote `""` where §T-envelope types
  fields nullable, and `int(pr)` raised on a null `pr_number` (measured:
  `ValueError: invalid literal for int() with base 10: 'null'`) → fixed: empty string stated as the
  wire form of `null`, `end` deliberately outside the mapping since it is typed non-null.
- P3: the `LEDGER_PATH` sentence claimed call sites cited it by name; none did → reworded to what
  is true.
- Nit ×2: dangling colon at T3; `check-ref-format` characterization corrected.

## Issues Remaining

### P1 Open
- none

### P2 Open
- none — both are closed below.

### P2 Closed at the gate (post-loop, by user direction)
- **`churn` was in the empty-string→null mapping, but `""` is a legitimate `churn` value.**
  `git diff --shortstat` prints an empty line for an empty diff, and §T-lane (eleven lines above the
  new rule) already says that means `{files: 0, insertions: 0, deletions: 0}`. Measured on a
  purpose-built add-then-revert branch: 2 commits in range, `--shortstat` output empty. So a
  *derived* lane run whose branch nets to no change would be written `churn: null` beside
  `basis: "first_commit"` — a combination §T-lane's table says occurs only on the two underivable
  arms. §T-path forbids rewriting a line, so such a record is permanent, and a reader filtering on
  `churn != null` silently drops a derived run. Secondary: `churn` is object-typed, so argv cannot
  carry it at all, and the snippet gave no form for it.
  → **Fixed.** `churn` left the mapping entirely and is now selected by the **arm**: zero-filled on
  derived, `null` only on squash/no-SHA. Verified by running the derived arm with an empty marker —
  it records `{"files": 0, "insertions": 0, "deletions": 0}`.
- **The `$LEDGER` → `$LEDGER_PATH` rename bound the snippet to a repo-relative path.** §T-path
  defines `LEDGER_PATH` as repo-relative, resolved against the writer's tree root, but the snippet's
  `open(path, "a")` resolves it against the **process cwd** — the only command in T1–T5 that is not
  explicitly rooted (`mkdir -p "$ROOT/…"`, `git -C "$ROOT" …`). It matters most in the lane, which
  never assumes cwd is the tree root. The failure is silent: the record lands in
  `<cwd>/docs/telemetry/runs.jsonl`, T4 re-reads that same wrong file and passes, T5 stages nothing
  so the commit is skipped, and the caller reports success with no record written.
  → **Fixed.** The snippet's path argument is now `"$ROOT/docs/telemetry/runs.jsonl"`, matching
  T1's and T5's rooting, and T2 and T4 name the rooted path too. §T-path's `LEDGER_PATH` paragraph
  no longer claims the snippet uses the bare name.

### P3 Open
- ~~§T-append's nullable-field list attribution~~ → **fixed alongside the P2s**: it is now three
  type-keyed forms covering every nullable across §T-envelope, §T-cycle and §T-lane, including the
  int-typed `challenge.blockers` / `challenge.concerns`. Verified: a cycle record keeps `blockers`
  `null` while `concerns` stays `0`.
- The `dev:fix` merge fence's fetch ordering was documented rather than restructured.

### Nits Surfaced
- `check-ref-format`'s list omits that a component may not begin with `.` (measured refused).
- The branch allowlist refuses legal-but-unusual refnames (`+`, `@`, non-ASCII) — a loud STOP, and
  it matches §A3 exactly, so it is a named cost rather than a defect.
- Two paragraphs left ragged by in-place edits (`telemetry.md:29` at 176 chars; `fix/SKILL.md`
  around the `check-ref-format` list).

## Notes

**Why the loop exited at 2 of 3 with P2s open — the same-region recurrence rule.** Step 4 step 8's
rule fired: this round's findings are in code loop 2 wrote, and the round before it also produced a
finding in the same region — `plugins/dev/references/telemetry.md` §T-append T3, the serialization
snippet. The converging-cascade exemption needs all three of its signals and two fail: severity is
**flat at P2** rather than strictly below the first round in that region, and loop 2 **changed the
fenced block itself** rather than only prose. So the shape is circling, not converging, and in
autopilot the rule is to attempt no further fixes in that region, buffer its remaining findings, and
continue.

**The region, and the unsettled question in one line:** §T-append T3 — *how should nullable and
non-scalar fields cross the argv boundary — a single emptiness test for every field, or a per-field
type-aware form — and should `LEDGER_PATH` name the repo-relative constant or the resolved absolute
path?* Each of the last two rounds answered half of that and broke the other half, which is what the
rule detects. Both open P2s follow from that one decision, and both have obvious mechanical fixes
once it is settled; what the loop could not do is settle it.

**This is a real firing, not a misfire.** The two candidate answers are genuinely different designs
with different consequences at both call sites, which is exactly the class of question the rule
routes to a human rather than to another loop iteration.

**Everything outside that region is clean.** The P1 and the four other P2s were fixed and
independently re-reviewed cold; the branch-name allowlist, the `MERGE_SHA` guards, the timestamp
format, the dedup key and the `dev:pr` prose all verified sound by the loop-2 re-reviewer, with the
measurements reproduced. An injection payload passed as a record value was measured landing inert as
escaped JSON data.
