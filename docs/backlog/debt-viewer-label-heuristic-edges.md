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
