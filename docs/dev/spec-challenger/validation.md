# Spec Challenger — Validation Report
*Branch: feature/spec-challenger · 2026-07-21*

## Summary
Loops run: 2 / 3
Final status: clean

Reviews ran **in-session** rather than as dispatched subagents — subagent dispatch is disabled
in this session's harness, which is the fallback `dev:validate` Step 2 specifies. Both
checklists (code review, security review) were run against `git diff 8461457..9cf6034`, the
diff since Build started.

Diff reviewed: 4 files, +121 / −18. Three `SKILL.md` edits (`spec`, `autopilot`, `reflect`)
plus this cycle's own `state.json`. No executable code, no dependencies, no config keys added.

## Issues Resolved

### Loop 1
- **P2 (autopilot never records applied fixes)** — Step 12a's counter semantics said
  `challenge.applied` / `challenge.dismissed` "are written by Step 13," but Step 13's autopilot
  branch is a no-gate pass-through. An autopilot cycle whose revision loop applied N blocker
  fixes would still report `applied: 0`, violating spec success criterion 6 (which is not
  qualified by mode) and leaving `dev:reflect`'s diagnostic matrix blind for every autopilot
  cycle. → Fixed: the loop now writes `applied` itself, incrementing per iteration by the fixes
  that iteration landed. Stated in both `spec` Step 12a (counter semantics *and* the autopilot
  mode paragraph) and `autopilot` Step 2, so the two files agree. `dismissed` is explicitly
  pinned at `0` in autopilot — nothing is declined there, since concerns pass through by design
  and unresolved blockers are surfaced at the STOP rather than dropped.

- **P2 ("user dismisses everything" never records `challenge.dismissed`)** — the `dismissed`
  increment lived only inside Step 13's Path A, which is gated on "if changes are requested."
  Dismissing every finding requests no changes, so that user goes straight to the approval
  path — which carried only Step 12a's pending `run` / `blockers` / `concerns` writes. The
  spec's Edge Cases and plan Task 4 both name this case as the signal reflect reads for "the
  brief has become noise," and it was the one case that could never be recorded. → Fixed: the
  "When approved" instruction now increments `dismissed` by the number of surfaced findings
  left unactioned, and says why this is the only path a fully-dismissed verdict takes.

- **P3 (autopilot claims concerns are "logged in the spec")** — `autopilot` Step 2 said concerns
  are "logged in the spec and passed through," but nothing anywhere specifies writing concerns
  into `spec.md`; they exist only as the `challenge.concerns` count. `spec` Step 12a said
  merely "logged." → Fixed: both files now say concerns are counted in `challenge.concerns` and
  passed through, never revised.

- **P3 (gate prompt is incoherent on a clean verdict)** — the Step 13 gate template printed
  "Reply `apply` to take all suggested fixes…" unconditionally, directly under a verdict that
  may legitimately be clean (spec success criterion 2). → Fixed: the line is now bracketed as
  conditional, following the file's existing `[If worktreePath is set: …]` convention, with an
  explicit instruction to omit it on a clean verdict.

- **Nit (security — guardrail scope)** — the injection guardrail named `spec.md` and
  `config.json` as data-under-review, but the reviewer also reads arbitrary repo files while
  re-verifying grounding, and those were uncovered. → Fixed: the guardrail now covers every
  repo file the subagent reads during grounding verification.

- **Nit (Step 11 redundancy)** — after the shrink, Step 11 said "Fix them inline" and then
  "Fix issues inline" one line later, a leftover of the five-item list. → Fixed: collapsed to
  one sentence.

- **Nit (stale attribution in reflect's matrix)** — the high-blockers/low-revisions row read
  "The author's own passes (spec Steps 7 and 11) are weak." Post-shrink, Step 11 is a
  placeholder scan and cannot plausibly be the net that misses clarity, consistency, scope, or
  grounding defects. → Fixed: the row now names Step 7's grounding pass alone.

### Loop 2
Re-review of the amended text found no new P1/P2. Consistency sweep confirmed clean — see below.

## Issues Remaining
### P1 Open
None.

### P2 Open
None.

### P3 Open
None.

### Nits Surfaced
None outstanding.

## Verification Performed

- **Plan coverage** — all seven tasks implemented. Task 1 (`challenge` block, top-level sibling
  of `validate`, seven keys) ✅; Task 2 (Step 11 shrink, retitle, reconciliation paragraph kept
  verbatim at line 397 and still feeding Step 12's read at line 405) ✅; Task 3 (Step 12a, all
  fifteen sub-steps present) ✅; Task 4 (verdict at the gate, two labelled paths, resume routed
  to Step 12a) ✅; Task 5 (autopilot bullet + both new stop conditions in the "When autopilot
  stops" line) ✅; Task 6 (reflect extract list, matrix, `dismissed` reading, qualitative
  constraint, unstaled Step 11 citation, no new retrospective row) ✅; Task 7 (consistency pass,
  `recovered-context.md` removed, worktree clean) ✅.
- **Spec success criteria** — all eleven satisfied after loop 1. Criteria 6 and the "user
  dismisses everything" edge case were the two that failed on first pass; both now hold.
- **Key spelling** — `grep -o "challenge\.[a-z_]*"` across all three files returns exactly the
  seven keys in Step 6's template. Nothing written that reflect cannot read; nothing read that
  spec never writes.
- **Cross-references** — every `Step 11` / `Step 12a` / `Step 13` citation across the three
  files resolves to a heading that exists.
- **Tier caps** — `micro 1 / standard 3 / deep 5` appears identically at all three sites (spec
  Step 6, spec Step 12a, autopilot Step 2) and matches `dev:validate` Step 1, where the
  convention originates.
- **Config contract** — no new key added to `docs/dev/config.json`, so the eight-reader audit
  obligation does not trigger. `spec/SKILL.md` Step 1 already reads `config.json`, which
  Step 12a hands to the subagent.
- **Security** — the diff adds no executable code, no dependencies, no credential handling, and
  no new external data path. The one real surface is prompt injection via spec content
  originating from a Linear issue (`dev:fix` → MCP); the guardrail is present, explicit, and
  now covers the grounding reads too. The subagent is read-only (`Read` / `Grep` / `Glob`, no
  write) and its output returns to the same session, so there is no exfiltration channel.

## Notes

Both P2s were the same shape: a rule written for the standard-mode gate, then relied upon by a
mode that has no gate. Step 12a delegates counter writes to Step 13, and Step 13's autopilot
branch is one line long. Worth watching in `dev:reflect` — the feature's own design splits
behavior across two files by mode, which is exactly where the next such gap would hide.

Nothing here required a Path B–style rewrite; every fix was additive prose in the file that
already owned the rule.
