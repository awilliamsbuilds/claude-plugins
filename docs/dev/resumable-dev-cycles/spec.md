# Resumable Dev Cycles

*Branch: feature/resumable-dev-cycles · Confidence: 95% — Ready · 2026-07-03*
*Cycle type: feature · Tier: deep*

## Intent

`/dev` cycles currently assume an uninterrupted conversation from Spec through Done. In practice, sessions get `/clear`ed — to save tokens, to start fresh, or just because time passes between stages. Today, resuming after a clear already works at the level `dev:dev`'s Step 3 provides (it scans `docs/dev/*/state.json` and offers to resume), but two real gaps remain, both surfaced by this very session:

1. **No explicit exit protocol.** A stage that completes doesn't tell the user *how* to safely clear and *exactly* what to run next — the user has to already know `/dev` exists and remember to run it.
2. **No cross-cycle memory.** When a single request turns out to cover multiple independent `/dev` cycles (as this session's original three-part request did), that decomposition lives only in conversation memory. `dev:spec`'s existing product-plan mechanism (Step 2) only triggers on obviously "product-scale" requests — it does not trigger when the multi-cycle nature only becomes clear via `Step 4`'s Scope Check ("this covers three independent things"), which is exactly what happened at the start of this session. Nothing was ever written down; if this conversation had been cleared after cycle 1, task 3 would have been lost.

This cycle closes both gaps, and — per research done during this Spec stage — ties them together: the harness's native `EnterWorktree`/`ExitWorktree` tools and 2026 community practice both point to worktree isolation being valuable specifically for cycles that are part of a multi-cycle plan (where the working directory may be touched by other things during the gap between cycles), not for quick standalone sequential work.

## Scope

1. **Per-stage exit protocol** — for every standard-mode gated stage (`dev:spec`, `dev:shape`, `dev:plan`, `dev:build`, `dev:validate`, `dev:pr`), after the artifact is committed, print:
   - Confirmation the artifact is saved and committed (already happens today)
   - **The exact resume command, self-contained with the prior stage's artifact path as an argument** — e.g. `/dev:plan docs/dev/resumable-dev-cycles/spec.md`, not a bare `/dev:plan`. This closes a real gap discovered while speccing this: today, `dev:plan`/`dev:build`/etc.'s Step 1 says "Read `docs/dev/<feature>/state.json`" but `<feature>` is never actually resolved anywhere — it silently depends on conversation memory (broken by `/clear`) or an implicit single-session assumption (breaks once nested/parallel worktrees exist). Every `dev:<stage>` skill's Step 1 is updated to accept an optional artifact-path argument and derive `<feature>` from it; if no argument is given, fall back to today's implicit behavior (scan `docs/dev/*/state.json`) for interactive same-session use.
   - If the cycle is in a worktree, the exact worktree path, so the instruction is correct even from a different terminal or a fresh session that isn't already there.
   - An explicit instruction that it's safe to run `/clear` now. **`/clear` must never trigger `ExitWorktree`** — nothing in this exit protocol calls it; the worktree (if any) persists across `/clear` by design, matching `ExitWorktree`'s own documented behavior ("do NOT call this proactively — only when the user asks"). This was an open assumption earlier in this spec; it's now a stated design requirement, not a guess.
   - **Not applied to `dev:autopilot`** — it runs end-to-end without stopping, so there's no natural moment for this messaging.

2. **Master-plan trigger extended beyond Scale Detection, and made recursive** — `dev:spec` Step 4 (Scope Check + YAGNI Gate), when it identifies that a single request covers multiple independent sub-features, now also creates/updates a product plan — not just asking "which should we start with?" and discarding the rest. This is the mechanism that would have captured this session's original three-part request. Critically, this isn't limited to the top level: **product plans nest**. If a cycle that is itself an item inside a product plan turns out, during its own Spec stage, to be product-scale in its own right (Step 2 or Step 4 fires again, one level down), it gets its own nested product plan at `docs/dev/<feature>/product-plan.md`, scoped to that feature's own sub-milestones — distinct from the top-level `docs/dev/product-plan.md`. The mechanism is identical at every level; it just recurses.

3. **Worktree isolation, conditional on product-plan membership at any depth** — `dev:spec` Step 6 (Create Feature Branch): if the cycle being started is an item in *any* product plan — the top-level one, or a nested one belonging to an enclosing feature — offer `EnterWorktree` isolation (consent-based, matching `superpowers:using-git-worktrees`'s detection-first, native-tool-preferred approach) before falling back to today's plain `git checkout -b` behavior. Standalone cycles (no product plan involved, at any level) keep today's plain-branch behavior unchanged. Worked example: 3 top-level tasks → 3 worktrees, each branched from `origin/main`. If task 3 alone turns out to need 4 sub-milestones → those 4 sub-milestones each also get their own worktree, but branched from **task 3's own branch HEAD**, not `origin/main` — each sub-milestone builds on the previous one's committed work, mirroring how tasks within a single `plan.md` already build on each other today, just promoted to full nested `/dev` cycles. Correspondingly, a nested cycle's `dev:pr` Step 4 targets `--base <parent-branch>` instead of `--base main`; only the outermost parent cycle's PR ultimately targets `main`.

4. **`dev:done` references the master plan explicitly on completion** — Step 8's existing "if product-plan.md exists, offer the next cycle" behavior is enhanced to explicitly state: which milestone/item was just completed, what remains, the exact `/clear` + resume instruction, and the exact command to start the next cycle (mirroring item 1's exit protocol, but for cross-cycle handoff instead of cross-stage).

## Out of Scope

- Rebuilding `dev:autopilot`'s behavior — it's explicitly excluded from the per-stage exit protocol (item 1) since it has no natural pause points.
- Retroactively adding worktree isolation or master-plan tracking to already-completed past cycles (the three cycles this session already ran).
- Adopting GitButler-style virtual branches — out of scope; this repo's toolchain is plain git + the harness's native worktree tool.
- Automatic worktree cleanup/garbage-collection for abandoned cycles — `ExitWorktree`'s existing keep/remove choice is sufficient; no new automation added.
- Changing how `dev:dev`'s Step 3 in-progress-session detection works — it already functions correctly today; this cycle adds messaging and master-plan awareness around it, not a rewrite of the detection logic itself.

## Success Criteria

- Every standard-mode gated stage, after committing its artifact, prints an explicit "safe to `/clear` now, run `<exact command with artifact-path argument>` to resume" message — e.g. `/dev:plan docs/dev/<feature>/spec.md` — plus the worktree path if applicable.
- Every `dev:<stage>` skill's Step 1 accepts an optional artifact-path argument and resolves `<feature>` from it, rather than leaving `<feature>` as an unresolved placeholder as it is today.
- Nothing in the exit protocol calls `ExitWorktree` — verified by grep across the updated skill files after Build.
- `dev:spec` Step 4, when it detects multiple independent sub-features in a single request, writes/updates `docs/dev/product-plan.md` — verified by re-running this exact scenario (a request that decomposes into 3 things via conversation, not an obviously product-scale opening ask) and confirming a product-plan.md exists afterward.
- Starting a cycle that's part of a product plan offers `EnterWorktree`; starting a standalone cycle does not — and this holds recursively: a cycle whose own Spec stage discovers it needs sub-milestones creates a nested product plan, and each sub-milestone is offered a worktree branched from the parent's branch HEAD, not `origin/main`.
- `dev:done` Step 8, when a product plan exists, explicitly names the completed item, the remaining items, and gives the exact next command — not just a general "start next cycle?" prompt.
- If `EnterWorktree` is unavailable or declined, the cycle proceeds with today's plain-branch behavior — no hard failure.

## Happy Path

**Single standalone cycle (most common case, unchanged from today):**
1. User runs `/dev`, request is feature-scale, single deliverable.
2. Plain branch created (`git checkout -b`), as today.
3. Each stage completes, prints exit-protocol instructions, e.g.: "Spec committed to `docs/dev/my-feature/spec.md`. Safe to `/clear` now — resume with `/dev:plan docs/dev/my-feature/spec.md`."
4. User runs `/clear`, then pastes the exact printed command. `dev:plan`'s Step 1 resolves `<feature>` = `my-feature` from the argument — no dependence on the cleared conversation's memory.

**Multi-cycle master-plan case (the gap this closes):**
1. User makes a request that turns out, through conversation, to cover 3 independent things.
2. `dev:spec` Step 4 flags this and — new behavior — writes `docs/dev/product-plan.md` recording all 3 items, not just the one being started.
3. User picks item 1; `dev:spec` Step 6 sees this is a master-plan item and offers `EnterWorktree` isolation.
4. Item 1's cycle runs to completion; `dev:done` Step 8 says: "Completed item 1/3. Remaining: item 2, item 3. Start item 2? Run `/dev` and I'll pick it up from the plan" (or similar).
5. Time passes, possibly a `/clear`, possibly other unrelated work happens in the main directory. User (or a fresh Claude session) runs `/dev` — it reads `product-plan.md`, sees 1/3 complete, and offers item 2 without needing any of this conversation's memory.

**Nested master-plan case (recursive — this cycle is itself an example):**
1. Item 3 from the top-level plan turns out, during its own Spec stage, to be Deep-tier and cover 4 distinct scope pieces.
2. `dev:spec` Step 2 or Step 4 fires again, one level down, and writes `docs/dev/resumable-dev-cycles/product-plan.md` listing the 4 sub-milestones.
3. Sub-milestone 3a gets a worktree branched from `feature/resumable-dev-cycles` (item 3's own branch), not `origin/main`.
4. Sub-milestone 3a's `dev:pr` targets `--base feature/resumable-dev-cycles`, not `--base main`. Once merged, 3b branches from the updated `feature/resumable-dev-cycles`.
5. Once all 4 sub-milestones are merged into `feature/resumable-dev-cycles`, item 3's own `dev:pr` targets `main` as usual.

## Edge Cases

| Case | Handling |
|------|----------|
| `EnterWorktree` unavailable in the current harness | Fall back to today's plain `git checkout -b`, same as `superpowers:using-git-worktrees`'s own fallback chain. |
| User declines the worktree offer | Proceed with plain branch — consent-based, never forced. |
| A cycle is jumped to directly (`/dev:build` without the orchestrator) | Exit-protocol messaging still applies per-stage regardless of entry point, same principle as the supersede notes from the earlier `remove-superpowers-convention` cycle. |
| `docs/dev/product-plan.md` already exists when Step 4 flags a new multi-item decomposition | Append the new items rather than overwriting existing milestones. |
| A worktree cycle is abandoned mid-way | No new automation — existing `ExitWorktree` keep/remove choice governs cleanup; not this cycle's problem to solve further. |
| Nesting goes deeper than 2 levels (a sub-milestone that itself needs sub-sub-milestones) | No explicit depth cap — the mechanism recurses naturally and terminates when a cycle's own Spec stage finds no further decomposition. Deeper-than-2 nesting is untested in this cycle but not architecturally blocked. |
| A nested sub-milestone's parent branch gets deleted or force-updated before the child cycle finishes | Not handled by this cycle — same class of risk as any long-lived branch depending on another; noted but not solved here. |

## UI Needed
No.

## Technical Constraints

- Depends on the harness providing `EnterWorktree`/`ExitWorktree` as native tools (confirmed present in this session) — must degrade gracefully where they're absent.
- Per this Spec stage's own research: working directory and git branch state are filesystem state, unaffected by `/clear`. Confirmed as a stated design requirement (not just an assumption): the exit protocol never calls `ExitWorktree`, matching that tool's own documented "don't call proactively" rule — so nothing in `/dev`'s own design causes a worktree exit on `/clear`. If some harness resets cwd on `/clear` independent of any tool call, that's outside this cycle's control and not something the exit-protocol messaging can fully guard against — the resume command's explicit artifact-path argument is the mitigation (Step 1 of every stage skill can re-derive its feature from the argument regardless of what directory it's re-invoked from).
- Must not change `dev:dev` Step 3's existing in-progress-session detection logic — only add messaging/master-plan awareness around it.
- Nested product plans require `dev:pr` to know its target branch is the parent feature's branch, not always `main` — Step 4 of `dev:pr` needs a way to determine "am I nested, and if so, under what branch," likely by checking whether `state.json` records a parent feature.

## Dependencies

None on the other two `/dev` plugin cycles from this session (`remove-superpowers-convention`, `dev-start-skill`) — both are fully merged and independent of this one.

## Audience
Personal, single-user plugin repo (Adam only) — `awilliamsbuilds/claude-plugins`.

---
*Auto-filled dimensions: none remaining. The two design decisions initially defaulted to their recommended option (worktree-trigger, exit-protocol-scope) were both explicitly confirmed by the user afterward — exit-protocol-scope as-is, worktree-trigger refined further into an explicit recursive/nested-product-plan design (scope items 2–3, the nested happy path, and two new edge cases) based on the user's clarification that a single large cycle can itself decompose into worktree-eligible sub-milestones.*
