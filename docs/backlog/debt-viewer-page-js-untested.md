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
