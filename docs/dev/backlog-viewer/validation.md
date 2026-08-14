# Backlog Viewer — Validation Report
*Branch: feature/backlog-viewer · 2026-08-14*

## Summary
Loops run: 3 / 3
Final status: clean — no open P1/P2

Reviews ran as fresh subagents denied this session's history, per Step 2: a code
review and a security review in parallel on the build diff (`bee9f3d..9d3dab9`), then a
cold re-review of each loop's own fix diff before the loop could exit.

Test suite: 88 tests, `OK`, no skips (`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest
discover -s plugins/dev/skills/debt -p 'test_*.py'`). Build shipped 79; the fix loops added 9.

## Issues Resolved

### Loop 1

- **P2** — Detail-pane bodies collapsed every labeled section into one run-on paragraph.
  `renderBody` split only on blank lines while the store's body format runs
  `**What's wrong:**` / `**Why deferred:**` / `**Done looks like:**` on consecutive lines.
  → Fixed by `white-space: pre-wrap`. *Superseded in loops 2–3 — see below.*
- **P2** — The 403 Host-allowlist rejection carried the identity headers, handing a DNS-rebinding
  attacker the absolute primary path and the server pid. That 403 is precisely the response such
  an attacker can read same-origin, and Task 2 step 6 had deliberately kept `primary` out of the
  page for the same reason. → Identity headers are now sent only to allowed hosts.
- **P2** — `cmd_stop` sent `SIGTERM` to a pid read off the wire. The security reviewer demonstrated
  end-to-end that a process squatting a port in 8730–8739 could make the stop path kill an
  unrelated process. → Added `_pid_is_viewer`, which verifies the pid's own command line before
  signalling, and a non-positive pid is now discarded at parse time (`os.kill(0, …)` signals the
  whole process group; `os.kill(-1, …)` signals every process the user may signal).
- **P2** — A start that exceeded `START_TIMEOUT` but then came up was read as a lost race, so
  `cmd_start` spawned a second server for the same primary. `find_running` returns the first match,
  so a later stop would only ever kill one, orphaning the other beyond any CLI path. Breaks
  Success Criterion 7. → The re-probe now recognizes our own viewer and reports success.
- **P3** — `do_HEAD` loaded and rendered the whole store per probe, against Task 6 step 8's stated
  contract that the probe is cheap and never renders. A single `stop` drove ~20 wasted full-store
  renders. → HEAD answers the identity question without touching the store.
- **P3** — A stem present in both the active corpus and `closed/` (what an interrupted
  `dev:debt close` leaves) shadowed one copy: both rows rendered, but either row opened the active
  item, and relationship links resolved ambiguously. The one path by which an item becomes
  effectively invisible, which is what Success Criterion 1 guards. → Items now carry a unique
  `key` alongside the display `id`; the page selects, highlights, and traverses on it.
- **P3** — Real-corpus facet tests asserted exact values, so ordinary store growth would turn the
  suite red (one `scope: plugin` capture, the first `P1`, a fifth `possibly_related_to`). → Relaxed
  to assert the ordering *rules*; the synthetic corpus keeps the exact orderings.
- **P3** — No `X-Frame-Options` or CSP; the page was framable by any origin. → Both added.
- **Nits** — malformed `recurrence` displayed as `seen 0×`; `--port` with no value reported the
  flag as unrecognized; `page.encode` sat outside the render guard (a non-UTF-8 filename would have
  killed the request rather than 500ing); the `Server` header named the exact Python patch version;
  `probe` followed redirects, letting a squatted port turn `/dev:debt view` into an outbound beacon.

### Loop 2

Both raised by loop 1's cold re-review.

- **P2** — Loop 1's `pre-wrap` fix separated the labels but froze the source's ~95-column hard
  wrapping into a 720px pane. Measured against the store: **21 of 31** bodies have the run-on label
  shape and **27 of 31** carry hard-wrapped prose, so `pre-wrap` traded one rendering defect for
  another across most of the corpus. (The re-reviewer reported only one file had the run-on shape;
  direct measurement contradicted that, and the count is what drove the fix.) → `paragraphsOf` now
  splits at bold-label lines and joins the rest with spaces: labels separate, prose reflows.
- **P2** — `assert_ranked_order`'s non-vacuity guard was `assertIsNot(values, [])`, which compares
  identity against a fresh literal and can never fail — every assertion below it would have passed
  on an empty facet list. → `assertNotEqual`, plus a guard on the ranked subset.

### Loop 3

Both raised by loop 2's cold re-review; both were regressions the loop 1–2 rendering work
introduced against the earlier `pre-wrap` behavior.

- **P2** — The space-join collapsed the corpus's one markdown table
  (`closed/debt-gate-path-state-writes`) into a single run-on line. → Table rows are exempt from
  the join, keep their own lines, and render monospaced.
- **P2** — The split tested "line starts with `**`", not "line starts with a bold label". Since most
  bodies are hard-wrapped, a bold span landing at a wrapped line's start is luck — it cut a sentence
  in half in `closed/debt-validate-fix-loop-verification`. → Matched on the label shape
  `/^\*\*[^*]+:\*\*/`, which correctly excludes both non-label bold spans in the corpus.
- **P3** — The `type`/`scope` non-vacuity guard counted the `None` bucket while the assertion it
  protects runs on the `None`-filtered list. → Counts the same list now.

**Circuit breaker:** loop 2's re-review attributed a P2 to loop 1's P3 fix (the relaxed facet
tests), so per Step 4 no further P3 fixes were attempted; every remaining P3 was buffered instead.
The loop 2 and 3 P2 work continued, as P2s are not subject to the breaker.

## Issues Remaining

### P1 Open
None.

### P2 Open
None.

### P3 Open
- No automated coverage of the page JavaScript; two demonstrated regressions this cycle passed a
  green suite.
- `_pid_is_viewer` proves the pid is *some* viewer process, not the one that answered the probed
  port, and carries no `subprocess` timeout.
- The CSP's correctness depends on template invariants (no external assets, no inline handlers) that
  no test enforces.
- Several real-corpus facet assertions still cannot fail, and a comment claims coverage in
  `TestFacetsWithNoLiveSample` that that class does not provide for `scope`/`type` ordering.

### Nits Surfaced
- `LABEL_START` has known edges in both directions — a false positive on a line-initial bold span
  carrying a colon (`**dev:validate**`), and a miss on a genuine label without a trailing colon
  (`**Cancelled … not delivered.**`, which renders correctly today only via a preceding blank line).
- `TestCliRoundTrip` self-skips when a viewer is running, silently dropping the only end-to-end
  coverage of detachment. Observed twice during this stage.
- `test_viewer.py` ships into the installed plugin snapshot alongside the runtime files.
- Dropped as not worth carrying: `send_error`-generated 501/400 responses bypass the shared header
  block; the sort tie-break compares the non-unique `id` (correct only because `Array.sort` is
  stable); `String(recurrence)` on a list value renders `seen 1,2×`; two comment figures are
  imprecise.

## Notes

**Success Criteria.** SC1, SC2, SC5, SC6 and SC7 were verified directly this stage; SC3 and SC4 were
verified by Task 9 during Build and re-confirmed here at the CLI layer.

- **SC1** — 31 of 31 items render (`31 of 31` in the header), no `PARSE ERROR` badge on any real item.
  The store has grown from the spec's 30; the count test asserts the glob property, not the literal.
- **SC2** — All four facet groups, both sorts, and search against body prose, a front-matter value,
  and a `files:` path exercised in the browser. `scope: plugin`, `status: in-progress`, `routing:`
  and an out-of-contract `severity: P7` are covered by the synthetic fixture, as the spec requires.
- **SC5** — `lsof` shows `TCP 127.0.0.1:8730 (LISTEN)`, not `*:8730`; `git status --porcelain
  docs/backlog/` clean after browsing; the suite's no-write-call assertion passes.
- **SC6** — `grep -rn '/Users/\|awilliamsbuilds\|adam' plugins/dev/` returns zero hits, including
  after the suite has run (no `__pycache__` under `plugins/dev/`).
- **SC7** — `start` from the worktree then from `$PRIMARY` printed the same URL and spawned nothing.

**Interface change for the decision log.** Task 2's item dict gained a `key` field and the `related`
dict gained a `key`, consumed by the page's selection, highlighting, and relationship traversal.
This is an addition to a plan-declared interface, made to fix the active/`closed` shadowing.

**For Milestone 3 (`lifecycle-viewer`), which reuses this page shell:** the untested-JS and
unenforced-CSP-invariant items above are the two worth paying before the shell is generalized, since
both get harder once there is a second consumer.

**Verification the tests cannot reach.** The body renderer, filtering, sorting, search, detail
rendering and relationship traversal were exercised in a real browser against the live store, since
Task 5 records that this repo has no JS test runner. No page-origin console errors, and no CSP
violations — confirming the new policy does not break the inline `<style>`/`<script>`.
