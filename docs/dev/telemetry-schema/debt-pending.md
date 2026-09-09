# Pending tech debt — telemetry-schema

## To Record

### debt-telemetry-argv-null-convention

````markdown
---
type: debt
scope: repo
status: open
severity: P2
first_recorded: 2026-09-09
cycles: [telemetry-schema]
recurrence: 1
files: [plugins/dev/references/telemetry.md]
---

**What's wrong:** §T-append T3 states one rule — the empty string is the wire form of `null` —
and applies it to `churn`, for which `""` is a legitimate value. §T-lane, eleven lines above,
says an empty `git diff --shortstat` means `{files: 0, insertions: 0, deletions: 0}`. Measured
on a purpose-built add-then-revert branch: 2 commits in range, `--shortstat` output empty. A
*derived* lane run that nets to no change would therefore be recorded `churn: null` beside
`basis: "first_commit"` — a combination §T-lane's table reserves for the two underivable arms.
`churn` is also object-typed, so argv cannot carry it at all and the snippet gives no form for it.
Separately, the same round bound the snippet's `open(path, "a")` to `LEDGER_PATH`, which §T-path
defines as **repo-relative** — making it the only command in T1–T5 not explicitly rooted, so it
resolves against the process cwd. That failure is silent end to end: the record lands in
`<cwd>/docs/telemetry/runs.jsonl`, T4 re-reads that same wrong file and passes, T5 stages nothing
so the commit is skipped, and the caller reports success having written no record.

**Why deferred:** `dev:validate` Step 4 step 8's same-region recurrence rule fired — two
consecutive re-review rounds landed in §T-append T3, severity flat at P2, with the fenced block
itself changed between them, so the converging-cascade exemption did not apply. Both findings follow
from one unsettled design question the fix loop demonstrated it could not settle on its own: should
nullable and non-scalar fields cross the argv boundary via a single emptiness test or a per-field
type-aware form, and should `LEDGER_PATH` name the repo-relative constant or the resolved absolute
path?

**What the next cycle pays:** the contract ships with two writers implementing it, so the cost
compounds per writer rather than being paid once. `dev:fix`'s lane will silently write no record
whenever it runs from a cwd that is not the tree root — the common case, since that lane uses
`git -C "$PRIMARY"` precisely because it cannot assume cwd — and every record it does write for a
net-zero branch is permanently mistyped under §T-path's no-rewrite rule. Milestone 3's viewer is
written against this contract, so it inherits both defects as parsing rules it must special-case.
Settling the question later means re-editing the contract plus both call sites plus the viewer,
against a ledger that already contains wrong lines that cannot be corrected in place.

**Done looks like:** §T-append T3 names which fields take the emptiness test and which take a
type-aware form (`int(x) if x else None` for the int-typed nullables, including §T-cycle's
`challenge.blockers`/`concerns` where `null` is a third value distinct from `0`); `churn`
is excluded from the mapping with its null sourced from the arm rather than an emptiness test; the
snippet opens `"$ROOT/docs/telemetry/runs.jsonl"` or §T-path redefines `LEDGER_PATH` as
resolved; and §T-append's nullable list is attributed correctly across §T-envelope, §T-cycle and
§T-lane.
````

## To Close
