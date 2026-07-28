# Unified Backlog + Tech-Debt Model
*Status: accepted · Date: 2026-07-28*

## Context

`/dev`'s tech-debt tracker is a single aggregate Markdown file per repo,
`docs/dev/tech-debt.md`, with an `## Open` and a `## Closed` section holding `###` entries.
Its shape and the four procedures that operate on it (the carrying-cost test, recurrence-merge,
the silent-degrade rule, recurrence ranking) live in the shared contract
`plugins/dev/references/tech-debt.md`. That model has served ten cycles well, but two limitations
have shown up in practice:

1. **Plugin debt leaks into the wrong repo.** The tracker is strictly per-repo. When a `/dev`
   cycle running in *some other* repo surfaces a finding about the `/dev` plugin's own skills,
   the finding lands in *that* repo's `tech-debt.md`, not the plugin's. There is no routing, so
   debt about the plugin scatters across every repo the plugin runs in and is never collected
   where it can be acted on.
2. **There is no purpose-built backlog.** There is a home for deferred *findings* (the tracker)
   but none for deferred *intentions* — "I want to build X later." Those get misfiled into
   `docs/dev/product-plan.md`: today `debt-backfill` and `debt-linear-promotion` sit there as
   unfinished milestones, even though the product plan is meant to be an ephemeral per-project
   milestone carrier, not a standing backlog (see Decision 7). Without a backlog, the only
   alternative is a third-party system (Linear), which is heavy for solo/plugin work.

This cycle designs a single, durable **backlog + tech-debt store** that holds both kinds of item,
routes plugin-scoped items back to the plugin repo, and lets the user capture "save this to the
backlog" on demand — removing the need for Linear for personal and plugin work.

**Why this is an architecture cycle.** The hard part is entirely design: the storage shape,
naming, header schema, lifecycle, and cross-repo routing all carry open trade-offs, and several
of them (recurrence-merge under per-item storage; routing on a known-flawed discovery heuristic)
are load-bearing enough to be worth settling *before* any code is written. So Build produces this
one ADR — nine decisions, each with alternatives and rationale — and nothing else. Implementation,
migration execution, the capture skill, and the product-plan correction are each deferred to
follow-on feature cycles that react to this document (see Consequences).

**Grounding.** This ADR is written against the real files, not from memory:

- `plugins/dev/references/tech-debt.md` — the shared contract. Its Tracker file format, buffer
  format, recurrence-merge procedure, silent-degrade rule, mode-symmetry rule, and the
  "where a field ends" prose-parsing rules are the parity floor every decision below measures
  against.
- `docs/dev/tech-debt.md` — the live tracker, with three Open entries (*Autopilot doesn't
  cross-note the spec grounding gate*; *A nested product plan cannot outlive its parent*;
  *dev:reflect dogfood shortcut can open a PR against a fork's upstream*) and several Closed
  entries. These are the concrete rows Decision 8's migration must carry.
- `docs/dev/product-plan.md` — the live multi-project plan, "Cycles completed: 3/5", spanning
  three unrelated projects, with the two misfiled backlog items named above still unchecked.
  Decision 7 corrects the model this file embodies.
