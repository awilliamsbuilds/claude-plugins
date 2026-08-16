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
| `/dev:review docs <paths>` | Committed decision documents at one or more **absolute** paths supplied by the caller — **all five bullets `dev:validate` Step 2 carries today** (`validate/SKILL.md:85-90`): internal consistency, sufficient context for implementation, realistic consequences, no contradiction between decisions, non-trivial rationale. No discovery, no default: a bare `/dev:review docs` is an error, exactly as a bare `/dev:review` is | `dev:validate` (architecture cycles) |

**`<paths>` is required, and that is how the `docs` mode gets tree-correct scoping without a `<tree>`
argument.** During a cycle the decision documents live under `$WORKDIR/docs/dev/<feature>/` and only
reach `docs/decisions/` at Done, so a `docs` reviewer that discovered its own paths — or resolved
relative ones — would resolve them against its own `$PRIMARY` and review the wrong tree's documents.
That is the same failure Scope 2 exists to kill, arriving by the other route. Absolute paths from the
caller close it, which is why the architecture route needs no `<tree>` of its own.

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
already binds its second token to the base (`BASE="$2"`), documents it in four places (tabled below), and is called
that way by `dev:fix` as `/dev:secure diff "$AUDIT_BASE"`. Tree-first would silently reparse `main` as
a path and break every existing caller.

`<tree>` is **optional**; when absent, both fall back to the existing `$PRIMARY` derivation, which the
whole-project verb continues to use unchanged — it has no caller to hand it a tree.

**`dev:secure` Step 1's parse rule changes with the signature, and this edit is required rather than
incidental.** Step 1 today reads "Parse the argument as **at most two tokens**" (`secure/SKILL.md:63`)
and "A third token → stop and say the argument was not understood" (`:68`) — so a builder who edits
only Step 2a ships a skill whose own parser refuses the three-token call the rest of this cycle depends
on. "At most two tokens" becomes **at most three**; the third token is consumed by the `diff` verb as
`<tree>`; the refusal narrows to a **fourth** token, and to a *second* token on the whole-project
verb, which takes none. The exact-match rule on the first token (`:70`) is untouched.

**The signature is documented in four places, and all four are in scope.** Editing the parser without
the prose leaves the skill contradicting itself:

| Surface | Today |
|---|---|
| The verb table, `secure/SKILL.md:30` | `/dev:secure diff [<base>]` |
| Step 1's parse rule, `:63-68` | "at most two tokens" |
| Step 2a's *Resolve the base*, `:154-161` | binds `BASE="$2"` |
| `## Invocation`, `:331-335` | three forms, none with a tree |

The verb table and `## Invocation` are the two most easily missed, since neither is where the behavior
lives — which is precisely why they are named here.

**`<tree>` is validated, not trusted — and it needs its own allowlist, not the base ref's.** The
pattern is `^/[A-Za-z0-9._][A-Za-z0-9._/-]*$`, deliberately **not** the base ref's
`^[A-Za-z0-9._][A-Za-z0-9._/-]*$` (`secure/SKILL.md:172`). Measured: that pattern's first character
class excludes `/`, so it rejects **every absolute path** — and both callers pass absolute paths by
derivation, since `WORKDIR` descends from `PRIMARY=$(cd "$(dirname "$GIT_COMMON")" && pwd)`
(`validate/SKILL.md:16`, `secure/SKILL.md:39`). Reusing "the same shape" would ship a `diff` verb that
refuses the `"$WORKDIR"` the Happy Path hands it. Requiring the leading `/` is what rejects a
`-`-leading value.

A value that passes the allowlist but fails `git -C "$tree" rev-parse --is-inside-work-tree` **stops**
— it never falls back to `$PRIMARY`, since a silent fallback reproduces the wrong-tree failure this
cycle exists to kill (see Edge Cases).

This is a behavior change to `dev:secure`, and both halves are load-bearing (see Edge Cases).

**3. `dev:validate` Step 2 stops carrying checklists.**

```
Feature cycle       → dispatch /dev:review diff + /dev:secure diff, in parallel
Architecture cycle  → dispatch /dev:review docs with the absolute paths of the decision
                      documents under "$WORKDIR/docs/dev/<feature>/"
```

Step 2 gives up exactly **five** things: the code checklist, the security checklist, the
**architecture document-review checklist** (`validate/SKILL.md:85-90` — Step 2 carries *three*
checklists, not two, and this is the third: internal consistency, sufficient context, realistic
consequences, non-contradiction, non-trivial rationale — which becomes the `docs` mode's checklist per
item 1), the Architecture severity mapping table that classifies that review's findings
(`:98-104`, moving with the checklist per item 1, leaving no copy behind), and **its cold-dispatch
block**
(`validate/SKILL.md:58-64` — the subagent input list, the conversation-history exclusion, the
data-not-instruction guardrail, and the in-session fallback), which moves into the two reviewers per
item 2. The fallback sentence is the tell that this block cannot stay: it says to "fall back to
running **both checklists** in-session," and after this cycle Step 2 holds no checklists to run. After
this cycle `dev:review`'s `## Cold dispatch` is the only statement of that discipline, and Step 2
cites it rather than restating it.

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
match the pattern together. It needs no **re-point**. Note that this is the same line item 4 edits, for
an unrelated reason: `:14` *is* the `**When autopilot stops:**` list that gains the new stop condition.
So "needs no edit" would be wrong here — it needs no *citation change*, while being touched anyway.

The seven genuine references do **not** split cleanly into one kind; they take four different
treatments:

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

**The sweep pattern is narrower than the citation exposure, so the build spot-checks past it.** Three
further references cite `dev:validate`'s cold-review *behavior* without containing the string "Step 2"
— `spec/SKILL.md:565` and `plan/SKILL.md:210` ("the same reason `dev:validate` withholds conversation
history from its reviewers") and `references/tech-debt.md:458` ("the same rule `dev:validate` and
`dev:spec` already apply to review subagents"). All three are expected to survive unedited, because
validate still withholds history from the reviewers it dispatches — it just dispatches reviewer skills
rather than checklists. The build **confirms** that reading rather than assuming it, and edits any of
the three that no longer holds. Named here so the seven is understood as the re-point set, not as the
whole citation surface.

**And the sweep excluded `validate/SKILL.md` itself, which hides two more.** Step 4 step 8
(`validate/SKILL.md:146`) cites Step 2 twice — "mirroring Step 2's reviewers" and "run the checklist
in-session, as Step 2 falls back" — and the second becomes false once item 3 removes those checklists.
Both re-point at `## Cold dispatch`. These are the only text edits permitted outside Step 2, and
Success Criterion 4 states that carve-out rather than leaving it to collide with "unchanged".

**8. Folded-in debt: `debt-secure-tree-scoping-unsettled`.** Its *Done looks like* has **three**
clauses, and all three are in scope:

- (a) one tree rule correct for the `dev:fix` call path, the `dev:validate` worktree call path, and
  standalone use — delivered by item 2's explicit-tree argument **for the `diff` verb, and by a
  documented refusal for the whole-project verb**, which keeps auditing `$PRIMARY` and discloses that
  via clause (b) rather than accepting a tree. The item's *Why deferred* allows exactly this — "a
  caller-supplied tree, **or a documented refusal**" — so the split satisfies (a) rather than partly
  meeting it. Stated here because a Validate reviewer who reads (a) as "every verb takes a tree" would
  otherwise reopen the item;
- (b) the **whole-project verb names the tree it audited** in its report header. Not "exactly as the
  `diff` verb's header already does" — measured, that header names the *branch*
  (`**Branch audited:** <AUDIT_BRANCH>`, `secure/SKILL.md:273`), not the tree path, so copying it would
  satisfy the words and miss the point. The header names the **path**:
  `**Tree audited:** <path> · **Branch:** <branch>`;
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
- **The sixteen other debt items surfaced at grounding stay open** —
  `debt-secure-report-fields-not-grounded-in-output`, `debt-primary-cd-failure-unchecked`,
  `debt-artifact-path-rule-artifact-component-unconstrained`,
  `debt-cross-file-line-citations-go-stale-silently`, `backlog-reflect-before-pr-merge-…`; the two
  that intersect only via item 9's `dev/SKILL.md` edit — `debt-no-ui-flag-stated-as-authoritative` and
  `backlog-project-context-lost-between-cycles`; and the four that reach the cycle only through item
  7's citation edits in `spec/SKILL.md` and `plan/SKILL.md` — `debt-arch-cross-boundary-transport`,
  `debt-plan-task-trust-boundaries`, `debt-declined-user-proposals-leave-no-record`, and
  `debt-spec-grounding-citation-unverified`; and the five that reach it only through
  `references/tech-debt.md`, which item 7's spot-check may edit — `debt-p9-slug-regex-allows-leading-dash`,
  `debt-p9-issue-body-fence-width`, `debt-p2-collision-escalation-not-in-contract`,
  `debt-p6-overlap-test-unsatisfiable-for-fileless-items`, and
  `debt-done-promotion-close-assumes-single-source`.

  All sixteen are named rather than left silent, because this cycle touches their files. None is the
  clause its item records: item 9 edits Step 1a's *enumerations*, not the tier rule the `no-ui` item
  describes; item 7 rewrites single citation sentences in `spec/SKILL.md` and `plan/SKILL.md`, and none
  of the four is that sentence. Adjacent, not the same clause. `debt-spec-grounding-citation-unverified`
  deserves a specific note: it records that `dev:spec`'s grounding inventory says what was read but
  nothing verifies the citations resolve — visibly on-topic for this spec's own footer, and still out of
  scope, because fixing it means changing `dev:spec`'s procedure rather than this cycle's reviewers.
- **No `dev:autopilot` change beyond the one new stop condition.**

## Success Criteria

1. `plugins/dev/skills/review/SKILL.md` exists, is report-only (`git status --porcelain` byte-identical
   before and after any run), and has two explicit modes with adjacent, distinct severity tables. A bare
   `/dev:review` errors.
2. `dev:review` and `dev:secure` each dispatch a fresh `general-purpose` subagent, withhold
   conversation history, carry the data-not-instruction guardrail, and state the in-session fallback.
3. Both accept `<base>` first and an optional `<tree>` second. Given a `<tree>` they audit it; given
   none they fall back to the `$PRIMARY` derivation. `/dev:secure diff main` still means base=`main`.
   A `<tree>` that fails the allowlist, or that passes it but does not resolve to a git worktree,
   **stops** with the argument named and never falls back to `$PRIMARY`. All **four** `dev:secure`
   surfaces that document the signature agree with the parser — the verb table (`:30`), Step 1's parse
   rule (`:63-68`), Step 2a's *Resolve the base* (`:154-161`), and `## Invocation` (`:331-335`) — and
   Step 1 refuses a **fourth** token on `diff` and a **second** on the whole-project verb.
4. `dev:validate` Step 2 contains **none** of its three review checklists and **no** Architecture
   severity mapping table — a grep for those checklists' bullets and for that table's rows
   **scoped to `plugins/dev/skills/validate/SKILL.md`** returns nothing (repo-wide would fail by
   construction, since `dev:review` carries all of them by design). Outside Step 2, `dev:validate`'s
   responsibilities (Steps 3, 4, 5, 5a, 5b, and the gate) are **behaviorally** unchanged, and the
   **only** permitted text edit is Step 4 step 8's two intra-file citations of Step 2 — "no
   conversation history, mirroring Step 2's reviewers" and "run the checklist in-session, as Step 2
   falls back" (`validate/SKILL.md:146`) — which re-point at `dev:review`'s `## Cold dispatch` per
   Scope 7. Every other sentence in those steps is byte-identical.

   This carve-out exists because the earlier phrasing ("textually unchanged") contradicted Scope 7
   outright: the sweep in item 7 excluded `validate/SKILL.md`, so these two intra-file citations were
   never counted among the seven — and the second of them becomes **false** the moment item 3 removes
   the checklists it says Step 2 falls back to running.
5. Running `/dev:validate` on a feature cycle in a worktree reviews **that worktree's** diff, not the
   primary checkout's.
5b. Running `/dev:validate` on an architecture cycle in a worktree reviews **that worktree's** decision
    documents, not the primary checkout's — delivered by `docs` mode's required absolute `<paths>`
    rather than by a `<tree>` argument.
6. A reviewer that cannot run leaves `stage` un-advanced with the reason in `validation.md`, and
   `dev:autopilot`'s stop list names it.
7. `dev:fix` Step 6 dispatches both reviewers in parallel, and a code-review P1/P2 blocks the PR under
   the one-round bound. The PR body's `## What was verified` block carries a `code review:` line beside
   its existing `security:` line, and `### The rigor floor` carries a matching bullet — the two lines
   Scope 5 names, and the only PR-body change in scope.
8. `dev:secure` names CSRF, and no sentence in it claims the checklist adds no new vector. The
   template-injection question is **settled in writing**: either Pass C's Injection bullet names
   server-side template rendering, or `validation.md` records that both readings were read and no gap
   was found. Unsettled is a failure — that is what makes item 6's second bullet checkable.
9. All **seven** genuine `dev:validate` Step 2 references resolve to a section that exists and says what
   the citing text claims it says — the four discipline citations at `dev:review`'s `## Cold dispatch`,
   `plan/SKILL.md:201`'s two clauses each pointing at their own target, `secure/SKILL.md`'s rewritten to
   cite something that still exists, and `fix/SKILL.md:677` stating **two** reviews per route rather
   than one. `autopilot/SKILL.md:14` receives **no citation re-point** — its only edit is item 4's new
   stop-condition entry — and a re-run of the sweep still returns it. The three references that cite
   validate's cold-review behavior without the string "Step 2" (`spec:565`, `plan:210`,
   `references/tech-debt.md:458`) each still say something true.
10. `debt-secure-tree-scoping-unsettled` moves to `docs/backlog/closed/`, with all three clauses of its
    *Done looks like* met — the tree rule, the whole-project report header naming its tree **as a path**,
    and no remediation line that cannot change the outcome.
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
1. Step 2 enumerates the committed decision documents under `$WORKDIR/docs/dev/<feature>/` and
   dispatches `/dev:review docs` with their **absolute** paths — never the bare verb, which Scope 1
   defines as an error
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
  previous bullet exists to prevent.

  **The reason is not argument injection, and saying so would be an unmeasured claim.** Measured:
  `git -C "-foo" status` and `git -C "--exec-path=/tmp/x" status` both fail with
  `fatal: cannot change to '<value>'` — `-C` consumes its operand positionally and never reparses it as
  an option, so a `-`-leading tree is not the injection shape the base ref's guard exists for. The
  allowlist is still worth having, for the ordinary reason: it turns a malformed path into a named
  refusal instead of a `git` error surfacing from inside a reviewer. This distinction is recorded rather
  than glossed because `dev:validate` Step 4 step 3b requires observable command behavior to be
  measured before a claim about it is committed, and the first draft of this bullet asserted the
  injection reading without running it.
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
*Grounding inventory: (1) "dev:validate Step 2 carries inline code + security checklists" → read `validate/SKILL.md` §Step 2 in full — confirmed as to both, 6 code bullets (`:67-72`) + 5 security bullets (`:75-79`), but **incomplete as a count of checklists**: the third cold review found Step 2 also carries the 5-bullet architecture document-review checklist at `:85-90`, which the framing "code + security" had made invisible across three rounds. Step 2 holds **three** checklists, and item 3 moves all three. (2) "dev:fix has no code review" → `grep -n "code review\|code-review" fix/SKILL.md` → no matches; security only. (3) "dev:secure is a superset of validate's security bullets" → read both verbatim and mapped them — superset by ~15 named vectors + 2 whole categories (Data exposure, Business logic), **except CSRF**, which validate names and dev:secure omits entirely. Re-measured at the second cold review, which found the exception list incomplete: `grep -n "template" secure/SKILL.md` → **one** hit (`:126`), and it is "template literals into queries" under SQL, whereas `validate:75` lists "template" as an injection type in its own right. So there are **two** candidate losses, not one, and the second is unresolved by reading alone — Scope 6 hands the build the choice with both readings named and forbids assuming the benign one. (4) "dev:secure adds no new vector" (`secure/SKILL.md` Pass C) → **false**, disproved by (3). (5) "dev:secure runs cold" → `grep -n "subagent\|general-purpose\|conversation history" secure/SKILL.md` → **no matches; it runs in-session**. (6) References to validate Step 2, enumerated by sweep not recall → `grep -rn "validate.*Step 2" plugins/` (excluding `validate/SKILL.md`) → **eight lines**: `spec/SKILL.md:556,569`, `plan/SKILL.md:201,214`, `fix/SKILL.md:652,677`, `secure/SKILL.md:123`, plus `autopilot/SKILL.md:14`. The eighth is a **false positive** — that line cites `dev:validate` Step *5b* and separately ends with autopilot's own "see Step 2"; the pattern spans the two fragments. Seven genuine. Counted twice and re-split twice: the first draft said "six", the first cold review corrected the count to seven and the second corrected the *classification* — the seven take **four** treatments, not two, because `plan:201` carries two citations in one sentence and `fix:677` is made false rather than stale (see Scope 7). (7) "dev:secure audits $PRIMARY while cycles run in worktrees" → read its `AUDIT_BRANCH`/`INVOKED_IN` block — confirmed; it discloses the mismatch rather than accepting a tree. (8) Open debt intersecting this cycle's files, by front-matter `files:` sweep over the P5 corpus → **12** items, of which `debt-secure-tree-scoping-unsettled` is a precondition rather than an adjacent pay-down. This count was wrong twice and for the same reason both times — the sweep's *file set* lagged the spec's own scope. It returned 6 before Scope 9 added `dev/SKILL.md`, then 8 before it included `spec/SKILL.md` and `plan/SKILL.md`, which item 7 edits. Then **12 before it included `references/tech-debt.md`**, which item 7's spot-check may edit — the true figure is **17** intersecting items, 1 paid and 16 left open. The correct sweep is over every file any Scope item touches *or may touch*; all 17 are now accounted for. The recurring failure is worth stating plainly, since it recurred three times inside one spec: a `files:` sweep is only as good as the file list handed to it, and this spec's file list grew after each of the three sweeps. The third cold review noted this was the third instance of the failure this very claim names in its own words. (9) "the whole-project verb may keep auditing `$PRIMARY` and still satisfy the debt item's clause (a)" → read `debt-secure-tree-scoping-unsettled.md` *Why deferred* verbatim → confirmed, it allows "a caller-supplied tree, **or a documented refusal**". (10) "validate Step 2's config-contract check exists nowhere else" → `grep -rn "Config contract" plugins/` → **one** hit, `validate/SKILL.md:72`; it is the sixth code bullet, and the first draft's five-lens `diff` row would have deleted it. (11) "`dev/SKILL.md` Step 1a hardcodes one skill list" → **false**, read Step 1a in full → **two** hand-maintained enumerations (item 4's printed `FYI — other skills` list, and the missing-registry fallback below it); the first is the one `/dev list` prints on the normal path. (12) "a bare SHA is a usable `<base>`" → ran `dev:secure`'s own two gates against `git rev-parse HEAD` → allowlist `^[A-Za-z0-9._][A-Za-z0-9._/-]*$` passes and `rev-parse --verify "$BASE^{commit}"` passes, so Happy Path needs no allowlist edit. (13) "`dev:secure` Step 1 will accept a three-token call" → **false**, `secure/SKILL.md:63` reads "at most two tokens" and `:68` "a third token → stop"; the parse rule is now an explicit deliverable in Scope 2 rather than an assumed one. Line numbers re-measured after the second cold review caught the first draft's `:64-70` off-by-one — the exact class `debt-cross-file-line-citations-go-stale-silently` records, reproduced inside a spec that cites that item. (14) "telemetry-schema is an architecture cycle" → read `docs/dev/product-plans/dev-observability.md` — confirmed, Milestone 2, next cycle on the plan, so `/dev:review docs` has a consumer immediately. (15) "the second-token signature is documented in three places" → **four**: the verb table (`:30`), Step 1 (`:63-68`), Step 2a's *Resolve the base* (`:154-161`), and `## Invocation` (`:331-335`) — all four now named in Scope 2. (16) "`autopilot/SKILL.md:14` is untouched by this cycle" → **false**, `:14` *is* the `When autopilot stops:` list Scope 4 extends; it takes no citation re-point, which is a different claim, and conflating the two put Scope 7 and Success Criterion 9 in contradiction with Scope 4 and Criterion 6. (17) "`dev:validate` Step 2 keeps its cold-dispatch block" → **false**, `validate/SKILL.md:58-64` holds the subagent input list, the history exclusion, the injection guardrail, and a fallback reading "fall back to running **both checklists** in-session" — checklists item 3 removes, so the block moves into the reviewers rather than staying. (18) "`/dev:review docs` can discover its own paths" → **rejected on measurement**: decision documents live at `$WORKDIR/docs/dev/<feature>/` during a cycle and reach `docs/decisions/` only at Done (`build/SKILL.md:81`), so discovery or relative resolution inside the reviewer lands on `$PRIMARY` — the wrong-tree failure by the other route. Hence required absolute `<paths>`. (19) "`<tree>` can reuse the base ref's allowlist" → **false, and it would have broken both callers**: `printf '/Users/adam/Development/claude-plugins' | grep -qE '^[A-Za-z0-9._][A-Za-z0-9._/-]*$'` fails, because that pattern's first character class excludes `/` and rejects every absolute path — while both callers pass absolute paths by derivation (`validate/SKILL.md:16`, `secure/SKILL.md:39`). `<tree>` gets `^/[A-Za-z0-9._][A-Za-z0-9._/-]*$` instead; verified to accept an absolute path and reject a `-`-leading one. (20) "a `-`-leading `<tree>` is an argument-injection shape" → **false**: ran `git -C "-foo" status` and `git -C "--exec-path=/tmp/x" status` → both `fatal: cannot change to '<value>'`; `-C` consumes its operand positionally and never reparses it as an option. The allowlist stays, the stated reason does not. (21) "`dev:validate` Step 4 step 8 needs no edit" → **false**, `validate/SKILL.md:146` restates the cold discipline *and* says "run the checklist in-session, as Step 2 falls back" — false once item 3 lands. The sweep in item 7 excluded `validate/SKILL.md`, so this intra-file citation escaped all three counts; Success Criterion 4 now carries it as the one permitted text edit. (22) "the `diff` verb's report header names the tree it audited" → **false**, `secure/SKILL.md:273` names the *branch* (`**Branch audited:**`); clause (b) therefore specifies a path explicitly rather than saying "as the diff verb does".*
