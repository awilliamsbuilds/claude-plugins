# init-rerun-hardening — Validation Report
*Branch: feature/init-rerun-hardening · 2026-07-23*

## Summary
Loops run: 1 / 5 (tier: deep)
Final status: clean — no open P1/P2/P3

Feature cycle. Code review and security review ran in parallel as fresh, context-free subagents
against the build diff (`fac9eed..HEAD`), the spec's Success Criteria, and the plan's task list.
Both independently confirmed all 8 plan tasks landed, the config contract closes both ways
(`component_policy`/`schema_version` written by init and read with documented defaults; dead
`worktree_root` write removed), and the two unreviewed-write-to-`main` vectors (init's commit,
spec's `origin/$INTEGRATION` product-plan push) are gone. Neither found a P1 or P2.

## Issues Resolved
### Loop 1
- P3 (code review): init migration step 3 carried a vestigial "unless init just asked the Setup
  Question" clause — unreachable on the migration path, which never re-runs Phase 2. → Removed the
  dead clause; `component_policy` now backfills to `can-propose` unconditionally.
- P3 (security review): init migration did not guard a malformed `config.json` or a non-integer
  `schema_version`; a hand-edited syntax error could fall back to the fresh template and clobber
  tuned values — the exact outcome migration exists to prevent. → Added an explicit malformed-config
  guard: if the file doesn't parse as JSON or `schema_version` isn't a non-negative integer, STOP
  and report for manual repair.
- P3 (code review): init migration backfilled `changelog: null` without noting that changelog
  detection is intentionally not re-run. → Added a one-line note that a repo with an existing
  changelog re-enables it via a fresh init or manual edit.
- Nit (code review): the Scenario D "keep" path exit line said the tech-debt file was "untracked —
  commit it when convenient," out of step with the cycle's standardized "review, commit, and push"
  phrasing. → Aligned the wording.
- Nit (security review): the spec deferred-write block substitutes `<product-name>` into a
  `git commit -m "…"` without a quoting caution. → Added a one-line "substitute as a plain literal;
  don't let quotes or `$(...)` break the `-m` quoting" note.

## Issues Remaining
### P1 Open
- None

### P2 Open
- None

### P3 Open
- None

### Nits Surfaced
- (code review) `dev:validate`'s config-contract review gate is worded "every skill that reads
  config.json," which is literally broader than the per-consumer convention the repo actually
  follows (only a reader of *that key* needs it in its read list). No diff change: editing the gate
  was out of scope, and the implementation correctly followed the per-consumer intent. Recorded to
  the tech-debt buffer (Step 5a) because the imprecision is systemic — every future config-touching
  cycle would rediscover the false positive.

## Notes
- `loops_max` in state.json was `3` at stage entry but the tier is `deep`; corrected to `5` per the
  tier table before reviewing.
- The one folded debt entry (*"dev:spec's product-plan procedure pushes straight to origin/main"*)
  is already staged for closure in this cycle's `debt-pending.md` `## To Close` — the restructure
  removed the exemption entirely.
- Verification for this prose/embedded-shell cycle is procedure-tracing plus confirming embedded
  shell exits 0 on the healthy path; there is no test harness (per spec Technical Constraints).
