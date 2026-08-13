# Backlog Viewer — Design
*Branch: feature/backlog-viewer · 2026-08-13*
*Milestone 1 of `docs/dev/product-plans/dev-observability.md`*

## Design Status

**Directional** — conveys intent; Plan and Build may adapt specifics.
Target device: **Desktop 1440 × 900**. The interactive prototype was built at those dimensions
1:1 against all 30 real store items. Below ~1000px the layout is expected to degrade gracefully
(detail pane wraps under the list); that narrow case was not designed and is not a requirement.

## Design Decision

**Option B — filter rail + compact list + detail pane**, selected from three structural
alternatives prototyped side by side at 1:1 with the real store.

| Option | Why not |
|---|---|
| A — rail + cards, body expands inline | An expanded card displaces everything below it. Bodies here run long (`debt-p9-issue-body-fence-width` is four paragraphs), so comparing two candidates far apart in the list means losing your place |
| C — toolbar + sortable table, body in a drawer | Metadata compares well, but the prose is what decides fold-in and a table hides it behind a click. `severity` is empty for 21 of 30 and `files` is a list — both degrade to a count in a cell |

**B wins because the list never moves while you read.** Triage means reading "Why deferred / Done
looks like" for a handful of candidates while keeping the shortlist on screen; B is the only option
that holds both. It also makes `possibly_related_to` traversal cheap and reversible — clicking a
link swaps the detail pane and highlights the target row without disturbing the filtered list.

Secondary reason: **Milestone 3 (`lifecycle-viewer`) inherits this shell.** Rail + list + detail
generalizes to a per-cycle lifecycle view; a table does not. The spec notes the shell was
deliberately not built as its own cycle, so its shape is decided here.

## Delivery Shape

Decisions that bind the page design and that Plan should not re-litigate:

- **One route, one response.** `GET /` returns a complete self-contained HTML document with the
  parsed store embedded as a JSON literal. All filtering, sorting, and search run client-side.
  Every other path returns 404. A browser refresh re-requests `/`, which re-reads disk — that is
  the whole of Success Criterion 3, with no API surface to design.
- **Not a static file server.** Build must use `BaseHTTPRequestHandler` with an explicit route
  allowlist, never `SimpleHTTPRequestHandler`, which serves its working directory and would expose
  the entire repo over HTTP. This is the cycle's single largest security decision.
- **No external assets.** CSS and JS are inlined in the one document. Nothing is fetched, so there
  is no second route to secure and no asset path to resolve.
- **Server identity probe, not a state file.** The running server answers with a
  `X-Dev-Backlog-Viewer: <primary-path>` response header. `view` probes ports 8730–8739 for that
  header before binding. This single mechanism serves both the idempotency requirement and the
  "port already in use" edge case: a matching header means our viewer is already up (print its
  URL, start nothing); a non-matching or absent header means the port belongs to something else
  (try the next). Exhausting the range is an error, not a silent bind elsewhere.
- **No runtime artifact in the repo.** Because identity is probed rather than recorded, nothing is
  written to `docs/backlog/`, the repo root, or `.gitignore`. This settles the spec's "deliberate
  home decision" — the home is nowhere.
- **`setsid` does not exist on macOS.** Confirmed while launching the prototype server
  (`/bin/bash: setsid: command not found`). The spec names it as an example detachment mechanism;
  the implementation must use `nohup … & disown` or equivalent. Detachment still means surviving
  the parent shell, not registering with the OS.

## User Flows

```
Flow 1: Happy path — triage a cycle
1. User runs /dev:debt view from anywhere in the repo (primary checkout or a cycle worktree)
2. System resolves PRIMARY, probes 8730–8739, binds the first free port, detaches the process
3. System prints the URL and the stop command
4. User opens the URL, bookmarks the tab, and sees all 30 items — nothing filtered by default
5. User filters (type/status/scope/severity), sorts, and searches to shortlist candidates
6. User clicks a row; the full body renders in the detail pane while the list holds its position
7. Days later the user refreshes the bookmarked tab and sees the current store — no skill re-run

Error: PRIMARY resolution fails (not a git repo, or git rev-parse errors, or the cd yields empty)
       → exit before binding, with the message under Copy › PRIMARY failure. Nothing is started.
Error: all of 8730–8739 are held by something that is not our viewer
       → exit with the message under Copy › No free port. Never bind silently outside the range.

Flow 2: Re-launch while already running (idempotent — Success Criterion 7)
1. User runs /dev:debt view again, in a new session or a different worktree
2. System probes the range and finds a server whose X-Dev-Backlog-Viewer matches this PRIMARY
3. System prints that server's URL and the stop command, and starts nothing

Error: a server on the range reports a *different* PRIMARY (another checkout of the repo)
       → treat the port as occupied by something else and continue probing. Two checkouts get
         two servers; neither is ever shown the other's store.

Flow 3: Stop
1. User runs /dev:debt view stop
2. System probes for the matching server and terminates it
3. System confirms it stopped

Error: nothing is running → say so plainly. Not an error state, not a stack trace.

Flow 4: Follow a relationship into the archive
1. User reads an item whose front-matter carries possibly_related_to
2. The link renders under the body, marked (closed) when the target is in closed/
3. Click swaps the detail pane to the target and highlights its row; the filtered list is unchanged

Error: the named slug exists in neither the active corpus nor closed/
       → render as plain text with a "not found in store" marker. Never a dead link.
   (3 of the 4 items carrying this field point into closed/, so cross-corpus resolution is the
    common case, not the exception.)

Flow 5: A malformed item
1. The parser fails on one file's front-matter
2. That item still renders — slug taken from the filename, a PARSE ERROR badge in place of chips
3. The detail pane shows the parser's message and the file's raw text
4. Every other item is unaffected and the server stays up

Flow 6: Empty or absent store
1. docs/backlog/ does not exist, or contains no item files
2. The page renders its shell and says which case it is (Copy › Empty states)
3. This is a normal response, not an error page
```

## Component/Screen Inventory

One screen. Component policy is `can-propose`; the repo contains **zero** existing HTML, CSS, JS,
or Python, so every component below is new by necessity rather than by preference.

| Component | Status | Notes |
|---|---|---|
| `dev:debt` `view` / `view stop` verbs | New (edit to existing skill) | Only `plugins/dev/skills/debt/SKILL.md` changes. No plugin.json or marketplace edit — skills are auto-discovered |
| Front-matter parser | New | **The risk centre**, per spec. Must handle inline lists (`cycles: [a, b]`, `files: []`), block lists (`files:` then `  - path`), optional keys, and empty values. All 30 real files are its test corpus. `docs/backlog/README.md` is not an item and must be excluded |
| HTTP server + route allowlist | New | `BaseHTTPRequestHandler`, loopback bind only, `GET /` and nothing else. Emits the identity header |
| Page shell (rail / list / detail) | New | The layout Milestone 3 reuses. Keep the three regions independent of what fills them |
| Facet rail | New | Options derived from values found on disk, never a hardcoded enum — this is why `P2` is filterable despite being outside the contract's `P3 \| Nit`. Ordered by the per-field display rank under UX Decisions, which affects sequence only |
| Item row | New | Slug, then a chip line (type · status · severity) with `first_recorded` right-aligned |
| Detail pane | New | Header + chips, meta line, front-matter field table, prose body, resolved relationship link |
| Chips | New | One visual vocabulary shared by rows and detail. Colour carries meaning: type, status, severity |
| Parse-error badge | New | Replaces the chip row on an unparseable item |

**Explicitly not built:** any write path, any second route, any cross-repo rendering, a dedicated
`files:` filter control, duplicate grouping or a relationship graph.

## Copy

### Terminal — `/dev:debt view`

**Started:**
```
Backlog viewer running at http://127.0.0.1:8730
Serving docs/backlog/ from <primary-path> — read-only, loopback only.
Refresh the page any time; it re-reads the files on every load.
Stop it with: /dev:debt view stop
```

**Already running** (Success Criterion 7 — nothing is started):
```
Backlog viewer is already running at http://127.0.0.1:8730
Stop it with: /dev:debt view stop
```

**Stopped:**
```
Backlog viewer stopped.
```

**Stop when nothing is running:**
```
No backlog viewer is running for this repo.
```

**PRIMARY failure:**
```
Can't resolve the repository root, so there's no store to serve.
<the failing command and its error>
Run this from inside the repository.
```

**No free port:**
```
Ports 8730-8739 are all in use by something else, so the viewer didn't start.
Free one of them, or stop whatever is holding them, and try again.
```

### Page

| Element | Copy |
|---|---|
| Document title | `dev backlog — <repo-name>` |
| Header | `dev backlog` · `<repo-name>` (muted) |
| Count | `<n> of <total>` — always both, so an active filter is never invisible |
| Search placeholder | `Search body, fields, file paths…` |
| Filter group headings | `type` · `status` · `scope` · `severity` (lowercase — they are field names, not labels), in that order |
| Facet: no value present | `none` — never `—`, which reads as a dash rather than a state |
| Sort control | `sort: recurrence` · `sort: first_recorded` |
| Clear filters | `Clear all` |
| Detail meta line | `recorded <date> · seen <n>× · <cycles>` — never `rec 1` or `9f` |
| Detail, nothing selected | `Select an item to read it.` / `<n> items in the current filter.` |
| Relationship link | `possibly related to <slug>` · `(closed)` suffix when the target is archived |
| Relationship, unresolved | `possibly related to <slug> — not found in store` |
| Parse-error badge | `PARSE ERROR` |
| Parse-error detail | `This file's front-matter couldn't be parsed, so its fields are unavailable. The raw file is below.` |
| Empty — filters match nothing | `No items match these filters.` / `Clear a filter, or widen the search.` |
| Empty — store has no items | `No items in docs/backlog/ yet.` / `Capture one with /dev:debt add.` |
| Empty — store absent | `docs/backlog/ doesn't exist in this repo.` / `Run /dev:init to set up the backlog store.` |

Copy rules applied throughout: no invented abbreviations (`9f`, `rec 1` were both removed after
review — a label the operator has to decode is a label that failed), field names shown as field
names so the page and the file agree, and every empty state naming its own cause and next step.

## Wireframe

```
1440 × 900
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ dev backlog · claude-plugins    30 of 30   [sort: recurrence ▾]   [⌕ Search…      ]   │ 52px
├────────────────┬───────────────────────────┬─────────────────────────────────────────┤
│ Filters  Clear │ debt-gate-path-state-…    │ debt-p9-issue-body-fence-width          │
│                │ [DEBT][CLOSED]  2026-07-21│ [DEBT] [OPEN] [P2]                      │
│ TYPE           ├───────────────────────────┤ recorded 2026-08-02 · seen 1× · legacy… │
│ ☐ backlog    8 │ backlog-backlog-viewer-app│ ┌─────────────────────────────────────┐ │
│ ☐ debt      22 │ [BACKLOG][PROMOTED] 08-12 │ │ type          debt                  │ │
│                ├───────────────────────────┤ │ status        open                  │ │
│ STATUS         │ …                         │ │ scope         repo                  │ │
│ ☐ open      16 │                           │ │ severity      P2                    │ │
│ ☐ promoted   2 │ ← selected row keeps its  │ │ first_recorded 2026-08-02           │ │
│ ☐ closed    12 │   place while you read →  │ │ files         plugins/dev/refere…   │ │
│                │                           │ └─────────────────────────────────────┘ │
│ SCOPE          │                           │                                         │
│ ☐ repo      30 │                           │ **What's wrong:** P9's issue-body …     │
│                │                           │                                         │
│ SEVERITY       │                           │ **Why deferred:** Success Criterion …   │
│ ☐ P2         1 │                           │                                         │
│ ☐ P3         7 │                           │ possibly related to debt-primary-pa…    │
│ ☐ Nit        1 │                           │                        (closed)         │
│ ☐ none      21 │                           │                                         │
└────────────────┴───────────────────────────┴─────────────────────────────────────────┘
   226px             396px                       flexible (~818px)
```

Higher-fidelity interactive prototype built at 1440 × 900 against all 30 real items, with working
filters, sort, search, and relationship traversal. Facet counts above are the live values.

## UX Decisions

- **Nothing is filtered by default.** All 30 items — open, promoted, and closed — render on load.
  Considered defaulting to `status: open` for a sharper triage answer, and rejected it: the store's
  whole point is that a promoted-but-unfinished plan should be something you trip over, and a
  default filter is a hidden state the operator has to remember. Success Criterion 1 is also
  satisfied literally rather than after a click.
- **`severity` is a filter, not the triage axis, and the viewer must not promote it into one.**
  It is written solely by `dev:validate` when it defers a finding (`references/tech-debt.md:104`,
  `validate/SKILL.md:215`), so it ranks only 9 of 30 items — anything captured by `dev:debt add`,
  by reflect, or by the tracker migration carries none. The contract is explicit that this is not
  a ranking field: it is *"**Informational** … not a routing/lifecycle field"* and *"drives no
  procedure"* (`tech-debt.md:104–106`), and the capture rule states flatly that **"severity is the
  wrong axis"**, to classify by what an item costs the *next* cycle rather than by the fix loop's
  label (`tech-debt.md:47–52`). Consequences for this design: the viewer neither infers nor
  computes severity, does not sort by it, and does not collapse `Nit` into `P3` — `Nit` is a
  review-time non-blocking label that `dev:validate` persists into the store, and reconciling that
  is a change to the contract, not to a viewer that must stay a pure function of the store.
  `first_recorded` (age) is the ranking axis that actually works across the whole corpus.
- **`recurrence` barely discriminates today** — 27 of 30 items are `1`, one is `2`, two are `0`. It
  stays as a sort dimension because the spec names it and because it will separate items as the
  store ages, but the sort control should not present it as the obvious default answer.
- **Sort stays at the spec's two dimensions.** The prototype also offered `severity` and `slug`;
  both were dropped rather than carried into the design, because neither is in the spec's Scope
  table and `severity` is absent from 21 of 30 items anyway.
- **Facets are ordered by meaning, not by count.** Count-descending order made the rail reshuffle
  as the store changed and put `none` above `P2`. Each field declares a display rank:

  | Field | Order | Source |
  |---|---|---|
  | `status` | `open` → `in-progress` → `promoted` → `closed` | the lifecycle diagram, `references/tech-debt.md:161–167` |
  | `severity` | `P1` → `P2` → `P3` → `Nit` → `none` | the severity ladder, `validate/SKILL.md:108–111`. Worst-first is the right order *for a severity list*, but severity is explicitly **not** the triage axis — see below |
  | `type`, `scope` | alphabetical | neither has an inherent sequence; alphabetical is at least predictable |

  **The rank list orders values; it never decides membership.** This is the one place the design
  admits a hardcoded list, and the distinction is load-bearing: the set of facets still comes
  entirely from disk, and a value missing from its rank list sorts to the end rather than
  vanishing. Build must not reuse these lists as a filter or a validity check. Ranked values with
  no live item render no checkbox at all — `P1` and `in-progress` appear the moment one exists.
- **Values with no live sample simply produce no facet.** Because options are derived from disk,
  `scope: plugin` and `status: in-progress` render no checkbox today and appear the moment one
  item carries them. Selecting a derived value can never hide an item that has it — the same
  property Success Criterion 2 asks be proven by synthetic fixture rather than against the store.
- **Chips, not prose, carry item state.** The first prototype rendered row state as grey text
  (`debt · closed · 2026-07-21 · 9f`); review found it unreadable at a glance. Rows and the detail
  pane now share one chip vocabulary, so an item looks the same wherever it appears.
- **Metadata that needs decoding was cut, not shrunk.** The row's file count (`9f`) is gone
  entirely — the detail pane lists the actual paths, which is the only form of that fact worth
  having. `rec 1` became `seen 1×`.
- **Search covers `files:` paths, and that is the files feature.** Typing `plan/SKILL.md` finds
  every item touching it, which is why the spec deliberately has no dedicated files filter.
- **A malformed item stays visible.** A dropped item is a debt item that stops existing; a badged
  one is merely ugly. The badge replaces the chips so the item cannot be mistaken for parsed.
- **`promoted` is styled distinctly but not de-emphasized.** It is neither a candidate nor
  finished, and `promoted_to` renders in the field table so the plan it went to is one glance away.
