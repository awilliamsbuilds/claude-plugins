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
