# Extract Review Skills
*Branch: feature/extract-review-skills · Confidence: 100% — Ready · 2026-08-16*
*Cycle type: feature · Tier: deep*

## Intent

`dev:fix` runs a security review but no code review, so every fast-lane PR ships unreviewed for
correctness. That gap is real — but bolting a checklist onto the lane would be the wrong fix, because
it treats a symptom of a structural problem.

The structural problem: **`dev:validate` is both a reviewer and an orchestrator, and only the
orchestrator half is stage-specific.** Knowing *what to look for* in a diff has nothing to do with
`state.json`, fix loops, or stage advancement. Because those two jobs live in one file, the lane
could not reuse the review half without inheriting the pipeline half — so it grew its own security
call and simply went without code review.

This cycle separates the two:

- **Reviewers** know what to look for. They report findings classified P1–Nit and write nothing.
  They know nothing about loops, state, artifacts, or cycles.
- **Orchestrators** know what to do about findings. They dispatch reviewers, then classify, fix,
  bound, record, and gate. They know nothing about vulnerability categories or naming conventions.

One rule keeps it honest: **a reviewer never writes; an orchestrator never defines a checklist.**

`dev:secure` already proved the reviewer half of this pattern. This cycle completes it.

## Scope

**1. New skill: `dev:review`** — report-only code/document review, sibling of `dev:secure`.

Two **explicit** modes, each carrying its own severity table adjacent to its checklist:

| Invocation | Reviews | Used by |
|---|---|---|
| `/dev:review diff <tree> <base>` | The diff — logic, edge cases, quality, conventions, plan coverage where a plan exists | `dev:validate` (feature cycles), `dev:fix` |
| `/dev:review docs <paths>` | Committed decision documents — consistency, sufficiency, realistic consequences, rationale | `dev:validate` (architecture cycles) |

A bare `/dev:review` is an **error**, never an inferred mode. The two modes do not share a severity
meaning — code review's P1 is a correctness blocker, document review's P1 is an internally
inconsistent or contradictory decision — so a reader must never be uncertain which table applies.

**2. Both reviewers own cold dispatch and take an explicit tree.**

`dev:review` and `dev:secure` each dispatch a fresh `general-purpose` subagent internally: no
conversation history, diff-and-artifacts-as-data guardrail, and the existing in-session fallback when
subagent dispatch is unavailable in the harness. Both accept the tree and base **from the caller**
rather than inferring `$PRIMARY`.

This is a behavior change to `dev:secure`, and both halves are load-bearing (see Edge Cases).

**3. `dev:validate` Step 2 stops carrying checklists.**

```
Feature cycle       → dispatch /dev:review diff + /dev:secure diff, in parallel
Architecture cycle  → dispatch /dev:review docs
```

Everything else `dev:validate` does is unchanged: classification into `state.json`, the fix loop to
`loops_max`, fix ordering, Step 4 step 8's cold re-review of each fix diff, Step 5a's carrying-cost
buffer, Step 5b's build check, `validation.md`, and the stage gate. The architecture-cycle
security carve-out is preserved verbatim.

**4. A reviewer that cannot run stops the stage.**

`dev:validate` records which reviewer failed and why to `validation.md`, withholds `"validate"` from
`completed[]`, and leaves `stage` un-advanced — the same shape Step 5b's build failure already uses.
This becomes a new entry in `dev:autopilot`'s "When autopilot stops" list.

**5. `dev:fix` Step 6 gains code review.**

`/dev:review diff` runs beside `/dev:secure diff`, in parallel, both against `origin/$DEFAULT_BRANCH`.
A code-review P1/P2 follows the identical rule security already uses: fix once, cold re-review that
fix's own diff, open the PR only on a clean re-review, `loops_max` pinned to 1. P3/Nit never block
and are captured per the rigor floor.

**6. Two `dev:secure` corrections, both preconditions rather than extras.**

- **CSRF coverage is restored.** `dev:validate`'s inline bullet names it; `dev:secure` has no
  counterpart anywhere in Pass C, and it is absent from the "deliberately not covered" list. Once
  validate stops carrying its own bullets, CSRF exists nowhere in the repo unless `dev:secure` gains
  it in this same cycle.
- **The false "adds no new vector" claim is corrected** (`secure/SKILL.md`, Pass C). Measured, Pass C
  adds roughly fifteen named vectors validate never mentions plus two whole categories (Data
  exposure, Business logic). The line matters beyond accuracy: a future cycle "reconciling the
  duplication" on the strength of that sentence would delete real coverage believing it redundant.

**7. The four cold-review citations re-point.** `dev:spec` Step 12a (×2), `dev:plan` Step 7a (×2), and
`dev:fix` (×2) cite `dev:validate` Step 2 by name as the canonical for both the cold-dispatch
principle and the in-session fallback. Each must still resolve to wherever that discipline now lives.

**8. Folded-in debt: `debt-secure-tree-scoping-unsettled`** — closed by scope item 2's explicit-tree
rule, which is correct for the `dev:fix` call path, the `dev:validate` worktree call path, and
standalone use.

**9. Docs reconciliation** — `CLAUDE.md` Component Registry (new `dev:review` row; `dev:validate`,
`dev:secure`, `dev:fix` rows updated) and README's `dev` skills list.

## Out of Scope

- **No whole-project `/dev:review` verb.** `dev:secure` has one; `dev:review` ships with only the
  modes that have callers. Addable later without breaking either caller.
- **No change to the P1/P2/P3/Nit vocabulary.** `dev:validate` Step 3 remains its canonical
  definition; both reviewers consume it, as `dev:secure` already does.
- **No change to `dev:validate`'s fix loop, Step 5b build check, or Step 5a debt buffer.**
- **No change to `dev:fix`'s build check, PR body, merge tail, or triage rule.**
- **No warm/cold caller flag.** Considered and declined: it would preserve today's lane speed at the
  cost of a parameter that drifts, and the lane is where cold review buys the most (see Technical
  Constraints).
- **The five other debt items surfaced at grounding stay open** —
  `debt-secure-report-fields-not-grounded-in-output`, `debt-primary-cd-failure-unchecked`,
  `debt-artifact-path-rule-artifact-component-unconstrained`,
  `debt-cross-file-line-citations-go-stale-silently`, `backlog-reflect-before-pr-merge-…`.
- **No `dev:autopilot` change beyond the one new stop condition.**

## Success Criteria

1. `plugins/dev/skills/review/SKILL.md` exists, is report-only (`git status --porcelain` byte-identical
   before and after any run), and has two explicit modes with adjacent, distinct severity tables. A bare
   `/dev:review` errors.
2. `dev:review` and `dev:secure` each dispatch a fresh `general-purpose` subagent, withhold
   conversation history, carry the data-not-instruction guardrail, and state the in-session fallback.
3. Both accept tree and base from the caller. Neither infers `$PRIMARY` when given an explicit tree.
4. `dev:validate` Step 2 contains **no** review checklist for either cycle type — a grep for its
   former checklist bullets returns nothing — and its other responsibilities are textually unchanged.
5. Running `/dev:validate` on a feature cycle in a worktree reviews **that worktree's** diff, not the
   primary checkout's.
6. A reviewer that cannot run leaves `stage` un-advanced with the reason in `validation.md`, and
   `dev:autopilot`'s stop list names it.
7. `dev:fix` Step 6 dispatches both reviewers in parallel, and a code-review P1/P2 blocks the PR under
   the one-round bound.
8. `dev:secure` names CSRF, and no sentence in it claims the checklist adds no new vector.
9. All six cold-review citations resolve to a section that exists and describes cold dispatch.
10. `debt-secure-tree-scoping-unsettled` moves to `docs/backlog/closed/`.

## Happy Path

**Feature cycle (pipeline)**
1. `dev:validate` Step 2 computes the diff range (`BASE_SHA..HEAD_SHA`) and the tree (`$WORKDIR`)
2. Dispatches `/dev:review diff` and `/dev:secure diff` in parallel, passing both explicitly
3. Each reviewer dispatches its own cold subagent and returns P1–Nit findings
4. Validate classifies into `state.json`, runs the fix loop, cold re-reviews each fix diff, runs the
   build check, writes `validation.md`, advances the stage

**Architecture cycle**
1. Step 2 dispatches `/dev:review docs` against the committed decision documents
2. Security does not run — the existing carve-out, preserved
3. Findings flow into the same classification and fix loop

**Lane**
1. `dev:fix` Step 6 dispatches both reviewers in parallel against `origin/$DEFAULT_BRANCH`
2. Clean → the PR opens, naming both outcomes
3. A P1/P2 from either → fix once, cold re-review that fix's diff, open only on a clean re-review

## Edge Cases

- **Reviewer cannot run** — stage stops, reviewer named, `stage` un-advanced (Scope 4). In the lane
  this is already `SECURITY_RESULT=not run — <reason>` → stop; the code-review equivalent matches it.
- **Wrong tree.** The failure this cycle exists to prevent: `dev:secure` audits `$PRIMARY` today while
  a cycle runs in `.dev-worktrees/<feature>`, and its own text calls a confident "nothing to audit"
  the worst available failure for a pre-PR gate. Explicit tree from the caller is the fix.
- **Empty diff** — reviewers report the diff is empty and say so; never "no findings", which reads as
  a review that ran and came back clean.
- **Subagent dispatch unavailable** — in-session fallback, matching the four existing statements of
  that rule. This is a harness limitation, not a broken skill, so it degrades rather than stops.
- **Architecture cycle + security** — security still does not run; the carve-out is preserved with its
  existing reasoning intact.
- **A reviewer returns findings in an unexpected shape** — treated as "returned nothing usable" and
  handled by Scope 4's stop, rather than being silently parsed as clean.

## Audience

Solo developer running `/dev` across several repos, dogfooding the plugin in the repo that defines it.
Every reader of these skills is either the author or an agent executing them.

## Technical Constraints

- **Markdown-only change.** Skills are prose; there is no build system in this repo. Verification is
  the 89-test `dev:debt` viewer suite (untouched by this cycle) plus manual walkthrough of the
  procedures against real files.
- **Cost.** The lane gains one parallel subagent wave, and its security review moves from warm
  (in-session, nearly free) to cold. Accepted deliberately: the lane has no other independent check —
  no cold spec review, no cold plan review, no separate Build stage — so its only checkpoint is a PR
  produced by the session that wrote the code. Cold review buys more there than in the pipeline,
  where three cold reviews already run.
- **Parallel dispatch is required, not optional** — it is what keeps the second review from doubling
  wall-clock on either route.

## Dependencies

None external. Everything this cycle touches is in `plugins/dev/`, plus `CLAUDE.md` and `README.md`.
No config keys, no new runtime dependency.

## UI Needed

No.

---
*Auto-filled dimensions: none*
*Grounding inventory: (1) "dev:validate Step 2 carries inline code + security checklists" → read `validate/SKILL.md` §Step 2 in full — confirmed, 6 code bullets + 5 security bullets. (2) "dev:fix has no code review" → `grep -n "code review\|code-review" fix/SKILL.md` → no matches; security only. (3) "dev:secure is a superset of validate's security bullets" → read both verbatim and mapped them — superset by ~15 named vectors + 2 whole categories (Data exposure, Business logic), **except CSRF**, which validate names and dev:secure omits entirely. (4) "dev:secure adds no new vector" (`secure/SKILL.md` Pass C) → **false**, disproved by (3). (5) "dev:secure runs cold" → `grep -n "subagent\|general-purpose\|conversation history" secure/SKILL.md` → **no matches; it runs in-session**. (6) Consumers of validate Step 2's cold-review principle, enumerated by sweep not recall → `grep -rn "validate.*Step 2" plugins/` → `spec/SKILL.md:556,569`, `plan/SKILL.md:201,214`, `fix/SKILL.md:652,677`, `secure/SKILL.md:123` — six citations across four files. (7) "dev:secure audits $PRIMARY while cycles run in worktrees" → read its `AUDIT_BRANCH`/`INVOKED_IN` block — confirmed; it discloses the mismatch rather than accepting a tree. (8) Open debt intersecting this cycle's files, by front-matter `files:` sweep over the P5 corpus → 6 items, of which `debt-secure-tree-scoping-unsettled` is a precondition rather than an adjacent pay-down. (9) "telemetry-schema is an architecture cycle" → read `docs/dev/product-plans/dev-observability.md` — confirmed, Milestone 2, next cycle on the plan, so `/dev:review docs` has a consumer immediately.*
