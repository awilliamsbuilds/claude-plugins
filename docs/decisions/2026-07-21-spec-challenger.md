# Spec Challenger — Decision Log
*2026-07-21 · Branch: feature/spec-challenger · PR #37*

## What was built

A cold-review step (`dev:spec` Step 12a) that dispatches a fresh subagent to re-review the
committed `spec.md` across four lenses before the user ever sees the approval gate — because
the mind that just wrote the spec cannot check it against a reader who wasn't in the room.

## Key decisions

- **Cold subagent, not an expanded self-review** → `dev:validate` Step 2 already solved this
  shape for code, deliberately withholding conversation history so the reviewer sees only the
  finished artifact. The spec deserves the same treatment one stage earlier, since every
  downstream stage resumes from `spec.md` alone.
- **Four lenses: clarity, internal consistency, scope right-sizing, grounding** → each is a
  failure mode the author is structurally blind to. A comprehensiveness lens was rejected
  outright for pushing specs toward bloat and fighting the Step 4 YAGNI gate; an
  ambition/conviction lens was deferred as a real but different job.
- **Advisory in standard mode, teeth in autopilot** → with the decision-maker present, a forced
  pre-gate revision would resolve judgment calls by the reviewer's taste rather than the
  user's, and hide the disagreement behind an already-clean spec. Autopilot has no such
  arbiter, so blockers there drive a tier-capped revision loop (micro 1 / standard 3 / deep 5).
- **Scope blockers escalate immediately in autopilot** → a right-sizing blocker isn't
  text-fixable. A cycle cannot be split by editing prose, so the loop handles only clarity,
  consistency, and grounding; scope goes straight to STOP.
- **`challenge.applied` is a separate counter from `metrics.spec_revisions`** → reflect calls
  `spec_revisions` "the strongest single signal" and reads it as churn the *human* had to catch.
  Folding challenger catches into it would drive the number up precisely when the feature is
  working. Kept apart, the two counters form a diagnostic matrix telling you *which net* caught
  the defect.
- **Step 11 shrinks rather than co-existing** → its consistency, scope, ambiguity, and grounding
  items moved wholesale to Step 12a. Running both would double-review and let each pass assume
  the other was thorough. Step 11 keeps only the placeholder scan and the
  `spec_questions_asked` reconciliation Step 12 depends on.
- **`Step 12a` rather than renumbering** → follows `dev:validate`'s `Step 4a` precedent and
  keeps every existing cross-reference to Step 13 valid.
- **No standalone `/dev:challenge` skill, no `config.json` toggle** → `dev:validate` defines its
  reviewers' checklists inline, and eight skills read `config.json`, so a new key carries an
  eight-file audit obligation for no demonstrated need.
- **Injection guardrail is load-bearing, not theoretical** → `dev:fix` seeds spec dimensions from
  Linear issue text fetched over MCP, so spec content can originate outside the repo. The
  subagent is instructed to treat `spec.md`, `config.json`, and every repo file it reads during
  grounding verification strictly as data under review.

## Design choices

Shape was skipped — terminal output only, rendered at the existing Step 13 gate. The one
interface decision worth recording: the verdict is a single summary line with per-lens
✅/⚠️/⛔ marks followed by one entry per finding, and **every Blocker carries a pre-drafted
suggested fix**, which is what makes one-word `apply` acceptance possible. Paired with a hard
rule that the reviewer must be able to return clean — a reviewer that always finds something
trains the user to skip it.

## Validation notes

- 2 loops run (tier: standard). Reviews ran **in-session** rather than as dispatched subagents —
  subagent dispatch was disabled in this session's harness, which is the fallback `dev:validate`
  Step 2 specifies. Diff reviewed: 4 files, +121 / −18.
- **P2 — autopilot never records applied fixes.** Step 12a delegated `challenge.applied` writes
  to Step 13, but Step 13's autopilot branch is a no-gate pass-through, so an autopilot cycle
  would always report `applied: 0`. Fixed: the revision loop writes the counter itself.
- **P2 — "user dismisses everything" never recorded.** The `dismissed` increment lived only in
  Path A, gated on "if changes are requested" — dismissing everything requests no changes. The
  one edge case reflect most needs was the one that could never be recorded. Fixed on the
  approval path.
- **P3 ×2** — autopilot claimed concerns were "logged in the spec" when they exist only as a
  count; the gate prompt printed "Reply `apply`…" unconditionally, under a verdict that may
  legitimately be clean. Both fixed.
- **Nits ×3** — injection guardrail didn't cover the reviewer's grounding reads; leftover
  duplicate "fix inline" sentence after the Step 11 shrink; stale Step 11 attribution in
  reflect's matrix. All fixed.
- Nothing accepted as-is. P1/P2/P3/Nits all closed at loop 2.
- Both P2s were the same shape: a rule written for the standard-mode gate, then relied upon by a
  mode that has no gate. Worth watching — this feature's design deliberately splits behavior
  across two files by mode, which is exactly where the next such gap would hide.

## Artifacts (archived)

Spec and plan committed at: `ba6f798eaf6df4b8b599800c3e89da18e95007e7` on branch
`feature/spec-challenger`. (Shape was skipped — no design.md.)
