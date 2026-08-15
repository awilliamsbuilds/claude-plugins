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
