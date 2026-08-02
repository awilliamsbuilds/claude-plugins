# Debt Pending — legacy-tracker-migration

Buffered backlog/debt items for this cycle. `dev:done` Step 6a flushes `## To Record` into
`docs/backlog/` and executes each `## To Close` close-intent, then Step 7 deletes this file. Nothing
else reads it.

## To Record

### p2-collision-escalation-not-in-contract
````markdown
---
type: debt
scope: repo
status: open
severity: P3
first_recorded: 2026-08-02
cycles: [legacy-tracker-migration]
recurrence: 1
files:
  - plugins/dev/references/tech-debt.md
  - plugins/dev/skills/migrate-tracker/SKILL.md
---

**What's wrong:** P2's collision rule stops at one level — on a taken slug, disambiguate to
`<type>-<slug>-<first-cycle>.md`. It says nothing about what happens when *that* name is also taken.
Every existing caller writes one item at a time against a settled tree, so the case never came up.
`dev:migrate-tracker` writes a whole tracker's worth at once and has to check names it has only
*decided* on, so it needed a further step — append `-2`, `-3`, … until free — and stated that rule
locally, in two places (its Step 7 canonical block and its Step 8 degrade mirror). Both restatements
violate the skill's own CITE-DONT-COPY rule, and the escalation is now a naming convention that lives
nowhere authoritative. The next writer that hits a double collision will either re-derive a different
escalation or not handle it at all.

**Why deferred:** Success Criterion 11 of this cycle forbids modifying `references/tech-debt.md`; it
was a protected file and had to end the cycle byte-identical. Fixing this correctly means editing P2,
which was out of scope by construction.

**Done looks like:** P2 in `references/tech-debt.md` states the escalation past `-<first-cycle>`, and
both restatements in `migrate-tracker/SKILL.md` collapse to a citation.
````

### p9-issue-body-fence-width
````markdown
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
````

## To Close
