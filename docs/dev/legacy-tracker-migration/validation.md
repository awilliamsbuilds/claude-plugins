# dev:migrate-tracker — Validation Report
*Branch: feature/legacy-tracker-migration · 2026-08-02*

## Summary

Loops run: 5 / 3 (tier: standard)
Final status: **clean** — no open P1 or P2

The tier budget was 3. At the Step 4a gate after loop 3, four P2s were still open and the user chose
**A — keep looping**. Loops 4 and 5 ran under that authorization; loop 5's cold re-review returned no
P1 and no P2.

Every loop's fix diff was reviewed by a fresh subagent that saw only that diff, `spec.md`'s Success
Criteria, and the checklist — no conversation history. Three of the five loops caught regressions
introduced by the loop before them, which is what those re-reviews are for.

Protected-files invariant (Success Criterion 11) verified after every loop: `references/tech-debt.md`,
`init/SKILL.md`, `debt/SKILL.md`, `done/SKILL.md` are byte-identical to `main`. The whole branch
touches only `migrate-tracker/SKILL.md`, `start/SKILL.md`, and cycle artifacts.

### Issue counts by loop

| Loop | Source | P1 | P2 | P3 | Nit |
|---|---|---|---|---|---|
| 1 | Step 2 parallel code + security reviews | 3 | 7 | 9 | 6 |
| 2 | loop 1 fix-diff re-review | 0 | 4 | 3 | 3 |
| 3 | loop 2 fix-diff re-review | 0 | 2 | 3 | 2 |
| 4 | loop 3 fix-diff re-review *(Step 4a gate here)* | 0 | 4 | 2 | 2 |
| 5 | loop 4 fix-diff re-review | 0 | 2 | 2 | 3 |
| — | loop 5 fix-diff re-review | 0 | **0** | 1 | 1 |

## Issues Resolved

### Loop 1 — from the two parallel cold reviews

- **P1:** Proposed slugs were checked only against disk, never against each other. Two editorialized
  ≤5-word slugs colliding meant the second write silently overwrote the first, *both* items still
  counted in bucket (a), the reconciliation passed, and the tracker — the only remaining copy — was
  deleted. → Rule C now dedupes at proposal time; Step 7 step 2 checks a third set (names already
  assigned in this run).
- **P1:** Nothing stated how an issue body reaches `gh`. The natural `--body "…"` form expands `$…`,
  `` `…` ``, and `$(…)`, and the reference fixture's own entries quote shell. → Step 8 now mandates
  `--body-file` or a single-quoted heredoc, citing the identical rule already in `reflect/SKILL.md:219`.
- **P1:** `ENTRY_COUNT` counted only `### ` headings under `## Open`/`## Closed`, so an entry under any
  other heading was excluded from both the numerator and the denominator — never migrated, never
  reported, reconciliation clean. → `FILE_HEADING_COUNT` cross-check; excess goes to `BUCKET_E`.
- **P2:** A `## Closed` entry could P6-merge into an active *open* item, producing no file in `closed/`
  and discarding `closed:`/`closed_by:` — a Success Criterion 2 violation. → Closed items never merge.
- **P2:** Step 8 built `SLUG_MAP` incrementally, which Step 7 explicitly forbids; pointer resolution
  became iteration-order dependent. → names first, pointers second, on both paths.
- **P2:** Rule C promised a slug per *entry* reviewed in the table; the table showed open items only,
  leaving 7 of the fixture's 11 permanent identifiers unseen. → closed rows now appear, slug-only.
- **P2:** `SLUG_MAP` was defined over "every local-write item's final slug from step 2", but step 2
  named only `BUCKET_A` items. → `BUCKET_B` items enter under the matched file's existing basename.
- **P2:** The `<first-cycle>` collision disambiguator was lifted from untrusted text and used as both a
  path component and a YAML value with no allowlist. → sanitized at Step 4 alongside the slug.
- **P2:** Bucket membership was self-reported; `rm "$TRACKER"` fired on arithmetic alone. → Step 9
  verifies each bucket against the filesystem first.
- **P2:** P9's issue body is a ```` ```markdown ```` fence, and **L5** documents that entry values
  contain code fences. → fence width now exceeds the body's longest backtick run.
- **P3/Nit (9 + 6):** `dev:init` guard paths that return before creating the store; `dev:init` writing
  before the Step 6 gate; unscoped `~/.claude/settings.json` read (a PAT lives there); a
  resolved-but-malformed target not degrading; `files:` path tests not rooted at `$PRIMARY`; undefined
  behavior on an empty table; duplicate cycle names on merge; an under-reporting closing report;
  `files: []` written without acknowledging P1 forbids it; missing-field dispositions; empty-slug
  fallback; unchecked `rev-parse` exit status; unvalidated dates; a wrong ADR path.

### Loop 2 — three of four were loop 1's own regressions

- **P2:** The new empty-table gate promised the tracker would survive in the empty-tracker case, which
  Step 9 deletes. → two sub-cases, two messages.
- **P2:** Step 9's `BUCKET_B` check tested for an *incremented* `recurrence`, which loop 1's cycle-dedup
  rule makes a correct no-op merge fail. → containment, not increment.
- **P2:** Step 8's degrade collision branch was left as a two-set mirror of a Step 7 procedure upgraded
  to three sets plus escalation. → mirror re-synced.
- **P2:** The rewritten no-match clause claimed `BUCKET_D` items have no local file. → Step 8 backfills.
- **P3:** `files[]` had neither sanitization nor a transport rule while Step 6 feeds it into a path
  test; cycle-name allowlisting stripped without lowercasing (`ENG-123-auth-bug` → `-123-auth-bug`);
  `dev:debt inbox` fence-width note.

### Loop 3

- **P2:** Loop 2's lowercase-then-strip rule guaranteed the very mismatch Step 7's dedup exists to
  prevent — store names come from `dev:done` branch names and may be mixed case. → case-insensitive.
- **P2:** Loop 2's `..` rejection on `files[]` discarded real paths to defend a threat this skill does
  not have (`files[]` composes no on-disk path here). → reverted to transport-only defense.
- **P3:** `FILE_HEADING_COUNT == 0` no longer asserts "empty" on its own; Step 8 split
  name-assignment from writing; corrected a false claim about the backfill being the only after-write edit.

### Loop 4

- **P2:** Step 9's `BUCKET_B` check was still comparing cycle names literally after Step 7 went
  case-insensitive. → propagated.
- **P2:** The `P9.degrade` paragraph still ordered a write at failure time, ahead of the decide-names
  split. → states disposition only.
- **P2:** The heading-drift guard fired only at `FILE_HEADING_COUNT == 0`, so a tracker mixing valid and
  drifted entries still reconciled clean and was deleted. → unconditional orphan sweep.
- **P2:** The `files[]` "never rewritten" wording read as exempting it from the newline rule, and **L5**
  makes a multi-line `**Files:**` value the common case. → explicit carve-out.
- **P3:** Backfill no longer overwrites an existing `possibly_related_to` (single scalar, not a list);
  drift gets its own `heading-drift` flag.

### Loop 5

- **P2:** The orphan sweep exempted the prose preamble wholesale, so drift hand-appended above
  `## Open` still reconciled clean and was deleted — the same failure, displaced. → preamble swept on
  the same marker test, which a real preamble passes on its own merits.
- **P2:** The `files[]` newline truncation discarded real paths with no flag. → `files-truncated`.
- **P3:** An out-of-section heading was recorded in `BUCKET_E` twice; a lone italic line no longer
  triggers the sweep (an ordinary `*Ordered by first recorded.*` note would otherwise make the tracker
  permanently unretirable, since `BUCKET_E` is what blocks retirement).

## Issues Remaining

### P1 Open
None.

### P2 Open
None.

### P3 Open
- The orphan sweep exempts a *span* the `FILE_HEADING_COUNT` cross-check recorded, but the cross-check
  records only *headings* and defines no extent — so a drifted entry under a hand-added section can be
  reported twice. Report accuracy only; no data loss, and the tracker correctly survives either way.

### Nits Surfaced
- "Every other lossy path in this skill carries a flag" (the `files-truncated` rationale) is a false
  universal — the any-lifted-scalar newline truncation and the empty-cycle-name substitution are both
  unflagged. Rationale prose, not an instruction.

Both were assessed against the carrying-cost test and **dropped**: each is a local one-clause fix in a
single file, fixed-once-and-forgotten, which is exactly what the test says not to put in the store.

## Notes

**On the loop count.** Five loops is well above this tier's budget, and the reason is worth recording
rather than smoothing over: three of them were spent on regressions the previous loop introduced. The
pattern was consistent — a rule fixed in one step and not propagated to the step that depends on it
(Step 7's cycle comparison vs. Step 9's verification of it; Step 7's collision procedure vs. Step 8's
mirror of it). The fix-diff cold re-review caught every one of these, and would not have if the review
had been run by whoever wrote the fix.

**One pre-existing store defect, out of scope and unfixed.**
`docs/backlog/closed/debt-gate-path-state-writes.md` carries `cycles: [state-write-mode-audit]` — one
name — against `recurrence: 2`, violating P1's `recurrence == len(cycles)` invariant. It is an artifact
of the earlier hand migration (`tech-debt-migration`, 2026-07-28), not of this cycle, and it is the
concrete evidence that Step 4's rule A padding is load-bearing rather than defensive. Flagged here so
it reaches the decision log; fixing it is a one-line edit somebody should make deliberately.

**Two items buffered to `debt-pending.md`** — both systemic and both blocked by Success Criterion 11,
which forbids this cycle from touching `references/tech-debt.md` or `dev:debt`. See that file.

**Verified empirically during the loops**, not just read: `git rev-parse --git-common-dir` returns
`.git` at a primary checkout's root, `../../../.git` deeper, and an absolute path from a linked
worktree — so the `cd … && pwd` form is required and the skill's rationale for it is now accurate.
