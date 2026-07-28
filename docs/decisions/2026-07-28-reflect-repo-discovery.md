# Reflect Repo Discovery — Decision Log
*2026-07-28 · Branch: fix/reflect-repo-discovery · PR #50*

## What was built
De-hardcoded `dev:reflect`'s skill-edit path so it locates the plugin **source** repo through a portable discover-or-ask procedure instead of the author's machine-specific `~/Development/claude-plugins` path and `local-plugins` marketplace name.

## Key decisions
- **Auto-discovery limited to the dogfood case → reason:** grounding showed no stored mapping from a marketplace to the user's *working* checkout exists. The managed `installLocation` clone under `~/.claude/plugins/marketplaces/` has `autoUpdate:true` and is overwritten on `/plugin update`, so it must never be branched/PR'd from. The only reliably self-resolving signal is "the current `/dev` checkout's `origin` slug == the marketplace's GitHub slug" — i.e. running `/dev` on the plugin repo itself.
- **Everything else asks the user → reason:** there is no reliable way to locate an arbitrary plugin's local source checkout, so the honest primary path for non-dogfood use is to ask, not to guess a path.
- **Claude-Code internal files named only as illustrative hints → reason:** referencing `known_marketplaces.json` as a required load-bearing step would re-couple the skill to Claude Code's cache layout; naming it with "e.g." keeps the procedure surviving a cache-layout change.
- **Kept `plugins/<plugin>/skills/<skill>/SKILL.md` → reason:** that is repo-structure, not environment-specific, so it is not a hardcoded identifier the fix needed to remove.

## Validation notes
- 1 loop run (tier: micro) — final status clean, no open P1/P2.
- Reviews ran as two fresh cold subagents (code + security) in parallel, denied session history.
- P3 (code): slug-vs-URL comparison was implicit → fixed by normalizing `git remote get-url origin` to an `owner/repo` slug before a plain string compare.
- P3 (security): remote-match alone couldn't distinguish the managed `~/.claude/plugins/cache/` clone (same `origin`) from the real working checkout → fixed by an explicit "never a checkout under `~/.claude/plugins/cache/` — fall through to ask" guard.
- Nit (security): slug quoting / shell-interpolation risk → folded into the normalization fix (compare as plain strings, don't shell-interpolate).
- 3 Nits accepted as-is: (1) `gh pr create` fork-base default — deferred to tech debt as out of scope (step 2 PR mechanics); (2) "within that repo" reads slightly ahead in the ask branch — phrasing only; (3) "(the common case)" frequency claim — reviewer-validated as defensible.
- Both spec grep criteria (SC1, SC2) verified in-session with zero matches: no `Development/claude-plugins` / `local-plugins` / `awilliamsbuilds` / `~/Development` / `adam` strings remain anywhere under `plugins/dev/`.

## Artifacts (archived)
Spec and validation committed at: `5d5c980` on branch `fix/reflect-repo-discovery`.
