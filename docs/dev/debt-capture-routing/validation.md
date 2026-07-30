# Backlog Capture + Cross-Repo Routing — Validation Report
*Branch: feature/debt-capture-routing · 2026-07-30*

## Summary
Loops run: 1 / 5
Final status: clean — no open P1/P2, all P3/Nit resolved inline

Feature cycle. Two cold reviews (code + security) ran in parallel on the diff since Build
(`acc88af..abb90cf`), as fresh subagents seeing only the diff, spec Success Criteria, and plan tasks.
One fix loop resolved every finding; a third fresh subagent cold-re-reviewed the fix diff
(`abb90cf..6fca918`) and found no regressions.

## Issues Resolved

### Loop 1

**P2 — correctness**
- **`add` ran local recurrence-merge unconditionally before route-by-scope** (`debt/SKILL.md` Step 7).
  For a `scope: plugin` item captured *off* the plugin repo, this wrote a stray file into the wrong
  repo's local corpus while step 5 reported "nothing written locally" — the exact debt-scatter the
  feature prevents. → Gated step 4 to local-write scopes (`repo`, dogfood `plugin`); off-plugin items
  skip local merge, with P9.intake-dedup as the cross-repo equivalent, mirroring `dev:done`'s
  buffered-route branch.
- **`dev:done` pending-retry pass was gated behind the no-buffer skip** (`done/SKILL.md` Step 6a). The
  contract calls it "always-reachable / runs on every cycle that has a stranded item," but item 1
  ("skip this whole step if no buffer") suppressed it whenever a cycle deferred nothing. → Hoisted the
  pass above item 1, guarded on `docs/backlog/` existence; item 1 now skips only the buffer flush
  (items 2–5).
- **`recurrence == len(cycles)` invariant broke on a manual re-hit** (`debt/SKILL.md` Step 7 & 8). When
  a matched file's `cycles:` already held `manual`, the append was skipped ("only if not already
  present") but the `recurrence:` bump still fired → `recurrence` 2, `len(cycles)` 1; a reader treating
  `cycles` as authoritative then discarded the bump. → The synthetic `manual` marker now repeats in
  `cycles:` (`[manual, manual]`), so len grows in lockstep with recurrence; `inbox`'s merge appends the
  incoming cycle marker(s) in lockstep too.
- **(security) `inbox` derived the local filename from an untrusted issue title without the P2
  allowlist** (`debt/SKILL.md` Step 8). `<type>-<slug>` is parsed off `[dev-backlog] <type>-<slug>`,
  which crossed a repo boundary; only collision disambiguation was mentioned, not the character
  allowlist → a title `[dev-backlog] debt-../../../../tmp/evil` could write outside the store. →
  Re-apply the P2 allowlist on the receiving side: `<type>` ∈ {debt, backlog}, `<slug>` matches
  `[a-z0-9-]+`, strip/reject otherwise; unsanitizable titles are skipped-and-left-open like unparseable
  issues.

**P3 — hardening**
- `list`'s pending-retry could empty the corpus after Step 1's empty-guard passed → added an
  emptiness re-check after the retry pass (prints the P7 direct-invocation message, not "0 items").
- `--repo` reached `gh` without an `owner/name` allowlist → P9.target-resolution now validates
  `^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$`, rejecting leading-`-` argument-injection values.
- Routing publishes an item's full body into a possibly-public tracker → the `add` echo/confirm now
  states this, and P9.delivery documents it.
- A degraded explicit `--repo` silently re-resolves to the config target on retry (no schema field to
  persist it) → documented in P9.retry-seam.

**Nits**
- Citation order `P9.delivery + P9.intake-dedup` corrected to `intake-dedup → delivery` at all five
  sites (dedup gates create).
- Dispatch-table placeholder `[--repo <t>]` → `[--repo <owner/name|URL>]`.

## Issues Remaining
None. No open P1/P2/P3; no Nits surfaced past the fix loop.

## Notes
- All three planned files were touched exactly as scoped; no new `state.json` key introduced (routing
  state lives in item front-matter `routing: pending`).
- Reviewers confirmed SC8 (single-source-of-truth: no skill restates §P9) and SC9 (mode symmetry) hold.
- Two fixes (1 and 3) closed the gap where `add` didn't mirror `dev:done`'s more careful plugin-scope
  handling — worth carrying into the decision log as the cycle's main correctness theme.
