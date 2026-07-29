---
type: backlog
scope: repo
status: open
first_recorded: 2026-07-21
cycles: []
recurrence: 0
files: []
---

**What:** Mine existing `docs/decisions/*.md` on init to seed the tech-debt tracker from
past cycles.
**Why:** Deferred from tech-debt-tracking — measured yield was ~3 items across 10 cycles with
2 of them cosmetic, and parsing ten unstructured log formats is far easier once real entries
exist to define the target shape. Depends on tech-debt-tracking (now shipped).
**Done looks like:** `dev:init` seeds `docs/backlog/` from prior decision logs.
