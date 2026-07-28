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

## Decision 1 — Storage model

**Decision.** Move to **per-item files**: one Markdown file per item, in a single shared
`docs/backlog/` tree. Debt and backlog items live in the **same tree**, distinguished by a
`type:` header field (Decision 3), not by separate directories. Active items sit flat in
`docs/backlog/`; a closed item is archived to `docs/backlog/closed/` — the one and only
file move in an item's life, made on close, not on every transition.

```
docs/backlog/
  debt-<slug>.md         # active debt item
  backlog-<slug>.md      # active backlog intention
  closed/
    debt-<slug>.md       # archived, status: closed
    backlog-<slug>.md
```

The recurrence-merge corpus (Decision 4) is exactly `docs/backlog/*.md` — the top-level,
non-recursive glob — so a merge scan sees active items and is never diluted by the closed archive.

**Alternatives considered.**

- **Keep the single aggregate** (`docs/dev/tech-debt.md`, one file, `## Open` / `## Closed`).
  What it buys: a one-file overview, and a recurrence-merge scan that is a single-file read. What
  it costs: cross-repo routing becomes text surgery — to send a plugin finding home you must
  extract one `###` entry from a file and splice it into another repo's file, preserving that
  file's section structure; and there is no natural place for backlog items without either a third
  section that overloads the file or a parallel second aggregate. Routing is the whole reason this
  cycle exists, and the aggregate makes the movable unit a *fragment of a file* rather than a file.

- **Hybrid** — per-item files for content plus a generated aggregate index. What it buys: per-item
  movability *and* a one-file overview. What it costs: the index is a second copy of the truth that
  drifts on every hand-edit, and the contract already forbids exactly this shape elsewhere (the
  per-key write-mode rule bans a standing registry table "which would be a second copy that drifts").
  The overview is recoverable on demand from the directory (`/dev:debt` list, Decision 9), so the
  standing index earns its drift risk nothing.

**Confronting the aggregate's real strengths** (Success Criteria requires this — the new model must
not silently lose them):

- **Hand-editability.** *Preserved, arguably improved.* Each item is a small self-contained file
  instead of one entry buried in a growing aggregate; editing one item no longer risks the
  "where does a field end" ambiguity that only exists because many entries share one file.
- **Greppability.** *Preserved.* `grep -r docs/backlog/` searches every item; `ls docs/backlog/debt-*.md`
  lists all active debt; the closed archive is one `grep -r docs/backlog/closed/` away. The one
  thing lost — reading every entry by opening a single file — is replaced by listing a directory,
  which `/dev:debt` already fronts.
- **Recurrence-merge.** *Preserved by retargeting, not by shape.* The procedure scanned one file
  because that file *was* the corpus of open entries; it now scans `docs/backlog/*.md`, which *is*
  that same corpus. Recurrence is carried as a per-item header field (Decision 3), so the "this
  keeps happening" signal is a property of the item, not of the aggregate's single-file layout.
  Decision 4 specifies the retargeted procedure in full; the point here is that per-item storage
  does not fragment the signal, because the merge step's corpus is the directory.

**Debt and backlog share one tree** rather than splitting into `docs/debt/` and `docs/backlog/`.
Rationale: the two kinds share their header schema, lifecycle, routing, and capture flow — a split
would duplicate all four sets of rules and force a directory commitment at capture time, when an
item's `type` can legitimately be re-judged (a "build X" intention that turns out to be a debt fix,
or vice versa). One tree filtered by a `type:` field means one set of rules and a type change is a
one-field edit, not a file move across trees.

**Technical Constraints honored.** Plain Markdown, hand-editable without tooling; fits the
`references/` shared-contract pattern (the contract is rewritten for this store in a follow-on, per
Decision 9); writes are worktree-relative like every other `/dev` artifact.
