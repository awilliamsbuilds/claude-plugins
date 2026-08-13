---
type: backlog
scope: repo
status: open
first_recorded: 2026-08-12
cycles: [manual]
recurrence: 1
files: []
---

**What:** A test harness that exercises the `/dev` skills against fixture repos and asserts
behavior, so editing a `SKILL.md` can't silently break a stage.
**Why:** `/dev` is now a dozen interlocking skills plus a shared contract, and the only
verification an edit gets is the cycle that made it. The cross-skill contracts — the
`debt-pending.md` buffer format, `state.json` fields, the P-numbered procedures in
`references/tech-debt.md` — are enforced by prose agreement alone. A stage can drift from the
contract and nothing catches it until a live cycle hits that seam, which is the worst possible
place to find out.
**Done looks like:** Editing a `/dev` skill can be checked by running a harness that exercises
the affected stages against fixture repos and fails on contract drift.
