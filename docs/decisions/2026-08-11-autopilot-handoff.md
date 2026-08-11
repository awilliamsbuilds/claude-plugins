# Autopilot Handoff at Pre-Execution Gates — Decision Log
*2026-08-11 · Branch: feature/autopilot-handoff · PR #68*

## What was built

A printed autopilot offer at the `/dev` pre-execution gates — the Spec gate when its next stage is Plan or Build, and the Shape gate — letting a user who wanted gates during definition hand the mechanical remainder of the cycle to autopilot across a `/clear` boundary, plus the `dev:autopilot` argument form, `WORKDIR` resolution, and `tier`/`stage` read that make that printed command actually runnable.

## Key decisions

- **The offer is printed, not asked** → No yes/no prompt, no session-ending path, no state write at either gate. Existing gate behaviour is untouched *by construction* rather than by a guarded branch, which is what kept the feature from needing a second code path in any of the eleven stage skills or the orchestrator.
- **The handoff is a `/clear` boundary, not an in-session mode flip** → By the time Shape is approved the session carries the whole spec/design conversation, and every stage after it reads from committed artifacts. Flipping `mode` in-session would have squandered the context saving that is half the point; the offer's payload is therefore a runnable command.
- **The marker records an observed event, not a stated intention** → `handoff_at` has exactly one write site, `dev:autopilot` Step 1, at the moment it flips a `"standard"` cycle to `"autopilot"`. Tagged `(writes: autopilot-only)` per the mode-symmetry contract. Because the gates write nothing there is no standard-side writer to keep symmetric, and the marker cannot go stale against a mode that never changed.
- **`handoff_at` records the stage autopilot *resumed at*, not the gate stage** → Gate approval advances `stage` before the user pastes the command, so the value is `plan` (or `build` on micro), never `spec`/`shape` on the offered path. Its domain is deliberately open — any stage name — so a manual `/dev:autopilot` at Validate still records accurately.
- **Absence is the value** → No `null`, no `false`, no empty string. Both readers treat an absent marker as today's behaviour, which makes every cycle predating the feature read correctly and keeps existing decision logs byte-comparable.
- **`dev:autopilot` reads `tier`/`stage` from the resolved `state.json`** → Step 3 previously detected tier "from the initial request," and a pasted resume command carries no request to infer from. Without this a micro cycle could not select its stage sequence.
- **Folded in `debt-primary-path-relative-in-dev-headers`** → Eleven skills derived `PRIMARY` relative, yielding `.` from the repo root. Directly load-bearing here, since the whole feature is a command pasted into a cleared session running from the primary checkout. Adopted the failure-checked `cd … && pwd` form already proven in `dev:migrate-tracker`, with the rationale paragraph stated at exactly one site (`dev:plan`) — eleven copies drift.
- **Declined to extract a shared canonical WORKDIR block** → Two files cite one that does not exist. Real gap, but its own cycle; this cycle repointed the dangling citations and inlined correct resolution at its own site.

## Design choices

Shape was skipped — `## UI Needed: No`. All surfaces are terminal text inside skill procedures, so gate copy was drafted directly in the plan's task steps rather than in a design document.

## Validation notes

- 9 loops run (tier: standard; limit 3, extended by the user at the Step 4a gate with an open P2). Both Step 2 reviews and all nine fix-diff re-reviews ran as fresh subagents denied the session's conversation history.
- **P2 — cold-start misclassification (loop 1).** A bare `/dev:autopilot` on a new feature would have let `dev:spec` Step 6 write `"mode": "standard"`, then read it back and record a handoff on a cycle that was autopilot end-to-end. Anchored the branch decision to the `state.json` that existed when the invocation began. Without this, Success Criterion 8 failed outright — the cycle's most valuable fix.
- **P2 — handed-off cycles pause at `dev:reflect` Step 4 (loop 1).** Autopilot's blanket "No approval gates" would have suppressed it, failing Success Criterion 6 at runtime. Added the carve-out to autopilot Step 2.
- **P2 — stale `PRIMARY` prose in `dev:reflect` (loop 1).** Asserted `PRIMARY` is "absolute only sometimes"; invalidated by Task 1 and named in the folded-in debt item's own *Done looks like*.
- **P2 — loop 1's own fix over-corrected past spec §Scope 4 (loop 2)** by extending `reflect` Step 6 to handed-off cycles, widening the feature to a third marker reader. Reverted rather than expanding scope during Validate.
- **P2 — the multi-hit escape hatch pointed at bare `/dev` (loop 3),** whose *Restart* option force-removes a worktree, in exactly the state the STOP fires. Retargeted to `/dev spec`.
- Loops 3–9 were self-correction confined to one paragraph of `dev:autopilot` Step 1, each closing the previous loop's defect: the `no-ui` exemption added in loop 4 was removed in loop 5 as over-reaching, carried into the printed message in loop 6, and scoped to Standard/Deep in loop 8 once a Micro cycle's `skipped: ["shape","plan"]` was shown to match it wrongly. Loop 7 resolved a `<feature>` placeholder collision that would have handed the user a pre-picked cycle — the very thing the STOP exists to prevent.
- **Accepted as-is (3 P3, 3 nits, all buffered to `docs/backlog/`):** the unchecked second line of the `PRIMARY` snippet across 13 sites (not a regression — the pre-cycle form was equally unchecked); `dev:dev` Step 5a having no new-session path for the `spec` stage jump that this cycle's multi-hit STOP now points at; three reference lines still stating flatly that `no-ui` skips Shape, contradicting the spec's `## UI Needed` authority that `dev:autopilot` was brought into line with; and the unconstrained `<artifact>` component of the shared artifact-path validation rule.

## Artifacts (archived)

Spec, plan, and validation committed at: `7506514` on branch `feature/autopilot-handoff`
