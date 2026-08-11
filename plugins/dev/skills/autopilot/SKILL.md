---
name: dev:autopilot
description: "No-gate orchestrator for the /dev workflow. Chains all stages end-to-end without approval gates or browser interaction. Self-review substitutes for comprehension checks. Spec questions capped at spec_max_questions, then auto-fills. Stops only on true blockers. Invoked via /dev:autopilot or /dev auto."
---

# dev:autopilot — No-Gate Orchestrator

**Announce:** "I'm using dev:autopilot to run the full /dev workflow without approval gates."

## Purpose

Chain all applicable stages end-to-end without stopping for user approval. Trade interactivity for speed. Use when you trust the spec enough to let the AI run the full cycle.

**When autopilot stops:** Only on genuine blockers — PR can't be merged, P1/P2 issues remain after loop limit, confidence is too low even after auto-fill, a spec-challenger scope blocker, challenger blockers remaining after `challenge.loops_max` revisions, plan-challenger blockers remaining after `challenge_plan.loops_max` revisions, 3 root-cause hypotheses fail for an unexpected test failure during Build (see `dev:build`'s "When a Test Fails Unexpectedly"), or Step 1 cannot resolve a single cycle to run (the artifact-path form names a feature with no `state.json`, or the session scan finds more than one in-progress cycle). Everything else runs through. (A handed-off cycle also *pauses* once, at `dev:reflect` Step 4, to ask the user for observations — a pause, not a stop; see Step 2.)

## Resolve the working directory (do this first)

This orchestrator never relies on the shell's current directory or current branch. Compute the
primary checkout, then locate this cycle's directory:

    GIT_COMMON=$(git rev-parse --git-common-dir) || { echo "Not a git repository."; exit 1; }
    PRIMARY=$(cd "$(dirname "$GIT_COMMON")" && pwd)

Find the cycle directory — first hit wins — by testing for `docs/dev/<feature>/state.json` under:
1. `$PRIMARY/.dev-worktrees/<feature>/`   → active worktree cycle
2. `$PRIMARY/`                            → legacy in-place cycle (worktreePath null)

Set `WORKDIR` to whichever matched. Neither branch is guarded by `worktreePath` — that field is a
set/null predicate only, never the resolver. For the rest of this run: run every git command as
`git -C "$WORKDIR" …`, and read/write all artifacts under `$WORKDIR/docs/dev/<feature>/…`.
Never `cd`, never assume the current branch.

## Step 1: Initialize

Check for `docs/dev/config.json`. If missing, run dev:init in autopilot mode (no questions — infer everything from codebase scan).

May be invoked with an artifact-path argument (`spec.md` or `design.md` path). If given, derive `<feature>` from the path instead of scanning. **Validate before using:** the path must match `docs/dev/<feature>/<artifact>.md` with `<feature>` matching `^[a-z0-9][a-z0-9-]*$` and containing no `..` segments. If it doesn't match, treat the argument as invalid and fall back to the scan.

**On the artifact-path form, a validated feature with no cycle is a stop — never a fresh start.** If `<feature>` passes validation but neither location above holds `docs/dev/<feature>/state.json`, STOP: "No /dev cycle found for `<feature>`. Checked `$PRIMARY/.dev-worktrees/<feature>/` and `$PRIMARY/`." Do **not** fall through to "begin from Spec" — the argument form exists to resume a *named* cycle, so a mistyped slug that silently launched a new unattended cycle instead would be the worst available reading of it. This mirrors the artifact gate every stage skill opens with.

With no argument: scan for an in-progress session; on exactly one hit resume it, and on none begin from Spec — both unchanged. (More than one hit is new; see the paragraph below.) The artifact-path form is additive. The scan covers the same two locations as the resolution block, one glob each — `$PRIMARY/.dev-worktrees/*/docs/dev/*/state.json` (active worktree cycles) and `$PRIMARY/docs/dev/*/state.json` (legacy in-place cycles) — deduplicated by feature name, matching `dev:dev` Step 3's globs. Once a session is picked `<feature>` is known, and the resolution block above applies to it.

**Borrow `dev:dev` Step 3's globs, not its multi-hit rule.** Where that skill lists several sessions and *asks* which to continue, autopilot may not — Step 2 forbids asking. So on more than one hit, STOP:

```
Found N in-progress cycles: <one line per hit — list them all>

Re-run naming the one you want:
  /dev:autopilot docs/dev/<feature>/spec.md
To start a new cycle instead, in standard mode: /dev spec
```

Picking one unattended would run Build, PR and merge on a cycle the user never named.

**Why `/dev spec` and not `/dev`.** Bare `/dev` lands on `dev:dev` Step 3's own resume/restart/abandon menu in exactly this state, whose *Restart* option force-removes a worktree. `/dev spec` is the documented new-session jump (`dev/SKILL.md:174`), parsed at that skill's Step 1 before its scan runs, and it combines with other flags — `/dev spec no-ui` for a no-UI cycle. It is standard mode, and the message says so: autopilot has no start-a-new-cycle-while-others-are-in-flight form, so pointing at the gated one is honest rather than implying an autopilot form exists.

**This STOP is the only thing the multi-hit case changes.** The zero-hit and single-hit paths are untouched for every invocation form, including `/dev:autopilot no-ui` — that argument fails the artifact-path validation above and falls back to this scan exactly as before, beginning from Spec when nothing is in flight and resuming the one hit when something is. Whether Shape is then skipped is settled by `dev:spec` Step 12 from the spec's own `## UI Needed`, which is authoritative over the launch flag (`spec/SKILL.md:478`) — this skill records nothing about it.

**Read `tier` and `stage` from the resolved `state.json`, not from the request.** On the artifact-path form — and on any resumed session — read both from the `state.json` that `WORKDIR` resolution found, and use them to pick the remaining-stage list in Step 3. A pasted resume command carries no initial request to infer from, so without this a micro cycle would have no way to select its `Spec → Build → Validate → PR → Done` sequence.

Check for in-progress session. If found:

```
/dev session in progress: <feature-name>
<stage-status-line>

Resuming from <current-stage> in autopilot mode.
```

If no in-progress session: begin from Spec.

Set mode in state.json by these two branches. **Decide which branch applies from the `state.json` that existed when this invocation began** — the one the resolution block found, read before any stage of this run has executed. A `state.json` that this same invocation caused to be created is never a handoff, whatever `mode` it is born with: `dev:spec` Step 6 writes `"mode": "standard"` into every new state file, so re-reading `mode` after Spec has run would see `"standard"` on a cold start and misclassify a pure-autopilot cycle as a handed-off one. Read `stage` **before** flipping `mode` — reading it after records the stage autopilot advances to rather than the one it took over at.

- **A prior session existed and its `mode` read `"standard"`** — this is a handoff. Set `handoff_at` `(writes: autopilot-only)` to the value of `stage` **as read before the flip** (the stage this invocation is resuming at), then set `mode` to `"autopilot"`. Both writes go in the same state.json update.
- **A prior session existed and its `mode` already read `"autopilot"`, or there was no prior session** (a fresh cycle this invocation starts from Spec) — set `mode` to `"autopilot"` as today and **do not write `handoff_at` at all.** Absent is the value; do not write `null`, `false`, or an empty string.

`handoff_at` holds the stage autopilot is resuming at — the first stage that runs unattended. On the **approved** path offered at the Spec and Shape gates that is `"plan"`, or `"build"` on micro, and not `"spec"`/`"shape"`, because gate approval advances `stage` to the next stage before the user pastes the command. A user who pastes the command *before* approving — a path both gates document as harmless — legitimately produces `"spec"` or `"shape"` here; that is a correct marker for what actually happened, not corruption. The value domain is deliberately open — any stage name, not an enum. No offer is printed at the Validate or PR gates, but a user who types `/dev:autopilot` there has still handed off, and the marker records that stage accurately.

**Read contract for downstream consumers** (`dev:reflect` Step 4, `dev:done` Step 5): an absent `handoff_at` means "no handoff," including on every cycle that predates this feature. Never an error.

This is the key's only write site. There is no standard-mode writer — the Spec and Shape gates print text and write nothing — so no standard-side default is needed.

## Step 2: Autopilot Behavioral Rules

These rules apply throughout all stages. They override the standard-mode behaviors described in each stage skill:

**No approval gates.** After each stage completes: read that the artifact exists and is non-empty (sanity check), then move immediately to the next stage. Do not ask "Continue?"

**One carve-out, and only one: `dev:reflect` Step 4 on a handed-off cycle.** When `handoff_at` is set, that step's user-observation turn runs and waits for a real answer even though `mode` reads `"autopilot"` — it is not an approval gate, and the rule above does not override it. A cycle that was autopilot from the start has no `handoff_at`, so the step stays skipped there. `dev:reflect` Step 6's skill-update gate is **not** a second carve-out: it is standard-mode-only in every case, so it does not run on a handed-off cycle — what the user raised at Step 4 is captured by Step 6's unconditional carrying-cost write instead. This is the one place a `/dev` run in autopilot mode pauses for a human without stopping.

**No browser, no visual companion.** At every point where standard mode would open the visual companion browser, substitute a self-review instead:
- Re-read the accumulated inputs for that decision point
- Check for contradictions or ambiguities
- Make a decision, record it in the artifact with "Design decision:" prefix
- Continue

**Spec questioning is capped.** Ask questions one at a time up to `spec_max_questions` (from config.json, default 10). After the cap:
- If Ready (85%) is not reached AND confidence hasn't increased in the last 2 questions → auto-fill remaining unscored dimensions via inference
- Record each auto-filled dimension in `confidence.auto_filled[]` with the inferred value
- If confidence is still below High (65%) after auto-fill → STOP: "Confidence too low to proceed without human input. Current score: XX%. Please clarify: [top 2 unscored dimensions]."

Auto-fill does not satisfy `dev:spec` Step 7's grounding gate — per Step 8, confidence cannot cross the proceed threshold while a load-bearing as-is claim is unverified, regardless of the weighted score. An unverified claim surfaces here through the existing "confidence too low even after auto-fill" STOP.

**Shape alternatives: auto-select.** Present 2-3 alternatives internally, select the recommended one, note the selection and reasoning in design.md under "Design decision."

**Worktrees are automatic.** Every cycle is isolated in its own worktree by `dev:spec` Step 6 —
there is no offer to accept. Autopilot inherits this with no special handling; any git it runs uses
`git -C "$WORKDIR"` per the working-directory resolution at the top of this skill.

**Backtrack is silent.** When a later stage discovers an earlier artifact gap:
1. Fix the earlier artifact
2. Commit the fix with message: `autopilot: backtrack — update <spec|plan> for <reason>`
3. Update state.json accordingly — and when the backtracked artifact is **spec.md**, increment
   `metrics.spec_revisions` and re-stamp `metrics.stage_timestamps.spec_end`, exactly as
   `dev:spec` Step 13's gate does in standard mode. Autopilot has no gate, so this is the only
   path that records spec churn: without it `spec_revisions` is structurally always 0 in
   autopilot, and `dev:reflect`'s primary signal reads clean on every autopilot cycle no matter
   how much the spec actually churned.
4. Continue — do not pause

**Debt surfacing: print, never ask.** `dev:spec` Step 7's fourth pass cross-checks open tech debt against the grounding inventory and, in standard mode, asks whether to fold matches into scope. In autopilot it **prints its matches into the run log and folds nothing in** — scope changes need a human. Nothing is written to `## To Close`. This is not a stop condition; the run continues normally. (The debt *writes* in `dev:build`, `dev:validate`, `dev:reflect`, and `dev:done` are unconditional and self-applied — they run identically here. Only the fold-in question is suppressed.)

**Validate: extended auto-fix.** After the loop limit, attempt one additional auto-fix pass. If P1/P2 remain → STOP: surface the issues and require human input.

**Spec challenger: bounded revision loop.** `dev:spec` Step 12a's blockers drive an auto-revision loop capped at `challenge.loops_max` (micro 1 / standard 3 / deep 5), incrementing `challenge.loops_run` per iteration and `challenge.applied` by the fixes each iteration lands. Concerns are counted in `challenge.concerns` and passed through — never revised, and never a reason to loop. If blockers remain after the cap → STOP: surface them and require human input. **Scope blockers bypass the loop entirely and STOP immediately.** A right-sizing blocker is not text-fixable — a cycle cannot be split by editing prose. The loop handles only clarity, consistency, and grounding.

**Plan challenger: bounded revision loop.** `dev:plan` Step 7a's blockers drive an auto-revision loop capped at `challenge_plan.loops_max` (standard 3 / deep 5 — micro never reaches Plan), re-dispatching on the revised `plan.md` each iteration, incrementing `challenge_plan.loops_run` per iteration and `challenge_plan.applied` by the fixes each iteration lands. Concerns are counted in `challenge_plan.concerns` and passed through — never revised, and never a reason to loop. If blockers remain after the cap → STOP: surface them and require human input. **There is no scope-blocker bypass class** — unlike the spec challenger, all three plan lenses (spec-coverage, sequencing, interface-consistency) are text-fixable, so the single stop path is the only halt. This mirrors `dev:plan` Step 7a's matching rule.

## Step 3: Stage Execution

Execute stages in sequence for the applicable tier:

**Tier detection:** same as dev:spec (see stage skill). The autopilot detects tier from the initial request, or reads `tier` from `state.json` when resuming.

**Micro tier:** Spec → Build → Validate → PR → Done
**Standard/Deep + no-ui:** Spec → Plan → Build → Validate → PR → Done
**Standard/Deep + UI:** Spec → Shape → Plan → Build → Validate → PR → Done

After each stage:

```
[Stage] complete → [brief one-line summary of what was produced]
Proceeding to [Next Stage]...
```

This gives visibility without gates.

## Step 4: Report on Completion

When Done completes (or when autopilot stops on a blocker):

```
/dev autopilot complete: <feature-name>

Stages run:
  Spec ✓   [confidence: XX%]
  Shape ✓  [or "Shape skipped (no-ui)"]
  Plan ✓
  Build ✓
  Validate ✓ [N loops]
  PR ✓       [PR URL]
  Done ✓

Retrospective appended to docs/decisions/YYYY-MM-DD-<feature>.md
```

If stopped on a blocker, show the blocker and what's needed to continue.

## Invocation

- `/dev:autopilot` — start or resume in autopilot mode
- `/dev:autopilot no-ui` — autopilot, skip Shape
- `/dev:autopilot docs/dev/<feature>/<artifact>.md` — resume a gated cycle in autopilot from the named artifact, deriving the feature from the path
- The main `/dev` skill redirects `/dev auto` to this skill
