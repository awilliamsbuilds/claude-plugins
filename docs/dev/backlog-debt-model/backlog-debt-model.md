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

## Decision 2 — File naming / identity

**Decision.** An item's identity is a **stable kebab-case slug**, fixed at creation and unchanged
for the item's life. The filename is **`<type>-<slug>.md`** where `type ∈ {debt, backlog}` — e.g.
`debt-autopilot-grounding-gate.md`, `backlog-debt-backfill.md`. The filename encodes **type**, but
**not status**: status lives in the header (Decision 3) and, terminally, in the `closed/` location
(Decision 1). Slugs must be unique within the tree; on a collision, disambiguate on the way in by
appending the first cycle name — `debt-<slug>-<first-cycle>.md` — reusing the contract's existing
title-collision instinct.

**The user's stated leaning was per-item files whose names reflect status.** This ADR adopts the
per-item files but **declines status-in-filename**, resolving the leaning at the coarse level that
actually matters (open vs. closed, via the `closed/` archive) rather than the fine-grained level
that churns.

**Alternatives considered.**

- **Status in the filename** (e.g. `debt-open-<slug>.md` → `debt-closed-<slug>.md`, or a
  `docs/backlog/open/` ↔ `docs/backlog/closed/` move on every transition). What it buys: `ls` alone
  tells you an item's status. What it costs: a **rename on every lifecycle transition**. With the
  four-state lifecycle of Decision 4 (open → in-progress → promoted → closed), an item's path would
  change up to three times. Each rename breaks any cross-reference to the file (a `possibly_related_to`
  pointer, a commit that mentions the path, a `promoted_to` back-link), fragments `git log` history
  for the item, and turns a status change — logically a one-field edit — into a path mutation that
  every reader must chase. The status is one `grep` of the header away; encoding it in the name buys
  legibility that the header already provides and pays for it in churn.

- **Type also omitted** (filename is just `<slug>.md`, type read only from the header). What it buys:
  even less to rename, and no prefix to keep in sync if type is re-judged. What it costs: `ls debt-*.md`
  no longer works — listing "all debt" or "all backlog" from the shell requires reading headers.
  Type is far more stable than status (it changes rarely, and only by deliberate re-judgement), so the
  prefix's sync cost is near zero while its greppability payoff is real. Type stays in the name; status
  does not.

**Identity across the lifecycle.** The slug never changes. On close, the file moves from
`docs/backlog/<type>-<slug>.md` to `docs/backlog/closed/<type>-<slug>.md` — same basename, new
directory — so `git log --follow` and `grep -r docs/backlog/` both still find it, and a
`possibly_related_to: <slug>` pointer stays valid because it references the slug, not the path.

If Decision 1 had chosen aggregate-only, a filename scheme would be N/A and items would be
identified by unique `###` titles within the file (as today's tracker requires). It did not; the
slug is the identity.

## Decision 3 — Header schema

**Decision.** Each item file carries a **YAML front-matter block** for structured metadata,
followed by a **Markdown body** in the current tracker's bold-label prose shape.

```markdown
---
type: debt              # debt | backlog
scope: repo             # repo | plugin
status: open            # open | in-progress | promoted | closed
first_recorded: 2026-07-21
cycles: [spec-grounding-and-clock]
recurrence: 1
files:
  - plugins/dev/skills/autopilot/SKILL.md
possibly_related_to:    # optional — slug of a suspected duplicate (Decision 4)
routing: delivered      # optional — delivered | pending (Decision 5), plugin-scope only
promoted_to:            # optional — path of the product-plan an item spawned (Decision 7)
closed: 2026-07-22      # optional — set on close
closed_by:              # optional — cycle name that closed it
---

**What's wrong:** …          # debt body (unchanged prose fields)
**Why deferred:** …
**Done looks like:** …
```

Backlog items use `What:` / `Why:` / `Done looks like:` in the body instead of the debt trio; the
front-matter is identical across both types.

**The floor.** Today's Open meta line carries `First recorded`, `Cycles`, `Recurrence`, and the
body carries `**Files:**` (required), `**What's wrong:**`, `**Why deferred:**`, `**Done looks
like:**`, and optionally `**Possibly related to:**`. Every one of those survives — `first_recorded`,
`cycles`, `recurrence`, `files`, `possibly_related_to` move into front-matter; the prose fields stay
in the body verbatim. The Closed meta line's `Closed …` and `by cycle …` map to `closed` /
`closed_by`. Nothing today's header carries is dropped.

**The new fields the unified model needs:**

- `type` — `debt | backlog`. The single field that lets one tree hold both kinds (Decision 1).
- `scope` — `repo | plugin`. **This is the field Decision 5's routing keys on.** Named here so
  routing binds to it cleanly; legible and hand-correctable by editing one line.
- `status` — `open | in-progress | promoted | closed`. **This is the field Decision 4's lifecycle
  drives.** Named here so the lifecycle binds to it cleanly.

**Syntax: front-matter vs. the current bold-label prose.**

- **Chosen: YAML front-matter for structured fields + prose body.** Per-item files make front-matter
  clean — exactly one block per file, no ambiguity about which entry a field belongs to. It is still
  hand-editable plain text, and it **retires the fragile "where does a field end" machinery** in the
  contract (the rules about line-initial labels, mid-line bold-colon spans, and never terminating at
  a blank line). That machinery exists *only* because many multi-paragraph entries share one aggregate
  file; with one item per file and structured fields in front-matter, a value's extent is unambiguous.
  The narrative fields stay in the body in the same prose the tracker uses today, so migration
  (Decision 8) is a lift of existing text, not a rewrite of it.

- **Rejected: keep everything as bold-label prose** (just split across files). What it buys: zero
  parsing change — the existing field-boundary rules carry over unchanged. What it costs: it keeps a
  set of rules whose entire reason for existing (disambiguating packed entries in one file) is gone,
  and it leaves structured fields like `status` and `scope` as prose that every reader must parse out
  of a paragraph rather than read as a key. Front-matter is the better fit for fields that routing and
  lifecycle machine-read.

**Invariant carried forward:** `recurrence` still equals the number of names in `cycles`, maintained
together, `cycles` authoritative on disagreement (Decision 4). `files` remains **required** — it is
what `dev:spec`'s cross-check keys on (Decision 9), and an item without it is invisible at the one
moment it would be actionable.

## Decision 4 — Item lifecycle

**Decision.** Four status states drive the `status` field (Decision 3):

| State | Meaning | Applies to |
|-------|---------|------------|
| `open` | Recorded, not yet being acted on | debt + backlog |
| `in-progress` | A cycle is actively paying (debt) or building (backlog) it | debt + backlog |
| `promoted` | A backlog item too big for one cycle has spawned a product-plan (Decision 7) | backlog only |
| `closed` | Paid, built, dropped, or obsolete — archived to `docs/backlog/closed/` | debt + backlog |

**Legal transitions:**

```
open ──► in-progress ──► closed
  │                        ▲
  ├──► closed  (dropped / paid directly / obsolete)
  │
  └──► promoted ──► closed   (backlog only: plan spawned, then plan completes)
```

`open → in-progress` when a cycle picks the item up; `in-progress → closed` when it lands.
`open → closed` covers the direct paths the tracker already has (a debt paid inside the cycle that
found it, or a stale item dropped). `open → promoted` is backlog-only and one-way: a backlog item
big enough to span cycles spawns a product-plan (Decision 7), sets `promoted_to:`, and moves to
`promoted`; when that plan completes, the item goes `promoted → closed`. `closed` is terminal and
is the only state whose entry triggers the archival move to `docs/backlog/closed/` (Decision 1).

`in-progress` and `promoted` are the states the current open/closed binary lacks — they exist so a
backlog can show *what is being worked on* and *what has grown into a plan*, which a debt-only
tracker never needed.

**Recurrence-merge under per-item storage — resolved: the signal survives, by retargeting the
procedure.** This is the sharpest open trade-off in the cycle, so it is settled concretely rather
than left implied.

The current procedure, on flush, compares each buffered `## To Record` entry against the entries in
`## Open` *of one file*, and on a **clear match** (the `files` sets overlap **and** the described
defect is the same defect — both, never either) appends the cycle name to `Cycles:`, increments
`Recurrence:`, and folds new detail into `**What's wrong:**` by appending. On uncertainty it creates
a new entry carrying `**Possibly related to:**`. The bias is deliberately asymmetric: a visible
duplicate is cheap to merge by hand; a wrong merge silently destroys an entry.

Under per-item storage **all of that is preserved unchanged except the corpus**:

- The corpus becomes `docs/backlog/*.md` (active items, top-level glob) instead of the `## Open`
  section of one file. That directory *is* the set of open entries, so the scan sees exactly what it
  saw before.
- A **clear match** still means `files` overlap **and** same defect — now read from front-matter
  `files:` and the body, instead of `**Files:**` and `**What's wrong:**`. Same two-condition test.
- **On a clear match:** append the new cycle to the matched file's `cycles:`, bump `recurrence:`,
  and append new detail to its body — never replace. `recurrence` stays equal to `len(cycles)`.
- **On uncertainty:** create a new item file with `possibly_related_to: <slug>` pointing at the
  suspected duplicate. The bias to create-over-merge is unchanged and just as load-bearing: a
  duplicate file is visible in `ls` and cheap to merge; a wrong merge still silently destroys an item.
- **Never merge on topic/keyword similarity alone** — two items both mentioning "autopilot" or
  "state.json" are not thereby the same item. Carried over verbatim.

So per-item files do **not** fragment the "this keeps happening" signal. `recurrence` is a header
field on the item, and the merge step's corpus is the directory — the exact set the old scan read.
The recurrence *ranking* (sort by `recurrence` descending, ties broken by the most recent name in
`cycles`) also carries over, now computed across the directory's front-matter.

**Alternatives considered.**

- **Accept the loss of recurrence-merge** and let per-item capture always create a new file. Rejected:
  the contract calls recurrence one of the aggregate's real strengths the new model must not silently
  lose, and it costs nothing to keep — the corpus is right there in the directory.
- **Two states only (open/closed), as today.** Rejected: a backlog needs to express "being worked on"
  and "grew into a plan"; folding those into `open` would make `/dev:debt` unable to distinguish a
  fresh intention from one already under construction.

## Decision 5 — Cross-repo routing

**Decision.** An item's `scope:` field (Decision 3) is `repo` or `plugin`. A `repo`-scoped item stays
in the current repo's `docs/backlog/`. A `plugin`-scoped item belongs in the `/dev` plugin's own
`docs/backlog/` tree, and gets there by **writing the item file directly into the plugin repo's
checkout** — never by opening a pull request.

**Classification** happens at capture (Decision 6) and is **legible and hand-correctable**: `scope`
is one front-matter line. A misclassified item (repo-scoped tagged `plugin`, or the reverse) is fixed
by editing that line and moving the file to the right repo's tree — no tooling, no re-capture. This
directly answers the "Misclassification" edge case: the model makes the classification a visible,
editable field rather than an irreversible routing act.

**Delivery reuses `dev:reflect`'s portable plugin-source discovery** — the git-remote / plugin-cache
resolution that finds the plugin's source repo with no hardcoded path and no hardcoded marketplace
name. Routing does **not** invent a second discovery path; it calls the one the plugin already has.

**Designing around the known discovery flaw — not past it.** There is a live Open tracker entry,
*"dev:reflect dogfood shortcut can open a PR against a fork's upstream"*: the `origin`-slug ==
marketplace-slug heuristic misfires on a fork (a user's fork of the plugin repo has an `origin` slug
that matches the marketplace slug), and `gh pr create` then defaults its base to the fork's *upstream*
— a repo the user may not own. The dogfood gate verifies the current checkout, not the PR base. This
ADR treats that flaw as real and designs so routing cannot inherit it:

1. **No PR in the routing path.** A backlog/debt note is not a code change; delivering it does not need
   `gh pr create`. Routing writes the item **file** into the resolved plugin checkout's `docs/backlog/`.
   Removing the PR step removes the exact mechanism (`gh pr create` defaulting to upstream) that the
   open entry describes. The follow-on that implements routing is the natural place to **close** that
   entry, because routing supersedes the PR-based delivery it was filed against (noted in Consequences,
   not closed here — this is a design-only cycle).
2. **Confirm the target before writing.** Discovery resolves a *candidate* plugin repo; routing then
   **confirms the target** — surface the resolved repo path/slug and require confirmation, or accept an
   explicit target the user passed — before writing anything. Because the origin-slug heuristic can
   resolve a fork, the resolved target is treated as a proposal, not a fact. Confirmation is a human
   surface (the capture flow, Decision 6), consistent with the mode-symmetry carve-out for
   scope-affecting acts.

**The failure case, specified end to end** (Success Criteria + the "Plugin repo unreachable" edge
case). When a `plugin`-scoped item cannot be delivered — the plugin repo is **not present locally**,
or is present but **not writable**, or the target **cannot be confirmed**:

- The item is **recorded locally** in the current repo's `docs/backlog/` with `scope: plugin` and
  `routing: pending`.
- The `routing: pending` marker is **surfaced** — `/dev:debt` list (Decision 9) shows pending-routing
  items distinctly, so the user knows an item is waiting to go home.
- The item is **never silently dropped.** This mirrors the contract's silent-degrade discipline
  exactly, but for a *writer*: a reader degrades by printing nothing; a writer degrades by writing
  **locally plus a visible marker**, never by discarding.
- Delivery is retried later — on the next capture/sync when the plugin repo is reachable, or by the
  user moving the file by hand. On successful delivery the local copy's marker flips to
  `routing: delivered` (or the local placeholder is removed once the item lives in the plugin repo).

**Alternatives considered.**

- **PR-based delivery** (mirror `dev:reflect`'s dogfood path: open a PR against the plugin repo).
  Rejected: it inherits the fork/upstream flaw verbatim, and it is disproportionate — a debt note is
  not reviewable code and does not warrant a PR round-trip. Direct file-write with target confirmation
  is both safer and lighter.
- **Auto-write on resolved origin with no confirmation.** Rejected: this is precisely what the open
  entry warns against — a fork's `origin` resolves to a repo the user did not intend, and an
  unconfirmed write puts the item in the wrong repo. Confirmation is the guard.
- **Silently keep every plugin item local** (no routing, just a `scope` tag). Rejected: that is the
  status quo the cycle exists to fix — plugin debt scattered across repos, never collected where it
  can be acted on.

## Decision 6 — Capture skill shape

**Decision.** "Save this to the backlog" is a **new capture verb on the existing `/dev:debt` skill**
— `/dev:debt add` (accepting a free-text description, or invoked with no argument to prompt for one) —
**not a new `/dev:backlog` skill.** `/dev:debt` already owns every user-facing operation on this store
(reads, ranking, manual lifecycle changes); creation is one more manual lifecycle operation and belongs
with them. The skill is renamed in spirit to cover the unified store, but the invocation stays
`/dev:debt`.

**How capture sets `type` and `scope`:**

- **`type`** — `debt | backlog`. Defaults to **`backlog`** on manual `/dev:debt add`, because the
  on-demand "save this to build later" is an *intention*. (The automatic buffer→flush path of the
  producing stages defaults the other way — `debt` — because those write *findings*; see Decision 9.)
  Overridable inline (`/dev:debt add --debt …` or a prompt).
- **`scope`** — `repo | plugin`. Defaults to **`repo`**; override to `plugin` (`--plugin`) when the
  item is about the `/dev` plugin's own skills. A `plugin` scope triggers the Decision 5 routing flow,
  including target confirmation and the local-degrade failure case.

Capture writes the front-matter (Decision 3), sets `status: open` (the initial lifecycle state,
Decision 4), assigns the `<type>-<slug>.md` filename (Decision 2) with collision disambiguation, and —
before writing a `plugin`-scoped item — runs the Decision 5 confirm-target step. On capture it also
runs the **recurrence-merge scan** (Decision 4) against `docs/backlog/*.md`, so a manually captured
item that duplicates an existing one merges (or creates-with-`possibly_related_to`) exactly as an
auto-flushed one does.

**Extend `/dev:debt` vs. a new skill — the argument.**

- **Chosen: extend `/dev:debt`.** It already reads and closes items and owns the store's user surface;
  adding create keeps one skill authoritative over one store. A user thinks "debt/backlog stuff →
  `/dev:debt`", and the read/rank/close/add verbs sit together where the store-shape knowledge already
  lives.
- **Rejected: a new `/dev:backlog` skill.** It would split ownership of one store across two skills, so
  the store-shape knowledge (front-matter, naming, tree layout, recurrence-merge) would live in two
  places and drift — the same second-copy-drifts failure the contract warns about elsewhere. The
  debt-vs-backlog distinction is a `type` field, not a reason for a second skill.

**Design-only.** This section decides the capture flow's *shape*; it does **not** write a `SKILL.md`.
Building `/dev:debt add` is a follow-on cycle (Consequences), which is also where the exact argument
syntax and prompts are finalized against the real skill.

## Decision 7 — Product-plan boundary + correction

**The corrected model.** A product-plan is an **ephemeral milestone carrier for a single multi-cycle
project, deleted on completion.** It is *not* a backlog and *not* a debt tracker: it holds the ordered
milestones of one project while that project is in flight, and it is removed when the project is done.
The backlog (`docs/backlog/`, this ADR) is the standing store of intentions and findings; a
product-plan is the transient decomposition of *one* intention that grew large enough to need cycles.

**This is a correction, not a description.** Today's *top-level* `docs/dev/product-plan.md` behaves the
opposite way: it **survives cycles** (nothing ever deletes it — verified in the spec's grounding
inventory: a grep for `rm .*product-plan` across all `dev:*` skills returned zero hits, and `dev:done`
Step 3 only checks boxes), and the live one spans **three unrelated projects** (voice tooling,
depersonalizing the writing plugin, tech-debt tracking) at "Cycles completed: 3/5". It has been serving
as a de-facto multi-project backlog — which is exactly the misfiling this cycle corrects. The corrected
model **changes current top-level behavior**: a product-plan will no longer be a durable multi-project
list; that role moves to `docs/backlog/`.

**What happens to the existing multi-project plan: migrate its unfinished items, then retire the file.**

- Its **two unfinished items** — `debt-backfill` and `debt-linear-promotion` — are backlog *intentions*
  misfiled here. They migrate into `docs/backlog/` as `type: backlog` items (Decision 8 handles the
  physical migration).
- Its **three completed milestones** (voice-extractor, depersonalize-writing, tech-debt-tracking, all
  `[x]`) are historical; each already has its record in the cycle history and decision logs. They are
  **not** carried into the backlog (a backlog holds *open* intentions, not a changelog).
- With its unfinished items rehomed, the top-level `product-plan.md` is **retired** — not kept as a
  standing multi-project list, because that role is now the backlog's. The retirement is a follow-on
  action (Decision 8 / Consequences), not this cycle.

**The one-way backlog → product-plan promotion flow.** A backlog item big enough to span cycles is
**promoted**: it spawns a `product-plan.md` for that one project, the backlog item's `status` becomes
`promoted` (Decision 4), and `promoted_to:` points at the spawned plan. The flow is one-way — a plan
never demotes back to a backlog item. When the project completes, the plan is **deleted** (the corrected
ephemeral behavior) and the backlog item moves `promoted → closed`. Promotion is the seam where the
corrected "deleted on completion" behavior actually bites, so the follow-on that implements deletion is
the same one that implements promotion.

**Relation to the open entry "A nested product plan cannot outlive its parent."** That Open tracker
entry sits on this exact surface: a nested plan at `docs/dev/<parent>/product-plan.md` is deleted by
`dev:done` Step 7's `rm -rf` of the cycle directory, so a plan meant to be durable dies inside a
directory designed to be destroyed. The corrected model bears on it directly: a promoted product-plan
must live somewhere that survives for the project's life and is deleted *on project completion*, not on
the parent cycle's teardown — i.e. **not** inside `docs/dev/<parent>/`. The implementing cycle (which
builds promotion + deletion) is the natural place to **close** that entry. This ADR does **not** close
it — a design-only cycle cannot pay implementation debt (noted in Consequences).

**Alternatives considered.**

- **Fold the product-plan into the backlog entirely** (no separate plan concept). Rejected: a
  multi-cycle project needs an ordered milestone decomposition that a flat backlog of items does not
  express; promotion gives the item a place to grow without turning the backlog into a project planner.
- **Keep the top-level plan as the multi-project backlog** and only add a debt store. Rejected: that
  leaves the misfiling in place — intentions still live in a file that also pretends to be a
  single-project plan — and never gives "save this to build later" a correct home.
- **Archive the existing plan wholesale** (keep the file, mark it done). Rejected: its two unfinished
  items are real open intentions that must not be lost; they belong in the backlog, not frozen in a
  retired file.
