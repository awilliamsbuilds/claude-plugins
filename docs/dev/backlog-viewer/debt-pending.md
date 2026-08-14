# Debt Pending — backlog-viewer

Buffered backlog/debt items for this cycle. `dev:done` Step 6a flushes `## To Record` into
`docs/backlog/` and executes each `## To Close` close-intent, then Step 7 deletes this file. Nothing
else reads it.

## To Record

### viewer-page-js-untested

````markdown
---
type: debt
scope: repo
status: open
first_recorded: 2026-08-14
cycles: [backlog-viewer]
recurrence: 1
severity: P3
files:
  - plugins/dev/skills/debt/viewer_page.html
  - plugins/dev/skills/debt/test_viewer.py
---

**What's wrong:** Nothing in the 88-test suite executes the page's JavaScript, so filtering,
sorting, search, detail rendering, relationship traversal and the body renderer are verified only
by a human opening a browser. This is not theoretical: this cycle's validate loops shipped two
rendering regressions that passed a fully green suite, and both were caught only by a cold reviewer
reimplementing the renderer by hand against the real corpus. Reverting either fix today still
passes.

**Why deferred:** The plan states the deviation deliberately (Task 5) — the repo has no build
tooling and no JS test runner, and adding one is a larger decision than this cycle should make. The
spec's Technical Constraints forbid introducing a build step.

**Done looks like:** The pure functions in the page — at minimum `paragraphsOf`, `escapeHtml` and
the body renderer — are exercised against the real corpus by something the suite runs. A `node`
harness invoked from `unittest` and skipped when `node` is absent would fit the stdlib-only
constraint without adding a build step. Worth paying before Milestone 3 generalizes this shell,
since a second consumer makes it harder.
````

### viewer-stop-pid-verification-gaps

````markdown
---
type: debt
scope: repo
status: open
first_recorded: 2026-08-14
cycles: [backlog-viewer]
recurrence: 1
severity: P3
files:
  - plugins/dev/skills/debt/viewer.py
---

**What's wrong:** `_pid_is_viewer` proves the pid reported over the wire belongs to *some*
`viewer.py serve` process, not to the one answering the port that reported it. With viewers up for
two repos, a local process that binds the lower port first and answers with repo A's identity plus
repo B's pid makes `/dev:debt view stop` kill repo B's viewer while reporting success for repo A.
The child's argv already carries `--port <n>`, so binding the check to the probed port closes it.
Separately, the `subprocess.run(["ps", ...])` call carries no `timeout=`, making it the only
unbounded blocking call in a module where every other wait is deadline-bounded.

**Why deferred:** The demonstrated arbitrary-process kill was fixed in this cycle's fix loop; these
are the residual gaps in that fix. Both need an attacker who already has a local process binding
ports in 8730-8739.

**Done looks like:** `_pid_is_viewer` takes the probed port and requires the argv to carry
`--port` immediately followed by that port, and the `ps` call has a timeout with the existing
fail-closed behavior on expiry.
````

### viewer-csp-template-invariant-unenforced

````markdown
---
type: debt
scope: repo
status: open
first_recorded: 2026-08-14
cycles: [backlog-viewer]
recurrence: 1
severity: P3
files:
  - plugins/dev/skills/debt/viewer.py
  - plugins/dev/skills/debt/viewer_page.html
  - plugins/dev/skills/debt/test_viewer.py
---

**What's wrong:** The served `Content-Security-Policy` is `default-src 'none'` with inline style and
script allowed. That is correct only because the template loads nothing external and uses no inline
event handlers — an invariant nothing checks. A later edit adding a web font link, a
`background-image: url(...)`, or an `onclick=` attribute produces a page that renders wrong in the
browser while every test stays green, because CSP failures surface only in the console. The existing
test asserts the header string, not the property the header depends on.

**Why deferred:** The CSP was added as defense-in-depth during the fix loop, after the loop's
circuit breaker had already tripped on P3 fixes.

**Done looks like:** A test in `TestRenderPage` scans the rendered document for external references
and inline `on*=` handlers and fails if any appear, so the policy and the page it protects are
enforced as a pair.
````

### viewer-facet-tests-vacuous-assertions

````markdown
---
type: debt
scope: repo
status: open
first_recorded: 2026-08-14
cycles: [backlog-viewer]
recurrence: 1
severity: P3
files:
  - plugins/dev/skills/debt/test_viewer.py
---

**What's wrong:** Several assertions in the real-corpus facet tests cannot fail. Every non-`None`
value in the live `status` and `severity` facets is in its rank list, so `unranked` is always `[]`
and both the `assertEqual(unranked, sorted(unranked))` check and the `if ranked and unranked:`
branch are dead. `test_no_facet_entry_is_ever_empty` restates a condition `derive_facets` cannot
violate without being rewritten. `scope` is single-valued, so its ordering assertion is trivially
true — and the comment justifying that points at `TestFacetsWithNoLiveSample` as carrying the
ordering burden, which that class does not do for `scope` or `type`.

**Why deferred:** These arrived from the cold re-review of the loop that relaxed these same tests;
that relaxation is what tripped the fix loop's P3 circuit breaker, so no further P3 edits to this
file were attempted.

**Done looks like:** The synthetic corpus asserts multi-value alphabetical ordering for `scope` and
`type`, the dead branches are either exercised there or removed, and the comment describes the
coverage that actually exists.
````

### viewer-label-heuristic-edges

````markdown
---
type: debt
scope: repo
status: open
first_recorded: 2026-08-14
cycles: [backlog-viewer]
recurrence: 1
severity: Nit
files:
  - plugins/dev/skills/debt/viewer_page.html
---

**What's wrong:** `LABEL_START` (`/^\*\*[^*]+:\*\*/`) decides where a paragraph breaks, and has a
known edge in each direction. False positive: it matches any line-initial bold span containing a
colon, and this store's prose is dense with colon-bearing identifiers, so a hard-wrapped line
beginning `**dev:validate**` would be split mid-sentence — the exact failure the regex replaced a
cruder test to prevent. False negative: a genuine section label without a trailing colon
(`**Cancelled 2026-08-12 — not delivered.**`) does not match, and renders as its own paragraph today
only because a blank line happens to precede it.

**Why deferred:** Neither edge is reachable with the 31 bodies in the store today; both were
identified by inspection, not by a failing render.

**Done looks like:** The split anchors on something the body format actually guarantees rather than
on a colon heuristic, or the known label vocabulary is matched explicitly — and whichever is chosen
is covered by the renderer tests from `viewer-page-js-untested`.
````

### viewer-cli-roundtrip-test-self-skips

````markdown
---
type: debt
scope: repo
status: open
first_recorded: 2026-08-14
cycles: [backlog-viewer]
recurrence: 1
severity: Nit
files:
  - plugins/dev/skills/debt/test_viewer.py
---

**What's wrong:** `TestCliRoundTrip` binds the real 8730-8739 range, so it calls `skipTest` when a
viewer is already running. That is the only end-to-end coverage of process detachment, the
`start`/`stop` round trip and idempotency — and it disappears silently for exactly the developer
most likely to have the viewer open, which is anyone working on the viewer. It self-skipped twice
during this cycle's own validation, once masking whether the CLI paths still worked at all.

**Why deferred:** The skip is deliberate and safe — the alternative of killing a running viewer
mid-test is worse — so this is a coverage-design question rather than a defect to patch.

**Done looks like:** The round trip runs against an injected port range disjoint from 8730-8739
rather than the real one, so it exercises the same code unconditionally, and a skip becomes a
failure rather than a silent pass.
````

### viewer-test-file-ships-in-plugin-snapshot

````markdown
---
type: debt
scope: repo
status: open
first_recorded: 2026-08-14
cycles: [backlog-viewer]
recurrence: 1
severity: Nit
files:
  - plugins/dev/skills/debt/test_viewer.py
---

**What's wrong:** `test_viewer.py` sits beside `viewer.py` and `viewer_page.html` in the skill
directory, so it ships into the installed plugin snapshot with no runtime purpose. `dev:debt` is the
first skill in this repo to carry executable code at all, so there is no convention yet for where a
skill's tests live or whether they are expected to ship — and Milestone 3 adds a second such skill,
which is when an unstated convention becomes an inconsistent one.

**Why deferred:** Harmless today; nothing loads it, and it violates no existing rule because no such
rule exists.

**Done looks like:** A stated convention for test files belonging to code-carrying skills — ship
them beside the code, or hold them outside the plugin tree — applied to `dev:debt` and available to
Milestone 3 before it makes the same choice independently.
````

## To Close
