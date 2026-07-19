# Product-Plan Worktree-Safe Commit
*Branch: fix/product-plan-worktree-safe · Confidence: 90% — Ready · 2026-07-18*
*Cycle type: feature · Tier: micro*

## Intent

Close the one gap left open by PR #28 (worktree isolation), tracked as issue #29.
`dev:spec` still commits the **product plan** to `main` (top-level) or the parent branch
(nested) with bare `git add`/`git commit` from the primary tree, *before* the cycle worktree
exists. Two failures under the worktree model:

1. **Concurrency:** committing to `main` from the primary tree assumes the primary is on
   `main` — a concurrent session may have moved it, the exact assumption #28 removed.
2. **Base correctness:** the cycle worktree is created from `origin/main`. A product-plan
   commit that only reached *local* `main` is invisible to the new worktree.

The rest of `/dev` is now concurrency-safe; this brings the product-plan commit in line.

## Scope

`plugins/dev/skills/spec/SKILL.md` only. Replace the two bare product-plan commit sites —
Step 2 (product-scale path, item 6) and Step 4 (decomposition path) — with a single shared
procedure that lands the product plan on `origin/$INTEGRATION` via an **ephemeral detached
worktree**, before the cycle worktree is created in Step 6.

`$INTEGRATION` = `main` for a top-level plan, the parent feature's branch for a nested plan
(same definition `dev:done` uses).

## Out of Scope

- Any other skill (`dev:done` already uses this pattern; nothing else commits pre-worktree).
- The `worktree_root` config key being unused, and `dev:reflect`-standalone-post-done — the
  other two known minors from #28; separate concerns.
- Changing *what* the product plan contains or *when* product-scale is detected — only *how*
  the commit reaches the integration branch.

## Success Criteria

- Starting a product-scale cycle **while the primary tree is on an unrelated branch** lands
  `product-plan.md` on `origin/main`, and the subsequently-created cycle worktree includes it.
- No product-plan commit is ever made from, and no `product-plan.md` is ever written into,
  the primary working tree.
- The append-to-existing-plan case still works (the ephemeral worktree starts from
  `origin/$INTEGRATION`, which already has any existing plan).
- Two concurrent `dev:spec` runs both landing product plans on `main` don't clobber each
  other (rebase-on-reject, as in `dev:done`).
- Nested cycles target the parent branch, consistent with the existing nested handling.

## Happy Path

1. `dev:spec` detects product-scale (Step 2) or multi-cycle decomposition (Step 4).
2. It writes/updates `product-plan.md` inside an **ephemeral detached worktree** at
   `origin/$INTEGRATION`, commits, and pushes via `HEAD:$INTEGRATION` (rebase-on-reject).
3. It removes the ephemeral worktree.
4. Step 6 runs `git -C "$PRIMARY" fetch origin` then creates the cycle worktree from
   `origin/main` — which now includes the just-pushed product plan.

## Edge Cases

- **Concurrent push race:** `HEAD:$INTEGRATION` push rejects → `fetch` + `rebase
  origin/$INTEGRATION` + re-push (identical to `dev:done`'s `push_integration`).
- **Nested cycle:** `$INTEGRATION` = parent branch; the ephemeral worktree detaches at
  `origin/<parent-branch>` and pushes there. (If the parent branch isn't yet on origin, that
  is the parent cycle's responsibility — noted, not solved here.)
- **Append to existing plan:** the ephemeral worktree already contains the current
  `product-plan.md` from `origin/$INTEGRATION`; append + commit there.
- **Push fails for reasons other than non-fast-forward** (auth, network): STOP and report,
  rather than leaving a half-created cycle — the ephemeral worktree is still removed.

## Dependencies

- Issue #29; builds directly on PR #28's `dev:done` detached-HEAD + `HEAD:<integration>`
  refspec pattern (`plugins/dev/skills/done/SKILL.md` Step 2/3). This fix reuses that shape.

## UI Needed

No — Markdown skill-content change.

## Implementation Note

**Files to touch:** `plugins/dev/skills/spec/SKILL.md` (Step 2 item 6; Step 4 commit paragraph).

**Approach:** Introduce one shared procedure (written once, referenced from both sites) that
replaces the bare `git add`/`git commit`:

```bash
# Land product-plan.md on origin/$INTEGRATION without depending on the primary tree's branch.
PRIMARY=$(dirname "$(git rev-parse --git-common-dir)")
git -C "$PRIMARY" fetch origin
TMP="$PRIMARY/.dev-worktrees/_planroot-<feature-name>"
git -C "$PRIMARY" worktree add --detach "$TMP" "origin/$INTEGRATION"
# write or append the product plan inside the ephemeral worktree:
#   $TMP/docs/dev/product-plan.md   (top-level)  or  $TMP/docs/dev/<parent>/product-plan.md (nested)
git -C "$TMP" add <product-plan-path>
git -C "$TMP" commit -m "docs: record product plan for <product-name>"
git -C "$TMP" push origin "HEAD:$INTEGRATION" || {
  git -C "$TMP" fetch origin && git -C "$TMP" rebase "origin/$INTEGRATION" && git -C "$TMP" push origin "HEAD:$INTEGRATION"
}
git -C "$PRIMARY" worktree remove --force "$TMP"
git -C "$PRIMARY" worktree prune
```

Key points for the edit:
- The `product-plan.md` content is written **into `$TMP`**, never the primary tree.
- `$INTEGRATION` is defined the same way as in `dev:done` (main vs. parent branch); state
  the definition where the procedure is introduced and reference it from both call sites
  (avoid duplicating the whole block twice — write it once, say "run the product-plan push
  procedure above" at the second site).
- Keep Step 6 unchanged: its existing `git -C "$PRIMARY" fetch origin` before `worktree add
  … origin/main` already picks up the pushed plan.
- Update the surrounding prose that currently justifies committing "to `main` … not a
  feature branch yet" so it explains the ephemeral-worktree push instead of a bare commit.

---
*Auto-filled dimensions: none (audience + technical constraints known from CLAUDE.md; happy path, edge cases, success criteria, and mechanism confirmed with the user)*
