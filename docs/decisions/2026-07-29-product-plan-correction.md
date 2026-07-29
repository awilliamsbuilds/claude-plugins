# Product-Plan Correction — Decision Log
*2026-07-29 · Branch: feature/product-plan-correction · PR #55*

## What was built
Corrected `/dev`'s product-plan from a de-facto persistent multi-project backlog back into an ephemeral single-project milestone carrier (deleted on project completion) per ADR Decision 7 + the product-plan slice of 8(c), finished the tech-debt-migration data move, and installed the one-way `backlog → product-plan` promotion flow.

## Key decisions
- **Durable plan location `docs/dev/product-plans/<project-slug>.md`** → outside any single cycle's dir, so a plan survives child-cycle `dev:done` teardown; replaces both the old top-level `docs/dev/product-plan.md` and nested `docs/dev/<parent>/product-plan.md` locations. Closes `debt-nested-product-plan-lifetime`.
- **`<project-slug>` = kebab-cased product name, constrained `^[a-z0-9][a-z0-9-]*$`** → reuses the repo's existing feature-slug allowlist shape; chosen once when the plan is first spawned. Also the value that keeps the shell `-m` in `dev:spec`'s commit safe.
- **Slug recovery via `state.json.product_plan` (full repo-relative path), inherited unconditionally on nesting** → a nested child copies the parent's `product_plan` even when the child never authored a plan, so `dev:done` can locate the plan uniformly (top-level and nested collapse into one read). No new state key; `parentFeature` no longer drives plan location.
- **Deletion trigger = every checkbox `[x]` after this cycle's check-off** → the plan is deleted only on project completion, never on a mid-project child teardown (which would re-create the bug being fixed).
- **Source-item close is bidirectional and inline** → on completion `dev:done` reverse-looks-up the source backlog item by `promoted_to`, sets `status: closed`, and `git mv`s it to `docs/backlog/closed/` in the same commit that removes the plan. This is a designed promotion terminus, distinct from the incidental debt closes routed through the buffer.
- **Migration drops the three completed milestones** → only the two live intentions (`debt-backfill`, `debt-linear-promotion`) are rehomed to `docs/backlog/` as `type: backlog`; the `[x]` milestones are historical and already in the decision logs, so the stale `docs/dev/product-plan.md` is hard-deleted, not archived.
- **Promotion documented once in `references/tech-debt.md`** → `promoted`/`promoted_to` un-reserved and the one-way flow + ephemeral lifecycle live in the shared contract as single source of truth, not copied into individual skills.

## Validation notes
- 1 loop run (tier: deep) — final status clean.
- **P1 (code):** `git rm <plan-path>` failed on the healthy completion path (Step 1's check-off left the plan locally modified) → fixed with `git rm -f`, plus corrected the false "sound end-to-end" prose.
- **P3 (security):** reverse-lookup grep could false-match a `promoted_to:` line in an untrusted backlog body → fixed by anchoring to the front-matter fence and requiring `status: promoted` (also idempotent).
- **P3 (security):** `dev:spec` Step 6 commit `-m` used the unnormalized product name → fixed to use the allowlisted `<project-slug>`.
- Three nits (debt empty-corpus wording, a guard-comment overstatement, unquoted `git mv` basenames) fixed inline.
- Forward-behavior note: the promotion back-link and completion-delete/close paths are plumbing for future cycles, not exercised by this cycle's own build — specified against the contract and audited by the cold reviews; the first real promotion is the true end-to-end test.

## Artifacts (archived)
Spec, plan, and validation committed at: 1de392b64cae02810e3087ea81902a298d9ef537 on branch feature/product-plan-correction

## Retrospective
*Reviewed by dev:reflect · 2026-07-29*

**Spec:** Confidence (90/Ready) matched actual clarity — 0 revisions, no auto-fills, and the 3 challenger concerns were all applied with none dismissed. Grounding pass held; nothing churned.

**Shape:** Skipped — correct for an agent-facing Markdown cycle with no UI.

**Plan:** Accurate — no mid-build updates, sequence held, single plan-challenger concern applied.

**Validate:** 1 loop / 5, clean. The loop caught a real P1 correctness bug in the plan's own specified git sequence — `git rm <plan-path>` fails on the healthy completion path because Step 1's check-off leaves the plan file locally modified — notable because plan Task 4 step 7 claimed to "trace the git sequence end-to-end" and still missed it. The two P3 security findings (untrusted-body false-match, unnormalized name reaching a shell `-m`) are the recurring "treat backlog/diff text as data + allowlist values reaching a shell" pattern. All caught by the cold review working as designed.

**Flow:** Deep tier was right — four coupled deliverables plus security-sensitive shell plumbing and forward-behavior that can't be self-tested. No unnecessary stages.

**Token efficiency:** No outliers — 7 files in build, no over-reading.

**Suggestions:** none actionable at the skill level — the git-precondition and shell-safety lessons are exactly what the validate cold-review exists to catch, and it did.

**Deferred to tech debt:** none new (this cycle closes `debt-nested-product-plan-lifetime`).
