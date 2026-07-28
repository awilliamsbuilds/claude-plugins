# Unified Backlog + Tech-Debt Model (ADR) — Validation Report
*Branch: arch/backlog-debt-model · 2026-07-28*

## Summary
Loops run: 3 / 5
Cycle type: architecture (deep tier) — document review, no security review
Final status: **clean** — no open P1/P2

## Review scope
Architecture-cycle document review of the committed ADR
(`docs/dev/backlog-debt-model/backlog-debt-model.md`) against the four review lenses:
internal consistency, sufficient context to implement, realistic consequences, non-trivial
rationale. Grounding claims were verified against the real source files — `docs/dev/tech-debt.md`,
the plugin install layout on disk (`~/.claude/plugins/cache/local-plugins/`), and the marketplace
registration in `~/.claude/settings.json`. Each loop's fix diff was cold re-reviewed by a fresh
`general-purpose` subagent denied this session's history (Step 4 step 8).

Findings confirmed strong:
- All nine Scope decisions have a `## Decision N` section, each with alternatives + why-chosen.
- Cross-decision field bindings are consistent: `status` (D3) ↔ lifecycle (D4); `scope` (D3) ↔
  routing (D5); `recurrence == len(cycles)` invariant; `docs/backlog/` + `closed/` paths (D1);
  `<type>-<slug>.md` naming (D2) ↔ D6 capture ↔ D8 migration.
- The three live Open entries, their `first_recorded` dates, and `files` in Decision 8(a)'s
  mapping table match `docs/dev/tech-debt.md` exactly.

## Issues Resolved

### Loop 1
- **P2 — Decision 8(b) Closed-entry miscount.** Said "five" Closed entries but enumerated six, while
  the live `tech-debt.md` has seven — the *stale-`loops_max`* entry was omitted. → Fixed: count
  corrected to seven and the omitted entry added. Verified against the file. Cold re-review clean.

### Loop 2
- **P2 — Decision 5 direct-file-write had no valid delivery target** (surfaced when the design was
  pressure-tested against the real install layout). The plugin, as installed, is a non-git,
  SHA-keyed cache under `~/.claude/plugins/cache/` with no `docs/` tree — so "write the item file
  into the plugin's checkout" has no committable target in the cross-repo case routing exists for,
  and only works in the dogfood case (which needs no routing). → Fixed: **Decision 5 redesigned to
  open a GitHub issue** in the plugin repo (slug read from the marketplace config, PAT auth) as a
  **triage inbox** the maintainer converts into `docs/backlog/` files. Issues have no base branch,
  so the fork/upstream flaw the old design contorted to avoid is unreachable by construction.
  Downstream references updated: Decision 3 (`routing` field), Decision 6 (capture trigger),
  Decision 9 (`dev:done`/`dev:debt` rows, worktree-relative invariant), Consequences (enable/cost
  bullets, follow-ons, the "related open tracker entries" correction — routing no longer *closes*
  the reflect-dogfood-PR entry, it models the fix pattern).

  Cold re-review of the loop-2 diff surfaced, and loop 3 fixed:
  - **P1 — intake dedup merged on slug alone**, contradicting Decision 4's "never merge on
    topic/keyword similarity alone" rule (a wrong merge silently buries a distinct finding). → Fixed:
    intake now uses the slug only to *find candidates*, then applies Decision 4's clear-match test
    (`files` overlap **and** same defect) with create-over-merge bias on uncertainty; the false
    "same bias" parity claim removed.
  - **P2 — the `routing: pending` retry seam was named but undefined.** → Fixed: named concrete
    drains — `/dev:debt` re-attempts on the same surface that surfaces pending items, and `dev:done`
    flush re-attempts them first; the Decision 9 rows now match.
  - **P3s** — `dev:done` plugin items now explicitly bypass the local recurrence-merge; the dogfood
    `origin`-match heuristic is noted as sound for home-detection though distrusted for target
    resolution; the `gh` search index race is acknowledged with conversion-merge as the backstop.
  - **Nit** — "delivered as an issue" → "opened as an issue".

### Loop 3
- All loop-2 re-review findings applied (above). Cold re-review of the loop-3 diff: **no open
  P1/P2**, no regressions, all four prior findings verified genuinely closed.

## Issues Remaining
### P1 Open — None
### P2 Open — None
### P3 Open — None
### Nits Surfaced — None

One residual observation from the re-review, **below Nit and non-blocking**: making `/dev:debt`
re-attempt delivery on the same invocation that *lists* means a list-style call carries a network
write side effect. The ADR states this deliberately ("surfacing and retrying are the same verb"), so
it is a documented design choice for the follow-on implementer to build knowingly — not an open
issue, and it does not qualify for the tech-debt buffer.

## Notes
This validation ran hotter than a typical architecture cycle because the user pressure-tested
Decision 5's soundness mid-review — the right instinct: the direct-file-write mechanism looked clean
on paper but had no valid target once checked against the real plugin install layout. The
issue-inbox redesign is grounded in verified facts (cache is non-git; canonical slug is in the
marketplace config; PAT is present). Two cold-review rounds hardened the dedup and retry semantics.
No security review runs for architecture cycles. All fix-loop re-reviews were dispatched as fresh
history-denied subagents per the pre-authorized `/dev` cold-review path.
