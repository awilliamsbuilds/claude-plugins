---
type: debt
scope: repo
status: closed
closed: 2026-08-24
closed_by: plan-linkage
first_recorded: 2026-08-20
cycles: [autopilot-resume-stage]
recurrence: 1
files:
  - plugins/dev/skills/spec/SKILL.md
  - plugins/dev/skills/done/SKILL.md
  - plugins/dev/skills/dev/SKILL.md
possibly_related_to: backlog-project-context-lost-between-cycles
---

**What's wrong:** A cycle that is an **item inside an existing product plan** never links itself to
that plan, so `dev:done` Step 3 skips the check-off and the plan silently under-reports progress.

`dev:spec` writes `state.json.product_plan` on exactly two paths, and its own precedence note names
both: **path (A)** — the cycle is itself product-scale and authors the plan; **path (B)** — the cycle
is a nested child of a plan-bearing parent and inherits the value. "Else `product_plan` stays
`null`." A plain top-level feature cycle that happens to be a milestone item is neither, so it takes
the else.

`/dev` Step 6 does not close it either. It renders the milestone map and then "invoke[s] dev:spec
with the chosen feature name" — the name only. The user has just told the workflow which plan they
are continuing, and that answer is discarded before Spec runs.

`dev:done` Step 3 then opens with "If `state.json.product_plan` is null, **skip this step
entirely**" — so the stage behaves correctly and the box is never ticked. There is no error, no
warning, and no line in the completion display. The omission is only visible by reading the plan
later.

**Observed:** `autopilot-resume-stage` was Milestone 1's second item in
`docs/dev/product-plans/dev-process-hardening.md`. It ran the full seven stages and merged as PR #88
with `product_plan: null`; Step 3 skipped; the plan still read `Cycles completed: 1/5` with
`- [ ] autopilot-resume-stage` unchecked afterwards. It was caught only because the user asked an
unrelated question about where the plan file lived, and corrected by hand in `a8273df`.

**Why deferred:** Discovered after that cycle had already merged, and the fix is a scope decision
about which skill owns the linkage rather than a one-line edit. Three candidate owners, and they are
not equivalent:

  1. `/dev` Step 6 passes the plan path to `dev:spec` alongside the feature name — smallest change,
     but only covers the cycle that entered through Step 6.
  2. `dev:spec` gains a path (C): a top-level cycle whose feature name matches an unchecked item in
     some `docs/dev/product-plans/*.md` adopts that plan. Covers every entry route, but needs a rule
     for a name matching items in two plans.
  3. Milestone 4 (`project-scoped-worktree`) makes it moot by putting the plan slug in the cycle
     directory's own identity, so the value is derivable rather than written.

**Relationship to Milestone 4 — the reason this is recorded separately.** Option 3 would very likely
fix this as a side effect, but `backlog-project-context-lost-between-cycles` never says so: its
subject is a *human* losing track of which milestone is current, its "Done looks like" speaks only to
what a person can see across a session boundary, and its two named design questions are branch
checkout and coexisting cycle directories. That milestone could ship, satisfy its acceptance criteria
in full, and leave this check-off still broken — an unnamed side effect is the kind that does not
happen. Recorded as its own item so Milestone 4's spec has to dispose of it explicitly: adopt it as
in-scope, or say why it stays open.

**Done looks like:** a cycle that is a milestone item in an existing plan reaches `dev:done` with
`state.json.product_plan` set, so Step 3 checks its box and bumps the cycles-completed count without
anyone remembering to. Whichever of the three owners is chosen, the check-off no longer depends on
the human noticing.

**Cost if not paid:** every plan-governed cycle that is not itself a decomposition cycle silently
under-reports, so the plan's own progress line is wrong exactly when it is being used to decide what
to run next. That is the same failure `backlog-project-context-lost-between-cycles` records — losing
track of which milestone is current — arriving through the machine-readable half instead of the human
half, and it is worse here because the plan *looks* authoritative. Each miss also costs a manual
correction commit straight to `main`, outside any PR.
