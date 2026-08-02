# dev:migrate-tracker — Decision Log
*2026-08-02 · Branch: feature/legacy-tracker-migration · PR #60*

## What was built

`/dev:migrate-tracker` — one skill that converts a repo's retired aggregate tech-debt tracker
(`docs/dev/tech-debt.md`, `## Open` / `## Closed`, `### <title>` entries) into the per-item
`docs/backlog/` store, routing plugin-scope items to the plugin repo per §P9 on the way. Run by
hand, once per repo; a one-line no-op everywhere else.

## Key decisions

**The skill states the legacy format itself, as its own `## The Legacy Format` section (L1–L8) →**
because no live document describes it any more. The old parsing rules were *retired* from
`references/tech-debt.md` when the contract moved to front-matter, leaving only a one-line note at
`:417`. Every rule was **recovered, not invented** — from `git show ab054df:…/tech-debt.md` (the
retired *§ Where a field ends*) and the real 11-entry example at `git show 7ebe89a^:docs/dev/tech-debt.md`.
This is the sole stated exception to the skill's own **CITE-DONT-COPY** rule, and the exception is
named as such in the text so a later editor doesn't "fix" it into a citation of something that no
longer exists.

**Store setup is delegated wholesale to `dev:init` Scenario D → no second copy of the tree-creation
logic.** `dev:init` already creates `docs/backlog/` + `closed/` idempotently on both its branches and
self-describes as the only automatic path by which a pre-store repo ever gets the store. The one cost
is that `dev:init` is *interactive*, so the skill must announce which of two things the user is about
to enter — a Scenario D config check, or a **full fresh init** in a repo with no `config.json` — so a
migration cannot silently turn into a first-time setup.

**One confirmation gate, covering both the slug and the scope → because the slug is permanent and the
routing is irreversible.** P2 fixes the slug as the item's identity, and it is *not* mechanically
derivable from the title (the real hand migration editorialized: *"Architecture-cycle design doesn't
pressure-test cross-boundary delivery mechanisms"* → `debt-arch-cross-boundary-transport`). Both the
proposed slug and the proposed scope go in one table with a per-item "why" column, confirmed before
any store write or `gh issue create`. The design point stated in the skill: **the heuristic does not
need to be perfect, only legible** — the "why" column is what makes a wrong guess cheap to catch.

**Five disjoint buckets, not a `parsed == written + routed` count → because that naive test fails
every mixed-state repo.** (a) new file, (b) P6-merged, (c) routed as an issue, (d) degraded to
`routing: pending`, (e) unparseable. A merged item creates *no* new file; a degraded item is *both*
written locally and route-attempted. The tracker is deleted only when (e) is empty and
(a)+(b)+(c)+(d) equals the parsed count. Mixed state is expected, not exotic — `dev:done`'s flush
creates the store the first time any cycle defers something.

**Never delete on doubt → the ordering principle for every parse rule.** An item lost in migration is
unrecoverable once the tracker is gone; a surviving tracker costs only a re-run. This is why an entry
missing `**Files:**` is written with `files: []`, flagged, and **counted as migrated** rather than
dropped, while an entry the parser cannot read at all goes to bucket (e), is reproduced verbatim, and
single-handedly blocks retirement.

**`cycles:` padding for closed items inverts the open-item precedence, deliberately.** On an open
entry the `Cycles:` list wins over `Recurrence: N` (the old format's own stated tiebreak). On a closed
entry there *is* no `Cycles:` list — `N` is the only surviving evidence of recurrence — so `N` wins and
`cycles` is seeded from `closed_by` and padded with the synthetic marker `migrated`. The skill states
this inversion and its reason explicitly, because writing the two rules without that sentence reads as
an inconsistency and invites a later "fix" that discards real data. The concrete evidence it is
load-bearing: the earlier hand migration got this wrong, and
`docs/backlog/closed/debt-gate-path-state-writes.md` still carries one cycle name against
`recurrence: 2`.

**`possibly_related_to` is resolved late, against final basenames → not at mapping time.** The legacy
field points at an exact *title*; P1 wants a *slug*. Resolving at map time would write a dangling
pointer on any user slug edit or any P2 collision rename, so the raw title is carried forward
unresolved and a `SLUG_MAP` built over the whole local-write set resolves every pointer against one
settled naming.

**An off-repo `scope: plugin` item skips local recurrence-merge entirely.** The local corpus belongs to
a different repo and structurally cannot hold an item bound for another; P9.intake-dedup is its
cross-repo equivalent. Merging locally anyway would leave a stray file in the wrong repo's store,
contradicting P9.delivery's "nothing written locally."

**`type: debt` for everything, no classification pass →** the legacy tracker held only debt by
construction; it *was* a debt tracker.

**Never commit, never stage →** same rule and reason as `dev:init` and `dev:debt`: this runs outside a
cycle, usually with the checkout on `main`.

**Two lines added to `dev:start` — the one file beyond the spec's named deliverable.** `dev:start`'s
FYI list is hardcoded per skill name, so a new non-pathway skill is otherwise invisible to the one
surface built to answer "which `dev:*` skill do I run next." Success Criterion 11's four protected
files (`references/tech-debt.md`, `init`, `debt`, `done`) end the cycle byte-identical.

## Validation notes

- **5 loops run** (tier: standard, budget 3). At the Step 4a gate after loop 3, four P2s were still
  open and the user chose to keep looping; loops 4 and 5 ran under that authorization. Loop 5's cold
  re-review returned no P1 and no P2.
- **P1s (3, all loop 1, all fixed):**
  - Proposed slugs were checked against disk but never against each other — two colliding
    editorialized slugs meant the second write silently overwrote the first, *both* items still
    counted in bucket (a), reconciliation passed, and the tracker (the only remaining copy) was
    deleted. Fixed by deduping at proposal time and checking a third set at write time.
  - Nothing stated how an issue body reaches `gh`. The natural `--body "…"` form expands `$…`,
    `` `…` ``, and `$(…)` — and the reference fixture's own entries quote shell. Fixed by mandating
    `--body-file` or a single-quoted heredoc.
  - `ENTRY_COUNT` counted only `### ` headings under `## Open`/`## Closed`, so an entry under any other
    heading was excluded from *both* numerator and denominator — never migrated, never reported,
    reconciliation clean. Fixed with a `FILE_HEADING_COUNT` cross-check feeding bucket (e).
- **P2s (19 across loops 1–5, all fixed).** The notable ones: a `## Closed` entry could P6-merge into
  an active *open* item, discarding `closed:`/`closed_by:`; `SLUG_MAP` built incrementally made pointer
  resolution iteration-order dependent; the `<first-cycle>` disambiguator was lifted from untrusted
  text and used as both a path component and a YAML value with no allowlist; bucket membership was
  self-reported, so `rm "$TRACKER"` fired on arithmetic alone; and the heading-drift guard escaped
  twice — once firing only at `FILE_HEADING_COUNT == 0`, then again by exempting the prose preamble
  wholesale.
- **Three of the five loops caught regressions the previous loop introduced.** The pattern was
  consistent: a rule fixed in one step and not propagated to the step that depends on it (Step 7's
  cycle comparison vs. Step 9's verification of it; Step 7's collision procedure vs. Step 8's mirror of
  it). Every one was caught by the fix-diff cold re-review — a fresh subagent seeing only that loop's
  diff, the Success Criteria, and the checklist. None would have been caught by whoever wrote the fix.
- **Accepted as-is (assessed against the carrying-cost test and dropped):** one P3 — the orphan sweep
  can double-report a drifted entry under a hand-added section, since the `FILE_HEADING_COUNT`
  cross-check records headings but defines no extent (report accuracy only, no data loss, tracker
  correctly survives either way); one Nit — "every other lossy path in this skill carries a flag" is a
  false universal in rationale prose. Each is a local one-clause fix in a single file,
  fixed-once-and-forgotten, which is what the test says not to put in the store.
- **Protected-files invariant verified after every loop:** `references/tech-debt.md`,
  `init/SKILL.md`, `debt/SKILL.md`, `done/SKILL.md` byte-identical to `main`. The whole branch touches
  only `migrate-tracker/SKILL.md`, `start/SKILL.md`, and cycle artifacts.
- **Verified empirically during the loops**, not just read: `git rev-parse --git-common-dir` returns
  `.git` at a primary checkout's root, `../../../.git` deeper, and an absolute path from a linked
  worktree — confirming the `cd … && pwd` form is required, and that the skill's stated rationale for
  it is accurate.

## Out of scope, recorded rather than fixed

- **One pre-existing store defect, left deliberately.**
  `docs/backlog/closed/debt-gate-path-state-writes.md` carries `cycles: [state-write-mode-audit]` — one
  name — against `recurrence: 2`, violating P1's `recurrence == len(cycles)` invariant. It is an
  artifact of the 2026-07-28 hand migration, not of this cycle. Fixing it is a one-line edit somebody
  should make deliberately.
- **Two items buffered to the backlog store**, both systemic and both blocked by Success Criterion 11:
  P2's collision rule stops at one level and says nothing about a *double* collision (this skill needed
  the escalation and had to state it locally, in two places, violating its own CITE-DONT-COPY rule);
  and P9's issue-body fence is documented as three backticks, which truncates any body containing a
  code fence — the producer side is fixed here, but `dev:debt inbox` still has to match on the
  `markdown` info tag rather than the delimiter width to close the loop.

## Artifacts (archived)

Spec, plan, build notes, and validation committed at `514032f` on branch
`feature/legacy-tracker-migration`.
