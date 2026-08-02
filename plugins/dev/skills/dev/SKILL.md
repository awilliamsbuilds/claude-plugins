---
name: dev
description: "Main entry point for the /dev workflow. Standard mode: manages the 7-stage development workflow (spec → shape → plan → build → validate → PR → done) with explicit approval gates between stages. Use /dev:autopilot for no-gate mode. Use /dev:init to set up a new project. Use /dev:fix for Linear issue entry."
---

# dev — Development Workflow Orchestrator

**Announce:** "I'm using the dev skill to manage the development workflow."

## Purpose

Orchestrate the full /dev workflow in standard mode — sequential stages with explicit approval gates between each. Each stage produces one artifact; each gate is a real stop.

## Superpowers Supersession

While a `/dev` session is active (a `docs/dev/<feature>/state.json` exists for the current feature), this workflow supersedes `superpowers:brainstorming` and `superpowers:writing-plans`. Do not invoke those skills separately — each `/dev` stage already contains the equivalent capability inline.

## Step 1: Parse Arguments

Arguments can appear in any combination:

- `auto` → this is a redirect: "For autopilot mode, use /dev:autopilot. Continuing in standard mode with approval gates."
- `no-ui` → set mode to no-ui; Shape stage will be skipped
- `init` → delegate to /dev:init immediately
- `spec`, `shape`, `plan`, `build`, `validate`, `pr`, `done` → jump to that stage (see Step 5)
- No arguments → standard flow (Step 2)

## Step 2: Check Initialization

Check if `docs/dev/config.json` exists in the current project.

If absent: "No /dev config found. Running /dev:init first."
Invoke `/dev:init` inline. Wait for it to complete. Then continue to Step 3.

If present: continue to Step 3.

## Step 3: Check for In-Progress Session

Compute the primary checkout:

```bash
GIT_COMMON=$(git rev-parse --git-common-dir) || { echo "Not a git repository."; exit 1; }
PRIMARY=$(cd "$(dirname "$GIT_COMMON")" && pwd)
```

Then scan for state.json in
both locations: `$PRIMARY/.dev-worktrees/*/docs/dev/*/state.json` (active worktree cycles) and
`$PRIMARY/docs/dev/*/state.json` (legacy in-place cycles). Deduplicate by feature name.

**If one or more found:**

For each session found, read state.json and display:

```
/dev session in progress: <feature-name>
<stage-status-line>
[If worktreePath is set: Worktree: <worktreePath>]
[If parentFeature is set: (nested under <parentFeature>)]
Resume from <current-stage>, restart, or abandon?
```

Stage status line format (completed stages show ✓, current stage shows →, pending stages show names):
```
Spec ✓  Shape ✓  Plan →  Build  Validate  PR  Done
```

If multiple sessions: list them all, ask which one to continue with.

**User choices:**
- **Resume:** proceed to the current stage (read from state.json `stage`). Resume resolves
  `WORKDIR` via the canonical block (worktree first, else primary) before proceeding to the
  stage — the user is never asked to `cd`.
- **Restart:** delete the cycle's state.json and `docs/dev/<feature>/` from the resolved WORKDIR (the worktree if `worktreePath` is set, else the primary tree). If `worktreePath` is set, run `git -C "$PRIMARY" worktree remove --force "$PRIMARY/<worktreePath>"` then `git -C "$PRIMARY" worktree prune` — which also removes the worktree's copy of `docs/dev/<feature>/`. Start over from spec.
- **Abandon:** remove this cycle entirely, then exit.
  - If `worktreePath` is set: `git -C "$PRIMARY" worktree remove --force "$PRIMARY/<worktreePath>"` then `git -C "$PRIMARY" worktree prune` — this deletes the worktree (including its `docs/dev/<feature>/` and state.json) and frees the feature branch, which was checked out only there; then delete it with `git -C "$PRIMARY" branch -D <branch>`.
  - If `worktreePath` is null (legacy in-place cycle): delete `$PRIMARY/docs/dev/<feature>/` (state.json included). The feature branch is the primary tree's current checkout, so it cannot be deleted from here — tell the user to delete it manually after switching branches, rather than switching their tree for them.

**If no in-progress session found:** proceed to Step 4.

## Step 4: Start New Session

Invoke `dev:spec` to begin the cycle.

After dev:spec completes and the user approves the spec:
- Read state.json to confirm `"spec"` is in `completed[]`
- Determine next stage from tier and the spec's UI decision (the spec is authoritative — read `## UI Needed`, which spec Step 12 also records into `skipped[]`):
  - Micro tier: jump to Build (Shape and Plan are in `skipped[]`)
  - Standard/Deep, spec says `UI Needed: Yes`: go to Shape
  - Standard/Deep, spec says `UI Needed: No` (or launched `no-ui`, i.e. `"shape" ∈ skipped[]`): skip Shape → go to Plan

## Step 5: Stage Sequencing (Standard Mode)

After each stage completes (stage added to `completed[]` in state.json):

**Display the next stage and offer:**
```
[Stage] complete. ✓

Next: [Next Stage] — [one-line description of what it does]

Continue? (yes / skip / stop)
```

Wait for user response:
- `yes`: invoke the next stage skill
- `skip`: ask for reason, update `skipped[]` in state.json, move to stage after
- `stop`: exit cleanly; state.json preserved for resume

**Stage sequence by tier:**

Micro:
1. Spec → 2. Build → 3. Validate → 4. PR → 5. Done

Standard + no-ui:
1. Spec → 2. Plan → 3. Build → 4. Validate → 5. PR → 6. Done

Standard + UI:
1. Spec → 2. Shape → 3. Plan → 4. Build → 5. Validate → 6. PR → 7. Done

Deep + UI:
1. Spec → 2. Shape → 3. Plan → 4. Build → 5. Validate → 6. PR → 7. Done

## Step 5a: Jump to Stage

When a stage name is given as argument (e.g., `/dev build`):
1. Read state.json to find the current feature
2. Check if required prior artifacts exist for the target stage:
   - build: requires plan.md (or spec.md Micro)
   - validate: requires build in completed[]
   - pr: requires validation.md
   - done: requires pr_url in state
3. If requirements met: invoke that stage skill directly
4. If requirements not met: "Build requires plan.md. Run /dev:plan first (or /dev to run the full flow)."

## Step 6: Product Plan Continuation

Product plans now live under `docs/dev/product-plans/` — one file per project
(`docs/dev/product-plans/<slug>.md`), and multiple projects can coexist there. Scope first, then
scan:

- **Scope to the governing plan first.** If a `state.json.product_plan` is in scope and non-null (a
  session whose state names its project), show **only** that single project's plan — never a blanket
  list.
- **Fall back to a directory scan only when no `product_plan` is in scope.** This is the common
  no-in-progress-session discovery case — a completed cycle's `state.json` is gone by then, so
  `product_plan` is usually unavailable here. Read `docs/dev/product-plans/*.md`:
  - **one** plan → show it;
  - **several** → list each project's slug + X/N cycles and let the user pick which to continue;
  - **none** → skip Step 6 entirely.

Under the PR-propagation model, a product plan created by a decomposition cycle becomes visible here only **after that cycle's PR merges** (`dev:spec` writes the plan into the creating cycle's worktree at `docs/dev/product-plans/<slug>.md`, and it reaches `main` via that cycle's PR). A parallel cycle cut from `origin/main` before the creating cycle merges won't see it yet — the plan-creating cycle should merge first.

For the single plan being shown, keep the existing per-milestone rendering:

```
Product plan: X/N cycles complete.

Milestone 1: ✓ feature-a  ✓ feature-b  → feature-c
Milestone 2: feature-d  feature-e

Start feature-c next? Or pick a different cycle.
```

Wait for user's choice, then invoke dev:spec with the chosen feature name.

## Invocation Reference

| Command | What happens |
|---------|-------------|
| `/dev` | Standard mode, new session or resume |
| `/dev no-ui` | Standard mode, Shape skipped |
| `/dev auto` | Redirects to /dev:autopilot |
| `/dev init` | Runs /dev:init |
| `/dev spec` | Jump to Spec (new session) |
| `/dev build` | Jump to Build (requires plan) |
| `/dev validate` | Jump to Validate (requires build) |
| `/dev pr` | Jump to PR (requires validation) |
| `/dev done` | Jump to Done (requires PR) |
| `/dev:fix ENG-123` | Linear issue entry |
| `/dev:<stage> docs/dev/<feature>/<artifact>.md` | Resume any stage without conversation memory — every `dev:<stage>` skill accepts an optional artifact-path argument (the prior stage's committed artifact) and derives `<feature>` from it. This is what the exit-protocol message after each stage prints as the exact resume command. |
