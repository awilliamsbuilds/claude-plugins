# Debt Pending — reflect-repo-discovery

Buffered tech debt for this cycle. `dev:done` Step 6a flushes this into `docs/dev/tech-debt.md`
and Step 7 deletes it. Nothing else reads it.

## To Record

### dev:reflect dogfood shortcut can open a PR against a fork's upstream
**What's wrong:** The de-hardcoded step 1 uses `origin`-slug == marketplace-slug to auto-detect the dogfood case, then step 2 opens the PR with `gh pr create`. If a user installed the marketplace from their own fork of the plugin repo, the fork's `origin` slug matches the marketplace slug, so the dogfood shortcut fires — but `gh pr create` defaults its base to the fork's parent/upstream, so the skill edit is proposed against a repo the user may not own or intend to touch. The dogfood gate verifies the current checkout, not the PR base.
**Why deferred:** The fix lands in step 2's PR/branch mechanics, which the reflect-repo-discovery spec explicitly listed as out of scope ("Any change to ... the PR/branch mechanics (steps 2–4)"). Surfaced as a Nit in validate's security review.
**Done looks like:** Step 2 tells the agent to confirm the PR base repo before `gh pr create` (or pass an explicit `--repo`), so a fork's `origin` can't silently target its upstream.
**Files:** plugins/dev/skills/reflect/SKILL.md
*Source: dev:validate (Nit) · reflect-repo-discovery*

## To Close

- "Hardcoded repo path in dev:reflect" — this cycle's entire scope is removing that hardcoded path and marketplace name and replacing them with a discovery-or-ask procedure.
