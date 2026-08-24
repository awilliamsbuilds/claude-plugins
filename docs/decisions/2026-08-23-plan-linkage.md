# Plan Linkage — Decision Log
*2026-08-23 · Branch: feature/plan-linkage · PR #93*
*Handed off to autopilot at Plan*

## What was built

A lookup that answers "given a feature name, which product plan governs it," plus its two cheap
consumers: `dev:spec` Step 6 path (C), which records the governing plan in
`state.json.product_plan`, and an order-mismatch check at `/dev:spec` and `/dev:fix` that fires
before anything is created.

## Key decisions

**The lookup is a shared reference, not a procedure restated per skill.** →
`plugins/dev/references/product-plans.md` joins `tech-debt.md` and `entry-adapters.md` as a
contract several skills cite. Two call sites exist today and a third (Milestone 4b) is already named
in the governing plan; restating §L4's four branches at each site is exactly the drift the reference
prevents.

**Milestone order is binding; item order within a milestone is not.** → The spec contradicted itself:
Scope 3's example fires on an out-of-order name, while the "next unchecked item is ambiguous" edge
case says a name matching *any* unchecked item is not a mismatch. Read literally, the check could
never fire on the failure it exists to catch. The milestone-level rule is the narrowest reading that
keeps both statements true, and it is disclosed in `plan.md` rather than smuggled in.

**The check runs before anything is created, at both sites.** → `dev:spec` calls it before
`worktree add`; `dev:fix` calls it at a new Step 2b, after the adapter resolves and before Step 5's
`checkout -b`. That placement is what makes "switch" free — no branch, no worktree, no state file to
unwind — and it is why the check can afford to ask at all.

**The check never refuses, in any mode.** → It turns an accidental skip into a deliberate one and
nothing more. In autopilot the two asking outcomes print and proceed, mirroring `dev:autopilot` Step
2's existing *Debt surfacing: print, never ask* rule. No stop condition was added anywhere.

**Both Linear entry points resolve one name.** → §A6's cycle slug is `<ID>-<short-title>` and its ID
prefix is uppercase, so passing the whole slug would make the Linear paths structurally incapable of
matching a plan item. Both `/dev:spec linear` and `/dev:fix linear` pass the ID-stripped
`<short-title>`, and `dev:done`'s check-off gained a matching try-unchanged-then-strip rule keyed on
`linear_issue.id` verbatim — the ID contains its own hyphen, so "strip to the first hyphen" would
have been wrong.

**Path (C) tests what was *prepared*, not the key's current value.** → Path (A) writes
`product_plan` in its own commit at the end of Step 6, so the key is still `null` at (C)'s decision
point on a product-scale cycle. A naive "is it non-null" test would let (C) write there — harmless
only by accident, since (A) overwrites it moments later.

## Validation notes

- 3 loops run (tier: standard), each loop's own fix diff cold re-reviewed before the loop could exit
- **P2 (code):** path (C) linked a cycle to an already-checked item — letting `dev:done` bump the
  cycles-completed count with no box to tick — or to a plan with every box ticked, which would send
  Step 3b down its project-complete path and delete the plan file on a cycle that completed nothing.
  Fixed by a fourth non-writing case at the writer, using fields §L1 already returns.
- **P2 (security):** `plan-path` came from an unallowlisted filesystem name and reaches `dev:done`'s
  interpolated `git rm -f` and an unquoted `git add`. §L1 now allowlists the filename stem and skips
  a file that fails it; the `git add` is quoted.
- 12 P3s and 11 nits, all resolved — including three rounds of cross-file count drift that the cycle's
  own `PRIMARY` guard introduced, and a §L4 example that illustrated the reading the plan had
  discarded.
- **A security P3 was closed by the P2 fix rather than separately:** with the already-checked guard in
  place, an adopted cycle can only reach Step 3b's delete path by itself completing the plan's last
  item, which is the intended behavior.
- Build check: no build system in the repo; `py_compile` clean, 89 tests OK (2 skipped), every
  tracked JSON parses.

## Artifacts (archived)
Spec, plan, and validation committed at: 7fa84cfea08c26875463a5aded36c8d0a93e097d on branch feature/plan-linkage

## Retrospective
*Reviewed by dev:reflect · 2026-08-23*

**Spec:** Confidence 90%/Ready with `spec_revisions: 0` — the score matched actual clarity, and the
challenger's 3 blockers + 4 concerns were all applied before the gate, so nothing churned afterward.
The healthy quadrant of the blockers/revisions table.

**Shape:** Skipped (no-ui).

**Plan:** The expensive stage — 2 challenger loops, 14 fixes of which 7 were concern-driven. Coverage
and sequencing went clean after round 1; **Interfaces never did.** Every surviving finding was the
same shape: a value crossing a task boundary with its name stated and its *type* left implicit —
`plan-path` absolute or repo-relative, one Linear name derived two incompatible ways at two call
sites, §L1's output missing two fields §L4 prints.

**Validate:** 3 of 3 loops, 0 P1, 2 P2. Both P2s were that same shape one stage later: a value
crossing a boundary without its constraint stated (an unallowlisted filename reaching an interpolated
`git rm -f`; a link written without checking whether the item was already checked). Two of the three
loops were spent on drift the cycle's *own* fix caused — adding a `$PRIMARY` guard falsified a "12
sites" count asserted in three other files and one backlog item.

**Flow:** Tier was right. Handed off to autopilot at Plan and ran to PR without a stop; the one
`dev:reflect` pause worked as designed.

**Token efficiency:** `files_read_in_build` reads 0 and is wrong — files were read throughout Build
and the counter was never bumped, so the metric is unreliable for this cycle. Stage durations were
unremarkable except Validate (~25 min), which is where the three loops went.

**Suggestions:**
- Plan tasks state a *name* for every value crossing a task boundary but not a *type*. Both this
  cycle's P2s and most of its plan-challenger findings were untyped-boundary defects. Worth
  considering whether `Interfaces:` should require a stated type per produced value.
- A fix that changes a counted fact (guard counts, site counts, "N places do X") should trigger a
  repo-wide grep for that count inside the same loop. Not doing it cost two of three validate loops.

**Deferred to tech debt:** `plan-interfaces-state-names-not-types`, `validate-counted-facts-not-regrepped`

**User observations:** None raised at the Step 4 turn.
