# Debt Pending — init-rerun-hardening

Buffered tech debt for this cycle. `dev:done` Step 6a flushes this into `docs/dev/tech-debt.md`
and Step 7 deletes it. Nothing else reads it.

## To Record

### validate's config-contract gate says "every reader" but the convention is "every reader of that key"
**What's wrong:** `dev:validate`'s Config-contract review gate reads "if this cycle adds a new key to config.json, verify every skill that reads config.json has that key in its Step 1 read list." Taken literally that is broader than the actual convention this repo follows: only a skill that reads *that specific key* needs it in its read list. Every existing key is handled per-consumer, and this cycle added `component_policy`/`schema_version` to just their consumers (shape, reflect; migration for schema_version) while spec/autopilot/pr read config.json for other keys and were correctly left alone. A strict future run of the gate as worded would flag those as violations — a false positive that each config-touching cycle will rediscover.
**Why deferred:** Editing `validate`'s checklist was explicitly out of scope for this cycle; the implementation correctly followed the per-consumer intent, so no diff change was warranted here.
**Done looks like:** The gate wording is narrowed to "every skill that reads that key" (or equivalent), so the literal reading matches the per-consumer convention and stops producing false positives.
**Files:** plugins/dev/skills/validate/SKILL.md
*Source: dev:validate (Nit) · init-rerun-hardening*

## To Close

- "dev:spec's product-plan procedure pushes straight to origin/main" — this cycle removes the exemption entirely: the product plan is written into the cycle worktree and reaches `main` through the cycle's own PR (the same lifecycle as `tech-debt.md`), so there is no direct push to `origin/main` left to justify.
