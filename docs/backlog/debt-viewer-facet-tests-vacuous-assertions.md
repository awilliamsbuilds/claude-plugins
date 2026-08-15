---
type: debt
scope: repo
status: open
first_recorded: 2026-08-14
cycles: [backlog-viewer]
recurrence: 1
severity: P3
files:
  - plugins/dev/skills/debt/test_viewer.py
---

**What's wrong:** Several assertions in the real-corpus facet tests cannot fail. Every non-`None`
value in the live `status` and `severity` facets is in its rank list, so `unranked` is always `[]`
and both the `assertEqual(unranked, sorted(unranked))` check and the `if ranked and unranked:`
branch are dead. `test_no_facet_entry_is_ever_empty` restates a condition `derive_facets` cannot
violate without being rewritten. `scope` is single-valued, so its ordering assertion is trivially
true — and the comment justifying that points at `TestFacetsWithNoLiveSample` as carrying the
ordering burden, which that class does not do for `scope` or `type`.

**Why deferred:** These arrived from the cold re-review of the loop that relaxed these same tests;
that relaxation is what tripped the fix loop's P3 circuit breaker, so no further P3 edits to this
file were attempted.

**Done looks like:** The synthetic corpus asserts multi-value alphabetical ordering for `scope` and
`type`, the dead branches are either exercised there or removed, and the comment describes the
coverage that actually exists.
