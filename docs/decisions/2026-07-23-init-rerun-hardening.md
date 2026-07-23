# init-rerun-hardening — Decision Log
*2026-07-23 · Branch: feature/init-rerun-hardening · PR #40*

## What was built
Made `dev:init`'s config contract coherent by construction, turned its rerun path into a safe, non-destructive migration, and stopped `dev:init`/`dev:spec` from writing to `main` outside the branch/PR flow.

## Key decisions
- **Two-sided config contract** → Close the missing-key contract from both ends: every `dev:*` skill that reads a config key documents a consumer-side fallback default (belt), *and* init's rerun migration backfills missing keys with those same defaults (suspenders). Neither depends on the other having run, so a config in any state (fresh, drifted, hand-edited) yields correct behavior.
- **Persist the one surviving setup answer** → `component_policy` is now written to `config.json` under a stable key that `dev:shape` and `dev:reflect` actually read, replacing the previously-unwritten "component policy" concept those skills read blindly.
- **Prune orphan questions and dead keys** → init's design-personality (Q1) and audience (Q3) questions reached no consumer and were removed; the `worktree_root` key was written but never read (every skill hardcodes `.dev-worktrees`) and is no longer emitted. init now asks exactly one setup question.
- **Schema versioning + merge migration** → Stamp `schema_version = 1`. The rerun "update" path becomes a merge migration: backfill absent keys with defaults, **preserve** existing (possibly tuned) values, never clobber. This generalizes and replaces the former hand-special-cased `tech-debt.md`-only backfill as the mechanism by which older repos gain new artifacts.
- **Future-version guard** → If a config's `schema_version` is newer than the running init knows, leave it untouched and report — never downgrade or corrupt a forward-versioned config.
- **Malformed-config guard** (from validation) → If `config.json` doesn't parse as JSON or `schema_version` isn't a non-negative integer, STOP and report for manual repair rather than falling back to the fresh template and clobbering tuned values.
- **No unreviewed `main` writes** → init makes no `git add` and no commit on any path — it leaves scaffolding **unstaged** (not merely uncommitted, matching the existing "keep" path) and reports that the files need reviewing, committing, and pushing.
- **Product-plan lifecycle onto the cycle PR** → Folds in the tracked debt entry *"dev:spec's product-plan procedure pushes straight to origin/main"*. The product plan is now written into the cycle's own worktree and reaches `main` through the cycle's PR (the `tech-debt.md` precedent), removing the ephemeral-detached-worktree push entirely. `state.json.product_plan` is wired so `done`'s top-level check-off fires.

## Validation notes
- 1 loop run (tier: deep). Code review and security review ran in parallel as fresh, context-free subagents against the build diff. Both confirmed all 8 plan tasks landed and found no P1/P2.
- P3s found and resolved in loop 1: removed a vestigial unreachable clause in the migration's `component_policy` backfill; added the malformed-config / non-integer-`schema_version` guard; added a note that changelog detection is intentionally not re-run on migration.
- Nits resolved: aligned the Scenario D "keep" exit-line wording to the standardized "review, commit, and push"; added a shell-quoting caution to the spec deferred-write `git commit -m` substitution.
- Nit accepted as-is (recorded to tech debt): `dev:validate`'s config-contract gate is worded "every skill that reads config.json," literally broader than the per-consumer convention the repo follows. Editing the gate was out of scope; the imprecision is systemic, so it was deferred to the tracker rather than silently patched.
- The one folded debt entry was closed by this cycle — the restructure removed the exemption entirely.

## Artifacts (archived)
Spec and plan committed at: 1be6847 on branch feature/init-rerun-hardening
