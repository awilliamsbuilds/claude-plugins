# Backlog Capture + Cross-Repo Routing — Decision Log
*2026-07-30 · Branch: feature/debt-capture-routing · PR #56*

## What was built

The last unbuilt follow-on to the unified backlog + tech-debt store: an on-demand capture verb
(`/dev:debt add`), the cross-repo routing machinery that sends `scope: plugin` items home to the
plugin repo as GitHub issues, and the `/dev:debt inbox` drain that converts them back into store
files — with the routing procedure itself living in `references/tech-debt.md` as §P9.

## Key decisions

**The procedure lives in the contract, not the skills** → `references/tech-debt.md` §P9 is the single
source of truth for routing; `debt/SKILL.md` and `done/SKILL.md` cite it by sub-procedure name
(P9.target-resolution, P9.dogfood, P9.delivery, P9.intake-dedup, P9.degrade, P9.retry-seam) and hold
no second copy. This is the contract's own second-copy-drifts warning applied to itself.

**Target resolution reads config, never `origin`** → the plugin repo slug comes from
`~/.claude/settings.json` (`enabledPlugins["dev@<mp>"]` → `extraKnownMarketplaces[<mp>].source.repo`).
`origin` is used for exactly one question — "am I already home?" (P9.dogfood) — which it is sound for,
and never to resolve a delivery target, which it is not (forks).

**Degrade, never drop** → any delivery failure (no network, no auth, API error, unresolvable slug)
writes the item locally with `routing: pending` plus a visible marker. This is the writer-side of the
contract's P7 silent-degrade discipline. Both `/dev:debt list` and the next `dev:done` flush re-attempt
those items *before* writing new ones, removing the local copy on success.

**`list` retries as a deliberate side effect** → a read verb that makes a network call and can mutate
the store is unusual, and was chosen anyway: surfacing and retrying are the same verb, so a stranded
item is never merely displayed. Documented as designed, not as an open issue.

**One cycle, not two — split honored in ordering** → the spec named a clean seam (Parts 1+2, then
Part 3). Plan kept the cycle whole but sequenced `inbox` last, so it was the natural cut if Build ran
long. Routing degrades gracefully without the drain: routed issues simply accumulate.

**Manual captures carry a synthetic `manual` cycle marker** → a hand-filed item belongs to no cycle,
but `cycles: []` + `recurrence: 0` would break the P1 invariant `recurrence == len(cycles)` on the
first merge. Seeding `cycles: [manual]` + `recurrence: 1`, and repeating `manual` on each re-hit,
keeps the invariant intact at both seed and merge time.

**Slug marker pinned at Plan time** → issue title `[dev-backlog] <type>-<slug>`, body a single fenced
`markdown` block holding the item's complete front-matter + body, label `dev-backlog` (created
idempotently). List-then-filter is the primary matching mechanism; `gh --search` is a convenience,
never the sole gate, because its index is eventually consistent.

**The buffered-route branch is forward-defensive, and said so** → no in-scope producing stage emits a
`scope: plugin` buffered item, so `dev:done`'s routing branch is exercised only by hand-editing a
buffer. Rather than manufacture a producer to make it testable, the cycle documented the reachability
split: the pending-retry half is the always-exercised one.

## Design choices

Shape was skipped — CLI skill-instruction and contract editing, no visual UI.

Ergonomics followed the audience (solo maintainer at a terminal): a fast default path
(`type: backlog`, `scope: repo`) with explicit overrides (`--debt`, `--plugin`, `--repo`). `--repo`
without `--plugin` is rejected with a message rather than silently ignored or treated as implying
`--plugin`. A `--plugin` capture echoes the normalized `owner/name` and confirms before routing,
because routing crosses a repo boundary and a typo would otherwise misfile silently.

## Validation notes

- 1 loop run (tier: deep). Two cold reviews (code + security) ran in parallel on the Build diff as
  fresh subagents; a third fresh subagent cold-re-reviewed the fix diff and found no regressions.
- **P1s:** none.
- **P2s found and resolved (4):**
  - `add` ran local recurrence-merge unconditionally before route-by-scope, writing a stray file into
    the wrong repo while reporting "nothing written locally" — the exact debt-scatter the feature
    exists to prevent. Gated the local merge to local-write scopes.
  - `dev:done`'s pending-retry pass sat behind the no-buffer skip, so it never ran on a cycle that
    deferred nothing — contradicting its "always-reachable" contract. Hoisted above the skip.
  - The `recurrence == len(cycles)` invariant broke on a manual re-hit (bump fired, append skipped).
    Fixed by repeating the `manual` marker in lockstep.
  - *(security)* `inbox` derived a local filename from an untrusted issue title without re-applying
    the P2 allowlist — a crafted title could write outside the store. Allowlist re-applied on the
    receiving side; unsanitizable titles skipped and left open.
- **P3s resolved inline (4):** `list` emptiness re-check after the retry pass; `--repo` `owner/name`
  allowlist against argument injection; explicit note that routing publishes an item body into a
  possibly-public tracker; documented that a degraded explicit `--repo` re-resolves to the config
  target on retry.
- **Nits resolved (2):** citation order `intake-dedup → delivery` corrected at five sites; dispatch
  table placeholder expanded.
- Nothing accepted as-is; no open items at close.
- The cycle's correctness theme: two of the four P2s were the same gap — `add` not mirroring
  `dev:done`'s more careful plugin-scope handling.

## Artifacts (archived)

Spec, plan, and validation committed at: `cde8b3d` on branch `feature/debt-capture-routing`
