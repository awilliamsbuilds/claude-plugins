---
name: dev
description: "Main entry point for the /dev workflow. Standard mode: manages the 7-stage development workflow (spec → shape → plan → build → validate → PR → done) with explicit approval gates between stages. Also the workflow's own reference: /dev list prints a quick reference — which skill covers each stage, how to invoke it, and the non-pathway skills as FYI. Use /dev list when you've forgotten how /dev works, need a refresher on the workflow stages and commands, or aren't sure which dev:* skill to run next. Use /dev:autopilot for no-gate mode. Use /dev:init to set up a new project. Use /dev:fix for the fast path — a grounded change straight to an open PR with no cycle artifacts, including /dev:fix linear ENG-123 and /dev:fix backlog <item>."
---

# dev — Development Workflow Orchestrator

**Announce:** "I'm using the dev skill to manage the development workflow."

## Purpose

Orchestrate the full /dev workflow in standard mode — sequential stages with explicit approval gates between each. Each stage produces one artifact; each gate is a real stop.

## Superpowers Supersession

While a `/dev` session is active (a `docs/dev/<feature>/state.json` exists for the current feature), this workflow supersedes `superpowers:brainstorming` and `superpowers:writing-plans`. Do not invoke those skills separately — each `/dev` stage already contains the equivalent capability inline.

## Step 1: Parse Arguments

Arguments can appear in any combination:

- `list` → print the workflow reference (Step 1a) and **return**. This one short-circuits: it never falls through to Step 2.
- `auto` → this is a redirect: "For autopilot mode, use /dev:autopilot. Continuing in standard mode with approval gates."
- `no-ui` → set mode to no-ui; Shape stage will be skipped
- `init` → delegate to /dev:init immediately
- `spec`, `shape`, `plan`, `build`, `validate`, `pr`, `done` → jump to that stage (see Step 5)
- No arguments → standard flow (Step 2)

## Step 1a: Print the Workflow Reference (`/dev list`)

Print a quick, accurate reference for how `/dev` works: the stage pathway, which skill covers each stage, exactly how to invoke it, the tier rules, and the skills that sit outside the pathway.

**Read-only, and it returns here — never continue to Step 2.** Step 2 runs `/dev:init` when `docs/dev/config.json` is missing, so falling through would turn "what are the commands?" into a repo that has just had files created in it. A reference must be safe to ask for in a repo that has never run `/dev`. For the same reason this step does no session-state check (that is Step 3's job) and writes nothing.

**1. Read the Component Registry.** Read `CLAUDE.md`'s `## Component Registry` table and pull the one-line "Purpose" description for each `dev:*` row. That table is the single source of truth for these descriptions — `dev:done` Step 4 maintains it on every feature cycle, so a second hardcoded copy here would go stale against it. If the table, or a specific row, is missing, fall back to the minimal descriptions in item 4 below rather than failing.

The stage rows' Purpose strings already start with their own "Stage N — " prefix (e.g. "Stage 1 — builds the feature specification") — strip that prefix when substituting, since the pathway below supplies its own numbering; use only the text after it.

**2. Print the stage pathway.** The stage order is fixed and stable, so it lives here rather than being read from anywhere. Each line pairs the stage with its registry description and its exact standalone command:

```
/dev workflow — 7 stages:

1. Spec     → dev:spec     — [registry description] — Run: /dev:spec
2. Shape    → dev:shape    — [registry description] — Run: /dev:shape   (skipped if no UI)
3. Plan     → dev:plan     — [registry description] — Run: /dev:plan    (skipped in Micro tier)
4. Build    → dev:build    — [registry description] — Run: /dev:build
5. Validate → dev:validate — [registry description] — Run: /dev:validate
6. PR       → dev:pr       — [registry description] — Run: /dev:pr
7. Done     → dev:done     — [registry description] — Run: /dev:done

Fastest path: just run /dev — it starts a new session or resumes an in-progress one, and walks every stage in order with approval gates.
```

**3. Print the tier rules.** State them as **rules over the pathway**, never as an enumerated table of tier × UI combinations — the same form Step 5 uses, for the reason given there:

```
Tier rules:
- Micro tier (small, bounded changes): Shape and Plan are skipped; spec.md's "Implementation Note" section serves as the plan.
- no-ui: Shape is skipped, for any tier.
```

**4. Print FYI — other skills.** Using the same registry lookup:

```
FYI — other skills (not part of the linear pathway):

- dev:init      — [registry description] — run once per repo, before the first /dev session (auto-triggered if missing)
- dev:fix       — [registry description] — the fast path: skips the pathway entirely, going straight to an open PR with no cycle artifacts; escalates to /dev when the request carries 2+ unresolved decisions. Also starts from an identifier: /dev:fix linear <id> and /dev:fix backlog <item>
- dev:autopilot — [registry description] — alternative to the gated flow above, and also its continuation: printed as an option at the Spec and Shape gates once definition is settled; runs all stages without stopping for approval
- dev:reflect   — [registry description] — runs automatically at the end of dev:done; also callable standalone
- dev:debt      — [registry description] — view deferred work outside a cycle; also closes an entry by hand
- dev:review    — [registry description] — report-only code and document review: /dev:review diff reviews a diff, /dev:review docs reviews decision documents at absolute paths. Reports only; writes nothing. dev:validate Step 2 and /dev:fix both call it before every PR
- dev:secure    — [registry description] — on-demand security review outside the pipeline: /dev:secure audits the whole project, /dev:secure diff audits the current diff. Reports only; writes nothing. dev:validate Step 2 and /dev:fix both call the diff verb before every PR
- dev:migrate-tracker — [registry description] — run once in a repo still on the old docs/dev/tech-debt.md tracker; a no-op everywhere else
```

**If the Component Registry table or a specific row is missing:** fall back to these minimal descriptions rather than failing:
- `dev:spec` — builds the feature spec
- `dev:shape` — produces the design doc
- `dev:plan` — writes the implementation plan
- `dev:build` — implements the plan
- `dev:validate` — reviews and fixes issues
- `dev:pr` — opens the pull request
- `dev:done` — merges and closes out
- `dev:init` — sets up /dev in a repo
- `dev:fix` — the fast path: request to open PR, no cycle artifacts; also `linear` / `backlog` entry forms
- `dev:autopilot` — no-gate full-cycle runner; also accepts an artifact path to take over a gated cycle mid-flight
- `dev:reflect` — cycle retrospective
- `dev:debt` — view and close tracked tech debt
- `dev:review` — report-only code and document review; `diff` and `docs` modes
- `dev:secure` — on-demand security review; whole-project or `diff`, report-only
- `dev:migrate-tracker` — migrates a legacy tech-debt.md into docs/backlog/

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
  `WORKDIR` via the two-location scan above (worktree first, else primary) before proceeding to
  the stage — the user is never asked to `cd`.
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

**Stage sequence by tier — stated as rules, not as rows.**

The full pathway is: 1. Spec → 2. Shape → 3. Plan → 4. Build → 5. Validate → 6. PR → 7. Done.

Two rules remove stages from it. They compose, and every tier/UI combination is **derived** by applying them rather than looked up:

- **Micro tier:** Shape and Plan are skipped (`spec.md`'s "Implementation Note" section serves as the plan). → Spec → Build → Validate → PR → Done.
- **no-ui:** Shape is skipped, at any tier. → Standard/Deep + no-ui is Spec → Plan → Build → Validate → PR → Done.

**The rule form is deliberate.** The enumerated table this replaced listed Micro, Standard + no-ui, Standard + UI, and Deep + UI — and had no row at all for **Deep + no-ui**, a combination this workflow genuinely produces, so the orchestrator could not describe a cycle it had just run. An enumeration goes stale by omission the moment a combination is added; a rule set does not. `dev:autopilot` Step 3 already states its equivalent as a rule ("Standard/Deep + no-ui"), and Step 1a's tier rules print the same two lines to the user.

Which stages are actually skipped for the current cycle is read from `skipped[]` in `state.json` (Step 4 sets it from the spec's `## UI Needed`), not re-derived here.

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
| `/dev list` | Print the workflow reference — every stage, its skill, its exact `/dev:<stage>` command, the tier rules, and the non-pathway skills. Read-only; runs safely in a repo that has never run `/dev:init` |
| `/dev no-ui` | Standard mode, Shape skipped |
| `/dev auto` | Redirects to /dev:autopilot |
| `/dev init` | Runs /dev:init |
| `/dev spec` | Jump to Spec (new session) |
| `/dev build` | Jump to Build (requires plan) |
| `/dev validate` | Jump to Validate (requires build) |
| `/dev pr` | Jump to PR (requires validation) |
| `/dev done` | Jump to Done (requires PR) |
| `/dev:fix "<what you want done>"` | Fast path — grounded change straight to an open PR, no cycle artifacts; escalates here at 2+ unresolved decisions |
| `/dev:fix merge` | Merge that fast-path PR and clean up |
| `/dev:fix linear ENG-123` | Fast path, sourced from a Linear issue (no ID opens a picker) |
| `/dev:fix backlog <item>` | Fast path, sourced from a `docs/backlog/` item |
| `/dev:spec linear ENG-123` | Full seven-stage cycle from a Linear issue — what `/dev:fix` prints when it escalates one |
| `/dev:<stage> docs/dev/<feature>/<artifact>.md` | Resume any stage without conversation memory — every `dev:<stage>` skill accepts an optional artifact-path argument (the prior stage's committed artifact) and derives `<feature>` from it. This is what the exit-protocol message after each stage prints as the exact resume command. |
| `/dev:autopilot docs/dev/<feature>/<artifact>.md` | Resume a gated cycle in autopilot from the named artifact — the alternative command printed at the Spec and Shape gates. Derives `<feature>` from the path. |
