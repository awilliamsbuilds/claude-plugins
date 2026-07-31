# dev:reflect — Explicit PR Target
*Branch: feature/reflect-pr-base-explicit-target · Confidence: 88% — Ready · 2026-07-31*
*Cycle type: feature · Tier: standard*

## Intent

`dev:reflect`'s skill-edit path (§ *Skill edits go through the plugins repo — always*) decides **where
it is** but never states **where the PR goes**. Step 1 resolves the plugin source repo by comparing the
marketplace slug from `~/.claude/settings.json` against the current checkout's `origin`; step 2 then
says only *"commit, push, and open a PR with `gh`"*. With no target named, `gh` resolves the repo from
the git remotes — and `gh`'s rule for a fork is to send the PR to the fork's **parent**.

So a user who forked this plugin repo, registered the fork as their own marketplace, and works in that
fork passes the dogfood check **correctly** (they *are* home) and still has their skill edit proposed
against `awilliamsbuilds/claude-plugins` — a repo they may not own or intend to touch. The gate verifies
the checkout; the PR destination is a separate question it never asks.

This pays `docs/backlog/debt-reflect-dogfood-pr-base.md` (open since 2026-07-28, recurrence 1), deferred
at the time because the `reflect-repo-discovery` spec put step 2's PR/branch mechanics out of scope.
It also completes the last outstanding item from ADR `2026-07-28-backlog-debt-model.md`, whose Decision 5
established the fix pattern — *read the target explicitly from config, never guess it from `origin`, pass
`--repo`* — and predicted that adopting it in `dev:reflect` would be its own cycle.

## Scope

One file, one section: `plugins/dev/skills/reflect/SKILL.md`, § *Skill edits go through the plugins repo
— always*, **step 2 only**.

- **Replace the prose with an explicit invocation.** Step 2 currently reads "open a PR with `gh`" — there
  is no command block and no flags (verified: `grep -rn "gh pr create" plugins/` returns no hit in
  `reflect/SKILL.md`). Build writes the actual `gh pr create` call, carrying `--repo` so `gh` has no repo
  decision left to make.
- **Dogfood path — reuse step 1's resolved slug.** Step 1 has already derived the marketplace slug for
  its comparison; step 2 passes that same value as `--repo`. Resolution and validation are **cited**
  from `references/tech-debt.md` §P9.target-resolution — which already specifies the config read
  (`enabledPlugins["dev@<mp>"]` → `extraKnownMarketplaces[<mp>].source.repo`), `owner/name`
  normalization, and the `^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$` allowlist that rejects a leading-`-`
  argument-injection value — **not restated**.
- **Ask-fallback path — derive, echo, confirm.** When step 1 falls through to asking the user where the
  plugin source repo lives, there is no config-derived slug. Derive one from `git remote get-url origin`
  **in the checkout the user named**, normalize to `owner/name`, validate it under the same §P9
  allowlist, then **echo the normalized target and confirm** before creating. A fork's own `origin` is
  its own slug, which is the correct home; the confirmation is what makes a wrong answer visible rather
  than silent.
- **Also pass `--head` explicitly**, mirroring `dev:pr` Step 4's existing guard against `gh` inferring
  the head branch from whatever the shared tree happens to be on.

## Out of Scope

- **`dev:pr` Step 4's `gh pr create`** — the same flag is absent there, but it is a different surface (the
  cycle's own PR in the user's project repo, not a plugin skill-edit PR), it already passes explicit
  `--base` and `--head`, and its correct target follows a different rule than the marketplace config.
  Deliberately left; if it is ever wanted, it is its own cycle.
- **Step 1's discovery logic** — the dogfood comparison and the ask fallback are both correct as written.
  The defect is entirely downstream of them. Step 1 is read but not modified.
- **Steps 3 and 4** of the same section (cache/repo parity, telling the user the PR URL) — untouched.
- **Any change to the two-confirmation gate** that precedes a skill edit — unrelated and already correct.

## Success Criteria

1. No path through step 2 reaches `gh pr create` without an explicit `--repo`.
2. The dogfood path passes step 1's config-derived slug, validated per §P9.target-resolution — including
   rejection of any value beginning with `-` — rather than a value inferred from the current checkout.
3. The ask-fallback path derives its slug from the named checkout's `origin`, and **echoes the normalized
   `owner/name` and confirms** before the PR is created.
4. §P9.target-resolution is **cited, not duplicated** — `reflect/SKILL.md` holds no second copy of the
   resolution or validation rule (the single-source-of-truth discipline the contract applies to itself).
5. A fork scenario is traceable end to end from the skill text: a user in `them/plugins`, marketplace
   registered to `them/plugins`, produces a PR in `them/plugins` and nowhere else.
6. `plugins/dev/skills/pr/SKILL.md` is unmodified.

## Happy Path

1. A `/dev` cycle running in a fork of this repo reaches `dev:reflect`, which suggests a skill improvement.
2. The user confirms the edit, and confirms again after seeing the diff (both existing gates, unchanged).
3. Step 1's dogfood shortcut fires: the marketplace slug (`them/plugins`) matches the checkout's `origin`
   slug. The current checkout **is** the source repo, and the resolved slug is carried forward.
4. Step 2 creates the branch, commits, pushes, and runs `gh pr create --repo them/plugins --head <branch> …`.
5. The PR opens in `them/plugins`. `gh`'s fork rule never engages, because nothing was left for it to
   resolve.

## Edge Cases

- **Ask-fallback with no config slug** → derive from the named checkout's `origin`, normalize, validate,
  echo, confirm. Never fall back to an unqualified `gh pr create`.
- **The named checkout has no `origin`, or several remotes** → there is no slug to derive. Say so and stop
  rather than guessing; the user can open the PR by hand. (Step 1 already refuses to guess a path for the
  same reason.)
- **A resolved slug fails the §P9 allowlist** (notably a leading `-`) → a user error per §P9: say so and
  stop, never pass it to `gh`.
- **Fork whose default branch is not `main`** → with `--repo` explicit, `gh` bases the PR on *that repo's*
  default branch, which is already correct. See the note carried to Plan below.
- **Checkout under `~/.claude/plugins/cache/`** → step 1 already routes this to the ask fallback (the cache
  is the managed clone `/plugin update` overwrites, and it shares the same `origin`). Unchanged; the
  fallback's new derive-echo-confirm applies.

## Audience

Solo maintainer of `awilliamsbuilds/claude-plugins` (per `CLAUDE.md`) — but the defect is specifically
about **other people**: this repo is not a fork, so `gh` already resolves correctly here. The fix exists
so the plugin is safe for anyone who forks it, which is the point of it being installable.

## Technical Constraints

- **Skill-instruction editing only** — the deliverable is Markdown prose plus a command block. No code.
- **All GitHub operations via `gh`**, which carries its own auth (grounding for the previous cycle found
  `gh` 2.88.1 authed via keyring, with no `GITHUB_PERSONAL_ACCESS_TOKEN` in the environment).
- **Single source of truth** — the resolution + validation rule lives in `references/tech-debt.md` §P9;
  `reflect/SKILL.md` links to it. A second copy would drift, which is the failure the contract names.
- **Slug allowlist enforced before `gh`** — `^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$`, rejecting leading-`-`
  argument-injection values. Already specified in §P9; reused, not rewritten.

## Dependencies

- **§P9.target-resolution** — shipped in `debt-capture-routing` (PR #56, merged). The pattern this cycle
  adopts already exists and is in use by `/dev:debt add`.
- **`gh` CLI, authenticated** — present.
- Nothing blocks this; it is the last outstanding follow-on from the backlog-debt ADR.

## UI Needed

No. CLI skill-instruction editing, no visual surface — Shape is skipped.

## Notes carried to Plan

- **Whether to pin `--base` as well as `--repo`.** With `--repo` explicit, `gh` bases the PR on that
  repo's default branch, which is already the correct outcome — so `--base` is not required to fix the
  defect. Adding it buys determinism but requires *querying* the target's default branch (`gh repo view
  --json defaultBranchRef`) rather than assuming `main`, since a fork's default may differ. Plan's call:
  cheap explicitness vs. an extra API round-trip and a new failure mode. The spec requires only `--repo`.

---
*Auto-filled dimensions: none — every dimension was answered from the backlog item, the grounding sweeps, or the two confirmed interface decisions.*
*Grounding inventory: `grep -rn "gh pr create" plugins/` → hits in `pr/SKILL.md:131` and `plan/SKILL.md:173` only, **none in `reflect/SKILL.md`** (correcting the backlog item's implication that an invocation exists to add a flag to — step 2 is prose); read `reflect/SKILL.md:177-190` → step 1 derives the marketplace slug and compares it to `origin`, step 2 says only "open a PR with `gh`"; read `pr/SKILL.md:120-140` → `gh pr create` there passes explicit `--base` and `--head` but no `--repo` (basis for the out-of-scope call); read `references/tech-debt.md:348-360` → §P9.target-resolution already specifies config read + normalization + the `^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$` allowlist incl. leading-`-` rejection (so it is cited, not restated); `grep -rln "marketplace"` across `plugins/dev/` → `tech-debt.md`, `reflect/SKILL.md`, `debt/SKILL.md` are the only slug-deriving consumers; Step 7 pass-4 cross-check → read `files:` front-matter of all 7 active backlog items, exactly one (`debt-reflect-dogfood-pr-base`, files: `[plugins/dev/skills/reflect/SKILL.md]`) intersects this cycle's surface and is the item being paid; no other item touches `reflect/SKILL.md`.*
