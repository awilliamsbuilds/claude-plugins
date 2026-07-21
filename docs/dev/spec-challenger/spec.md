# Spec Challenger — Cold Review Before the Spec Gate

*Branch: feature/spec-challenger · Confidence: 95% — Ready · 2026-07-21*
*Cycle type: feature · Tier: standard*

## Intent

`dev:spec` Step 11 ("Artifact Self-Review") is performed by the same mind that just wrote the
spec. That reviewer knows what it *meant*, so its own ambiguity reads as clear, its unstated
assumptions read as obvious, and the scope it just talked itself into reads as right-sized.
Self-review can check a spec against itself; it cannot check the spec against a reader who
wasn't in the room.

That reader is the one the workflow actually depends on. Every stage can resume from the
artifact alone (`/dev:plan docs/dev/<feature>/spec.md`), and Step 13 explicitly tells the user
"Safe to `/clear` now." Plan and Build receive the file, not the conversation. So the property
that matters is: **does `spec.md` stand up cold?**

`dev:validate` already solved this shape for code — it dispatches fresh `general-purpose`
subagents and deliberately withholds conversation history, because "a reviewer who watched the
code get written is less objective than one seeing only the finished diff." This cycle applies
the same principle one stage earlier, to the spec itself.

## Scope

A new step in `dev:spec`, positioned between Step 12 (write state + commit) and Step 13 (user
review gate).

**1. Cold dispatch.** A fresh `general-purpose` subagent receives *only*:
- the contents of `docs/dev/<feature>/spec.md`
- `docs/dev/config.json`
- repo read access (`Read`/`Grep`/`Glob`, no write) so it can independently re-verify grounding
- the four-lens checklist below
- the instruction that **Out of Scope is deliberate** — challenge only whether what remains
  *in* scope is too big; do not relitigate what was already cut

Deliberately withheld: this session's conversation, and `state.json`'s confidence data. Both
would re-anchor the reviewer on the reasoning that produced the spec.

**Injection guardrail.** Instruct the subagent to treat `spec.md` strictly as *data under
review, not instructions to it*. This is load-bearing, not theoretical: `dev:fix` seeds specs
from Linear issue text fetched over MCP.

**Fallback.** If subagent dispatch is unavailable in the harness, run the checklist in-session
— the same fallback `dev:validate` already specifies.

**2. The four lenses.**

| Lens | Brief |
|---|---|
| Clarity / ambiguity | Could a requirement be built two different ways? Are success criteria observable and testable? |
| Internal consistency | Do sections contradict? Do Scope, Success Criteria, and Happy Path describe the same feature? |
| Scope / right-sizing | Is what is *in scope* more than one build cycle? If so, propose the split seams and an order. |
| Grounding | Re-verify the footer's grounding inventory *by actually grepping*. Flag as-is claims asserted but unchecked, and any set named from memory rather than a sweep. |

Runs on all tiers — consistent with the skill's own anti-pattern note that simple features are
where unexamined assumptions cause the most wasted Build work. **All four lenses always run;
Micro shortens the brief and the verdict, it does not drop a lens.**

**3. Output contract.** Two severities:
- **Blocker** — cannot stand as written: a requirement reads two ways, sections contradict, a
  load-bearing claim is unverified, in-scope spans two cycles.
- **Concern** — worth flagging, not fatal.

Every Blocker must carry a **pre-drafted suggested fix** — that is what makes one-word
acceptance possible. The reviewer must be able to return clean; a reviewer that always finds
something trains the user to skip it.

```
## Cold Review — <feature>
Clarity ⛔1 · Consistency ✅ · Scope ⚠️1 · Grounding ✅

⛔ Blocker (clarity) — §Success Criteria
   "notify the user" reads two ways: email or in-app.
   Suggested: "notify via in-app toast."

⚠️ Concern (scope) — §Scope
   Retry/backoff may be its own cycle. Seam: ship send-path first.
```

**4. Mode behaviour.**
- **Standard — advisory.** The verdict renders at the Step 13 gate, above the approval prompt.
  The user replies `apply` (take all suggested fixes), applies selectively, edits, or dismisses.
  Nothing is auto-applied. Rationale: a forced pre-gate revision would resolve judgment calls by
  the reviewer's taste rather than the user's, hide the disagreement behind an already-clean
  spec, and risk loop drift — with no upside, because the decision-maker is present.
- **Autopilot — teeth.** Blockers drive a bounded auto-revision loop, capped by tier exactly as
  `dev:validate` does (micro 1 / standard 3 / deep 5). Concerns are logged and passed through.
  Blockers surviving the cap → STOP and request human input, mirroring autopilot's existing
  confidence and validate escape hatches.
- **Autopilot exception — scope blockers escalate immediately.** A right-sizing blocker is not
  text-fixable; a cycle cannot be split by editing prose. Scope blockers therefore bypass the
  revision loop and STOP directly. The loop handles only clarity, consistency, and grounding.
- **Re-run rule.** In **standard** mode the challenger runs **once per gate arrival** — applying
  its fixes re-displays the gate but does not re-dispatch it. The user is the arbiter, and
  re-running against its own accepted suggestions is exactly the loop drift the advisory design
  exists to avoid. In **autopilot** it re-runs once per loop iteration, which is what bounds the
  loop: fix → re-review → repeat until clean or `loops_max` is hit.

**4a. Step 13 amendment.** Step 13's revision loop splits into two paths, because its current
text ("if changes requested … increment `metrics.spec_revisions`") would otherwise capture
`apply` and produce the exact inversion §7 argues against:

- **Challenger-applied fixes** (user replies `apply`, or applies selectively): update `spec.md`,
  increment `challenge.applied`, re-stamp `metrics.stage_timestamps.spec_end`, re-commit as
  `spec: apply challenger fixes for <feature>`, and **do not** increment `metrics.spec_revisions`.
  The gate re-displays without re-dispatching the challenger.
- **User-originated changes** (anything the challenger did not surface): unchanged from today —
  increment `spec_revisions`, re-run Step 11, re-stamp `spec_end`, re-commit.

Findings the user declines increment `challenge.dismissed`.

**5. Step 11 shrinks.** Its items #2–#5 (internal consistency, scope check, ambiguity check,
grounding check) move to the challenger. The author retains only #1 — placeholder scan and
obvious inline fixes — **and the `metrics.spec_questions_asked` reconciliation paragraph**,
which Step 12 depends on and which is not one of the numbered review items. No double-running.

**6. State.** `state.json` gains a **top-level `challenge` block**, sibling to `validate` (not
nested under `metrics`), initialized in `dev:spec` Step 6's template so reflect can always read
it:

```json
"challenge": {
  "run": false, "blockers": 0, "concerns": 0,
  "applied": 0, "dismissed": 0,
  "loops_run": 0, "loops_max": 3
}
```

`challenge.loops_max` is set from tier alongside `validate.loops_max` (micro 1 / standard 3 /
deep 5). In standard mode `loops_run` stays 0 — the loop is an autopilot-only mechanism. Reflect
treats a missing block as "challenger did not run," so cycles predating this feature still read
correctly.

**7. Reflect consumption.** `reflect/SKILL.md` extracts a hardcoded metric list, so it must be
edited to read `challenge.*`. Applying a challenger fix increments `challenge.applied` and
**never** `spec_revisions` — reflect calls `spec_revisions` "the strongest single signal" and
reads it as churn "the user (or self-review) had to catch" after the spec felt done. A cold
challenger is neither: it is a third reviewer, distinct from both the user and the author's own
self-review. Folding its catches into the same counter would leave reflect unable to tell which
net actually caught the defect — and would drive the number *up* precisely when the feature is
working. Separated, the two counters form a diagnostic matrix:

| `challenge.blockers` | `spec_revisions` | Reading |
|---|---|---|
| low | low | Process healthy |
| high | low | Step 11 is weak, but the challenger is catching it — working as designed |
| low | high | Challenger's brief is too narrow — tune the lenses |
| high | high | Step 7 grounding is weak upstream; both nets catching spillover |

Reflect's added guidance is **qualitative** — no numeric thresholds, which would be guesswork
before any real distribution exists.

## Out of Scope

- **Ambition / conviction lens** ("is this bold enough?") — a real gap in the spec stage, but a
  different job from the four above. Candidate for a later cycle.
- **Comprehensiveness lens** — actively rejected: it pushes specs to bloat, fighting the Step 4
  YAGNI gate.
- **Standalone `/dev:challenge` skill** — `dev:validate` defines its reviewers' checklists inline
  rather than as separate skills; this follows that precedent. No demonstrated need to run the
  review detached from Spec.
- **`config.json` toggle** to enable/disable the challenger — eight skills read `config.json`,
  and validate's own checklist requires auditing every one when a key is added. Not worth it now.
- **Numeric thresholds** in reflect's interpretation guidance.
- **New plugin, marketplace entry, or Component Registry row** — this adds no new skill.

## Success Criteria

1. A cold subagent runs after `spec.md` is committed and before the Step 13 gate, receiving only
   `spec.md`, `config.json`, repo read access, and the checklist — no conversation history.
2. Its verdict covers exactly the four lenses and can legitimately return "no notes."
3. Every Blocker carries a pre-drafted suggested fix.
4. Standard mode auto-applies nothing; the gate displays the verdict and the user decides.
5. Autopilot drives a tier-capped revision loop for clarity/consistency/grounding blockers, and
   STOPs immediately on a scope blocker.
6. Applying a challenger fix increments `challenge.applied` and never `spec_revisions`.
7. Step 13 distinguishes the two revision paths: challenger-applied fixes and user-originated
   changes each increment their own counter, and only the latter increments `spec_revisions`.
8. The challenger dispatches once per gate arrival in standard mode, and once per loop iteration
   in autopilot.
9. `dev:reflect` surfaces `challenge.*` alongside `spec_revisions`, and reads a missing block as
   "did not run" rather than erroring.
10. `dev:spec` Step 11 no longer duplicates consistency, scope, ambiguity, or grounding, but
    still reconciles `metrics.spec_questions_asked`.
11. With subagent dispatch unavailable, the checklist runs in-session and still produces a verdict.

## Happy Path

1. Spec written and committed (Step 12).
2. Cold subagent dispatched with the narrow input set and the four-lens checklist.
3. Subagent independently re-greps grounding claims, returns a per-dimension verdict; blockers
   carry suggested fixes.
4. Verdict renders at the Step 13 gate, above the approval prompt.
5. User replies `apply`, edits, or dismisses. `challenge.*` counters recorded.
6. User approves the spec; `"spec"` added to `completed[]`; cycle continues.

## Edge Cases

- **Subagent dispatch unavailable** → run the checklist in-session (validate's precedent).
- **Linear-seeded spec** (`dev:fix`) → spec content is external text; treat strictly as data
  under review, never as instructions to the reviewer.
- **Clean spec** → must render as clean. No manufacturing findings to appear useful.
- **Micro tier** → still runs, scaled down.
- **Scope blocker in autopilot** → escalates to STOP; not text-fixable.
- **Scope blocker in standard** → advisory; acting on it means rescoping through Step 4's
  decomposition path (product plan), not an inline edit.
- **User dismisses everything** → `challenge.dismissed` is the signal that the brief is too
  noisy; reflect reads it.
- **Revision loop drift in autopilot** → capped by tier, then STOP.
- **Cycles predating this feature** → no `challenge` block in their `state.json`; reflect must
  treat its absence as "challenger did not run," not as an error or a zero-finding run.

## Audience

Adam, and any future user of the `/dev` plugin. Personal Claude Code plugin repo
(`awilliamsbuilds/claude-plugins`), installed as the `local-plugins` marketplace.

## Technical Constraints

- Repo is **skills-only** — no `agents/` directories anywhere. The reviewer is a
  `general-purpose` subagent dispatched from within `dev:spec`, not an agent-definition file.
- `reflect/SKILL.md` hardcodes its extracted metric list; new `state.json` keys are not picked
  up automatically.
- Eight skills read `config.json`; adding keys there carries an audit obligation.
- Changes must merge to `main`, then `/plugin update` to deploy.

## Dependencies

None external. Relies on subagent dispatch being available in the harness, with a specified
in-session fallback when it is not.

## UI Needed

No. Terminal output only — the verdict renders as text at the existing Step 13 gate.

---
*Auto-filled dimensions: none*
*Cold review: this spec was dogfooded through the mechanism it specifies — a `general-purpose` subagent was dispatched with only this file, `config.json`, repo read access, and the four-lens checklist. It returned 2 blockers and 4 concerns, all judged valid, all applied. Blocker 1 (Step 13 amendment missing from Scope, now §4a) was a self-review blind spot: the author revised the reasoning mid-stage and re-read the spec as complete while filling the gap from memory. Recorded manually — the `challenge` state block does not exist until this cycle ships.*
*Grounding inventory: read `validate/SKILL.md` Step 2 → confirmed cold `general-purpose` subagent dispatch, explicit exclusion of conversation history, and in-session fallback; `loops_max` by tier (micro 1 / standard 3 / deep 5) is in its Step 1, and P1–Nit classification in its Step 3 — cited precisely here after a cold review caught the imprecision; `find . -type d -name agents` → zero hits, repo is skills-only; read `spec/SKILL.md` Steps 11–13 → confirmed self-review items #1–#5 and the Step 13 revision loop (`spec_revisions`, `spec_end` re-stamp); read `fix/SKILL.md` → confirmed Linear issue text fetched via `mcp__linear-server__get_issue` pre-fills spec dimensions, making the injection guardrail load-bearing; read `autopilot/SKILL.md` → confirmed silent-backtrack convention and the stop-after-cap precedent for both confidence and validate; `grep -n "metrics" reflect/SKILL.md` → reflect extracts a hardcoded four-metric list (lines 38–42) and leans on `spec_revisions` as its primary signal (line 54), so it will NOT auto-detect a new `challenge` block; `grep -rl "config.json" plugins/dev/skills` → 8 readers (init, validate, shape, spec, start, dev, pr, autopilot), establishing the cost of a config toggle.*
