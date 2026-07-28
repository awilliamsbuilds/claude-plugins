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
routing: pending        # optional — set only on a local-degrade hold (Decision 5), plugin-scope only
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
in the current repo's `docs/backlog/`. A `plugin`-scoped item belongs to the `/dev` plugin's own
store — and it gets there by **opening a GitHub issue in the plugin repo**, which serves as a
**triage inbox** the maintainer later converts into a `docs/backlog/` file. Routing **never** writes
into another checkout and **never** opens a pull request.

**Why an issue — not a file-write, not a PR.** The plugin, *as installed*, has no committable working
tree. The marketplace `github` source materializes it as a content-addressed cache under
`~/.claude/plugins/cache/…`, keyed by commit SHA — verified on disk: **not a git repo** (no `.git`,
no remote), versioned side-by-side by SHA (so a write is orphaned on the next `/plugin update`), and
it does **not** even carry the repo's `docs/` tree. So "write the item file into the plugin's
checkout" has **no valid target in the very case routing exists for** — a cycle running in *another*
repo. The one place a file-write would stick, a local *source* checkout, exists only in the dogfood
case, which needs no routing at all. The only durable destination is the plugin's **GitHub repo**,
and its native surface for "a thing to act on here" is an **issue**. An issue also sidesteps the
fork/upstream flaw **by construction**: that flaw is specific to `gh pr create` defaulting its *base*
to a fork's upstream — **issues have no base branch**, so an issue created against an explicit
`--repo` lands there and nowhere else.

**The target is read, not guessed.** The destination is the slug the marketplace registration already
names — `extraKnownMarketplaces.<marketplace>.source.repo` (here `awilliamsbuilds/claude-plugins`) —
passed explicitly to `gh issue create --repo <slug>`. This is the non-guessing source of truth: it is
**not** inferred from the foreign repo's `origin`, so a foreign remote can never misdirect delivery.
If the marketplace itself was registered from a fork, that field *names the fork* — the correct home —
and the explicit target keeps the issue in the fork, never its upstream. Delivery uses the
`GITHUB_PERSONAL_ACCESS_TOKEN` the repo already requires, so it works **from any repo without a local
plugin checkout**.

**Classification** happens at capture (Decision 6) and is **legible and hand-correctable**: `scope`
is one front-matter line. A misclassified item (repo-scoped tagged `plugin`, or the reverse) is fixed
by editing that line — and, if it was already delivered as an issue, closing that issue — no tooling,
no re-capture. This
directly answers the "Misclassification" edge case: the model makes the classification a visible,
editable field rather than an irreversible routing act.

**The inbox is an inbox, not a terminal home.** A routed issue is a *queue entry*, not the item's
final resting place. The maintainer, working in the plugin repo, drains the queue — one label filter,
`gh issue list --label <dev-backlog> --state open` — by **converting** each issue into a
`docs/backlog/<type>-<slug>.md` file (lifting the front-matter block the issue body carries) and
closing the issue with a reference to the file, or by simply fixing and closing it. `docs/backlog/`
remains the single authoritative store *within* the plugin repo; the issue tracker is only the
cross-repo transport into it. (The `/dev:debt` convert verb that fronts this is Decisions 6 and 9;
design-only here. The exact label set is left to the implementing cycle — the design requires only
*a* stable label + slug marker to filter and dedup on.)

**Dedup is two-layer, so the inbox stays bounded — this is the scalability guarantee.**

- **At intake**, before opening an issue, search open inbox issues for the item's slug marker
  (`gh issue list --search`). On a hit, **add a comment** ("recurred in `<repo>` on `<date>`") instead
  of a duplicate — the same create-over-merge bias the recurrence-merge procedure uses, and a comment
  is a richer recurrence log than a bumped counter. This keeps the *open-issue queue* free of
  duplicates.
- **At conversion**, the item is merged into `docs/backlog/*.md` under the ordinary recurrence-merge
  procedure (Decision 4): `files` overlap **and** same defect → bump `recurrence:` on the existing file
  and close the issue **without** creating a new file. This catches recurrences whose earlier issue was
  already converted-and-closed (and is therefore invisible to the intake search over *open* issues).

Intake dedups the queue cheaply; conversion dedups against the authoritative store. The queue is
drained by triage and cannot grow unbounded — the two failure modes of a naive inbox (duplicate
entries, and unbounded accumulation) are both closed.

**Dogfood exception.** When a cycle runs *inside the plugin repo itself* (`git remote get-url origin`
resolves to the marketplace slug — as in this very cycle), a `plugin`-scoped finding is already home:
it is written straight to the local `docs/backlog/` as an ordinary file. No issue, no conversion — it
never left.

**The failure case, specified end to end** (Success Criteria + the "Plugin repo unreachable" edge
case). When a `plugin`-scoped item cannot be delivered as an issue — **no network, no auth, the
GitHub API call fails, or the target slug cannot be resolved**:

- The item is **recorded locally** in the current repo's `docs/backlog/` with `scope: plugin` and
  `routing: pending`.
- The `routing: pending` marker is **surfaced** — `/dev:debt` list (Decision 9) shows pending-routing
  items distinctly, so a stranded item is visible.
- The item is **never silently dropped.** This mirrors the contract's silent-degrade discipline
  exactly, but for a *writer*: a reader degrades by printing nothing; a writer degrades by writing
  **locally plus a visible marker**, never by discarding.
- Delivery is **retried** on a later capture/sync when the API is reachable, or the user files it by
  hand. On success the local `pending` copy is **removed** — the item now lives as an issue in the
  plugin repo. In the healthy path there is **no lingering copy** in the foreign repo: the item lives
  in exactly one place, upholding the anti-scatter goal.

**Alternatives considered.**

- **Direct file-write into the plugin's checkout** (the intuitive first design, and this ADR's own
  earlier draft). Rejected on inspection of the real install layout: the installed plugin is a
  non-git, SHA-keyed cache with no `docs/` tree, so there is **nothing committable to write to** in
  the cross-repo case; and the one place a write *would* stick — a local *source* checkout — is
  exactly the dogfood case that needs no routing. A file-write is a dead drop everywhere routing
  actually fires. (This is the P2 that reopened validation; the issue-inbox model replaces it.)
- **PR-based delivery** (open a PR against the plugin repo). Rejected: heavier than a debt note
  warrants — a note is not reviewable code — and a PR is the one mechanism that carries the
  fork/upstream base-defaulting flaw. An issue is lighter and, having no base branch, cannot be
  misdirected.
- **Reuse `dev:reflect`'s discovery and confirm a guessed target.** Rejected: the fork flaw lives in
  *guessing* the target from a local `origin`, not in the delivery verb. Reading the explicit slug
  from the marketplace config removes the guess outright, so no per-item confirmation prompt is
  needed — the target is known, not proposed.
- **Silently keep every plugin item local** (a `scope` tag, no routing). Rejected: that is the status
  quo the cycle exists to end — plugin debt scattered across every repo, never collected where it can
  be acted on.

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
  item is about the `/dev` plugin's own skills. A `plugin` scope triggers the Decision 5 routing flow —
  an issue into the plugin repo (or the dogfood-local / degrade-to-pending paths), no confirmation
  prompt, because the target slug is read from the marketplace config, not guessed.

Capture writes the front-matter (Decision 3), sets `status: open` (the initial lifecycle state,
Decision 4), assigns the `<type>-<slug>.md` filename (Decision 2) with collision disambiguation, and —
for a `plugin`-scoped item off the plugin repo — runs the Decision 5 issue-delivery step (with its
intake dedup and degrade-to-pending fallback). On capture it also
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

## Decision 8 — Migration design

Design only — a follow-on cycle executes it (Out of Scope). This section maps every existing deferred
item onto the target model (Decisions 1–4, 7) concretely enough that the follow-on can run it without
re-deciding.

**(a) `tech-debt.md` Open entries → active item files.** Each `###` entry in `## Open` becomes one
`docs/backlog/debt-<slug>.md`, `status: open`, `type: debt`, `scope: repo` (all three current Open
entries are about the plugin's own skills, but scope is set to `repo` on migration and re-judged by
hand — migration does not silently reclassify; Decision 5 makes `scope` a hand-editable line). The
meta line maps to front-matter, the body prose transfers verbatim:

| Current Open entry | New file | front-matter derived from |
|---|---|---|
| Autopilot doesn't cross-note the spec grounding gate | `debt-autopilot-grounding-gate.md` | `first_recorded: 2026-07-21`, `cycles: [spec-grounding-and-clock]`, `recurrence: 1`, `files: [plugins/dev/skills/autopilot/SKILL.md]` |
| A nested product plan cannot outlive its parent | `debt-nested-product-plan-lifetime.md` | `first_recorded: 2026-07-22`, `cycles: [tech-debt-tracking]`, `recurrence: 1`, `files: [plugins/dev/skills/spec/SKILL.md, plugins/dev/skills/done/SKILL.md]` |
| dev:reflect dogfood shortcut can open a PR against a fork's upstream | `debt-reflect-dogfood-pr-base.md` | `first_recorded: 2026-07-28`, `cycles: [reflect-repo-discovery]`, `recurrence: 1`, `files: [plugins/dev/skills/reflect/SKILL.md]` |

**(b) `tech-debt.md` Closed entries → `docs/backlog/closed/`.** Each `## Closed` entry becomes
`docs/backlog/closed/debt-<slug>.md`, `status: closed`, with `closed:` and `closed_by:` taken from the
Closed meta line (`*Closed YYYY-MM-DD by cycle <name> · First recorded: … · Recurrence: N*`). The seven
current Closed entries (hardcoded reflect path; spec product-plan push-to-main; feature-slug allowlist;
gate-path state-write sweep; validate fix-loop verification; the config-contract wording entry; and the
stale-`loops_max` entry) migrate the same way — meta line to front-matter, body verbatim.

**(c) Misfiled `product-plan.md` items → backlog intentions** (per Decision 7):

| Product-plan item | New file | front-matter |
|---|---|---|
| `debt-backfill` | `backlog-debt-backfill.md` | `type: backlog`, `scope: repo`, `status: open`, `first_recorded: 2026-07-21` (the plan's Created date, the best available provenance), `cycles: []`, `recurrence: 0`, `files: []` (an intention has no defect site yet — `files` is required by schema but legitimately empty for a not-yet-built backlog item) |
| `debt-linear-promotion` | `backlog-debt-linear-promotion.md` | same shape |

Their descriptive prose (including the "Depends on tech-debt-tracking" note and the deferral rationale)
transfers into the body under `What:` / `Why:`. Note the slugs keep their existing `debt-` *names* even
though `type: backlog` — the name is historical; the `type` field, not the slug, classifies them.

**Migration collisions** (the edge case). The `<type>-` filename prefix means a `debt-*` item and a
`backlog-*` item never collide even with the same slug. Within one type, a duplicate slug is resolved
by the contract's existing instinct: **append the first cycle name** — `debt-<slug>-<first-cycle>.md`.
Where a migrated item has no cycle (the two backlog intentions have `cycles: []`), disambiguate by
appending a short qualifier from the source instead (e.g. `-from-product-plan`). Migration must apply
this on write, exactly as the recurrence-merge procedure's create-bias makes near-duplicate titles the
expected steady state today.

**Execution is a follow-on cycle.** This section is the map; running it (creating the files, retiring
`tech-debt.md` and the top-level `product-plan.md`, verifying counts) is deferred (Consequences).

## Decision 9 — Producing-stage integration

Design-level: name each seam and the change it needs; **do not edit any skill** (Out of Scope). This
section is where the cross-skill ripple is enumerated **in one place**, so the follow-on Build changes
a known list rather than discovering seams piecemeal.

**The current seams** (from the contract's "Where things live"):

- Producing stages `dev:build`, `dev:validate`, `dev:reflect`, `dev:spec` **append** to the per-cycle
  buffer `docs/dev/<feature>/debt-pending.md`.
- `dev:done` Step 6a **flushes** the buffer into `docs/dev/tech-debt.md`; Step 7 then deletes the cycle
  directory (and the buffer with it).
- `dev:init` **creates** the tracker in a fresh repo.
- `dev:reflect` invoked **standalone** (after the cycle directory is gone) appends **directly** to the
  tracker.
- `dev:spec` Step 7 **cross-checks** current debt against the cycle's files, and writes a `## To Close`
  bullet when the cycle pays an entry.
- `dev:debt` **reads, ranks, and closes**.

**The integration map — every skill the follow-on must change:**

| Skill | Current behavior | Change under the new store |
|---|---|---|
| `dev:init` | Creates `docs/dev/tech-debt.md` with the canonical H1 header | Seed the `docs/backlog/` tree (and `docs/backlog/closed/`) instead — a directory with a `README.md` stating the store's contract, no single tracker file |
| `dev:build` | Appends `###` entries to `debt-pending.md` | **Buffer survives.** Append front-matter'd items (Decision 3) to the buffer, `type: debt` default; unchanged trigger (the carrying-cost test) |
| `dev:validate` | Appends `###` entries to `debt-pending.md`, tagged `*Source: dev:validate (P3\|Nit)*` | Same — front-matter'd items into the buffer; the `Source`/severity tag carries as a front-matter field |
| `dev:reflect` | Appends to buffer (in-cycle) or directly to the tracker (standalone) | In-cycle → buffer as above; standalone → write item file(s) directly into `docs/backlog/` (no buffer exists) |
| `dev:spec` | Step 7 cross-check parses `## Open` entries; writes `## To Close` bullet | Cross-check scans `docs/backlog/*.md` front-matter `files:` (Decision 3); "close" a paid item = set `status: closed` + move to `closed/` (Decision 1/4) rather than a bullet in a buffer section |
| `dev:done` | Step 6a flushes buffer → one tracker file; Step 7 deletes cycle dir | Flush writes **one file per buffered item** into `docs/backlog/`, running recurrence-merge (Decision 4) against `docs/backlog/*.md`; a `scope: plugin` item off the plugin repo is delivered per Decision 5 (`gh issue create` into the inbox, or `routing: pending` on degrade) instead of a local file |
| `dev:debt` | Reads/ranks/closes the aggregate; user-invoked | Reads the directory, ranks by front-matter `recurrence:`, closes by editing `status:` + moving to `closed/`; **gains `add` (Decision 6)**; surfaces `routing: pending` items (Decision 5); **gains an inbox/convert verb** — list open inbox issues in the plugin repo and convert each into a `docs/backlog/` file, running recurrence-merge on conversion (Decision 5) |
| `references/tech-debt.md` | The shared contract for the aggregate | **Rewritten** for the new store: front-matter schema replaces the "where a field ends" prose-parsing rules; the buffer/flush/recurrence-merge/silent-degrade/mode-symmetry sections are retargeted to per-item files |

`dev:autopilot` writes no debt itself (it orchestrates and delegates), so it needs **no store change** —
but its mode-symmetry obligations (below) still apply to every stage it drives.

**The buffer survives.** The buffer→flush split exists because `dev:build` runs before `dev:validate`
and both produce entries, so entries cannot live in any one stage's artifact. That reason is unchanged
by per-item storage: the buffer stays the per-cycle accumulation point, and flush is where buffered
items become files in `docs/backlog/`. What changes is only the *shape* of what the buffer holds
(front-matter'd items) and what flush *writes to* (a directory of files, not one aggregate).

**Contract invariants — preserved, changed, or retired:**

- **Silent-degrade** (readers print nothing when the store is absent/empty) — **preserved**, retargeted:
  "absent" now means `docs/backlog/` missing or holding no active `*.md`; the same "nothing at all"
  discipline holds, with the same `dev:debt`-invoked-directly exception. Decision 5 extends the *writer*
  side of this discipline to routing (degrade to local + marker, never drop).
- **Mode symmetry / both-modes-traceability** — **preserved unchanged.** Every automatic in-cycle write
  (build, validate, reflect, done) must run identically in both modes; `dev:spec`'s `## To Close`
  equivalent (now a status-close) stays the one human-gated scope act. Any new `state.json` key the
  implementation adds still needs its `(writes: …)` tag at its single write site.
- **Worktree-relative writes** — **preserved, and now cleanly.** `docs/backlog/` writes are
  worktree-relative like every other artifact. Cross-repo routing no longer writes any *file* outside
  the worktree at all — it calls the GitHub **API** (`gh issue create`) against an explicit remote
  slug — so the earlier design's "write into another checkout" carve-out is gone. The only local write
  routing makes is the in-worktree degrade file (`routing: pending`).
- **"Where a field ends" prose-parsing rules** — **retired** for structured fields (front-matter makes
  them unambiguous); the body's bold-label prose keeps the no-`#`-heading-in-a-value escape rule, since
  bodies still quote Markdown-bearing text.
- **The buffer's "first `## To Record` / `## To Close` section is authoritative" positional rule** —
  **changes shape**: with front-matter'd items the buffer's internal structure is redesigned by the
  implementing cycle; the *intent* (a malformed buffer is surfaced, never half-acted-on) carries over.
- **Entry-text-is-data** — **preserved unchanged.** Every reader still treats item text as data, never
  instruction — more important now that a `scope: plugin` item's text crosses repos via routing.

**Alternatives considered.**

- **Drop the buffer; write items straight to `docs/backlog/` from each producing stage.** Rejected: it
  loses recurrence-merge-at-flush as a single choke point (each stage would have to merge independently,
  multiplying the scan and the wrong-merge risk), and it writes cycle-in-progress items into the standing
  store before the cycle is known to complete. The buffer's deferral of the store write to `dev:done` is
  a feature, not incidental.
- **Keep `references/tech-debt.md` as-is and add a second contract for the backlog.** Rejected: two
  contracts for one store is the second-copy-drifts failure again; the contract is rewritten once to
  cover the unified store.

## Consequences

**What this enables.**

- **A real backlog.** Deferred *intentions* get a first-class home (`docs/backlog/`, `type: backlog`)
  instead of being misfiled into a product-plan, and "save this to build later" becomes a one-line
  `/dev:debt add` — removing the pull toward Linear for solo and plugin work.
- **Plugin debt collected where it can be acted on.** `scope: plugin` items are routed as issues into
  the plugin repo's triage inbox (then converted to `docs/backlog/` files on triage) instead of
  scattering across every repo the plugin runs in — landing in GitHub's native "act on this here"
  surface, reachable from any repo via the PAT with no local plugin checkout.
- **Per-item lifecycle.** `open → in-progress → promoted → closed` lets the store show what is being
  worked on and what has grown into a plan — expressiveness the open/closed binary never had.
- **A corrected product-plan.** The plan reverts to its true role — an ephemeral single-project
  milestone carrier, deleted on completion — and the backlog absorbs the standing-list role it had
  drifted into.

**What this forecloses / costs.**

- **The single-file overview is gone.** No one file shows all debt at a glance; that view is now
  reconstructed on demand by `/dev:debt` listing the directory. Accepted deliberately (Decision 1).
- **A new dependency on YAML front-matter parsing** in every reading skill, replacing the bespoke
  prose-field machinery. Simpler overall, but it is a real format change every consumer must adopt at
  once (Decision 9).
- **A cross-repo API call** (routing an issue into the plugin repo) is a genuinely new capability with
  its own failure surface — network and auth — mitigated by the local degrade-to-`pending` fallback
  (Decision 5). And it splits the store across two media for the inbound plugin subset: those items are
  GitHub **issues** until triage converts them to files, so they are not hand-editable `docs/backlog/`
  Markdown while queued (queried via `gh issue` instead of `grep`). Accepted deliberately: across a
  repo boundary a transport is unavoidable, and an issue is the honest one.

**The follow-on cycles this ADR requires** (implementation is entirely deferred — this cycle is
design-only):

1. **Store implementation + producing-stage edits + contract rewrite.** Build `docs/backlog/`, rewrite
   `references/tech-debt.md` for the new store, and update every seam in Decision 9's integration map
   (`dev:init`, `dev:build`, `dev:validate`, `dev:reflect`, `dev:spec`, `dev:done`, `dev:debt`).
2. **Migration execution.** Run Decision 8's map: create the item files, retire `docs/dev/tech-debt.md`
   and the top-level `docs/dev/product-plan.md`, verify counts.
3. **The capture + inbox verbs.** Build `/dev:debt add` per Decision 6 (type/scope defaults,
   recurrence-merge on capture, the plugin issue-routing hook of Decision 5) **and** the inbox/convert
   verb that drains open plugin-repo issues into `docs/backlog/` files (Decision 5).
4. **Product-plan deletion + promotion.** Implement the corrected ephemeral behavior and the one-way
   `backlog → product-plan` promotion (Decision 7) — the seam where "deleted on completion" bites.

These may be sequenced or combined, but the storage/contract cycle (1) must land before migration (2)
and capture (3), which both target the store it defines.

**Related open tracker entries** (this ADR notes them; a design-only cycle does not pay them):

- ***"A nested product plan cannot outlive its parent"*** — **closed** by the product-plan correction
  cycle (follow-on 4), which defines a durable, project-lifetime plan location — exactly what that
  entry asks for (Decision 7).
- ***"dev:reflect dogfood shortcut can open a PR against a fork's upstream"*** — **not closed by
  routing** (routing uses issues, which have no base, and never touches `dev:reflect`'s skill-edit PR
  path). But Decision 5 establishes the fix *pattern* that entry needs — read the target slug
  explicitly from the marketplace config, never guess it from `origin`, and pass `--repo` so nothing
  defaults to a fork's upstream. The follow-on that hardens `dev:reflect`'s PR path closes the entry by
  adopting that same explicit-target discipline; it is a separate change from routing.
