# Product-Plan Worktree-Safe Commit — Decision Log
*2026-07-18 · Branch: fix/product-plan-worktree-safe · PR #30*

## What was built
`dev:spec` now lands the product plan on `origin/$INTEGRATION` via an ephemeral detached worktree instead of a bare `git add`/`commit` from the primary tree — closing the last worktree-isolation gap left by PR #28 (issue #29).

## Key decisions
- **Reuse `dev:done`'s push pattern rather than invent a new one** → the ephemeral-worktree + `push origin HEAD:$INTEGRATION || { fetch; rebase; push }` shape is identical to `done/SKILL.md`'s `push_integration`, satisfying the spec's "identical to dev:done" requirement and keeping one concurrency-safe idiom across the workflow.
- **Write the plan into the ephemeral `$TMP` worktree, never the primary tree** → guarantees no `product-plan.md` is ever written into, or committed from, the primary working tree, so a concurrent session's checkout state can't corrupt the commit.
- **Detach the ephemeral worktree at `origin/$INTEGRATION`** → the append-to-existing-plan case works for free (the ephemeral tree already carries the current plan) and the base is always the true remote tip the cycle worktree will later be created from.
- **Write the shared procedure once, reference it from both call sites** (Step 2 item 6 and Step 4) → avoids duplicating the whole block twice in the skill.
- **Keep Step 6 unchanged** → its existing `git -C "$PRIMARY" fetch origin` before `worktree add … origin/main` already picks up the just-pushed plan for the top-level path.

## Validation notes
- 1 loop run (tier: micro) — code + security review against `80c7e46..b78ff71`, scoped to `plugins/dev/skills/spec/SKILL.md`.
- No P1/P2 found; no fix commit required.
- P3 accepted as-is: **nested product-plan visibility** — the nested path pushes to `origin/<parent-branch>`, but Step 6 resets the cycle worktree to the *local* parent ref, so a nested plan may not appear in the nested worktree. Pre-existing Step 6 behavior; the spec's nested criterion only requires the push to *target* the parent branch (met), and the Implementation Note directs keeping Step 6 unchanged. A follow-up could switch line 146 to `reset --hard origin/<parent-branch>` if nested-worktree visibility is later brought in scope.
- Nit surfaced (not fixed): Step 2's `TMP` path uses `<feature-name>` before the feature is selected (item 7); the product name would be the more accurate uniqueness token there.
- Security review: clean — quoted git plumbing inside a Markdown skill file, no secrets or injection surface.

## Artifacts (archived)
Spec and validation committed at: dd3d9dcef1e4365225ba421164ce56363783cd0b on branch fix/product-plan-worktree-safe. (Shape and Plan were skipped — micro-tier feature.)
