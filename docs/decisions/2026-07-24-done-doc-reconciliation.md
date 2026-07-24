# Doc Reconciliation in dev:done — Decision Log
*2026-07-24 · Branch: feature/done-doc-reconciliation · PR #46*

## What was built
A new `dev:done` Step 4a that checks whether a merged feature cycle left `README.md` or the prose of `CLAUDE.md` (everything outside the Component Registry table) factually stale, and applies targeted edits (standard mode) or records them to the tech-debt tracker (autopilot/dismissed).

## Key decisions
- **Mirror the tech-debt mode split rather than invent a new convention** → the standard/autopilot behavior (apply-with-approval vs. record-durably, never auto-apply prose) is already understood for tech debt; reusing it means both are governed by one convention and change together.
- **Detection is agent judgment over the merged diff, not a mechanical differ** → the spec fixes *what* counts as a mismatch (new/renamed/removed skill, plugin, command, flag, config key; a documented workflow step whose description no longer matches), not a parsing algorithm. Style/tone/voice rewrites are excluded.
- **Silent no-op is the dominant, first-class path** → most cycles change no docs; the step must manufacture no empty prompt, commit, debt entry, or report line when there's no mismatch.
- **Durable record reuses the existing `debt-pending.md` → Step 6a flush mechanism** → a dismissed (standard) or any autopilot detection becomes a `## To Record` buffer entry, so it lands in `docs/dev/tech-debt.md` and `/dev:debt` with no new machinery.
- **Slot after Step 4, before Step 6a** → the Component Registry is already current (Step 4) and any `## To Record` write is flushed by Step 6a's existing flush.
- **Never create a missing target, never touch the Component Registry table** → absent `README.md`/`CLAUDE.md` is skipped with a one-line note, never created; Step 4 remains the table's sole writer.
- **Close tech-debt #1 at the source rather than guard a sixth commit site** → instead of adding another unguarded `git commit -m "… <feature>"` interpolation, `<feature>` is allowlisted to `^[a-z0-9][a-z0-9-]*$` by construction at its two derivation points (`dev:spec` Step 6, `dev:fix` Step 3), making every downstream commit interpolation injection-safe. `dev:fix` tolerates uppercase only to preserve the Linear ID prefix; the pre-existing lowercase-only bare-slug arg matchers in `done`/`plan` were deliberately left unchanged.

## Validation notes
- 1 loop run (tier: standard). Two fresh cold subagents (code review + security review) ran in parallel on the Build-since diff, each given only the diff, spec success criteria, plan tasks, and its checklist.
- **P2 (both reviewers)** — `dev:spec` Step 6 normalization sat *after* the worktree-creation command it was meant to protect. → Hoisted derive-and-normalize above the first interpolation.
- **P2 (both reviewers)** — Step 4a hardcoded a two-file `git add`/`commit`, which would fail the supported one-file-absent case with a pathspec error. → Rewrote to stage/commit only the file(s) actually edited.
- **P3** — `dev:fix` Step 3 lacked the empty-slug STOP guard `dev:spec` has. → Added for parity.
- **P3** — Step 4a read a merged diff without a data-as-instruction note. → Added, mirroring the tech-debt contract's rule.
- **Nits (2)** — Step 8 report-line anchor undefined when the tech-debt line is omitted (added a fallback anchor); recurrence-merge rationale misdescribed the flush key (corrected to `**Files:**` overlap + same defect).
- No open P1/P2/P3 at close. Two surfaced nits were run through the carrying-cost test and deliberately dropped as pre-existing / out-of-scope (a transitively-safe pre-existing interpolation; an already-documented scoped limitation).

## Artifacts (archived)
Spec and plan committed at: cb2effd65e2a44d9e45c9e43ad6b56de0eadfcb0 on branch feature/done-doc-reconciliation (Shape was skipped — no design.md).
