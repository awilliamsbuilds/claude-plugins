---
type: backlog
scope: repo
status: closed
first_recorded: 2026-07-21
cycles: []
recurrence: 0
files: []
closed: 2026-08-12
closed_by: manual
---

**What:** `/dev:debt promote <id>` turns a tracker entry into a Linear issue with link-back.
**Why:** The Linear seam already exists via `dev:fix`. Deferred from tech-debt-tracking as an
independent second deliverable. Depends on tech-debt-tracking (now shipped). Note: this is a
distinct mechanism from this cycle's `backlog → product-plan` promotion.
**Done looks like:** `/dev:debt promote <id>` creates a Linear issue from a backlog item and
records the link.

**Cancelled 2026-08-12 — not delivered.** Closed as a deliberate cancellation, not as work paid
off, so nothing in the codebase implements this. Reason: the decision to stop depending on Linear.
The item's stated justification was "the Linear seam already exists via `dev:fix`" — with that seam
no longer something to invest in, the justification is gone. The promotion need it served is also
already met by the `backlog → product-plan` path (P3 `promoted` / `promoted_to`), which is internal
and needs no external tracker. Recorded as `closed_by: manual` because no cycle paid it; the
contract's status vocabulary has no `cancelled` value and adding one would mean changing the
`/dev` plugin, which was explicitly out of scope.
