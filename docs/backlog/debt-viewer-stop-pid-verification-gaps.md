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
---

**What's wrong:** `_pid_is_viewer` proves the pid reported over the wire belongs to *some*
`viewer.py serve` process, not to the one answering the port that reported it. With viewers up for
two repos, a local process that binds the lower port first and answers with repo A's identity plus
repo B's pid makes `/dev:debt view stop` kill repo B's viewer while reporting success for repo A.
The child's argv already carries `--port <n>`, so binding the check to the probed port closes it.
Separately, the `subprocess.run(["ps", ...])` call carries no `timeout=`, making it the only
unbounded blocking call in a module where every other wait is deadline-bounded.

**Why deferred:** The demonstrated arbitrary-process kill was fixed in this cycle's fix loop; these
are the residual gaps in that fix. Both need an attacker who already has a local process binding
ports in 8730-8739.

**Done looks like:** `_pid_is_viewer` takes the probed port and requires the argv to carry
`--port` immediately followed by that port, and the `ps` call has a timeout with the existing
fail-closed behavior on expiry.
