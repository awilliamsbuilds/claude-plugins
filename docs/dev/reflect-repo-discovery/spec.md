# Reflect Repo Discovery
*Branch: fix/reflect-repo-discovery · Confidence: 90% — Ready · 2026-07-27*
*Cycle type: feature · Tier: micro*

## Intent
`plugins/dev/skills/reflect/SKILL.md` (line 181) is the **only** repo-specific string in the
entire `/dev` plugin. Its "Skill edits go through the plugins repo" section tells the agent to
"Locate the source repo (the `local-plugins` marketplace checkout, e.g. `~/Development/claude-plugins`)"
— hardcoding both a local filesystem path and a marketplace name that exist only on the plugin
author's machine. A `/dev` installed anywhere else follows an instruction pointing at a directory
that doesn't exist there. This cycle removes both hardcoded strings and replaces them with a
portable discovery procedure.

## Scope
Rewrite step 1 (and reconcile the closing fallback line) of the `### Skill edits go through the
plugins repo — always` subsection in `reflect/SKILL.md` so locating the plugin **source** repo is
discovered-or-asked, with nothing environment-specific hardcoded:

- **Dogfood auto-shortcut:** derive the plugin's own marketplace repo identity (the GitHub slug
  backing the marketplace this skill was installed from), then check whether the current `/dev`
  checkout's `origin` remote points at that same repo. If it does, the current checkout **is** the
  source repo — use it directly. This is the only case that self-resolves, and it is exactly the
  case of running `/dev` on the plugin repo itself.
- **Ask fallback (primary in the general case):** in every other case — running `/dev` on an
  unrelated project — there is no reliable way to locate an arbitrary plugin's local source
  checkout, so ask the user where the source repo lives. The skill already has this fallback line;
  keep it as the honest primary path for non-dogfood use.
- **No hardcoded path, no hardcoded marketplace name** anywhere in the skill after the change.
  Claude-Code-internal files (e.g. `known_marketplaces.json`) may be named only as illustrative
  hints ("e.g."), never as required load-bearing steps — so the procedure survives Claude Code
  changing its cache layout.

## Out of Scope
- The deeper question of whether `dev:reflect` should attempt an upstream port **at all** when the
  user is not the plugin author (most `/dev` users install plugins rather than author them). That is
  a behavioral redesign of the section's purpose, not a de-hardcoding, and belongs to its own cycle.
- Any change to the two-confirmation gate, the PR/branch mechanics (steps 2–4), or the standalone-
  invocation tracker-write path elsewhere in the skill.
- Touching any file other than `reflect/SKILL.md`.

## Success Criteria
1. `grep -n "Development/claude-plugins\|local-plugins" plugins/dev/skills/reflect/SKILL.md` returns
   **zero** matches (the marketplace name `local-plugins` may still appear only if it is a generic
   illustrative example, not a required identifier — target is zero).
2. A repo-wide sweep of the `/dev` plugin for person-, company-, and environment-specific strings
   (`Development/claude-plugins`, `local-plugins`, `awilliamsbuilds`, `~/Development`, `adam`)
   returns nothing — the property the tech-debt entry was built around is restored.
3. The rewritten step 1 describes: (a) derive the plugin's marketplace repo identity, (b) use the
   current checkout when its remote matches (dogfood), (c) otherwise ask the user.
4. The existing "ask the user where it lives" fallback remains present and coherent with the new
   step 1 (no dangling or contradictory instruction).
5. The section still reads as a single coherent procedure — a fresh agent following it in a
   non-plugin repo lands on "ask the user," and in the plugin repo lands on "use the current
   checkout."

## Happy Path
1. `dev:reflect` reaches its Step 6 skill-update flow and the user approves a skill edit.
2. The agent reads the rewritten step 1: it derives the plugin's marketplace repo slug and checks
   the current checkout's remote.
3. **Dogfood:** remote matches → the current `/dev` checkout is used as the source repo; branch,
   edit, PR proceed.
4. **Non-dogfood:** remote doesn't match (or can't be derived) → the agent asks the user where the
   source repo lives, then proceeds.

## Edge Cases
- Marketplace repo identity can't be derived (unexpected cache layout / missing metadata): fall
  through to the ask path — never guess a path.
- Current checkout has no `origin` remote, or multiple remotes: treat as "no match" → ask.
- User running `/dev` inside a fork of the plugin repo: the remote slug differs; falls to ask,
  which is correct (the fix should land where they actually work).

## Audience
Maintainers of the `/dev` plugin, and any third party who installs `/dev` into their own repo —
for whom the hardcoded path is a live correctness bug today. (From CLAUDE.md: personal Claude Code
plugin repo, agent-facing skill files.)

## Technical Constraints
- The artifact is executable prose (a `SKILL.md`), read by an agent at runtime — not code. "Correct"
  means an agent following the instruction reaches the right repo; there is no unit test.
- Any shell snippet introduced must exit 0 on its healthy path (the standing `dev:validate` rule for
  skill snippets).
- Must not couple to Claude Code internal file paths as required steps (illustrative only).

## Dependencies
None. Single-file change to `reflect/SKILL.md`.

## UI Needed
No.

## Implementation Note
**Files to touch:** `plugins/dev/skills/reflect/SKILL.md` (only).

**Approach:** In the `### Skill edits go through the plugins repo — always` subsection, replace the
current step 1 —

> 1. Locate the source repo (the `local-plugins` marketplace checkout, e.g. `~/Development/claude-plugins`). The skill lives at `plugins/<plugin>/skills/<skill>/SKILL.md`.

— with a discovery procedure that (a) derives the plugin's marketplace repo identity (the GitHub
`source.repo` slug backing the marketplace this skill was installed from — discoverable from the
running skill's own cache path → marketplace name → its entry in `known_marketplaces.json`, named as
an illustrative hint, not a hard requirement), (b) checks whether the current `/dev` checkout's
`origin` remote points at that repo and, if so, uses the current checkout as the source repo (the
dogfood case), and (c) otherwise defers to the ask-the-user fallback. Keep "The skill lives at
`plugins/<plugin>/skills/<skill>/SKILL.md`" — that path is repo-structure, not environment-specific.
Ensure the closing line ("If the source repo can't be found, ask the user where it lives …") reads
as the explicit fallback for the non-dogfood case rather than an afterthought. Remove `local-plugins`
and `~/Development/claude-plugins` as load-bearing identifiers entirely.

---
*Auto-filled dimensions: none*
*Grounding inventory: `grep -n "Development/claude-plugins\|local-plugins"` across `plugins/dev/` → single hit at reflect/SKILL.md:181 (verified sole repo-specific string in the plugin). `known_marketplaces.json` inspected → maps marketplace name `local-plugins` → GitHub slug `awilliamsbuilds/claude-plugins`, with `installLocation` pointing at CC's managed marketplace cache, NOT the user's dev checkout (so no stored mapping to the local source checkout exists — auto-discovery of an arbitrary plugin's local checkout is not possible; only the dogfood case is). Current repo `origin` = `git@github.com:awilliamsbuilds/claude-plugins.git`, which matches the marketplace slug → confirms the dogfood-detection signal is real and firing in this very session. Plugin cache dir (`~/.claude/plugins/cache/local-plugins/...`) is NOT itself a git checkout, so "where the plugin cache resolves" is not a viable git-remote discovery path — ruling out one of the tech-debt entry's suggested mechanisms.*
