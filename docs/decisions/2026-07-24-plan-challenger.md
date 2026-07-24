# Plan Challenger — Decision Log
*2026-07-24 · Branch: feature/plan-challenger · PR #47*

## What was built
A cold-review challenger for `dev:plan` (new Step 7a) — a fresh subagent that re-reviews the just-written `plan.md` against the spec through three mechanical lenses before the user gate, closing the one artifact-producing `/dev` stage that had no cold review.

## Key decisions
- **Clone spec Step 12a's machinery, deliberately narrowed** → reuse proven, already-shipped challenger structure (dispatch, injection guardrail, in-session fallback, two severities) rather than invent a new mechanism; narrow it to three mechanical lenses because spec already did the judgment work.
- **Three lenses: spec-coverage, sequencing/dependencies, interface-consistency** → these are the mechanical failure modes a plan can carry that Build executes blind and Validate treats as ground truth; a grounding lens was excluded (would duplicate spec's, one stage earlier) and a scope lens was excluded (scope is settled at spec — relitigating it is out of scope).
- **Separate `challenge_plan.*` counter namespace, not nested under `challenge.*`** → reflect reads `challenge.blockers` paired with `spec_revisions` as a *spec*-net signal; a shared object would corrupt it. This was the load-bearing constraint.
- **Standard advisory / autopilot teeth** → verdict renders at the Step 8 gate in standard (user decides); in autopilot, blockers drive a bounded revision loop capped at `challenge_plan.loops_max` with a single STOP path (blockers surviving the cap). No scope-blocker bypass class — all three lenses are text-fixable.
- **SC5 counter-mode invariant designed into the task split** → the repo has three recorded instances of "gate-path write dead in autopilot," and the last challenger-adding cycle reproduced it. Mitigation: `applied` has an autopilot-path writer (the revision loop) *and* a gate writer; `dismissed` is gate-only *because* its autopilot-correct value is its init default 0; `loops_run` is autopilot-only. Reachability, not write-location.
- **Four-skill ripple kept in one cycle** → `spec` (sole state.json template), `plan` (challenger + gate), `reflect` (reads new counters, degrades gracefully when absent), `autopilot` (stop surface + bounded-loop rule) — because the change alters plan's stopping behavior and adds an autopilot STOP condition.

## Validation notes
- 1 loop run (tier: deep). Code + security cold reviews dispatched in parallel as fresh subagents, each fed only the build diff + spec Success Criteria + plan task list.
- **P1 (correctness/consistency) — resume-mid-approval bypassed Step 7a.** Step 1's resume check routed a resumed plan gate straight to Step 8, whose template renders the Step 7a verdict verbatim; on a `/clear`-and-resume the challenger never re-ran and the verdict isn't persisted, so the gate would render empty. Fixed by rerouting the resume check to Step 7a (re-dispatch, regenerate verdict, then flow into Step 8), with the counter-carry note: `run`/`blockers`/`concerns` overwritten, `applied`/`dismissed` carry forward.
- **Nit accepted as-is** — soft exclusion of `state.json` from the challenger subagent: the subagent is told `state.json` is excluded from what it receives, yet it holds read access over the repo so the file stays physically reachable. This is intent (don't re-anchor the reviewer), not a hard sandbox, and is inherited verbatim from the already-shipped spec Step 12a challenger. No fix required.
- Security review clean: injection guardrail present and adequate, read-only trust boundary held, verdict displayed not executed, `<feature>` slug-normalized at every interpolation site.

## Artifacts (archived)
Spec and plan committed at: a801db1 on branch feature/plan-challenger

## Retrospective
*Reviewed by dev:reflect · 2026-07-24*

**Spec:** Clean — `spec_revisions: 0`, final score 95/Ready matched actual clarity; spec challenger caught 1 blocker (applied), the healthy "challenger catches what grounding missed" reading.
**Shape:** Skipped — correct for a prose/state-template change with no user-facing UI.
**Plan:** Accurate — `files_read_in_build: 1`, no mid-build task additions.
**Validate:** 1 loop / 5, clean after one. The single P1 (resume-mid-approval bypassing the new Step 7a) is the exact cross-step consistency class this feature's own challenger is built to catch — but the plan for this feature predated the challenger, so Validate caught it cheaply instead.
**Flow:** Deep tier was right for a four-skill change bound by the `challenge_plan` namespace constraint; no unnecessary stages.
**Token efficiency:** No outliers — post-spec stages ran 4–7 min each; the long spec span is wall-clock across a break, not active work.
**Suggestions:** none
**Deferred to tech debt:** none
