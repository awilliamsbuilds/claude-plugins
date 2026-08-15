# Backlog Viewer
*Branch: feature/backlog-viewer · Confidence: 100% — Ready · 2026-08-13*
*Cycle type: feature · Tier: standard*
*Milestone 1 of `docs/dev/product-plans/dev-observability.md`*

## Intent

Deciding what tech debt to fold into an upcoming cycle currently means reading `/dev:debt list`
output, which is strictly linear: one block per item, one sentence of body, ranked only by
recurrence, with no filtering available at any verb. The verb set is `list` / `show` / `closed` /
`close` / `add` / `inbox` — the only partition the store can be viewed through today is
active-vs-closed, and even that requires two separate invocations whose output can't be compared
side by side.

The store is now 30 items (18 active, 12 closed) across two types, three live statuses, and twelve
distinct front-matter keys — thirteen counting the contract-defined but as-yet-unused `routing`.
That is past the size where a linear dump is scannable.

This cycle ships a **triage view**: a browsable, filterable rendering of the whole store, optimized
for the question "what should I fold into the cycle I'm about to start?" Legibility for its own
sake is a welcome side effect, not the goal — when the two conflict, triage wins.

## Scope

**A `view` verb on `dev:debt`** that launches a local HTTP server and prints its URL.

- **Idempotent.** Re-running when a viewer is already live prints that server's URL rather than
  starting a second one. The skill also prints how to stop it.
- **Detached from the launching session.** The process must outlive the terminal and the Claude
  Code session that started it — a session-bound background process would die on exit and break
  both Happy Path step 5 and Success Criterion 3, which are the reason this is a server at all.
  Detachment here means surviving its parent (e.g. `setsid`/`nohup`), not registering with the OS
  to restart at boot; the latter is out of scope.
- **Read-only and local-only.** Binds `127.0.0.1` exclusively. The server never writes to
  `docs/backlog/` or anywhere else in the repo.
- **Live, not snapshotted.** The store is read from disk on every request, so a browser refresh
  always reflects current files. This is the property that makes the tab worth bookmarking, and it
  is why a generated static file was rejected: a `file://` page cannot fetch local files, so a
  static build is frozen at generation time and silently stale thereafter.
- **Always serves the primary checkout's store.** `PRIMARY` is resolved via
  `git rev-parse --git-common-dir` (the same derivation the other `dev` skills use), so the view is
  identical regardless of which cycle worktree it was launched from. The backlog is a repo-wide
  thing; two launches must never disagree about what it contains.
- **Renders active corpus and `closed/` archive together** — the first time open and closed items
  can be seen in one view.

**View capabilities:**

| Capability | Dimensions |
|---|---|
| Filter | `type`, `status`, `scope`, `severity` — **options for every one of these are derived from the values present on disk, never from a hardcoded enum.** The contract's enums and the store disagree: `severity` is specified `P3 \| Nit` but the store carries `P3` ×7, `P2` ×1 (`debt-p9-issue-body-fence-width`), `Nit` ×1, and 21 items with none. Deriving from disk is what keeps an out-of-contract value filterable instead of invisible |
| Sort | `recurrence`, `first_recorded` |
| Search | free text across body prose **and** front-matter values, including `files:` paths — typing `plan/SKILL.md` finds every item touching that file |
| Link | `possibly_related_to` renders as a clickable link that jumps to the named item, resolving across both the active corpus and `closed/` |

Search covering `files:` paths is deliberate: it delivers the triage benefit of a files filter
without a dedicated filter control to build and maintain.

## Out of Scope

- **Writes of any kind.** No closing, editing, capturing, or reordering from the view. Those remain
  `dev:debt` verbs. The viewer is a pure function of the store.
- **Cross-repo items.** No rendering of `dev-backlog` GitHub issues routed from other repos under
  §P9. Local `docs/backlog/` only.
- **A dedicated `files:` filter control.** Free-text search covers the need.
- **Duplicate grouping or relationship graphs.** `possibly_related_to` links, but items are not
  clustered, paired, or visualized as a graph.
- **Closing `debt-primary-cd-failure-unchecked`.** See Technical Constraints — this cycle must not
  add an unguarded fourteenth site, but fixing the other thirteen is its own cycle.
- **Server lifecycle management beyond start and stop.** No `launchd`/login-item registration, no
  auto-restart after reboot, no idle timeout, no health monitoring. Starting and stopping are
  manual. This does **not** mean session-bound: see the detachment requirement in Scope.

## Success Criteria

1. All 30 items render — 18 active and 12 closed — with no item silently missing.
2. Every filter, sort, and search dimension in the Scope table works against the real store. Two
   values have **zero live samples** and so cannot be verified against it: `scope: plugin` (all 30
   items are `repo`) and `status: in-progress` (live statuses are `open` ×16, `closed` ×12,
   `promoted` ×2). Both are verified the same way `routing:` is — by synthetic fixture, not by the
   store — and neither may cause an item to disappear when selected.
3. Editing any file under `docs/backlog/` and refreshing the browser shows the change, with **no
   re-invocation of any skill**.
4. Launching from inside a cycle worktree serves the same data as launching from the primary
   checkout.
5. The server accepts no connection from a non-loopback address, and performs no write to disk.
6. `grep -rn '/Users/\|awilliamsbuilds\|adam' plugins/dev/` still returns nothing — the repo's
   portability convention survives this cycle.
7. Running the verb twice does not start a second server.

## Happy Path

1. Run `/dev:debt view` from anywhere in the repo — primary checkout or a cycle worktree.
2. The server boots on a loopback port; the skill prints the URL and the stop instruction.
3. Open the URL and bookmark the tab.
4. Filter, sort, and search to identify fold-in candidates for the cycle being planned.
5. Days later, refresh the tab — the view reflects the current store without any re-invocation.

## Edge Cases

- **Port already in use.** If the occupant is our own viewer, print its URL and do not start a
  second. If the port is held by something else, bind the next free port and print the actual URL —
  never print a URL that isn't the one serving.
- **Malformed front-matter in an item.** Render the item with a visible parse-error badge. Never
  drop it silently and never let one bad file take down the server — a dropped item is a debt item
  that stops existing, which is worse than a visibly broken one.
- **`possibly_related_to` names a slug that exists in neither the active corpus nor `closed/`.**
  Render as plain text with a "not found" marker rather than a dead link.
- **`docs/backlog/` absent, or present but empty.** Serve a page that says so. Not an error, not a
  stack trace, not an empty page.
- **`PRIMARY` resolution fails** (not a git repository, or `git rev-parse` errors). Exit with a
  clear message rather than proceeding against an unresolved path.
- **A `severity` value outside the contract's `P3 | Nit`.** `debt-p9-issue-body-fence-width` carries
  `severity: P2` today. Severity filter options are derived from the values found on disk, so an
  out-of-contract value stays filterable rather than invisible; items carrying no `severity` (21 of
  30) remain visible in any unfiltered view. The same rule applies to every other enum field — the
  contract describes intent, the store is the authority.
- **The `routing:` field.** Defined in the contract but carried by zero items today. The renderer
  must handle it as a normal optional field — it has no live sample to have been tested against.
- **Items with no `files:` entries.** Four active items carry an empty `files:` list
  (`backlog-debt-backfill`, `backlog-dev-skill-test-harness`,
  `backlog-stage-lifecycle-telemetry-app`, `backlog-verboseness-check`); they must remain findable
  by search and must not be excluded from any unfiltered view.

## Audience

Single operator — the repo owner running `/dev` cycles in this plugin repo. The plugin is
nonetheless distributed via the `local-plugins` marketplace and must remain installable by anyone,
so nothing may hardcode a personal path, username, or machine-specific location.

## Technical Constraints

- **No build tooling.** The repo has no `package.json` anywhere and ships as markdown skills. This
  cycle must not introduce a build step, a bundler, or a package manager.
- **Skills are auto-discovered.** `plugins/dev/.claude-plugin/plugin.json` has no skills array, so
  adding behavior to `dev:debt` means editing one `SKILL.md` — no marketplace or plugin.json edit.
- **`python3` is 3.9.6** (macOS system Python). Stdlib only, no pip installs. Language features
  introduced after 3.9 are unavailable.
- **No PyYAML — the front-matter parser is hand-rolled.** Verified: `python3 -c "import yaml"`
  raises `ModuleNotFoundError`. "Stdlib only" therefore implies writing a parser against a schema
  that mixes inline lists (`cycles: [a, b]`, `files: []`), block lists (`files:` followed by
  `  - path`), and optional keys with empty values. This parser is the single largest source of the
  "item silently missing" failure that Success Criterion 1 guards against, and it must be treated
  as the risk centre of the build rather than as glue code — every one of the 30 real files is a
  test case.
- **Portability.** `grep -rn '/Users/\|awilliamsbuilds\|adam' plugins/dev/` returns zero hits today.
  That must remain true.
- **New `PRIMARY` derivation must carry a non-empty guard.** `debt-primary-cd-failure-unchecked`
  records that all 13 existing `PRIMARY=` sites lack a check after the derivation. That item was
  deliberately not folded into this cycle, but this cycle writes a *new* site — it must carry the
  guard so the count of unguarded sites does not grow.
- **Serving repo contents over HTTP is a security surface.** Loopback-only binding and read-only
  behavior are requirements, not defaults to be relaxed for convenience.
- **`.gitignore` currently holds `.dev-worktrees/` and `.DS_Store`.** Any generated or runtime
  artifact this cycle produces needs a deliberate home decision.

## Dependencies

- Introduces the repo's **first runtime dependency**: `python3`, stdlib only.
- Depends on the `docs/backlog/` front-matter contract defined in
  `plugins/dev/references/tech-debt.md` (§ Fields). The viewer is a consumer of that schema and
  must not fork it.
- **Blocks Milestone 3** (`lifecycle-viewer`), which reuses the server and page shell established
  here. The shell was deliberately not built as its own cycle — an abstraction with no live
  consumer is speculative — so its shape is decided here and generalized later.

## UI Needed

**Yes.** The delivery form is settled (local server, browser-rendered), but page layout, filter
controls, item rendering, and the active/closed presentation are open design questions for Shape.

---
*Auto-filled dimensions: none — all ten answered directly.*
*Grounding inventory: `/dev:debt list` linearity and P8 recurrence ranking verified against
plugins/dev/skills/debt/SKILL.md:85–115 and references/tech-debt.md:314–318 (claim confirmed);
verb set enumerated from debt/SKILL.md:62–67 and 343–349 — corrected the source item's claim that
filtering means "re-invoking with a different verb", as no filtering exists at any verb; store size
counted by `ls` (18 active, 12 closed = 30); front-matter keys enumerated by awk sweep over all 30
files rather than from the contract — type/status/scope/recurrence/first_recorded/files/cycles ×30,
closed+closed_by ×12, severity ×9, possibly_related_to ×4, promoted_to ×2, and `routing:` ×0 despite
being contract-defined; enum **values** swept separately after the cold review found the first draft
had taken them from the contract rather than from disk — `severity` is P3 ×7 / P2 ×1 / Nit ×1 (P2 is
outside the contract's stated enum), `status` is open ×16 / closed ×12 / promoted ×2 (no
in-progress), `scope` is repo ×30 (no plugin); PyYAML absence verified by
`python3 -c "import yaml"` → ModuleNotFoundError; `possibly_related_to` targets read from the 4 carrying files (2 point into
closed/); build tooling absence verified by `find . -name package.json` → no results; portability
verified by `grep -rn '/Users/\|awilliamsbuilds\|adam' plugins/dev/` → zero hits; skill
auto-discovery verified by reading plugins/dev/.claude-plugin/plugin.json (no skills array);
runtime availability checked directly — python3 3.9.6, node v25.8.0, deno/bun absent; hook
infrastructure checked — zero hook events configured in ~/.claude/settings.json; `.gitignore` read
directly. The source item `backlog-stage-lifecycle-telemetry-app` was also fact-checked for
Milestone 2's benefit: its claim that no per-transition timestamps exist is wrong —
`metrics.stage_timestamps` is written by spec/shape/plan/build/validate/pr and already read by
reflect/SKILL.md:47 and :97; the real gaps are per-stage `_start` (only spec has one), a done stamp,
invocation counts, and cost data.*
