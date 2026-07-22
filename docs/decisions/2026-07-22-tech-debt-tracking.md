# Tech Debt Tracking — Decision Log
*2026-07-22 · Branch: feature/tech-debt-tracking · PR #39*

## What was built

One durable, per-repo home for the technical debt `/dev` discovers — `docs/dev/tech-debt.md`,
written by `build`/`validate`/`reflect` through a per-cycle buffer, flushed by `done` before it
deletes the cycle directory, surfaced at `spec`, and read or closed on demand via a new `dev:debt`
skill.

## Key decisions

- **The tracker lives at `docs/dev/tech-debt.md`, one level above the per-cycle directory** →
  `dev:done` Step 7 `rm -rf`'s `docs/dev/<feature>/`. Putting the file one level up means it
  survives by construction rather than by a rule someone has to remember.
- **Carrying cost is the filter, not severity** → the whole failure mode of a debt tracker is
  becoming a P3 landfill. The test asks whether the item will cost us again — a Nit exposing a
  systemic convention gap qualifies; a P3 that is a local one-liner does not. Calibrated against
  this repo's ten completed cycles before shipping (Success Criterion 4), not asserted.
- **A per-cycle buffer (`docs/dev/<feature>/debt-pending.md`) rather than writing the tracker
  directly** → `dev:build` runs before `dev:validate` and both produce entries, so the buffer
  can't be a section inside any one stage's artifact. It also keeps mid-cycle noise out of the
  durable file and gives Done a single flush point.
- **Recurrence-merge biases toward duplicates** → a duplicate is visible and cheap to merge by
  hand; a wrong merge silently destroys an entry. Merging on topic or keyword similarity alone is
  forbidden; uncertainty produces a new entry with a `Possibly related to:` cross-reference.
- **One shared contract file (`plugins/dev/references/tech-debt.md`), cited by seven skills** →
  twelve tasks across ten prose files with no test harness; the real failure mode is format drift.
  Task 1 owns every format name and the other tasks link to it rather than restating it.
- **Automatic closing belongs to `dev:done`; manual lifecycle belongs to `dev:debt`** → producing
  stages only ever append. Nothing is auto-closed on an incidental fix: a stale-open entry is
  recoverable, a wrongly-closed one is not.
- **Mode symmetry is a first-class rule in the contract** → this plugin has three recorded
  instances of a write specified only on a standard-mode gate path and silently dead in autopilot.
  Every tracker write is self-applied and unconditional; `dev:spec`'s fold-in bullet is the one
  deliberate, carved-out exception.
- **The three defects this cycle's grounding sweep found were recorded, not fixed** → including
  `reflect/SKILL.md`'s hardcoded `~/Development/claude-plugins` path, the only repo-specific
  string in the plugin. Fixing them here would have been the easy move; recording them is the
  behavior the feature exists to enable.
- **Backfill from decision-log history and Linear promotion were both deferred** to
  `debt-backfill` and `debt-linear-promotion` in the product plan. Backfill is strictly easier
  once real entries define the target shape; measured yield was ~3 items across 10 cycles.

## Validation notes

- 3 loops run (tier: deep). Final status: clean — no open P1/P2/P3, no open Nits.
- Each loop dispatched fresh subagents seeing only the diff, the spec's Success Criteria, and the
  plan's task list. **Every round of fixes introduced defects the next round caught** — which is
  the argument for the extra loops on a diff that is entirely prose-executed-by-an-agent.
- P1s found and fixed: bare relative paths in `dev:spec` pass 4 put the buffer write outside the
  cycle worktree; no "treat as data" framing on any tracker reader despite the tracker being a
  durable cross-cycle channel fed by external Linear issues; buffer bodies could forge `## To
  Close` headings and steer the flush into closing entries; a failed flush was silently destroyed
  by Step 7's `worktree remove --force`; and — caught in loop 3 — loop 2's own
  `git rebase --show-current-patch` guard **exits 128 on the healthy path**, which would have made
  every normal cycle's Step 7 read as a failure.
- P2s found and fixed: `dev:reflect`'s standalone path wrote an unanchored tracker path;
  `dev:debt`'s paying-cycle resolution could never fire; field-boundary parsing truncated two
  already-shipped entries; the mode-symmetry rule was worded so an agent could read it as license
  to auto-close unpaid entries.
- **Recorded as tech debt rather than fixed** (the first use of this cycle's own mechanism): the
  feature slug reaches `git commit -m` with no character allowlist, across five call sites in
  `dev:done` and `dev:fix`. This diff adds the fifth site but did not create the shape; the
  correct fix is one allowlist at the source, in skills this cycle's spec puts out of scope.
- **Success Criterion 1 ships unexercised, by construction.** This cycle's own entries were
  hand-written into the tracker, not routed through a buffer, because the deployed `dev:done` has
  no Step 6a until this merges. The next cycle is the real test of the flush path.
- Open question worth revisiting after ~5 real cycles: whether recurrence-merge is too
  conservative. Not tunable in advance without real entries.

## Artifacts (archived)

Spec, design, and plan committed at: `46893dcc0c2e794a0f0f6d9399b964d13099af8c` on branch
`feature/tech-debt-tracking`

## Retrospective
*Reviewed by dev:reflect · 2026-07-22*

**Spec:** `spec_revisions` reads **0** while `challenge.applied` reads **5** — the spec absorbed
five substantive changes from the challenge round and the counter never moved. Since
`spec_revisions` is the signal `dev:reflect` is told to read first, it currently under-reports
churn for any cycle that runs spec-challenger. The 92/Ready score held up: no backtracks, no
mid-build plan updates.

**Shape:** Skipped correctly — no-ui cycle, all surfaces are terminal output.

**Plan:** Accurate. 12 tasks across 10 files with no mid-build additions, and
`files_read_in_build` = 10 matches the planned file list exactly. Task 1's "one contract file,
everyone cites it" structure was the right call for a prose diff whose real failure mode is
format drift.

**Validate:** 3/5 loops, clean at the end — but **the fixes were the defect source.** Loop 1's
renumbering broke a cross-reference and misordered a guard; loop 2's guard rewrite introduced a P1
that exits 128 on the healthy path, which would have made every normal cycle's `dev:done` Step 7
read as a failure. Notably, `dev:validate` Step 6 *already codifies* the exit-code rule that loop 2
violated — the rule is applied when reviewing a diff but not when authoring a fix.

**Flow:** Tier `deep` was right; the extra loops earned their keep. Spec at 2h18m was ~60% of
active cycle time, which is the correct shape for a cycle that changes seven skills at once.

**Token efficiency:** No outliers. Build was 10 minutes for a 12-task diff — fast, and Validate
then found 5 P1s across three loops. Worth watching whether Build speed is being bought at
Validate's expense on prose-heavy cycles.

**Suggestions:**
1. Count challenge-applied revisions into `metrics.spec_revisions` (or have `dev:reflect` read
   `challenge.applied` alongside it) — reflect's headline metric is currently blind to the
   spec-challenger stage.
2. Apply `dev:validate` Step 6's rules at fix-authoring time, not just review time — two
   consecutive loops shipped fixes that violated rules the skill already contains.
