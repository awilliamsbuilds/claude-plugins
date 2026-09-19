# Telemetry Schema — Decision Log
*2026-09-09 · Branch: feature/telemetry-schema · PR #96*
*Handed off to autopilot at Plan*

## What was built

A committed, append-only ledger at `docs/telemetry/runs.jsonl` that makes a finished run's
telemetry survive `dev:done` Step 7's `rm -rf`, plus the two stamp pairs (`pr`, `done`) the
workflow was missing.

## Key decisions

**One reference, two call sites — not two implementations.** The record format has two writers
(`dev:done`, `dev:fix`) and a future third reader (Milestone 3's viewer). `references/telemetry.md`
is canonical and both writers cite it; each names its own divergences (D1 root, D2 push helper,
D3 failure treatment) rather than restating the procedure. → The plan's "same procedure, two call
sites" failure mode is where two independently-written implementations drift while each reads
correct in isolation.

**`docs/telemetry/`, not `docs/dev/telemetry/`.** The latter is a sibling of `docs/dev/<feature>/`,
so a future cycle slugged `telemetry` would put Step 7's `rm -rf` directly on top of the ledger. →
The one artifact whose entire purpose is surviving that command must not live where it can be its
target.

**Named `runs`, not `cycles`.** The file holds both cycle and lane records. → Naming it after one
kind is the exact conflation the `kind` field exists to prevent.

**`done_start`/`done_end` bypass `state.json` entirely.** → `dev:done` writes no `metrics.*`, and
Step 7 deletes that file seconds later; a state round trip would add a writer to a file being torn
down, for no reader.

**The lane derivation is merge-commit-relative, never branch-relative.** → By the time a record can
be written the merge fence has deleted both branches and moved the checkout, so a branch name is
unusable. Corollary: the derivation must sit *inside* the fence, where `BRANCH` and `PR_NUMBER` are
still bound.

**Three lane branches, not two.** A merge commit `gh` reports but `git` cannot read is a *tooling
failure*, not a squash — `gh` speaks HTTPS with its own token while the remote may be SSH. →
Folding it into the squash arm would write `merge_sha: ""` and a `note` asserting a merge shape
nobody observed. Same class of misreading the `basis` field exists to prevent.

**Lane dedup keys on `pr_number`, cycle dedup on `id`.** → Branch names are reusable: the fence
deletes them, so the branch-collision check at creation time sees no trace of a prior run, and two
free-text `/dev:fix` runs kebabing to the same summary collide. Uniformity across kinds would have
traded a real silent under-count for a cosmetic gain.

**The architecture cycle collapsed into a feature cycle.** Milestone 2 originally scoped
`telemetry-schema` (architecture, ADRs) then `telemetry-instrumentation` (feature). → Grounding
showed most instrumentation already exists and the only blocking gap is persistence, so the contract
is one file format with two writers rather than a decision needing ADRs. The plan edit recording
this also corrected its false claim that only `spec` carries a `_start`.

## Validation notes

- 2 loops run (tier: standard, cap 3). Exited on the **same-region recurrence** rule, not clean and
  not on the loop limit.
- **P1 — mixed timestamp formats.** `git log --format=%cI` emits the committer's local offset and
  `TZ` does not change it, while every other writer used `date -u`. One file would have carried two
  formats and lexicographic compare would have been wrong. → Resolved: one format pinned in
  §T-envelope; git derivations use `TZ=UTC --date=format-local:`; a Python 3.9 reader note added
  (measured: `fromisoformat('…Z')` raises on the 3.9.6 floor).
- **P2 (security) — unvalidated branch name into a shell `-m`.** Refnames legally carry `$` and
  backticks, and the merge tail does not require the branch to have been created by the lane. →
  Resolved: re-validated against §A3's allowlist at the resolve step, enforced rather than inherited.
- **P2 — false hard-STOP on re-entry.** §T-append was self-contradictory about whether T4 runs on
  the already-recorded path. → Resolved: control flow stated; "already recorded" is a success.
- **P2 — lane dedup dropped genuine second runs.** → Resolved: keyed on `pr_number`.
- **P2 — `dev:pr` prose went stale.** Step 5e commits after `dev:reflect`'s push, so
  `Everything up-to-date` flipped from expected to a warning sign. → Resolved.
- **Two P2s survived the loop and were settled at the gate.** Both sat in §T-append T3: `churn`
  wrongly inside the empty-string→null mapping (an empty `--shortstat` legitimately means
  `{0,0,0}`), and the snippet resolving `LEDGER_PATH` against the process cwd. The same-region
  recurrence rule stopped the loop and routed the question underneath them — *how should nullable
  and non-scalar fields cross the argv boundary?* — to a human, which is exactly what that rule is
  for. → The user settled it and directed both be fixed before merge. **Resolved:** `churn` is now
  selected by the arm rather than by an emptiness test; the path argument is rooted at `$ROOT`; and
  the nullable list became three type-keyed forms covering every nullable across all three sections.
  Nothing ships open.
- **The loop was generating defects in that region at about the rate it removed them.** Both loop-2
  P2s were introduced by the loop-1 fix, and both loop-3 findings by the loop-2 fix. That is the
  signature the same-region rule detects, and it detected it correctly — a third iteration would
  have produced a fourth round of the same.
- P3/Nits accepted as-is: nullable-field list attribution, merge-fence fetch ordering documented
  rather than restructured, `check-ref-format` leading-dot omission, the branch allowlist's refusal
  of legal-but-unusual refnames (`+`, `@`, non-ASCII — a loud STOP matching §A3), ragged wrapping.

## Artifacts (archived)
Spec and plan committed at: efd2ef400604e342866a794f714a0df721bb0125 on branch feature/telemetry-schema

## Retrospective
*Reviewed by dev:reflect · 2026-09-09*

**Spec:** 4 challenger blockers / 5 concerns against `spec_revisions: 0` — the high-blockers,
low-revisions cell: the author's own grounding pass (Step 7) was weak, and the challenger caught it
before the gate. Working as designed. Confidence 90% held with no auto-fills and no backtracks, and
the grounding inventory did real work — it disproved the product plan's standing claim that only
`spec` carried a `_start`, which is what collapsed the cycle from two items to one.

**Shape:** skipped (no-ui).

**Plan:** 0 blockers but 2 challenger loops and 11 applied fixes, 8 of them concern-driven. The
plan challenger's value here was almost entirely non-fatal findings, and the ones that mattered came
from it opening the files the plan cited rather than reading the plan alone — the
rationale-asserting-another-skill's-behavior check earning its place.

**Validate:** 2 loops / 3, exited on same-region recurrence rather than clean. Every loop-1 finding
was real. **Both loop-2 P2s were introduced by the loop-1 fix, and both loop-3 findings by the
loop-2 fix** — in that one region the loop was producing defects at roughly the rate it removed
them. The same-region rule detected exactly that and routed the question to a human, which is the
outcome it was designed for and the single most useful process control in this cycle.

**Flow:** tier right. A 40-minute spec against a 3-minute build is the correct shape for a cycle
whose deliverable is a contract, not code.

**Token efficiency:** Validate (26 min) cost roughly 5× Build. Four cold dispatches at ~85k–155k
tokens each dominated the cycle — the cost is in the reviewing, not the writing, which is the
expected shape for docs-as-code and not an outlier to chase.

**Suggestions:** none actionable this cycle. The same-region recurrence rule and its
converging-cascade exemption were both exercised for real here — the exemption correctly declined to
fire (severity flat at P2, and the fenced block itself changed between rounds), and the rule
correctly stopped a loop that was not converging. Worth leaving alone.

**Deferred to tech debt:** none. The two P2s the loop could not settle were settled at the PR gate
and fixed before merge, so the buffered item was withdrawn rather than flushed.
