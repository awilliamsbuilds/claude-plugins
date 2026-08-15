# Debt Pending — fast-path

Buffered backlog/debt items for this cycle. `dev:done` Step 6a flushes `## To Record` into
`docs/backlog/` and executes each `## To Close` close-intent, then Step 7 deletes this file. Nothing
else reads it.

## To Record

### debt-p9-slug-regex-allows-leading-dash

````markdown
---
type: debt
scope: plugin
status: open
first_recorded: 2026-08-15
cycles: [fast-path]
recurrence: 1
files:
  - plugins/dev/references/tech-debt.md
  - plugins/dev/skills/reflect/SKILL.md
---

**What's wrong:** §P9.target-resolution's slug allowlist is
`^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$`, and both §P9 itself and `reflect/SKILL.md:205` describe it as
rejecting any value beginning with `-` — "an argument-injection vector into the `gh --repo`
invocation". It does not reject one: `-` is inside the character class, so `-foo/bar` and
`--repo/x` both pass. Verified empirically. The stated security property is not the delivered one.

**Why deferred:** §P9 is the shared cross-repo routing contract, read by `dev:debt` (`add`/`list`/
`inbox`), `dev:done`'s flush, and `dev:reflect`. Tightening the regex there changes validation
behavior for all of them, which is a scope decision rather than an edit — and `fast-path`'s Success
Criterion 6 forbids this cycle touching those skills beyond the rename and the duplication pointers.
`dev:fix` protects itself by anchoring the first character
(`^[A-Za-z0-9._][A-Za-z0-9._-]*/[A-Za-z0-9._][A-Za-z0-9._-]*$`) and saying why, so the new site is
not exposed while the shared claim stays wrong.

**Done looks like:** §P9's regex anchors its first character in both segments, or its prose stops
claiming a property it does not deliver. `reflect/SKILL.md:205`'s matching claim is corrected in the
same pass, and `dev:fix` drops its local divergence note in favour of citing §P9 plainly.
````

### debt-fix-tail-guard-stale-when-offline

````markdown
---
type: debt
scope: plugin
status: open
first_recorded: 2026-08-15
cycles: [fast-path]
recurrence: 1
files:
  - plugins/dev/skills/fix/SKILL.md
---

**What's wrong:** the merge tail's interrupted-tail guard refreshes `origin/$DEFAULT_BRANCH` with
`git fetch … || true`, then scans `for-each-ref --merged "$SCAN_REF"`. When the fetch fails but a
stale remote-tracking ref still exists, `rev-parse` succeeds, the fallback does not fire, and the scan
comes back empty — so the lane prints the flat "nothing to merge (the tail already completed)" over a
branch that is merged server-side and still present locally. It asserts a state it did not verify,
which is the exact failure the file's own Report rule forbids.

**Why deferred:** transient rather than permanent — one re-run with connectivity gives the right
answer — and largely fenced already, since both causes the prose names (network loss, expired token)
trip Step 2 check 1's `gh auth status` first, which exits before the tail is reached. The residual
window is a git-transport-only failure with `gh` healthy: a broken SSH agent, or a git-only proxy.
Found by the final cold review after this cycle's Validate loop budget was already spent.

**Done looks like:** the fetch's exit status is captured (`FETCH_OK=0` on failure) and the empty-scan
message is downgraded when it is unset — "nothing merged is left behind, but `origin/$DEFAULT_BRANCH`
could not be refreshed, so this reading may be stale; re-run once connectivity returns."
````

### debt-fix-tail-multiple-open-prs-unchecked

````markdown
---
type: debt
scope: plugin
status: open
first_recorded: 2026-08-15
cycles: [fast-path]
recurrence: 1
files:
  - plugins/dev/skills/fix/SKILL.md
---

**What's wrong:** the merge tail's prose says "if more than one **open** PR resolves for the branch,
stop and report rather than guessing," but the snippet implementing it uses
`gh pr list … --json number -q '.[0].number'`, which silently takes the first. The stated guard is not
the delivered one.

**Why deferred:** reachable only by manually opening a second PR from the same head branch to a
different base, which the lane itself never does. Non-blocking, and found after this cycle's Validate
loop budget was spent.

**Done looks like:** the count is read (`--json number -q 'length'`) and a result greater than 1 stops
with both PR numbers named, matching what the prose already promises.
````

## To Close

- backlog-reflect-before-pr-merge — this cycle has to decide where reflection sits for a lane that merges in one motion; answering it for the fast path settles the open question
- debt-dev-stage-jump-has-no-new-session-path — the fast path adds an invocation form to `dev:dev` Step 5a's surface, so it either inherits the inconsistency or fixes it while it is there
- debt-state-advancement-commit-durability — the lane's state model is decided here; whichever way it goes, the durability question is answered rather than left dangling
