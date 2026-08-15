# Backlog Viewer — Decision Log
*2026-08-15 · Branch: feature/backlog-viewer · PR #73*

## What was built

A `view` verb on `dev:debt` that serves the whole `docs/backlog/` store — active corpus and `closed/` archive together — as a browsable, filterable triage view, answering "what should I fold into the cycle I'm about to start?"

## Key decisions

- **A local HTTP server, not a generated static file** → a `file://` page cannot fetch local files, so a static build is frozen at generation time and silently stale thereafter. Reading the store from disk on every request is the property that makes the tab worth bookmarking.
- **One route, one response** → `GET /` returns a complete self-contained document with the parsed store embedded as a JSON literal; everything filters client-side. No API surface to design, and Success Criterion 3 falls out of the per-request `load_store` call.
- **`BaseHTTPRequestHandler` with an explicit route allowlist, never `SimpleHTTPRequestHandler`** → the latter serves its working directory, which would expose the entire repo over HTTP. The cycle's single largest security decision.
- **Identity probed over the wire, never recorded to disk** → the server answers with `X-Dev-Backlog-Viewer: <primary-path>`; `start` probes 8730–8739 for it before binding. One mechanism serves both idempotency (SC7) and the port-in-use edge case, and it means no pidfile, lockfile, or `.gitignore` entry — the runtime artifact's home is nowhere, so a stale one is impossible to leave behind.
- **Always serves the primary checkout's store**, resolved via `git rev-parse --git-common-dir` → the backlog is repo-wide, so two launches from different worktrees must never disagree about what it contains. Exactly one new `PRIMARY=` derivation site, and it carries the non-empty guard, so `debt-primary-cd-failure-unchecked`'s count of 13 unguarded sites does not grow.
- **Detachment via `start_new_session=True`** → macOS ships no `setsid` binary (confirmed while launching the Shape prototype), and the server must outlive both the terminal and the Claude Code session. All three standard streams at `DEVNULL`, or an inherited stdout holds the launching shell's pipe open and hangs the caller.
- **The hand-rolled front-matter parser is the build's risk centre, not glue code** → no PyYAML on Python 3.9.6 stdlib, and a silently dropped or mangled field is exactly the failure SC1 guards against. Every rule is a loud `ParseError` rather than a lenient guess; every real store file is a test case.
- **Facet options derive from disk, never from a hardcoded enum** → the contract says `severity: P3 | Nit` while the store carries a `P2`. Deriving from disk is what keeps an out-of-contract value filterable instead of invisible. A rank list orders values; it never gates membership.
- **A malformed item stays visible with a `PARSE ERROR` badge** → a dropped item is a debt item that stops existing; a badged one is merely ugly.

## Design choices

- **Filter rail + compact list + detail pane (Option B)**, over inline-expanding cards and a sortable table, both prototyped 1:1 against the real store → B is the only layout where the list never moves while you read a candidate's body, which is what triage actually is. Bodies here run to four paragraphs, so an expanding card displaces everything below it; a table hides the prose that decides fold-in behind a click. B also generalizes to Milestone 3's `lifecycle-viewer`, which inherits this shell — a table does not.
- **Nothing is filtered by default** → a default `status: open` filter is hidden state the operator has to remember, and the store's whole point is that a promoted-but-unfinished plan should be something you trip over.
- **`severity` is a filter, never the triage axis** → the contract is explicit that it is informational and drives no procedure, and `dev:validate` is its only writer, so it ranks 9 of 30 items. `first_recorded` is the axis that works across the whole corpus; `recurrence` stays a sort dimension but is not the default, since 27 of 30 items read `1`.
- **Facets ordered by meaning, not by count** → count-descending made the rail reshuffle as the store changed and put `none` above `P2`.
- **Chips, not prose, carry item state** → the first prototype's grey run-on (`debt · closed · 2026-07-21 · 9f`) was unreadable at a glance. Rows and detail share one chip vocabulary, so an item looks the same wherever it appears.
- **Metadata needing decoding was cut, not shrunk** → the row's `9f` file count is gone entirely (the detail pane lists actual paths, the only form of that fact worth having); `rec 1` became `seen 1×`. A label the operator has to decode is a label that failed.
- **Search covers `files:` paths, and that is the files feature** → typing `plan/SKILL.md` finds every item touching it, which is why there is deliberately no dedicated files filter control.

## Validation notes

- 3 loops run (tier: standard), ending clean — no open P1 or P2. Reviews ran as fresh subagents denied the session's history: code and security review in parallel on the build diff, then a cold re-review of each loop's own fix diff before that loop could exit. Suite: 88 tests, `OK`, no skips (build shipped 79; the fix loops added 9).
- **P2 — 403 leaked identity headers.** The Host-allowlist rejection carried the absolute primary path and the server pid, and that 403 is precisely the response a DNS-rebinding attacker can read same-origin. Identity headers now go only to allowed hosts.
- **P2 — `SIGTERM` to a pid read off the wire.** The reviewer demonstrated end-to-end that a process squatting a port in range could make `stop` kill something unrelated. Added `_pid_is_viewer` (verifies the pid's own command line before signalling) and a non-positive-pid discard at parse time, since `os.kill(0, …)` signals the whole process group.
- **P2 — double-spawn on a slow start.** A start that exceeded `START_TIMEOUT` but then came up was read as a lost race, so a second server was spawned for the same primary; `find_running` returns the first match, so a later stop would orphan the other beyond any CLI path. Breaks SC7. The re-probe now recognizes our own viewer.
- **P2 ×3 — the detail-pane body renderer,** each regression surfaced by the previous loop's cold re-review. `pre-wrap` separated the run-on labels but froze the source's ~95-column hard wrapping into a 720px pane (measured: 21 of 31 bodies have the run-on shape, 27 of 31 are hard-wrapped — the re-reviewer's claim that only one file was affected was contradicted by direct measurement, and the measurement is what drove the fix). The space-join that fixed that then collapsed the corpus's one markdown table. The label split then matched "starts with `**`" rather than "starts with a bold label", cutting a sentence in half where a bold span happened to land at a wrapped line's start.
- **P2 — a test guard that could never fail.** `assertIsNot(values, [])` compares identity against a fresh literal, so every assertion below it would have passed on an empty facet list.
- **P3 — active/`closed` stem shadowing**, the one path by which an item becomes effectively invisible, which is what SC1 guards. Items now carry a unique `key` alongside the display `id` — an addition to a plan-declared interface, made deliberately.
- Circuit breaker fired: loop 2's re-review attributed a P2 to a loop 1 P3 fix, so no further P3 fixes were attempted and the rest were buffered. P2 work continued, as P2s are not subject to the breaker.
- **Accepted as-is — 4 P3 and 3 Nits**, buffered to the store. The two worth paying before Milestone 3 generalizes this shell: no automated coverage of the page JavaScript (two demonstrated regressions this cycle passed a green suite), and a CSP whose correctness depends on template invariants no test enforces. Both get harder once there is a second consumer.
- SC1, SC2, SC5, SC6 and SC7 verified directly; SC3 and SC4 verified in Build and re-confirmed at the CLI layer. SC4/SC7 were reported **as a proxy** — the installed plugin is a snapshot of `main`, so the `/dev:debt view` wrapper only goes live after this merge plus `/plugin update`.

## Artifacts (archived)

Spec, design, and plan committed at: `132278d` on branch `feature/backlog-viewer`

## Retrospective
*Reviewed by dev:reflect · 2026-08-15*

**Spec:** 14 questions over 2h43m — the longest stage by 3× — and it earned the time: confidence 100, nothing auto-filled, zero user revisions at the gate. The cold review's single blocker was the one that mattered (enum values had been taken from the contract rather than from disk) and it redirected the entire facet design; all 5 findings applied, none dismissed.

**Shape:** Design was followed closely — Option B's rail/list/detail survived into Build unchanged. Two post-draft corrections landed as separate commits (severity's role, facet ordering) that no counter records: `spec_revisions` has no Shape or Plan analogue, so churn after those stages' first drafts is invisible to this retrospective.

**Plan:** Accurate — 4 files read in Build, no mid-build task additions, and Task 5 was honest up front about the layer it couldn't test. Plan challenger: 1 blocker, 3 concerns, all 4 applied, none dismissed.

**Validate:** 3 loops / 3 max — the budget was exhausted, not comfortably cleared. Loops 2 and 3 were each opened by the previous loop's cold re-review, and three of the eight P2s were regressions the fix loop itself introduced, all in the page's body renderer — the one layer Plan had declared untestable. The run ended clean, but with no budget left had the final re-review found a fourth.

**Flow:** Standard tier was right. No backtracks, no skipped stages, no stage that felt unnecessary.

**Token efficiency:** `files_read_in_build` of 4 is low — the plan carried enough that Build didn't go looking. All 4 Shape screens were load-bearing. The real outlier is invisible to `stage_timestamps`: ~30 hours of wall clock between `plan_end` and `build_start`, 13 more between `validate_end` and the PR, and no `done` stamp at all.

**Suggestions:**
- When a Plan task declares a TDD deviation, `dev:validate`'s fix loop should require that task's manual verification be re-run on edits to those files, not just a diff review — three of eight P2s were regressions in exactly that layer, each caught only because a cold re-review happened to look. **Implemented:** `validate/SKILL.md` step 8a, PR #74.
- Metrics have no per-stage revision counter beyond `spec_revisions` and no `done` timestamp; both were felt directly while writing this. Recorded rather than fixed here — it belongs to the contract Milestone 2's `telemetry-schema` cycle is chartered to design.

**Deferred to tech debt:** `stage-metrics-blind-to-revisions-and-done`
