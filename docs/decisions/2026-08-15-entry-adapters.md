# Entry Adapters — Decision Log
*2026-08-15 · Branch: feature/entry-adapters · PR #81*
*Handed off to autopilot at Spec*

## What was built

One adapter seam on the `dev:fix` lane with two sources on it — `/dev:fix linear [<issue-id>]` and
`/dev:fix backlog <item>` — replacing the retired `dev:linear` and closing the gap where anything
that already stated a request had to be retyped by hand.

## Key decisions

- **One seam with two sources, not two adapters** → Two adapters of the same shape drift. The seam is
  defined once as four hook points (Resolve, Pre-lane, Post-PR, Closeout) in a shared reference both
  consumers cite. A seam shaped by a single consumer is a guess; two real consumers validate it.
- **Four hook points, not three** → The spec's original Scope table named three, but its own Happy
  Path required the Linear "in review" transition to fire at PR-open, which is neither pre-lane nor
  closeout. Caught at Plan and backtracked into the spec rather than papered over in the plan.
- **Status resolution is asked-and-cached, never inferred** → Verified against the live Linear API:
  `In Progress` and `In Review` are **both** `type: "started"`, so semantic type can distinguish
  "started" from "completed" but not "work began" from "PR opened" — exactly the pair being
  automated. The skill asks once per team, caches resolved **IDs** in `docs/dev/config.json`, and
  never matches a display name. Keyed on team ID because names are renameable and status IDs differ
  per team.
- **The backlog branch is named `fix/<item>`** → `/dev:fix merge` is a separate invocation and the
  lane persists no `state.json`, so the branch name is the only durable carrier of the item's
  identity across the two invocations. This is load-bearing, not cosmetic — and it forced a matching
  decision that a branch collision on that dispatch is a **STOP**, never the lane's usual `-2` suffix,
  because a suffix breaks the derivation and turns the closeout into a silent no-op.
- **The closeout is a marked mirror, not a reuse** → The spec required closing "via the existing close
  path." `dev:debt` Step 6 is not literally invocable from the tail (it requires a confirmation turn
  and refuses to commit), and the `debt-pending.md` buffer is flushed by `dev:done`, which the lane
  never enters. A mirror that restates the canonical in full and names **all three** divergences is
  the closest available reading; both ends carry the identical list.
- **`dev:linear`'s deletion moved three things, not one** → Besides the issue→dimension mapping, it
  owned the uppercase-tolerant cycle-slug allowlist that lets a `ENG-123` prefix survive
  normalization, and `dev:done` cited that allowlist **by name** as its shell-interpolation safety
  argument. Deleting without re-pointing would have left a live safety claim referring to a file that
  no longer exists.
- **A security finding overturned a Plan out-of-scope decision** → `dev:pr`'s double-quoted `--body`
  was explicitly deferred at Plan. Review established that this cycle is what routes external Linear
  text into it, so the deferral was expanding exposure knowingly. Fixed rather than carried.

## Validation notes

- **3 loops run** (tier: deep, limit 5). Final status clean — no open P1 or P2.
- **P1 — the backlog closeout could never run.** Its bind guard asserted variables that cannot exist
  at that point (the merge fence has deleted the branch and moved the checkout), and pointed at a
  recovery that dead-ends. SC3 would have failed on the ordinary path. → Fixed by making those
  agent-substituted literals, asserting only what has a re-runnable derivation, and re-deriving
  `RECONCILED` from observable state.
- **P2 — the closeout could archive an unrelated item.** `status: open` catches an already-closed
  item and nothing else, and `fix/` is not exclusive to the backlog dispatch. Found independently by
  both reviewers. → Fixed with a `^(debt|backlog)-…` basename allowlist; both guards documented as
  required and non-redundant.
- **P2 — `BRANCH_NAME` was consumed by five shell lines and assigned by none.** → Fixed with a
  documented re-derivation.
- **P2 — `dev:pr` command-substitution path.** → Fixed with a single-quoted heredoc and `--body-file`.
- **Two regressions were introduced by the fix loop itself and caught by its own cold re-review** — a
  temp-file path that fails in a worktree (`.git` is a file there), then one that is relative from the
  primary checkout while the fence `cd`s. Both verified empirically rather than by reasoning.
- **P3 accepted as-is:** `autopilot/SKILL.md:139` cites a line this cycle's spec edits shifted.
  Repairing it would edit `dev:autopilot`, which SC10 requires byte-identical — a success criterion
  and a correctness fix in direct conflict. The criterion won; the conflict is recorded as debt
  because it is structural and will recur.
- **Seven of eleven success criteria were not executed.** SC1, SC2, SC3, SC4, SC5, SC7, SC9 assert
  behavior, and this repo has no harness that can run a skill. They were verified by walking the
  edited procedures against the real files and by three independent cold reviewers. The four
  mechanical criteria (SC6, SC8, SC10, SC11) were run as commands; the regression suite passes at
  89 tests.

## Artifacts (archived)

Spec, plan, and validation committed at: `08cc248` on branch `feature/entry-adapters`
