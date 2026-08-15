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
