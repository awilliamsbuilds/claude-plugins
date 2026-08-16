---
type: debt
scope: repo
status: open
first_recorded: 2026-08-14
cycles: [backlog-viewer]
recurrence: 1
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
