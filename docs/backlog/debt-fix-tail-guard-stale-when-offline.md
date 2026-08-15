---
type: debt
scope: repo
status: open
severity: P3
first_recorded: 2026-08-15
cycles: [fast-path]
recurrence: 1
files:
  - plugins/dev/skills/fix/SKILL.md
---

**What's wrong:** `dev:fix`'s merge-tail interrupted-tail guard refreshes `origin/$DEFAULT_BRANCH`
with `git fetch … || true`, then scans `for-each-ref --merged "$SCAN_REF"`. When the fetch fails but a
stale remote-tracking ref still exists, `rev-parse` succeeds, the local-ref fallback does not fire,
and the scan comes back empty — so the lane prints the flat "nothing to merge (the tail already
completed)" over a branch that is merged server-side and still present locally. It asserts a state it
did not verify, which is the exact failure the file's own Report rule forbids.

**Why deferred:** transient rather than permanent — one re-run with connectivity gives the right
answer — and largely fenced already, since both causes the prose names (network loss, expired token)
trip Step 2 check 1's `gh auth status` first, which exits before the tail is reached. The residual
window is a git-transport-only failure with `gh` healthy: a broken SSH agent, or a git-only proxy.
Found by the final cold review after the cycle's Validate loop budget was already spent.

**Done looks like:** the fetch's exit status is captured (`FETCH_OK=0` on failure) and the empty-scan
message is downgraded when it is unset — "nothing merged is left behind, but `origin/$DEFAULT_BRANCH`
could not be refreshed, so this reading may be stale; re-run once connectivity returns."
