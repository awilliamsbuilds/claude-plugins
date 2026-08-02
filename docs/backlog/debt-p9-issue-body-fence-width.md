---
type: debt
scope: repo
status: open
severity: P2
first_recorded: 2026-08-02
cycles: [legacy-tracker-migration]
recurrence: 1
files:
  - plugins/dev/references/tech-debt.md
  - plugins/dev/skills/debt/SKILL.md
  - plugins/dev/skills/migrate-tracker/SKILL.md
---

**What's wrong:** P9's issue-body format is "a single fenced markdown block holding the item's
complete front-matter block + body, verbatim", and `dev:debt inbox` lifts that block back out as the
authoritative content when converting an issue into the store. Both describe a three-backtick fence.
But an item body can legitimately contain a code fence, so a three-backtick wrapper terminates early:
the converted item is truncated, and text after the premature terminator can open its own block with
front-matter of its choosing. `dev:migrate-tracker` is the first producer that knowingly hits this —
its bodies are lifted verbatim from a legacy tracker whose entries quote fenced shell — so it composes
a fence wider than the body's longest backtick run. That fix is only half the loop: `inbox` still has
to match on the info tag rather than the delimiter width, or a wide-fenced issue fails to convert.

**Why deferred:** Success Criterion 11 forbids this cycle from modifying `references/tech-debt.md` or
`dev:debt`. The producer side is fixed; the consumer side and the contract could not be touched.

**Done looks like:** P9's slug-marker section states the variable-width fence rule, and `dev:debt
inbox` identifies the authoritative block by its `markdown` info tag rather than by three backticks.

**Behavior today:** a wide-fenced body is not silently lost — `inbox` skips an unparseable issue with
a visible note and leaves it open — so this degrades to "needs a human", not to data loss.
