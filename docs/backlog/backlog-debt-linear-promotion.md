---
type: backlog
scope: repo
status: open
first_recorded: 2026-07-21
cycles: []
recurrence: 0
files: []
---

**What:** `/dev:debt promote <id>` turns a tracker entry into a Linear issue with link-back.
**Why:** The Linear seam already exists via `dev:fix`. Deferred from tech-debt-tracking as an
independent second deliverable. Depends on tech-debt-tracking (now shipped). Note: this is a
distinct mechanism from this cycle's `backlog → product-plan` promotion.
**Done looks like:** `/dev:debt promote <id>` creates a Linear issue from a backlog item and
records the link.
