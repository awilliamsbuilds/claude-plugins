---
type: debt
scope: repo
status: open
first_recorded: 2026-07-28
cycles: [backlog-debt-model]
recurrence: 1
files:
  - plugins/dev/skills/build/SKILL.md
  - plugins/dev/skills/plan/SKILL.md
---

**What's wrong:** When an ADR decision hinges on a cross-boundary delivery/write mechanism (e.g. getting a plugin-scoped item from one repo into another), the automated design process (`dev:build` ADR authoring, reinforced by the plan/spec challenger lenses) does not force enumeration of concretely *different* transports, nor grounding of each candidate's target against the real runtime/install environment. In the backlog-debt-model cycle, Build committed to writing item files directly into the plugin's checkout; that transport had no valid target (the installed plugin is a non-git, SHA-keyed cache), and both the flaw *and* the winning fix (GitHub issues as a triage inbox) came from the user during Validate — the issues transport was never in the automated candidate set. The ADR "alternatives considered" discipline was satisfied on paper, but the initial candidate set for the load-bearing mechanism was too narrow until a human widened it.
**Why deferred:** Surfaced in dev:reflect; the user declined an immediate skill edit. It is a process/design-net gap rather than a defect in this cycle's shipped ADR (which is clean), so it is recorded rather than patched into the completing cycle.
**Done looks like:** Architecture-cycle guidance requires, for any decision that hinges on a cross-boundary delivery/write mechanism, (a) at least two concretely different transports enumerated (not variants of one), and (b) each candidate's target grounded against the real runtime/install environment before a transport is chosen — so the load-bearing mechanism is pressure-tested up front rather than discovered as flawed in Validate.
