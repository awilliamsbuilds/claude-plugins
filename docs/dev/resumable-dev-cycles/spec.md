# Resumable Dev Cycles

*Branch: feature/resumable-dev-cycles · Confidence: 80% — High · 2026-07-03*
*Cycle type: feature · Tier: deep*

## Intent

`/dev` cycles currently assume an uninterrupted conversation from Spec through Done. In practice, sessions get `/clear`ed — to save tokens, to start fresh, or just because time passes between stages. Today, resuming after a clear already works at the level `dev:dev`'s Step 3 provides (it scans `docs/dev/*/state.json` and offers to resume), but two real gaps remain, both surfaced by this very session:

1. **No explicit exit protocol.** A stage that completes doesn't tell the user *how* to safely clear and *exactly* what to run next — the user has to already know `/dev` exists and remember to run it.
2. **No cross-cycle memory.** When a single request turns out to cover multiple independent `/dev` cycles (as this session's original three-part request did), that decomposition lives only in conversation memory. `dev:spec`'s existing product-plan mechanism (Step 2) only triggers on obviously "product-scale" requests — it does not trigger when the multi-cycle nature only becomes clear via `Step 4`'s Scope Check ("this covers three independent things"), which is exactly what happened at the start of this session. Nothing was ever written down; if this conversation had been cleared after cycle 1, task 3 would have been lost.

This cycle closes both gaps, and — per research done during this Spec stage — ties them together: the harness's native `EnterWorktree`/`ExitWorktree` tools and 2026 community practice both point to worktree isolation being valuable specifically for cycles that are part of a multi-cycle plan (where the working directory may be touched by other things during the gap between cycles), not for quick standalone sequential work.

## Scope

1. **Per-stage exit protocol** — for every standard-mode gated stage (`dev:spec`, `dev:shape`, `dev:plan`, `dev:build`, `dev:validate`, `dev:pr`), after the artifact is committed, print:
   - Confirmation the artifact is saved and committed (already happens today)
   - The exact resume command for the next stage (already happens today, informally)
   - An explicit instruction that it's safe to run `/clear` now, and the exact command to run afterward to resume (`/dev` or the specific `/dev:<stage>`), including which branch/worktree to be in if not the current directory
   - **Not applied to `dev:autopilot`** — it runs end-to-end without stopping, so there's no natural moment for this messaging.

2. **Master-plan trigger extended beyond Scale Detection** — `dev:spec` Step 4 (Scope Check + YAGNI Gate), when it identifies that a single request covers multiple independent sub-features, now also creates/updates `docs/dev/product-plan.md` (the same artifact Step 2's product-scale detection already produces) — not just asking "which should we start with?" and discarding the rest. This is the mechanism that would have captured this session's original three-part request.

3. **Worktree isolation, conditional on master-plan membership** — `dev:spec` Step 6 (Create Feature Branch): if the cycle being started is a milestone/item in `docs/dev/product-plan.md`, offer `EnterWorktree` isolation (consent-based, matching `superpowers:using-git-worktrees`'s detection-first, native-tool-preferred approach) before falling back to today's plain `git checkout -b` behavior. Standalone cycles (no product plan involved) keep today's plain-branch behavior unchanged.

4. **`dev:done` references the master plan explicitly on completion** — Step 8's existing "if product-plan.md exists, offer the next cycle" behavior is enhanced to explicitly state: which milestone/item was just completed, what remains, the exact `/clear` + resume instruction, and the exact command to start the next cycle (mirroring item 1's exit protocol, but for cross-cycle handoff instead of cross-stage).

## Out of Scope

- Rebuilding `dev:autopilot`'s behavior — it's explicitly excluded from the per-stage exit protocol (item 1) since it has no natural pause points.
- Retroactively adding worktree isolation or master-plan tracking to already-completed past cycles (the three cycles this session already ran).
- Adopting GitButler-style virtual branches — out of scope; this repo's toolchain is plain git + the harness's native worktree tool.
- Automatic worktree cleanup/garbage-collection for abandoned cycles — `ExitWorktree`'s existing keep/remove choice is sufficient; no new automation added.
- Changing how `dev:dev`'s Step 3 in-progress-session detection works — it already functions correctly today; this cycle adds messaging and master-plan awareness around it, not a rewrite of the detection logic itself.

## Success Criteria

- Every standard-mode gated stage, after committing its artifact, prints an explicit "safe to `/clear` now, run `<exact command>` to resume" message.
- `dev:spec` Step 4, when it detects multiple independent sub-features in a single request, writes/updates `docs/dev/product-plan.md` — verified by re-running this exact scenario (a request that decomposes into 3 things via conversation, not an obviously product-scale opening ask) and confirming a product-plan.md exists afterward.
- Starting a cycle that's part of a product plan offers `EnterWorktree`; starting a standalone cycle does not.
- `dev:done` Step 8, when a product plan exists, explicitly names the completed item, the remaining items, and gives the exact next command — not just a general "start next cycle?" prompt.
- If `EnterWorktree` is unavailable or declined, the cycle proceeds with today's plain-branch behavior — no hard failure.

## Happy Path

**Single standalone cycle (most common case, unchanged from today):**
1. User runs `/dev`, request is feature-scale, single deliverable.
2. Plain branch created (`git checkout -b`), as today.
3. Each stage completes, prints exit-protocol instructions (item 1).
4. User can `/clear` between any two stages and resume cleanly by running the printed command.

**Multi-cycle master-plan case (the gap this closes):**
1. User makes a request that turns out, through conversation, to cover 3 independent things.
2. `dev:spec` Step 4 flags this and — new behavior — writes `docs/dev/product-plan.md` recording all 3 items, not just the one being started.
3. User picks item 1; `dev:spec` Step 6 sees this is a master-plan item and offers `EnterWorktree` isolation.
4. Item 1's cycle runs to completion; `dev:done` Step 8 says: "Completed item 1/3. Remaining: item 2, item 3. Start item 2? Run `/dev` and I'll pick it up from the plan" (or similar).
5. Time passes, possibly a `/clear`, possibly other unrelated work happens in the main directory. User (or a fresh Claude session) runs `/dev` — it reads `product-plan.md`, sees 1/3 complete, and offers item 2 without needing any of this conversation's memory.

## Edge Cases

| Case | Handling |
|------|----------|
| `EnterWorktree` unavailable in the current harness | Fall back to today's plain `git checkout -b`, same as `superpowers:using-git-worktrees`'s own fallback chain. |
| User declines the worktree offer | Proceed with plain branch — consent-based, never forced. |
| A cycle is jumped to directly (`/dev:build` without the orchestrator) | Exit-protocol messaging still applies per-stage regardless of entry point, same principle as the supersede notes from the earlier `remove-superpowers-convention` cycle. |
| `docs/dev/product-plan.md` already exists when Step 4 flags a new multi-item decomposition | Append the new items rather than overwriting existing milestones. |
| A worktree cycle is abandoned mid-way | No new automation — existing `ExitWorktree` keep/remove choice governs cleanup; not this cycle's problem to solve further. |

## UI Needed
No.

## Technical Constraints

- Depends on the harness providing `EnterWorktree`/`ExitWorktree` as native tools (confirmed present in this session) — must degrade gracefully where they're absent.
- Per this Spec stage's own research: working directory and git branch state are filesystem state, unaffected by `/clear` — the exit-protocol instructions rely on this being true; if a harness resets cwd on `/clear`, the resume instructions need to say so explicitly (flagged as an assumption to validate, not proven with certainty in this session).
- Must not change `dev:dev` Step 3's existing in-progress-session detection logic — only add messaging/master-plan awareness around it.

## Dependencies

None on the other two `/dev` plugin cycles from this session (`remove-superpowers-convention`, `dev-start-skill`) — both are fully merged and independent of this one.

## Audience
Personal, single-user plugin repo (Adam only) — `awilliamsbuilds/claude-plugins`.

---
*Auto-filled dimensions: worktree-trigger and exit-protocol-scope design decisions were presented as recommended options via AskUserQuestion; no response was received within the wait window, so both proceeded with the recommended (and research-grounded) choice. Flagged explicitly here — confirm or correct at the review gate below. All other dimensions (success criteria, happy path, edge cases, dependencies) filled directly from the Spec-stage research and the user's own detailed framing of the problem, not blind inference.*
