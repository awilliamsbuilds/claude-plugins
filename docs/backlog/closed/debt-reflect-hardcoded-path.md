---
type: debt
scope: repo
status: closed
first_recorded: 2026-07-22
cycles: [reflect-repo-discovery]
recurrence: 1
files:
  - plugins/dev/skills/reflect/SKILL.md
closed: 2026-07-28
closed_by: reflect-repo-discovery
---

**What's wrong:** `plugins/dev/skills/reflect/SKILL.md:166` hardcodes `~/Development/claude-plugins`
as the source-repo location and names the `local-plugins` marketplace directly. Found by the
tech-debt-tracking cycle's negative-space sweep, which grepped the whole plugin for
person-, company-, and environment-specific strings: this is the **only** repo-specific string
in the entire `/dev` plugin. It directly violates the portability property that cycle was built
around — a `/dev` installed in any other repo follows an instruction pointing at a directory
that doesn't exist there.
**Why deferred:** Found by that cycle's grounding sweep and explicitly placed out of scope in
its spec. Best fixed by a later cycle already working in that file — which is the behavior this
tracker exists to enable.
**Done looks like:** The source repo is discovered (from the git remote, or from where the
plugin cache resolves) or asked for, with no path and no marketplace name hardcoded anywhere in
the skill.
