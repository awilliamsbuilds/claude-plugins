# Entry Adapters

*Branch: feature/entry-adapters · Confidence: 88% — Ready · 2026-08-15*
*Cycle type: feature · Tier: deep*
*Milestone 2 of `docs/dev/product-plans/dev-fast-path.md` (absorbs and supersedes `fast-path-backlog`)*

## Intent

`/dev:fix` takes free text. Everything else that could start work — a Linear issue, a `docs/backlog/`
item — has no way in, so the request has to be retyped by hand from a source that already states it.

Two half-built paths exist today and neither works. `dev:linear` opens the **full seven-stage cycle**
from a Linear issue, which is the ceremony problem this project exists to solve; it also writes
`state.json.linear_issue` that **nothing reads**, never sets the issue's status, never uses Linear's
`gitBranchName`, and never writes a `Closes` line — so the Linear round trip is inert in both
directions. Milestone 2 (`fast-path-backlog`) was going to build a second, separate path for backlog
items.

Building those as two adapters would produce two mechanisms that drift. They are the same shape: read
an identifier, resolve it to a request, hand it to the lane, and close the loop on merge. This cycle
builds that shape **once**, with two sources on it, and retires `dev:linear`.

## Scope

**One adapter seam, four hook points.** An adapter is not a workflow — it is a resolver that runs
*before* the lane and side effects that fire at fixed points around it:

| Hook | What the adapter supplies |
|---|---|
| **Resolve** | identifier → request text + grounding hints + a display label |
| **Pre-lane** | optional side effect when work starts (Linear: set the "started" status) |
| **Post-PR** | optional side effect once the PR is open (Linear: set the "in review" status) |
| **Closeout** | optional side effect after merge (Linear: nothing — the `Closes` line does it; backlog: close the item) |

Post-PR is a distinct hook rather than a variant of Pre-lane because the lane's two irreversible
boundaries are *work started* and *PR opened*, and the two statuses SC4 caches map one to each. Folding
them into a single hook would set "in review" before the change exists.

The lane itself is unchanged: ground → triage → branch → change → verify → PR → stop. An adapter
feeds it and cleans up after it; it never alters what happens in between.

**Two sources on that seam.**

- **`/dev:fix linear [<issue-id>]`** — resolves a Linear issue. With no ID, lists the user's assigned
  issues in an unstarted state and asks which. Sets the issue's status when work starts, uses Linear's
  `gitBranchName` for the branch, and writes `Closes [<ID>](<url>)` into the PR body so the issue
  closes on merge.
- **`/dev:fix backlog <slug>`** — resolves `docs/backlog/<slug>.md`. The item's body becomes the
  request, its front-matter `files:` become grounding hints, and on merge the item is closed through
  the existing path rather than a second closer.

**Triage still decides the weight.** Adapter-sourced work runs the lane's existing escalation rule
unchanged — 0 decisions proceed, 1 is asked inline, 2+ stops. The *source* no longer determines
whether work is heavy or light; the *work* does.

**Escalation carries context.** When triage stops a Linear-sourced request, it prints
`/dev:spec linear <issue-id>`, and `dev:spec` pre-fills confidence dimensions from the issue —
absorbing `dev:linear`'s existing issue→dimension mapping rather than deleting it. Without this, the
lane declining a ticket would silently destroy the pre-fill capability that both `dev:linear` and the
legacy `fix.md` had.

**Portability: nothing about one workspace is assumed.** Linear workflow status names are
workspace-configurable, and semantic `type` cannot disambiguate them (see Technical Constraints). So
the skill **asks once per repo** which status means "work started" and which means "in review",
storing the resolved IDs under a `linear` key in `docs/dev/config.json`. Subsequent runs are silent.
No status name, team name, team ID, user, or project identifier is ever hardcoded in the plugin.

**`dev:linear` is deleted.** Its Linear-fetch and dimension-mapping logic moves onto the escalation
path; the skill file and all its references go.

**Deleting it moves two things besides the mapping, and both are load-bearing.** `dev:linear` Step 3
also owns the **uppercase-tolerant cycle-slug allowlist** `^[A-Za-z0-9][A-Za-z0-9-]*$`, which exists
so a Linear issue-ID prefix (`ENG-123`) survives slug normalization — `dev:spec`'s own rule is
strict-lowercase. That tolerance moves to `dev:spec`'s Linear entry path, or the escalated cycle
silently lowercases the issue prefix. More importantly, `done/SKILL.md:260` **cites that allowlist by
name** as the reason `<feature>` is safe to interpolate into a shell `-m`. Deleting the skill without
re-pointing that citation leaves a live injection-safety argument referring to a file that no longer
exists — a checkable claim that stops being checkable. The citation must be updated in the same
change, not left for a later reader to notice.

**Three tracked debt items are paid here**, all in files this cycle already opens:

- `debt-fix-tail-guard-stale-when-offline` — capture the fetch exit status in the merge tail's
  leftover-branch scan and downgrade the empty-scan message when `origin` could not be refreshed.
- `debt-fix-tail-multiple-open-prs-unchecked` — read the PR count rather than `.[0]`, so the tail
  actually performs the multiple-open-PR stop its prose already promises.
- `debt-primary-cd-failure-unchecked` — **forced, not elective.** The item lists 13 files carrying an
  unguarded `PRIMARY` derivation, and one of them is `plugins/dev/skills/linear/SKILL.md`, which this
  cycle deletes. Its `files:` list and its "all 13 sites" wording must drop to 12 or the item becomes
  a false record the moment this merges. This is a bookkeeping correction, not a fix — the remaining
  12 sites stay unguarded and the item stays open.

**Note for Plan — this is at the top of one deep cycle's range.** In scope: the seam, two adapters,
live-MCP status resolution plus a new config key, the `dev:spec` escalation pre-fill, the `dev:pr`
reader, deletion of `dev:linear` with its reference sweep, and three debt items. It was deliberately
kept as one cycle because a seam shaped by a single consumer is a guess — two real consumers are what
validate it. **If the task list comes back oversized, the split seam is source-shaped, not
layer-shaped:** (1) the seam + the backlog adapter + the two `debt-fix-tail-*` items — no external
dependency, fully testable offline; then (2) the Linear adapter + the `dev:linear` deletion + the
`debt-primary-cd-failure-unchecked` bookkeeping correction, which is forced by that deletion and must
ride with it. This is a fallback ordering, not an instruction to split.

## Out of Scope

- **Retiring `~/.claude/commands/fix.md`.** This cycle *unblocks* it, but those files live in the
  user's home directory and no PR here can delete them. The manual step is documented, not performed.
- **Retiring `pr.md` and the two `security-review` commands.** Separately blocked: `/dev:fix` runs no
  security review, and no `dev` skill does whole-project security scanning. Both are Milestone 3.
- **A security review inside the lane.** Named here because retiring `pr.md` depends on it, and
  deliberately not solved here — "should the fast path run a security review" is a design question
  about the lane itself, not about entry adapters.
- **Linear status transitions beyond the two named.** No transition on merge; the `Closes` line is
  the closer. A second writer for one state invites double-transitions.
- **Any third adapter** (GitHub issues, Jira, a URL). The seam should make them cheap; building one
  now would be speculative.
- **Changing the lane's triage rule, escalation thresholds, or PR flow.** Adapters feed the existing
  lane; they do not reshape it.
- **`/dev linear` as a command.** Rejected: the routing decision is triage's, so a name that
  presupposes the full cycle would misdescribe the behavior. The lane owns the door.

## Success Criteria

1. `/dev:fix linear <id>` on a 0-decision issue reaches an open PR with **no user turn** between
   invocation and the PR report, and the PR body contains `Closes [<ID>](<url>)`.
2. The same command on an issue carrying 2+ unresolved decisions **stops before changing any file**,
   lists the decisions, and prints `/dev:spec linear <id>`. Running that command marks the
   **issue-derived** dimensions filled — at minimum `intent` and `success_criteria`, from the issue's
   title/description and its acceptance criteria — and the opening confidence reading names the issue
   as their source. **"Confidence above zero" is deliberately not the test:** `dev:spec` already
   pre-fills `audience` and `technical_constraints` from `CLAUDE.md` on any repo that has one, so a
   nonzero opening score is satisfied by a repo having a `CLAUDE.md` and would pass even if the
   issue→dimension mapping were dropped entirely — the exact regression this criterion exists to catch.
3. `/dev:fix backlog <slug>` resolves the item, runs the lane, and after `/dev:fix merge` the item
   file is in `docs/backlog/closed/` with `status: closed` — closed via the existing close path, not a
   second implementation.
4. On a repo with no `linear` key in `docs/dev/config.json`, the first `/dev:fix linear` asks exactly
   two status questions, writes the resolved IDs to config, and asks nothing on subsequent runs
   **against the same team**. A first issue from a *different* team asks its own two questions, since
   status IDs are per-team (see Edge Cases).
5. **Status resolution reads the live workspace.** The skill calls `list_issue_statuses` and offers
   the returned statuses as the choices — it never presents a hardcoded list and never matches on a
   display name.
6. `grep -rn '/Users/\|awilliamsbuilds\|adam\|FORGE\|Cash Flow' plugins/dev/` returns zero — the same
   sweep the grounding footer ran. The scope is `plugins/dev/` deliberately: `plugins/plugin-manager/`
   and `plugins/writing/` legitimately name the repo owner (9 hits today) and are outside this cycle.
   Additionally, no Linear team ID, status ID, user ID, or project ID appears anywhere in `plugins/`.
7. With the Linear MCP unavailable or unauthenticated, `/dev:fix linear` fails **before** creating a
   branch, naming the reason. `/dev:fix backlog` and free-text `/dev:fix` are unaffected — a missing
   Linear does not degrade the rest of the skill.
8. `plugins/dev/skills/linear/` no longer exists, and every reference to `dev:linear` across
   `plugins/`, `README.md`, and `CLAUDE.md` either resolves to the new form or is gone. Historical
   records under `docs/decisions/` and closed items under `docs/backlog/closed/` are excluded.
9. The three entry forms plus the tail are mutually unambiguous: a free-text request whose first word
   is `linear`, `backlog`, or `merge` is still treated as free text (see Edge Cases).
10. `/dev`, `/dev:autopilot`, and stages `shape`/`plan`/`build`/`validate`/`done` are byte-identical
    except for `dev:linear` rename references. `dev:spec` and `dev:pr` change by design — Spec gains
    the escalation pre-fill, PR gains the `Closes` line — and `dev:fix` and `dev:debt` change as the
    Scope requires.
11. `docs/backlog/debt-primary-cd-failure-unchecked.md` names 12 files, not 13, and no longer lists
    `plugins/dev/skills/linear/SKILL.md`. Its body's site count agrees with its `files:` list, and the
    item remains `status: open` — the deletion removed a site, it did not guard one.

## Happy Path

1. `/dev:fix linear FOR-12` from anywhere in the repo.
2. Preflight passes; the adapter fetches the issue and reads its title, description, and
   `gitBranchName`.
3. Config has no `linear` key, so the skill lists the team's statuses and asks which means "started"
   and which means "in review". Both are written to `docs/dev/config.json`.
4. The issue is set to the "started" status.
5. The lane grounds the request against the real files, triages it at 0 unresolved decisions, and
   proceeds.
6. Branch created from Linear's `gitBranchName`; the minimal edit is made; the suite runs.
7. PR opened with `Closes [FOR-12](https://linear.app/…)` in the body. The issue moves to the
   "in review" status. The lane stops and reports.
8. User reviews, runs `/dev:fix merge`. PR merges; Linear closes the issue from the `Closes` line.

## Edge Cases

- **Ambiguous first word.** `/dev:fix linear auth is broken` is a free-text request about Linear auth,
  not an adapter invocation. Resolve as the `merge` token already does: `linear` and `backlog` are
  adapter tokens **only** when followed by nothing or by a single well-formed identifier. Anything
  longer is free text.
- **A backlog slug that looks like free text.** `/dev:fix debt-p9-slug-regex-allows-leading-dash`
  without the `backlog` keyword. Resolution is by *existence*, not syntax — but the bare form is
  deliberately **not** supported, because a request could legitimately be one word. The `backlog`
  keyword is required.
- **Linear MCP not configured.** Fail before branching, naming it. Never partially start.
- **Issue ID not found, or in another workspace.** Stop and report; do not fall back to free text.
- **Issue already in the "in review" status** (a re-run). Do not move it backwards; proceed and note it.
- **No unstarted issues assigned** when invoked with no ID. Say so; do not open a picker over an empty
  list.
- **Backlog item already `status: closed`.** Refuse — reopening is a decision the lane must not make.
- **Backlog item is `status: promoted`.** It became a product plan; the lane is the wrong tool. Refuse
  and name the plan.
- **Linear write permission missing** (read works, `save_issue` fails). The change is more valuable
  than the status update: warn, continue, and state in the final report that status was not updated.
- **A repo whose issues span multiple Linear teams.** Status IDs are per-team. Key the config by team
  so a second team asks its own two questions rather than reusing the first team's IDs.
- **`gitBranchName` fails the branch-name allowlist.** It is external input reaching git commands.
  Validate it; on failure fall back to the lane's own derived name rather than refusing the work.
- **Escalation on a backlog-sourced request.** Symmetric with Linear: print `/dev:spec` and name the
  item, leaving the item `open`.

## Audience

Single operator — the repo owner, running this many times a day across several repos and more than
one Linear workspace. The plugin is distributed via the `local-plugins` marketplace and must stay
installable by anyone, so nothing may hardcode a personal path, username, team, workspace, or status
name. This is the constraint that makes the status-resolution design load-bearing rather than
cosmetic.

## Technical Constraints

- **Linear status `type` cannot identify the two transitions.** Verified against the live API: in both
  teams of this workspace, `In Progress` and `In Review` are **both** `type: "started"`. A
  type-based mapping can tell "started" from "completed" but cannot tell "work began" from "PR
  opened" — which is exactly the pair being automated. This is why resolution is asked-and-cached
  rather than inferred. Status IDs also differ per team for identically-named statuses, so the cache
  must be team-scoped.
- **`list_issue_statuses` requires a team argument** and returns `{id, type, name}`. The team must be
  resolved before statuses can be listed — from the issue itself on the `<issue-id>` path.
- **`state.json.linear_issue` currently has no readers.** Written by `dev:linear`, initialized to
  `null` by `dev:spec`, read by nothing. Two writers of the `Closes` line follow, on **different
  transports** — this is the cycle's easiest thing to build backwards. On the **lane**, `dev:fix`
  holds the issue ID and URL in-turn and writes `Closes [<ID>](<url>)` directly into the PR body it
  creates itself; the lane persists no `state.json` (`fix/SKILL.md:16`, `:577`) and never enters
  `dev:pr`, so `linear_issue` is not involved at all. On the **escalated cycle**, `dev:spec` writes
  `linear_issue` into `state.json` and `dev:pr` becomes its first reader. What the two share is the
  line's format, not its plumbing.
- **The lane's argument parse is currently binary** — the bare token `merge` versus free text. Adding
  two adapter tokens makes it four-way, and free text remains the catch-all. The `merge` token's
  exact-match rule is the precedent to follow.
- **`docs/dev/config.json` gains a new key.** Per the config contract, every skill that reads that key
  must declare it in its Step 1 read list. Only the skills that read `linear` need to list it.
- **`dev:debt` Step 6 already owns "close an item."** The backlog closeout must reuse it or the
  `debt-pending.md` buffer that `dev:done` Step 6a flushes — not add a third way to close.
- **No `.mcp.json` in this repo.** The Linear MCP is configured per-consuming-project, so the plugin
  can never assume its presence; absence must degrade cleanly rather than error at an awkward point.
- **Frontmatter `name:` must stay bare** (`fix`, not `dev:fix`) or autocomplete renders `/dev:dev:fix`.
- **No build tooling.** The repo ships markdown skills; this cycle must not introduce a build step.

## Dependencies

- **Depends on** the `dev:fix` lane shipped by the `fast-path` cycle (PR #79) — the seam attaches to
  its ground/triage/branch/PR structure.
- **Depends on** `plugins/dev/references/tech-debt.md` for the backlog item schema and lifecycle. The
  backlog adapter is a consumer of that contract and must not fork it.
- **Requires** the `linear-server` MCP at runtime for the Linear adapter only; the backlog adapter and
  free-text lane have no external dependency.
- **Unblocks** retiring `~/.claude/commands/fix.md` (Milestone 3), which is the last consumer of the
  standalone Linear round trip.

## UI Needed

**No.** Terminal output only. The surface is the issue picker, two one-time status questions, the
escalation notice, and the final report — short copy that settles in this spec and the plan. The
`fast-path` cycle established the same reasoning for the same kind of surface.

---
*Auto-filled dimensions: none — every dimension was either answered directly or derived from a
verified grounding result, with the derivation stated.*

*Grounding inventory: `state.json.linear_issue` readers enumerated by repo-wide sweep
(`grep -rn 'linear_issue' plugins/`) → two hits, both writers (`linear/SKILL.md:100` writes,
`spec/SKILL.md:214` initializes to null), **zero readers** — the claim that the Linear round trip is
inert is verified, not assumed. `dev:linear` status/branch/Closes gaps each checked by targeted grep:
no `save_issue`/`In Progress`/`In Review` in `linear/SKILL.md`, no `gitBranchName`, and
`grep -rn 'Closes \[' plugins/dev/skills/` → zero. Lane argument parse read directly at
`fix/SKILL.md` §Step 1 — confirmed binary (`merge` token vs free text), which is what makes the
four-way parse a real design constraint. **Linear status ambiguity verified against the live API, not
documentation:** `list_issue_statuses` called for both teams in this workspace; both returned
`In Progress` and `In Review` as `type: "started"` with team-specific IDs — this is the spec's most
load-bearing claim and the reason the portability design is asked-and-cached. `list_teams` confirmed
team names are workspace-specific. Negative space swept for the portability criterion
(`grep -rn '/Users/\|awilliamsbuilds\|adam\|FORGE\|Cash Flow' plugins/dev/`) → zero, so SC6 starts
from a clean baseline. Backlog item schema read from `references/tech-debt.md` §P1 — confirmed
`status`, `files:`, and the `**Done looks like:**` body give an adapter everything it needs.
`dev:debt` step headings enumerated → Step 6 "Close an Item" already exists, which is why the
closeout must reuse rather than reimplement. `.mcp.json` absence in this repo confirmed by `ls`.
Open-debt cross-check run against the P5 corpus — 27 active items, each item's front-matter `files:`
intersected against this cycle's surface by script, **not by reading**. **This pass corrected a false
claim in an earlier draft of this footer**, which asserted zero intersections without having run the
sweep; the sweep returned **6**. Two were folded into Scope
(`debt-fix-tail-guard-stale-when-offline`, `debt-fix-tail-multiple-open-prs-unchecked`, both in
`skills/fix/SKILL.md`); three were surfaced and declined
(`debt-artifact-path-rule-artifact-component-unconstrained`, `debt-spec-grounding-citation-unverified`,
`debt-p9-issue-body-fence-width`); and one — `debt-primary-cd-failure-unchecked` — is not elective,
because its `files:` list names `skills/linear/SKILL.md`, which this cycle deletes. The declined three
remain open and untouched. Recording the correction rather than the tidy result is deliberate: the
inventory is evidence, and an inventory that hides its own miss is worth less than one that shows it.*
