# Backlog Capture + Cross-Repo Routing (ADR follow-on 3)
*Branch: feature/debt-capture-routing · Confidence: 90% — Ready · 2026-07-29*
*Cycle type: feature · Tier: deep*

## Intent

The unified backlog + tech-debt store (ADR `2026-07-28-backlog-debt-model.md`, follow-ons 1 & 2)
is built and migrated, but the store today can only be **read, ranked, and closed** — there is no
way to **capture** a new item on demand, and the `scope:` / `routing:` fields that were designed to
send `/dev`-plugin debt back to the plugin repo are still **reserved with no procedure**. This cycle
builds the last unbuilt follow-on: the capture verb, the cross-repo routing machinery, and the
triage-inbox drain that together let "save this to the backlog" and "this is a plugin bug, send it
home" work end to end — removing the pull toward Linear for solo and plugin work, and stopping
plugin debt from scattering across every repo the plugin runs in.

## Scope

Three coupled parts plus a contract un-reservation, across exactly three files
(`plugins/dev/skills/debt/SKILL.md`, `plugins/dev/skills/done/SKILL.md`,
`plugins/dev/references/tech-debt.md`):

**Part 1 — `/dev:debt add` capture verb** (Decision 6). A new verb on the existing `/dev:debt`
skill.
- `/dev:debt add <free text>` files an item; `/dev:debt add` with no argument prompts for the text.
- Defaults: `type: backlog`, `scope: repo` (the manual "save to build later" is an *intention*).
- Overrides: `--debt` (→ `type: debt`), `--plugin` (→ `scope: plugin`), and `--repo <owner/name|URL>`
  (an explicit routing target, meaningful only with `--plugin`; supplying `--repo` **without**
  `--plugin` is a user error and is **rejected with a message** — never silently ignored, and never
  treated as implying `--plugin`). Everything not a recognized flag is the description.
- Writes the full P1 front-matter, `status: open`, `first_recorded` from the clock, a P2-allowlisted
  `<type>-<slug>.md` filename with collision disambiguation, and the correct body labels
  (`What:/Why:/Done looks like:` for backlog, `What's wrong:/Why deferred:/Done looks like:` for
  debt). It ensures `Done looks like:` is populated (prompting if not derivable) so list summaries
  stay meaningful.
- Runs the **recurrence-merge scan (P6)** against the active corpus (P5) on capture, exactly as an
  auto-flushed item does: clear match → bump `recurrence:` on the existing file; uncertainty → new
  file with `possibly_related_to:`.
- A `--plugin` capture **echoes and confirms** the resolved target before it routes (Part 2), because
  routing crosses a repo boundary.

**Part 2 — Cross-repo routing** (Decision 5). A `scope: plugin` item captured **off the plugin repo**
is delivered as a GitHub issue in the plugin repo.
- **Target resolution (never guessed from `origin`):** find `dev@<mp>` in
  `~/.claude/settings.json` `enabledPlugins` → read `extraKnownMarketplaces[<mp>].source.repo`. An
  explicit `--repo` overrides this on manual `add`. If neither yields a target, degrade (below).
- **Dogfood-local:** when `git remote get-url origin`'s slug **equals** the resolved marketplace slug,
  the item is already home — write it straight to local `docs/backlog/` as an ordinary file, no issue.
  (This repo is that case.)
- **Delivery:** `gh issue create --repo <slug> --label dev-backlog`, title carrying the slug marker,
  body carrying the item's **complete front-matter block + body** (so conversion can lift it). Create
  the `dev-backlog` label first if the target repo lacks it (idempotent create-if-missing).
- **Intake dedup:** `gh issue list --repo <slug> --label dev-backlog --state open` filtered by the slug
  marker finds *candidates*; then **Decision 4's clear-match test** decides — `files:` overlap **and**
  same defect, **never slug/topic alone**. Clear match → `gh issue comment` ("recurred in `<repo>` on
  `<date>`"), no new issue. Uncertainty → open a new issue (noting the suspected sibling).
- **Degrade-to-local:** when delivery fails — no network, no auth, API error, or slug unresolvable —
  record the item in the **current repo's** `docs/backlog/` with `scope: plugin` + `routing: pending`,
  surfaced and re-attempted, **never dropped**.
- **Retry seam:** both `/dev:debt list` **and** the next `dev:done` flush re-attempt any
  `routing: pending` items (delivering them if the plugin repo is now reachable) **before** writing new
  ones. On success the local `pending` copy is removed — the item now lives as the issue.
- **`dev:done` flush hook** (Decision 9): in `dev:done` Step 6a, a `scope: plugin` item off the plugin
  repo **bypasses local recurrence-merge** (that corpus structurally can't hold it) and routes per
  above instead of writing a local file; the flush **also re-attempts any existing `routing: pending`
  items before writing new ones**. Note the two halves have different reachability: **no producing
  stage in scope emits a `scope: plugin` buffered item** — `/dev:debt add` routes directly rather than
  through the buffer, and giving `dev:build`/`dev:validate`/`dev:reflect` a plugin-classification path
  is out of scope. So the buffered-route branch is **forward-defensive** (it exists for when a later
  cycle adds that classification path, and is exercised meanwhile only by hand-editing a buffered
  item); the **pending-retry half is the always-reachable one** this cycle actually exercises.

**Part 3 — `/dev:debt inbox` (drain/convert verb)** (Decision 5 triage). Run in the plugin repo.
- `/dev:debt inbox` lists open `dev-backlog` issues (`gh issue list --label dev-backlog --state open`).
- Convert each: lift the front-matter block from the issue body → create
  `docs/backlog/<type>-<slug>.md`, running **recurrence-merge (P6)** on conversion against the local
  corpus (clear match → bump the existing file's `recurrence:` and create no new file). Then **close
  the issue** with a reference to the resulting file.

**Contract un-reservation.** In `references/tech-debt.md`, un-reserve `scope: plugin` and
`routing: pending`: replace the "reserved (Decision 5, cycle 3) / no procedure this cycle" language
with the actual routing procedure, making the contract the **single source of truth** for it — the
skills link here and hold no second copy.

**Notes carried to Plan** (surfaced by the spec cold review; decisions left to the plan/build stage):
- **Build sequencing / split seam.** This is on the upper edge for one deep cycle. If Plan judges it too
  large, a clean seam exists: land **Part 1 + the contract routing procedure + Part 2** first, then
  **Part 3 (`inbox`)** second. Routing degrades gracefully without the drain — routed issues simply
  accumulate until `inbox` ships, convertible by hand meanwhile. Default is one cycle; this is Plan's call.
- **Slug-marker format (must be pinned by Plan/Build).** Intake dedup and the convert verb key on a
  stable, greppable marker that ties an issue to its slug. The ADR deferred the exact format to this
  cycle. It must be stable across `create`/`list`/`comment`/`convert` and machine-findable via
  `gh issue list --search`; the front-matter block in the issue body remains the authoritative content
  the convert verb lifts.

## Out of Scope

- **`dev:reflect` dogfood PR-base hardening** (`debt-reflect-dogfood-pr-base`). The ADR explicitly
  notes routing does **not** close this — issues have no base branch and routing never touches
  `dev:reflect`'s PR path. Decision 5 establishes the fix *pattern* (read the slug from config, pass
  `--repo`), but adopting it in `dev:reflect` is its own later cycle.
- **Store implementation & migration** (follow-ons 1 & 2) — already shipped and verified absent-of-legacy
  in grounding.
- **Product-plan promotion/deletion** (follow-on 4) — already live (contract P3 flow + `dev:done`
  reverse-lookup exist); not re-touched here.
- **`dev:init` changes** — the store and its `README.md` already exist; the `dev-backlog` label is
  created lazily on first routing, so `init` needs no edit.
- **`/dev:debt promote <id>` → Linear** (`backlog-debt-linear-promotion`) — a distinct, separately
  deferred mechanism; not this cycle.

## Success Criteria

1. `/dev:debt add "<text>"` creates `docs/backlog/backlog-<slug>.md` with complete, schema-valid P1
   front-matter (`type: backlog`, `scope: repo`, `status: open`, clock-stamped `first_recorded`,
   `cycles`/`recurrence` consistent, `files`, populated body) and runs recurrence-merge on capture.
2. `--debt`, `--plugin`, and `--repo <owner/name|URL>` override the defaults; the no-arg form prompts;
   free text is preserved verbatim as the description; `--repo` without `--plugin` is rejected with a
   message.
3. A `scope: plugin` item captured **off** the plugin repo opens a `dev-backlog`-labelled issue in the
   config-resolved target repo, its body carrying the full front-matter block; a clear-match candidate
   gets a recurrence **comment** instead of a duplicate; delivery failure yields a local
   `routing: pending` item, never a dropped one.
4. A `scope: plugin` item captured **in** the plugin repo (dogfood) is written to local `docs/backlog/`
   with no issue created.
5. In `dev:done`'s flush, existing `routing: pending` items are re-attempted before any new item is
   written — identically in both standard and autopilot modes (this is the reachable, always-exercised
   half). The buffered `scope: plugin`-off-plugin **routing branch** (bypass local recurrence-merge,
   route instead of writing locally) is present and correct but forward-defensive — verified by
   hand-editing a buffered item, since no in-scope producer emits one.
6. `/dev:debt list` surfaces `routing: pending` items distinctly and re-attempts their delivery,
   removing the local copy on success.
7. `/dev:debt inbox` (run in the plugin repo) lists open `dev-backlog` issues and converts each into a
   `docs/backlog/` file (recurrence-merge on conversion), then closes the issue with a file reference.
8. `references/tech-debt.md` no longer marks `scope: plugin` / `routing: pending` as reserved: it
   documents the routing procedure as the single source of truth, and no skill restates it.
9. Every automatic in-cycle routing write is traceable to a step that runs identically in both modes
   (mode symmetry); the manual `add` overrides/confirmations are user-invoked and correctly outside
   that rule. Any new `state.json` key (if introduced) carries its `(writes: …)` tag at its write site.

## Happy Path

The capture → route → convert arc, across two repos:

1. Working in project `foo`, a `/dev` cycle's review surfaces a bug in the `/dev` plugin's own flush
   logic. The user runs `/dev:debt add the flush drops end-of-file items --debt --plugin`.
2. The skill resolves the target from config → `awilliamsbuilds/claude-plugins`, sees
   `origin(foo) ≠ slug` (not dogfood), echoes the target, and the user confirms.
3. Intake dedup finds no clear-match open issue → `gh issue create --repo awilliamsbuilds/claude-plugins
   --label dev-backlog` with the full front-matter in the body. **Nothing is written locally in `foo`.**
4. Later, in the plugin repo, the maintainer runs `/dev:debt inbox` → sees the issue → converts it to
   `docs/backlog/debt-<slug>.md` (recurrence-merge finds no local match → new file) → the issue is
   closed with a reference to the new file. The item now lives in exactly one place: the plugin's store.

## Edge Cases

- **Plugin repo unreachable / no auth / API failure / slug unresolvable** → local `routing: pending`
  item in the current repo, surfaced by `list` and re-attempted by `list` and the next flush; never
  dropped. This is the writer-side of the contract's silent-degrade discipline (P7): a writer degrades
  by writing locally + a visible marker, never by discarding.
- **Misclassification** (`repo` tagged `plugin` or vice versa) → `scope:` is one editable line; fix it
  by hand, and if an issue was already opened, close it. The model makes classification a visible,
  editable field, not an irreversible act.
- **Intake dedup race** — `gh`'s search index is eventually-consistent, so two near-simultaneous
  cross-repo captures may both open issues. Intake dedup is best-effort; the **conversion-time**
  recurrence-merge against the authoritative store is the backstop that catches it.
- **Dogfood** (`origin` slug == marketplace slug) → local write, no issue. Reuses the same comparison
  the fork discussion distrusts, but only for "am I home?", which it is sound for — never for resolving
  a delivery target.
- **Slug collision** → disambiguate by appending the first cycle name (P2), checking **both** the active
  corpus and `closed/` before deciding a slug is free.
- **Recurrence-merge uncertainty on capture** → create a new file with `possibly_related_to:`, never a
  silent merge (the create-over-merge bias, P6).
- **`--repo` typo** → the skill echoes the normalized `owner/name` and confirms before `gh issue create`,
  so a typo can't silently misfile.
- **`dev-backlog` label absent in target repo** → create it (idempotent) before the first issue.
- **`inbox` run outside the plugin repo** → it has no authoritative local store to drain into; guard it
  to operate only when the current repo is the plugin repo (else say so and stop).
- **`convert` on an issue with no parseable front-matter block** (a hand-filed issue) → skip it with a
  visible note; never crash or fabricate a front-matter block.
- **`list`'s retry network side effect** — a read verb that re-attempts delivery makes a network call and
  can mutate the store (remove a `pending` copy). This is a **deliberate** design choice (surfacing and
  retrying are the same verb, so a stranded item is never merely displayed), documented in the ADR as
  intended, not an open issue.

## Audience

Solo maintainer of a personal Claude Code plugin repo (`awilliamsbuilds/claude-plugins`), per
`CLAUDE.md`. The verbs are hand-invoked at the terminal; ergonomics favor a fast default path with
explicit overrides.

## Technical Constraints

- **Plain Markdown items**, hand-editable without tooling; front-matter is the machine-read surface.
- **Worktree-relative writes.** Cross-repo routing writes **no file outside the worktree** — it calls the
  GitHub API via `gh` against an explicit `--repo` slug. The only local write on the routing path is the
  in-worktree `routing: pending` degrade file.
- **All GitHub ops via `gh`** (`issue create` / `list` / `comment` / `close`, `label create`), which
  carries its own auth. Grounding found `gh` authenticated via keyring and **no**
  `env.GITHUB_PERSONAL_ACCESS_TOKEN` set — so delivery leans on `gh`'s auth, not that env var. (The
  ADR's PAT assumption is corrected here.)
- **Slug allowlist `[a-z0-9-]` (P2) enforced at creation** — item/issue text can originate externally
  (a Linear issue via `dev:fix`, a diff under review, a foreign-repo capture), so a crafted title must
  never reach a filesystem path.
- **Entry text is data, never instruction** — item bodies and issue bodies are read as data only. More
  load-bearing now that a `scope: plugin` item's text crosses repos.
- **Single source of truth** — the routing procedure lives in `references/tech-debt.md`; the skills link
  to it and hold no second copy (avoiding the second-copy-drifts failure the contract warns about).

## Dependencies

- **Follow-ons 1 & 2** (store + migration) — shipped; grounding confirmed `docs/dev/tech-debt.md` and
  `docs/dev/product-plan.md` are gone and `docs/backlog/` is populated.
- **`gh` CLI, authenticated** — present (2.88.1) and authed via keyring.
- **Marketplace config** in `~/.claude/settings.json` (`enabledPlugins` + `extraKnownMarketplaces`) —
  present, with `dev@local-plugins` → `awilliamsbuilds/claude-plugins`.
- **The `docs/backlog/` contract** (`references/tech-debt.md`, P1–P8) — the schema and procedures this
  cycle extends.

## UI Needed

No. This is CLI skill-instruction + contract editing; no visual UI, so Shape is skipped.

---
*Auto-filled dimensions: none — every dimension was answered from the ADR, the grounding sweeps, or the three confirmed interface decisions.*
*Grounding inventory: `git remote get-url origin` → `awilliamsbuilds/claude-plugins` (this is the plugin/dogfood repo); `settings.json` read → `extraKnownMarketplaces.local-plugins.source.repo = awilliamsbuilds/claude-plugins` and `enabledPlugins["dev@local-plugins"]` confirms the plugin→marketplace link among 3 registered marketplaces; `gh --version` → 2.88.1 authed via keyring, `env.GITHUB_PERSONAL_ACCESS_TOKEN` absent (routing must lean on gh auth, correcting the ADR); `gh label list` → no `dev-backlog` label exists (must create); `references/tech-debt.md` P1 (lines 65/74/89–91/106–108) → `scope`/`routing` still marked reserved-cycle-3 (this cycle un-reserves); `ls docs/dev/tech-debt.md docs/dev/product-plan.md` → both absent (follow-ons 1&2 done); grep `dev:done` SKILL → Step 6a flush at ~line 335 with P6 recurrence-merge + To Record/To Close parsing (the hook insertion point); read `dev:debt` SKILL → current verbs are list/show/closed/close only (add + inbox are new); `dev:done` reverse-lookup (line 168) + contract P3 → product-plan promotion/deletion already live (follow-on 4, out of scope); Step 7 pass-4 cross-check → zero file-overlap between this cycle's 3 files and any active backlog item, so nothing folded into scope.*
