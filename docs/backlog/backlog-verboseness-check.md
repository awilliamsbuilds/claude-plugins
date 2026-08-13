---
type: backlog
scope: repo
status: open
first_recorded: 2026-08-12
cycles: [manual]
recurrence: 1
files: []
---

**What:** Add a concision check to the `/dev` workflow that flags verboseness in both code and
skill/reference prose.
**Why:** Skill and reference markdown is this plugin's actual product, and every padded line is
context cost paid on every session that loads it; the same argument applies to code. Nothing in
the workflow currently pushes back on length — `dev:validate` reviews correctness and security,
`dev:plan` reviews sequencing, and concision is nobody's job. Open question this item has to
settle: whether the check is a one-time audit pass over what already exists, a standing lens in
Validate, or both.
**Done looks like:** Verboseness has a named owner in the workflow — a check that flags padded
prose and code and reports it, rather than length going unexamined.
