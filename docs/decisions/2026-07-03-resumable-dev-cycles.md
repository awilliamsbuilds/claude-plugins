# Resumable Dev Cycles — Decision Log
*2026-07-03 · Branch: feature/resumable-dev-cycles · PR #16*

## What was built
Made `/dev` cycles resumable across `/clear` at two granularities: cross-stage (every gated stage ends with an explicit "safe to `/clear` now, resume with `<exact command>`" message carrying the prior artifact's path as an argument) and cross-cycle (multi-cycle requests get a durable, recursively-nestable product plan instead of living only in conversation memory).

## Key decisions

- **Worktree offer conditional on product-plan membership, not universal** → research during Spec (harness's native `EnterWorktree`/`ExitWorktree`, 2026 community practice, `superpowers:using-git-worktrees`) showed worktrees earn their keep for independent/parallel work, not quick sequential cycles. Standalone cycles keep plain branches (proven across this session's first two cycles); only cycles that are part of *any* product plan — top-level or nested — get offered isolation.
- **Product plans nest recursively** → the same mechanism (product-plan.md, worktree-eligibility) applies uniformly at every decomposition depth: a top-level task can itself turn out to need sub-milestones, which get their own nested product plan and their own worktrees branched from the parent's branch HEAD rather than `origin/main`. This cycle is itself a worked example — item 3 of this session's original 3-task decomposition, which the master-plan mechanism this cycle builds would itself have captured had it existed at session start.
- **`/clear` never triggers `ExitWorktree`** → stated as a design requirement, not left as an assumption: nothing in the exit protocol calls it, matching `ExitWorktree`'s own "don't call proactively" rule. Worktree cleanup is entirely deferred to the user calling it explicitly.
- **Resume commands carry the prior artifact's path as an argument** → e.g. `/dev:plan docs/dev/<feature>/spec.md`, not a bare `/dev:plan`. This closed a real pre-existing gap discovered while speccing: every `dev:<stage>` skill referenced `docs/dev/<feature>/state.json` without `<feature>` ever being resolved from anywhere concrete — it silently depended on conversation memory.
- **Exit protocol excludes `dev:autopilot`** → no natural pause points to hang the messaging on. The worktree offer's consent step also needed an autopilot-specific auto-accept rule, documented in `dev:autopilot` itself (not just `dev:spec`) after Plan self-review caught the same class of cross-file gap flagged in the `remove-superpowers-convention` cycle's own retrospective.
- **Nested PRs target the parent branch, pushed first** → `dev:pr`'s `--base` becomes the parent feature's branch (not `main`) when `state.json.parentFeature` is set, and that branch is explicitly pushed to the remote first — Validate caught that this step was missing and would have made every nested PR fail outright.

## Validation notes
- 2 loops run (tier: deep, max: 5)
- **P1 fixed**: `dev:spec` Step 4 wrote product plans but never committed them — would silently orphan the artifact under worktree isolation, defeating the feature's own purpose.
- **P1 fixed**: nested-cycle PRs would fail outright — parent branch never pushed to remote before `gh pr create --base <parent-branch>`.
- **P2 fixed**: `dev:spec` Step 2 (product-scale detection) didn't implement nesting at all, contradicting the spec's own stated design.
- **P2 fixed**: `dev:done` Step 7 would crash on cleanup for any worktree-isolated cycle (`git branch -d` fails on a branch checked out elsewhere) — deletion now guarded, deferred to `ExitWorktree`.
- **P2 fixed**: the new artifact-path argument had no input validation — added a kebab-case regex check across all 6 files that adopted the convention, matching the codebase's existing feature-naming guarantee.
- Also resolved an ambiguity the plan itself flagged (rebase vs. reset for worktree base-refs) to one concrete, reasoned command (`git reset --hard`, since a freshly-created branch has zero unique commits).
- Loop 2 was a targeted verification pass confirming all loop 1 fixes were correct and introduced no regressions. No open P1/P2/P3/Nit issues remained.

## Artifacts (archived)
Spec, plan, and validation committed at: 745bf7d35569cd2169df9d3d7726bd759e0d84b0 on branch feature/resumable-dev-cycles
