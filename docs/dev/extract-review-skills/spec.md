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
| `/dev:review diff <base> [<tree>]` | The diff — **all six bullets `dev:validate` Step 2 carries today**: logic, edge cases, quality, conventions, plan coverage where a plan exists, and the config-contract check | `dev:validate` (feature cycles), `dev:fix` |
| `/dev:review docs <paths>` | Committed decision documents — consistency, sufficiency, realistic consequences, rationale | `dev:validate` (architecture cycles) |

**The sixth bullet is named explicitly because it is the one at risk.** `dev:validate` Step 2's
config-contract check ("if this cycle adds a new key to `docs/dev/config.json`, verify every skill
that reads *that key* lists it in its Step 1 read list") is the only occurrence of that check in the
repo — measured: `grep -rn "Config contract" plugins/` returns one hit, `validate/SKILL.md:72`. A
five-lens `diff` mode would delete it out of existence, which is exactly the coverage loss item 6
caught for CSRF on the security side.

**The `docs` mode's severity table is `dev:validate` Step 2's existing Architecture severity mapping,
moved rather than copied** (`validate/SKILL.md:98-104`). It travels with the checklist it classifies,
because a reviewer that cannot classify its own findings is not report-complete. `dev:validate` keeps
**no** copy; Step 3 remains the canonical generic P1–Nit vocabulary that both modes consume, and its
architecture-cycle reinterpretation now lives beside the checklist that produces those findings.

A bare `/dev:review` is an **error**, never an inferred mode. The two modes do not share a severity
meaning — code review's P1 is a correctness blocker, document review's P1 is an internally
inconsistent or contradictory decision — so a reader must never be uncertain which table applies.

**2. Both reviewers own cold dispatch and take an explicit tree.**

`dev:review` and `dev:secure` each dispatch a fresh `general-purpose` subagent internally: no
conversation history, diff-and-artifacts-as-data guardrail, and the existing in-session fallback when
subagent dispatch is unavailable in the harness.

**Both take the base first and the tree second — `/dev:review diff <base> [<tree>]` and
`/dev:secure diff <base> [<tree>]`** — so `dev:secure`'s existing two-token call keeps its current
meaning and the two reviewers share one argument order. This ordering is not cosmetic: `dev:secure`
already binds its second token to the base (`BASE="$2"`), documents it in three places, and is called
that way by `dev:fix` as `/dev:secure diff "$AUDIT_BASE"`. Tree-first would silently reparse `main` as
a path and break every existing caller.

`<tree>` is **optional**; when absent, both fall back to the existing `$PRIMARY` derivation, which the
whole-project verb continues to use unchanged — it has no caller to hand it a tree.

**`dev:secure` Step 1's parse rule changes with the signature, and this edit is required rather than
incidental.** Step 1 today reads "Parse the argument as **at most two tokens**" and "A third token →
stop and say the argument was not understood" (`secure/SKILL.md:64-70`) — so a builder who edits only
Step 2a ships a skill whose own parser refuses the three-token call the rest of this cycle depends on.
"At most two tokens" becomes **at most three**; the third token is consumed by the `diff` verb as
`<tree>`; the refusal narrows to a **fourth** token, and to a *second* token on the whole-project
verb, which takes none. The exact-match rule on the first token is untouched.

**`<tree>` is validated, not trusted.** It reaches `git -C "$tree"` from the same trust level as the
base ref one argument over, where `dev:secure` already carries an anchored allowlist plus
`--end-of-options` precisely because a `-`-leading value becomes a `git` option. `<tree>` gets an
anchored path check of the same shape, and a value that does not resolve to a git worktree **stops** —
it never falls back to `$PRIMARY`, since a silent fallback reproduces the wrong-tree failure this
cycle exists to kill (see Edge Cases).

This is a behavior change to `dev:secure`, and both halves are load-bearing (see Edge Cases).

**3. `dev:validate` Step 2 stops carrying checklists.**

```
Feature cycle       → dispatch /dev:review diff + /dev:secure diff, in parallel
Architecture cycle  → dispatch /dev:review docs
```

Step 2 gives up exactly three things: the code checklist, the security checklist, and the Architecture
severity mapping table that classifies the document review's findings (which moves with the `docs`
checklist per item 1, leaving no copy behind).

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

**Two PR-body lines come with it, and they are the only PR-body change in scope.** The
`## What was verified` block gains a `code review:` line mirroring the existing `security:` line, and
`### The rigor floor` gains a matching bullet. Without them the lane would run a second review and
report only the first — and the Out of Scope bullet below is narrowed accordingly.

**6. Two `dev:secure` corrections, both preconditions rather than extras.**

- **CSRF coverage is restored.** `dev:validate`'s inline bullet names it; `dev:secure` has no
  counterpart anywhere in Pass C, and it is absent from the "deliberately not covered" list. Once
  validate stops carrying its own bullets, CSRF exists nowhere in the repo unless `dev:secure` gains
  it in this same cycle.
- **Server-side template injection is resolved the same way.** `dev:validate:75` lists injection as
  "(SQL, command, **template**)"; `grep -n "template" secure/SKILL.md` returns exactly one hit
  (`:126`), and it is "template literals into queries" *under SQL* — a different vulnerability class
  from a user-controlled template rendered server-side. Either validate's third word is already
  subsumed by that SQL clause, in which case the builder records that it checked and found no gap, or
  it is a second CSRF-shaped loss, in which case Pass C's Injection bullet gains it. The build settles
  which by reading both, and may not settle it by assuming the first.
- **The false "adds no new vector" claim is corrected** (`secure/SKILL.md`, Pass C). Measured, Pass C
  adds roughly fifteen named vectors validate never mentions plus two whole categories (Data
  exposure, Business logic). The line matters beyond accuracy: a future cycle "reconciling the
  duplication" on the strength of that sentence would delete real coverage believing it redundant.

**7. The seven `dev:validate` Step 2 references re-point.** A sweep
(`grep -rn "validate.*Step 2" plugins/`, excluding `validate/SKILL.md` itself) returns **eight lines,
seven of them genuine**: the eighth, `autopilot/SKILL.md:14`, is a false positive — that line names
`dev:validate` Step *5b* and separately ends with autopilot's own "see Step 2", and the two fragments
match the pattern together. It needs no edit. The seven genuine references do **not** split cleanly
into one kind; they take four different treatments:

- **Four re-point at the cold-review discipline** — `dev:spec` Step 12a (`:556`, `:569`), `dev:plan`
  Step 7a (`:214`), `dev:fix` (`:652`) — for the principle and for the in-session fallback. These cite
  **`dev:review`'s `## Cold dispatch` section**, which becomes the canonical statement of that
  discipline. Naming the target here rather than deferring it to Build is deliberate: two defensible
  targets exist (the reviewer skills, or `dev:validate` Step 4 step 8, which keeps its own cold
  re-review), and a builder should not have to pick. `dev:validate` Step 4 step 8 keeps its
  re-review and cites that same section rather than restating it.
- **`plan/SKILL.md:201` needs a split edit, not a re-point.** One sentence carries *two* citations:
  Step 2 as the plan-coverage consumer ("treats the plan as ground truth — *were all plan tasks
  implemented?*", which is the bullet item 3 moves) and, at the sentence's close, the cold-review
  principle. The first clause re-points at `dev:review`'s `diff` mode, which now owns that bullet; the
  second at `## Cold dispatch`. Re-pointing the whole sentence at either target alone produces a
  citation that does not say what the citing text claims.
- **`fix/SKILL.md:677` is rewritten, not re-pointed** — it is the one reference this cycle makes
  *false* rather than merely stale. It asserts "**The pipeline and the lane each run exactly one
  review** … There is no double review," which Scope 5 falsifies by giving the lane a second reviewer.
  New text: *"The pipeline and the lane each run the same two reviews, once. A cycle that goes through
  the full seven stages is reviewed at `dev:validate` Step 2 and never reaches this section; a lane run
  is reviewed here and never enters that stage. There is no double review, and no route to a PR with
  none."*
- **`secure/SKILL.md:123` cites Step 2's *security checklist*** — the thing item 3 deletes — so this
  cycle would otherwise leave a citation that is both dangling and false. It is rewritten in the same
  edit as item 6's false-claim correction, since the two sit in the same paragraph.

**8. Folded-in debt: `debt-secure-tree-scoping-unsettled`.** Its *Done looks like* has **three**
clauses, and all three are in scope:

- (a) one tree rule correct for the `dev:fix` call path, the `dev:validate` worktree call path, and
  standalone use — delivered by item 2's explicit-tree argument **for the `diff` verb, and by a
  documented refusal for the whole-project verb**, which keeps auditing `$PRIMARY` and discloses that
  via clause (b) rather than accepting a tree. The item's *Why deferred* allows exactly this — "a
  caller-supplied tree, **or a documented refusal**" — so the split satisfies (a) rather than partly
  meeting it. Stated here because a Validate reviewer who reads (a) as "every verb takes a tree" would
  otherwise reopen the item;
- (b) the **whole-project verb names the tree it audited** in its report header, exactly as the `diff`
  verb's header already does;
- (c) **no remediation line instructs an action that cannot change the outcome** — the live "run
  `/dev:secure diff` from the primary checkout of it" line is replaced by one naming the tree argument.

**9. Docs reconciliation** — `CLAUDE.md` Component Registry (new `dev:review` row; `dev:validate`,
`dev:secure`, `dev:fix` rows updated), README's `dev` skills list, and **`dev/SKILL.md` Step 1a's
two hardcoded skill enumerations**, which each enumerate every skill by hand and would otherwise omit
`dev:review` entirely:

- item 4's **`FYI — other skills` printed list** — the list that decides what `/dev list` prints on the
  **normal** path, where the registry is present;
- the **missing-registry fallback list** below it, used only when the Component Registry table or a row
  is missing.

Both, not just the second. A build that reconciled only the fallback would ship a `/dev list` that
never mentions `dev:review` except when the registry is broken — the inverse of the intended behavior.

## Out of Scope

- **No whole-project `/dev:review` verb.** `dev:secure` has one; `dev:review` ships with only the
  modes that have callers. Addable later without breaking either caller.
- **No change to the P1/P2/P3/Nit vocabulary.** `dev:validate` Step 3 remains its canonical
  definition; both reviewers consume it, as `dev:secure` already does.
- **No change to `dev:validate`'s fix loop, Step 5b build check, or Step 5a debt buffer.**
- **No change to `dev:fix`'s build check, merge tail, or triage rule.** The PR body changes only by
  the two lines named in Scope 5 — the `code review:` verified-line and its rigor-floor bullet.
- **No warm/cold caller flag.** Considered and declined: it would preserve today's lane speed at the
  cost of a parameter that drifts, and the lane is where cold review buys the most (see Technical
  Constraints).
- **The seven other debt items surfaced at grounding stay open** —
  `debt-secure-report-fields-not-grounded-in-output`, `debt-primary-cd-failure-unchecked`,
  `debt-artifact-path-rule-artifact-component-unconstrained`,
  `debt-cross-file-line-citations-go-stale-silently`, `backlog-reflect-before-pr-merge-…`, and the two
  that intersect only via item 9's `dev/SKILL.md` edit: `debt-no-ui-flag-stated-as-authoritative` and
  `backlog-project-context-lost-between-cycles`. The last two are named rather than left silent
  because item 9 touches their file — but item 9 edits Step 1a's *enumerations*, not Step 1a's tier
  rule, which is the clause the `no-ui` item records. Adjacent, not the same clause; both stay open.
- **No `dev:autopilot` change beyond the one new stop condition.**

## Success Criteria

1. `plugins/dev/skills/review/SKILL.md` exists, is report-only (`git status --porcelain` byte-identical
   before and after any run), and has two explicit modes with adjacent, distinct severity tables. A bare
   `/dev:review` errors.
2. `dev:review` and `dev:secure` each dispatch a fresh `general-purpose` subagent, withhold
   conversation history, carry the data-not-instruction guardrail, and state the in-session fallback.
3. Both accept `<base>` first and an optional `<tree>` second. Given a `<tree>` they audit it; given
   none they fall back to the `$PRIMARY` derivation. `/dev:secure diff main` still means base=`main`.
4. `dev:validate` Step 2 contains **no** review checklist for either cycle type and **no** Architecture
   severity mapping table — a grep for its former checklist bullets and for that table's rows
   **scoped to `plugins/dev/skills/validate/SKILL.md`** returns nothing (repo-wide would fail by
   construction, since `dev:review` carries both by design) — and `dev:validate`'s responsibilities
   outside Step 2 (Steps 3, 4, 5, 5a, 5b, and the gate) are textually unchanged.
5. Running `/dev:validate` on a feature cycle in a worktree reviews **that worktree's** diff, not the
   primary checkout's.
6. A reviewer that cannot run leaves `stage` un-advanced with the reason in `validation.md`, and
   `dev:autopilot`'s stop list names it.
7. `dev:fix` Step 6 dispatches both reviewers in parallel, and a code-review P1/P2 blocks the PR under
   the one-round bound.
8. `dev:secure` names CSRF, and no sentence in it claims the checklist adds no new vector.
9. All **seven** genuine `dev:validate` Step 2 references resolve to a section that exists and says what
   the citing text claims it says — the four discipline citations at `dev:review`'s `## Cold dispatch`,
   `plan/SKILL.md:201`'s two clauses each pointing at their own target, `secure/SKILL.md`'s rewritten to
   cite something that still exists, and `fix/SKILL.md:677` stating **two** reviews per route rather
   than one. `autopilot/SKILL.md:14` is unedited, and a re-run of the sweep still returns it.
10. `debt-secure-tree-scoping-unsettled` moves to `docs/backlog/closed/`, with all three clauses of its
    *Done looks like* met — the tree rule, the whole-project report header naming its tree, and no
    remediation line that cannot change the outcome.
11. `dev/SKILL.md` Step 1a names `dev:review` in **both** its `FYI — other skills` list and its
    missing-registry fallback list.
12. `grep -rn "Config contract" plugins/` still returns exactly one hit — now in `review/SKILL.md`
    rather than `validate/SKILL.md`. The check is moved, never dropped.

## Happy Path

**Feature cycle (pipeline)**
1. `dev:validate` Step 2 resolves the base it wants reviewed (`BASE_SHA`) and the tree (`$WORKDIR`)
2. Dispatches `/dev:review diff "$BASE_SHA" "$WORKDIR"` and `/dev:secure diff "$BASE_SHA" "$WORKDIR"`
   in parallel. Both arguments are passed explicitly; neither reviewer takes an end-ref, because each
   diffs the given base against **the given tree's own `HEAD`** — which is what makes the tree argument
   sufficient. A bare SHA is a valid `<base>`: measured, it passes `dev:secure`'s existing base
   allowlist (`^[A-Za-z0-9._][A-Za-z0-9._/-]*$`) and its `rev-parse --verify "$BASE^{commit}"` check
   unchanged, so no allowlist edit is needed to hand a SHA rather than a branch name
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
- **`<tree>` is malformed or does not resolve** — a `-`-leading value, or a path that is not a git
  worktree. Both **stop** with the argument named, and neither falls back to `$PRIMARY`. Falling back
  would turn a caller's typo into a silent audit of the wrong tree, which is the precise failure the
  previous bullet exists to prevent; and the `-`-leading case is the same argument-injection shape
  `dev:secure` already guards on its base ref.
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
*Grounding inventory: (1) "dev:validate Step 2 carries inline code + security checklists" → read `validate/SKILL.md` §Step 2 in full — confirmed, 6 code bullets + 5 security bullets. (2) "dev:fix has no code review" → `grep -n "code review\|code-review" fix/SKILL.md` → no matches; security only. (3) "dev:secure is a superset of validate's security bullets" → read both verbatim and mapped them — superset by ~15 named vectors + 2 whole categories (Data exposure, Business logic), **except CSRF**, which validate names and dev:secure omits entirely. Re-measured at the second cold review, which found the exception list incomplete: `grep -n "template" secure/SKILL.md` → **one** hit (`:126`), and it is "template literals into queries" under SQL, whereas `validate:75` lists "template" as an injection type in its own right. So there are **two** candidate losses, not one, and the second is unresolved by reading alone — Scope 6 hands the build the choice with both readings named and forbids assuming the benign one. (4) "dev:secure adds no new vector" (`secure/SKILL.md` Pass C) → **false**, disproved by (3). (5) "dev:secure runs cold" → `grep -n "subagent\|general-purpose\|conversation history" secure/SKILL.md` → **no matches; it runs in-session**. (6) References to validate Step 2, enumerated by sweep not recall → `grep -rn "validate.*Step 2" plugins/` (excluding `validate/SKILL.md`) → **eight lines**: `spec/SKILL.md:556,569`, `plan/SKILL.md:201,214`, `fix/SKILL.md:652,677`, `secure/SKILL.md:123`, plus `autopilot/SKILL.md:14`. The eighth is a **false positive** — that line cites `dev:validate` Step *5b* and separately ends with autopilot's own "see Step 2"; the pattern spans the two fragments. Seven genuine. Counted twice and re-split twice: the first draft said "six", the first cold review corrected the count to seven and the second corrected the *classification* — the seven take **four** treatments, not two, because `plan:201` carries two citations in one sentence and `fix:677` is made false rather than stale (see Scope 7). (7) "dev:secure audits $PRIMARY while cycles run in worktrees" → read its `AUDIT_BRANCH`/`INVOKED_IN` block — confirmed; it discloses the mismatch rather than accepting a tree. (8) Open debt intersecting this cycle's files, by front-matter `files:` sweep over the P5 corpus → **8** items, of which `debt-secure-tree-scoping-unsettled` is a precondition rather than an adjacent pay-down. Re-swept at the second cold review, which caught that the original sweep returned 6 because it predated Scope 9's addition of `dev/SKILL.md` to this cycle's file set; the two additional items reach the cycle only through that file and are now named in Out of Scope rather than left silent. (9) "the whole-project verb may keep auditing `$PRIMARY` and still satisfy the debt item's clause (a)" → read `debt-secure-tree-scoping-unsettled.md` *Why deferred* verbatim → confirmed, it allows "a caller-supplied tree, **or a documented refusal**". (10) "validate Step 2's config-contract check exists nowhere else" → `grep -rn "Config contract" plugins/` → **one** hit, `validate/SKILL.md:72`; it is the sixth code bullet, and the first draft's five-lens `diff` row would have deleted it. (11) "`dev/SKILL.md` Step 1a hardcodes one skill list" → **false**, read Step 1a in full → **two** hand-maintained enumerations (item 4's printed `FYI — other skills` list, and the missing-registry fallback below it); the first is the one `/dev list` prints on the normal path. (12) "a bare SHA is a usable `<base>`" → ran `dev:secure`'s own two gates against `git rev-parse HEAD` → allowlist `^[A-Za-z0-9._][A-Za-z0-9._/-]*$` passes and `rev-parse --verify "$BASE^{commit}"` passes, so Happy Path needs no allowlist edit. (13) "`dev:secure` Step 1 will accept a three-token call" → **false**, `secure/SKILL.md:64-70` reads "at most two tokens" and "a third token → stop"; the parse rule is now an explicit deliverable in Scope 2 rather than an assumed one. (9) "telemetry-schema is an architecture cycle" → read `docs/dev/product-plans/dev-observability.md` — confirmed, Milestone 2, next cycle on the plan, so `/dev:review docs` has a consumer immediately.*
