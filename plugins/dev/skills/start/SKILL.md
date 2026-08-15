---
name: start
description: "Prints a quick reference for the /dev workflow — which skill covers each stage, how to invoke it, and non-pathway skills as FYI. Use when you've forgotten how /dev works, need a refresher on the workflow stages and commands, or aren't sure which dev:* skill to run next."
---

# dev:start — Workflow Reference

**Announce:** "I'm using dev:start to show the /dev workflow reference."

## Purpose

Print a quick, accurate reference for how `/dev` works: the stage pathway, which skill covers each stage, exactly how to invoke it, and the skills that sit outside the pathway. Read-only — no session-state checks, no file writes. (For in-progress session status, that's `dev:dev`'s Step 3 job, not this one.)

## Step 1: Read the Component Registry

Read `CLAUDE.md`'s `## Component Registry` table. Pull the one-line "Purpose" description for each `dev:*` row. This is the single source of truth for descriptions — do not keep a second, hardcoded copy of them here; if the table or a specific row is missing, fall back to the minimal descriptions in Step 4.

## Step 2: Print the Stage Pathway

Using the fixed stage order below (this structure is stable and doesn't need to be read from anywhere), print each stage paired with its registry description. The registry's Purpose strings for stage skills already start with their own "Stage N — " prefix (e.g. "Stage 1 — builds the feature specification") — strip that prefix when substituting, since the line below supplies its own numbering; use only the text after it.

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

## Step 3: Print Tier Variations

```
Tier shortcuts:
- Micro tier (small, bounded changes): Spec → Build → Validate → PR → Done. Shape and Plan are skipped; spec.md's "Implementation Note" section serves as the plan.
- no-ui mode: Shape is skipped, for any tier.
```

## Step 4: Print FYI — Other Skills

Using the same registry lookup, print the non-pathway skills:

```
FYI — other skills (not part of the linear pathway):

- dev:init      — [registry description] — run once per repo, before the first /dev session (auto-triggered if missing)
- dev:fix       — [registry description] — entry point when starting from a Linear issue instead of a blank spec
- dev:autopilot — [registry description] — alternative to the gated flow above, and also its continuation: printed as an option at the Spec and Shape gates once definition is settled; runs all stages without stopping for approval
- dev:reflect   — [registry description] — runs automatically at the end of dev:done; also callable standalone
- dev:debt      — [registry description] — view deferred work outside a cycle; also closes an entry by hand
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
- `dev:fix` — Linear issue entry point
- `dev:autopilot` — no-gate full-cycle runner; also accepts an artifact path to take over a gated cycle mid-flight
- `dev:reflect` — cycle retrospective
- `dev:debt` — view and close tracked tech debt
- `dev:migrate-tracker` — migrates a legacy tech-debt.md into docs/backlog/

## Step 5: Note Setup Status

If `docs/dev/config.json` doesn't exist in the current project, append: "Note: this repo hasn't run `/dev:init` yet — run that first, or just run `/dev` and it'll trigger init automatically."

## Invocation

`/dev:start` — no arguments.
