# Spec Review Autoloop — Decision Log
*2026-11-10 · Branch: feature/spec-review-autoloop · PR #100*
*Handed off to autopilot at Plan*

## What was built
Spec and plan cold reviews now apply their own fixes and re-review on their own when a round is heavy, in both gated and autopilot cycles, under one rule stated once.

## Key decisions
- **One rule across Spec/Plan × gated/autopilot** → the user asked explicitly that the trigger and the cap not be two rules that could conflict. `dev:spec` Step 12a is canonical, `dev:plan` Step 7a mirrors it and `dev:autopilot` restates it.
- **Heavy = ≥1 Blocker or ≥5 Concerns** → the user's threshold. It replaces "concerns never extend the loop": concern volume is now a legitimate reason to look again.
- **Tier caps kept (1/3/5)** → the user chose tier scaling over a flat 3.
- **A heavy final round applies nothing** → a heavy round's fixes are never applied unreviewed: either a following round checks them or a human does.
- **The gate becomes a per-round log plus one approval question** → the user was accepting every fix unread, so asking was pure overhead. Revert and edit stay available as Path B.
- **The modes differ only at the exit** → the gated flow shows leftovers at the gate, and autopilot STOPs (now also on a concern-heavy final round, accepted as the cost of one rule).
- **Resume carries `loops_run` forward** → a `/clear` must not buy a fresh cap. On a spent cap the resume is exit-neutral, because the exit reason is not persisted and no new state key was allowed.
- **Suggested fixes are data** → a fix is applied only as a text edit to the artifact under review. This matters now that fixes land without a human reading them first.
- **Folded debt** → the plan errored-dispatch mirror, and `plan_end`/`spec_end` re-stamped after the loop.

## Validation notes
- 3 loops run (tier: standard), final status clean
- P2: the spent-cap resume assumed a `limit` exit → made exit-neutral (loop 1)
- 6 P3s in loop 1 (including the fix-as-data guard and the autopilot STOP not committing state), plus 2 + 2 P3s in loops 2–3 on the same resume paragraph (converging cascade), all fixed
- Nit accepted as-is: awkward possessive phrasing at spec/SKILL.md:56

## Artifacts (archived)
Spec, design, and plan committed at: 3e3c81c on branch feature/spec-review-autoloop

## Retrospective
*Reviewed by dev:reflect · 2026-11-10*

**Spec:** 87% confidence, 7 questions, 0 user revisions. The cold review found 0 blockers and 6 concerns (applied 6, all concern-driven; dismissed 0). The user accepted them with one "apply all" turn, which is the turn this feature removes. The score matched actual clarity.
**Shape:** Shape skipped (no UI).
**Plan:** The plan review found 0 blockers and 4 concerns, folded in 1 round. One unplanned Build change was recorded in `plan.md` (the `telemetry.md` null-counter note, a consequence of mirroring the errored-dispatch rule).
**Validate:** 3 / 3 loops. Loop 1 fixed the one P2 (the spent-cap resume assumed a `limit` exit). Loops 2–3 were a converging cascade on that same resume paragraph, prose-only. Spec flagged the resume edge case but never fully specified it, and that is where Validate's churn landed.
**Flow:** Standard tier was right. The handoff to autopilot at Plan ran to PR with no stops.
**Token efficiency:** no outliers. Validate was the longest stage, about 6 minutes over 3 re-review dispatches.
**Suggestions:** none. The user raised no observations.
**Deferred to tech debt:** none
