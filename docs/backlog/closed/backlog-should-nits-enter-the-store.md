---
type: backlog
scope: repo
status: closed
closed: 2026-08-16
closed_by: "fix/backlog-should-nits-enter-the-store"
first_recorded: 2026-08-13
cycles: [manual]
recurrence: 1
files:
  - plugins/dev/references/tech-debt.md
  - plugins/dev/skills/validate/SKILL.md
---

**What:** Evaluate whether an item classified `Nit` should ever be recorded in `docs/backlog/` at
all, given how small and inconsequential a nit is by definition. The capture rule currently says it
should: "A **Nit** that exposes a systemic convention gap — a naming rule nothing enforces, a
pattern the next five cycles will each rediscover — **qualifies**"
(`references/tech-debt.md:49-51`). This item questions that rule rather than assuming it.

**Why:** `Nit` is a review-time label, not a tracker priority. In `dev:validate` it does real work —
step 5 attempts Nit fixes "only if P1/P2/P3 all resolved" (`validate/SKILL.md:124`), the standard
non-blocking-review-comment semantics. But the label is then persisted into the store, where the
contract itself says it is "**Informational** ... not a routing/lifecycle field" and "drives no
procedure" (`tech-debt.md:104-106`), and where the capture rule separately declares that "severity
is the wrong axis" (`tech-debt.md:47`). So the store carries a distinction it explicitly refuses to
act on. Industry convention places a nit below P3, or off the priority scale entirely, precisely
because most nits are applied in the moment or dropped rather than tracked. One Nit item exists in
the store today (`debt-artifact-path-rule-artifact-component-unconstrained`), which is a thin
evidence base either way — worth deciding deliberately before the count grows. Surfaced while
designing the backlog viewer, where the severity facet renders `P3` and `Nit` as peer levels and
made the overlap visible.

**Done looks like:** A decision recorded on whether `Nit` items belong in the store. If they do, the
capture rule states why a nit ever outlives its review. If they do not, `dev:validate`'s flush stops
writing them, `references/tech-debt.md` drops `Nit` from the `severity` field's stated values, and
the one existing Nit item is reclassified or closed.
