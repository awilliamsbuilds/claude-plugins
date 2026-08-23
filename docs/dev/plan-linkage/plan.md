# Plan Linkage — Implementation Plan
*Branch: feature/plan-linkage · 2026-08-23*

## Files

| File | Action | Purpose |
|------|--------|---------|
| plugins/dev/references/product-plans.md | Create | Canonical lookup + plan-order-check contract (§L1–§L5) that both entry points cite |
| plugins/dev/skills/spec/SKILL.md | Modify | Step 1 reads the new reference; Step 6 runs the check and adds product-plan path (C) |
| plugins/dev/skills/fix/SKILL.md | Modify | Step 1 reads the new reference; new Step 2b runs the check before anything is created |
| plugins/dev/skills/autopilot/SKILL.md | Modify | Step 2 records the autopilot suppression of the check's question |
| plugins/dev/skills/done/SKILL.md | Modify | Step 3's plan-locate paragraph names path (C) as a third writer of `product_plan` |
| docs/dev/plan-linkage/debt-pending.md | Create | `## To Close` close-intent for the backlog item this cycle adopts |

**Design decision — one contract, two call sites.** The lookup and the check live once, in a new
shared reference, because `dev:spec` and `dev:fix` both need them and a third consumer (Milestone 4b
`plan-scoped-worktree`) is already named in the governing plan. This matches the repo's existing
shape: `references/tech-debt.md` and `references/entry-adapters.md` are both contracts loaded by
several skills rather than procedures restated per skill.

**Design decision — what counts as a mismatch.** The spec's Edge Case "the plan's next unchecked item
is ambiguous" says order *within a milestone* is not binding, while its Scope 3 example fires on a
name from a different plan. Read literally as "any unchecked item in the plan is not a mismatch," the
check could never fire on the failure it exists to catch. Resolved in §L4 as: **milestone order is
binding, item order within a milestone is not.** A name matching an unchecked item in the same
milestone as the plan's first unchecked item is on-order; one matching an item in a *later* milestone,
or an already-checked item, is a mismatch. This is the narrowest reading that keeps both spec
statements true.

**Design decision — where the plan files are read from.** Both call sites read
`$PRIMARY/docs/dev/product-plans/*.md`, and both run **before** anything is created (before
`dev:spec`'s `worktree add`, before `dev:fix`'s `checkout -b`), so answering "switch" costs nothing.
The cost is that a plan merged to `origin/main` but not yet pulled into the primary checkout is
invisible: the cycle prints nothing and stays unlinked, which is exactly today's behavior. `dev:done`
Step 7 fast-forwards the primary checkout at the end of every cycle, so this is the rare case, and
degrading to today's behavior is the correct failure direction for a check that must never block.

## Tasks

### Task 1: Write the product-plan lookup contract
What: Create `plugins/dev/references/product-plans.md`, the single canonical definition of how a
feature name resolves to a governing product plan and what each resolution outcome prints.
Used by: `dev:spec` Step 6 (Task 2) and `dev:fix` Step 2b (Task 3) cite it by section; `dev:done`
Step 3 (Task 5) cites §L1 for the value it reads; Milestone 4b will consume §L1 unchanged.
Depends on: nothing — first task.
Files: create `plugins/dev/references/product-plans.md`
Interfaces:
- Consumes: nothing
- Produces: the reference file and its five section anchors — `§L1` (the lookup), `§L2` (collision),
  `§L3` (next unchecked item), `§L4` (the four outcomes and their exact output), `§L5` (mode
  behaviour). Later tasks cite these anchors by name and never restate their content.
- State keys: introduces no new `state.json` key. §L1's result is written to the **existing**
  `product_plan` key by Task 2 `(writes: both)`.
- Shared procedure: **canonical** for the procedure named *plan-order check* (and for the *governing
  plan lookup* it rests on). Tasks 2 and 3 are call sites that cite these sections rather than
  reimplementing them; they restate only their own divergences, which Task 2 and Task 3 enumerate
  explicitly. Restating the branch structure at each call site is what this reference exists to
  prevent, so the Isolation Principle is satisfied by each call site naming its divergences in full
  rather than by duplicating §L4.

Implementation steps:
1. Open the file with a one-paragraph purpose: given a feature name, find the product plan that
   governs it, and say whether starting that name now follows the plan's order. State that the
   contract is repo-agnostic and assumes only `docs/dev/product-plans/*.md`.
2. Write **§L1 — The lookup.** Input: a name already normalized to `^[a-z0-9][a-z0-9-]*$` — strict
   lowercase, always. State that a **Linear-sourced caller passes the ID-stripped `<short-title>`
   half** of §A6's uppercase-tolerant cycle slug (`<ID>-<short-title>`), never the slug itself: the
   ID prefix is uppercase and unique per issue, so an ID-prefixed slug could match no plan item under
   any circumstances, and passing it would make the Linear entry points structurally incapable of
   linking or warning. Both Linear callers (Task 2's `/dev:spec linear`, Task 3's `/dev:fix linear`)
   therefore resolve to the same name, so the two entry points behave identically on one issue. State
   that matching is exact and case-sensitive. Read every
   `$PRIMARY/docs/dev/product-plans/*.md`. In each file, a *plan item* is a line matching
   `- [ ] <name>` or `- [x] <name>`, where `<name>` is the first whitespace-delimited token after the
   checkbox (the parenthesised suffix `(feature)` / `(feature, deep)` is not part of the name). Match
   the input against item names, exactly, case-sensitively. Output: `plan-path`, `item-name`,
   `item-checked` (bool), `item-milestone` (the nearest preceding `##` heading, or `"(top of file)"`
   where none precedes it), plus the plan's header cycles-completed string as written — or **no
   plan**. State the read root explicitly: `$PRIMARY`, not `$WORKDIR`, because both call sites run
   before their working tree exists. State that a missing or empty `docs/dev/product-plans/`
   directory returns no plan and is not an error.
3. Write **§L2 — Collision.** If the name matches items in **more than one** plan file, return **no
   plan** and print both matches:
   ```
   plan-scoped-worktree appears in 2 product plans:
     docs/dev/product-plans/dev-process-hardening.md
     docs/dev/product-plans/dev-observability.md
   Proceeding without linking to either — resolve by renaming one item.
   ```
   State the consequence in one line: `product_plan` stays `null`, so `dev:done` skips the check-off
   and the operator ticks the box by hand. Guessing is worse than not linking.
4. Write **§L3 — The plan's next unchecked item.** Define it as the **first `- [ ]` item in file
   order**, across all milestones. Define *the current milestone* as that item's `item-milestone`. A
   plan with no `- [ ]` item at all (every box ticked) has no next item; §L4 treats that as
   `unlinked`, prints nothing, and does not error — the plan is finished and `dev:done` Step 3b will
   delete it.
5. Write **§L4 — The four outcomes**, exhaustive, keyed on §L1's output. Give each its exact output:
   - **unlinked** — no plan matched (§L1), or the matched plan has no next unchecked item. Prints
     **nothing**. State that this is the ordinary standalone cycle and roughly half of recent cycles
     take it; printing here is what would train the reader to skip the check.
   - **on-order** — matched, `item-checked` is false, and `item-milestone` equals the current
     milestone. Prints one line, asks nothing:
     ```
     Plan dev-process-hardening (4/6) — plan-linkage is in the current milestone.
     ```
   - **mismatch** — matched, `item-checked` is false, and `item-milestone` is a **later** milestone
     than the current one. Prints and asks:
     ```
     Plan dev-process-hardening is 4/6 cycles complete.
     Next up is plan-scoped-worktree, not telemetry-schema.
     Continue anyway, or switch?
     ```
   - **already-done** — matched and `item-checked` is true. Prints and asks, naming the real
     condition rather than reusing the mismatch wording:
     ```
     Plan dev-process-hardening is 4/6 cycles complete.
     retro-inside-pr is already checked off. Next up is plan-scoped-worktree.
     Continue anyway, or switch?
     ```
   State the milestone rule that separates on-order from mismatch in one sentence — milestone order is
   binding, item order within a milestone is not — and cite the spec Edge Case it comes from.
6. In §L4, state the **never refuses** invariant: neither asking outcome can stop the cycle by itself.
   `continue` proceeds unchanged; `switch` stops **having created nothing** and prints the next item's
   exact command, `/dev:spec "<next-item-name>"`. Both call sites run the check before they create a
   branch, a worktree, or a file, which is what makes `switch` free.
7. Write **§L5 — Mode behaviour.** In **standard** mode the two asking outcomes ask and wait. In
   **autopilot** mode they **print and proceed** — no question, no stop — matching
   `dev:autopilot` Step 2's existing *Debt surfacing: print, never ask* rule
   (`autopilot/SKILL.md:135`, verified), which suppresses the same class of scope question for the
   same reason: a scope change needs a human, and autopilot has none. State that `unlinked` and
   `on-order` are mode-independent, and that the mode is read the way the calling skill already reads
   it (`dev:spec` Step 1's mode determination; `dev:fix` runs unattended and is always in the asking
   mode, per Task 3). Add one line closing the Linear symmetry: both Linear entry points pass the
   ID-stripped `<short-title>`, so `/dev:spec linear <id>` and `/dev:fix linear <id>` produce the same
   §L4 outcome for the same issue — the full-cycle escalation target is covered, not exempt.
8. Add a closing **Loaded by** line naming `dev:spec` (Step 1 reads, Step 6 calls), `dev:fix` (Step 1
   reads, Step 2b calls), and *cited by* `dev:autopilot` Step 2 and `dev:done` Step 3 — the same
   footer shape `references/entry-adapters.md` and `references/tech-debt.md` carry.

### Task 2: Add the check and product-plan path (C) to `dev:spec` Step 6
What: Make `/dev:spec` run the plan-order check on the normalized feature name before the worktree is
created, and record the governing plan in `state.json.product_plan` when the name matches exactly one
plan item.
Used by: every `/dev:spec` invocation; `dev:done` Step 3 reads the `product_plan` value this writes.
Depends on: Task 1 (cites §L1–§L5 by anchor).
Files: modify `plugins/dev/skills/spec/SKILL.md`
Interfaces:
- Consumes: Task 1's `§L1`–`§L5` anchors in `plugins/dev/references/product-plans.md`, and §L1's
  output fields `plan-path`, `item-name`, `item-checked`, `item-milestone`.
- Produces: `state.json.product_plan` set to §L1's `plan-path` on the exactly-one-match case — the
  same repo-relative `docs/dev/product-plans/<slug>.md` shape paths (A) and (B) already write.
- State keys: introduces **no new** `state.json` key. Path (C) is a third writer of the existing
  `product_plan` key `(writes: both)` — it is part of the initial state.json commit, gated by
  nothing, identical in standard and autopilot, exactly as path (B) already is.
- Shared procedure: *plan-order check* — **call site**, not an implementation. Task 1 is canonical.
  This site's divergences from the contract, stated in full at the site: (i) the name checked is the
  normalized `<feature-name>` derived in this same step — on the Linear entry path, the `<short-title>`
  half of §A6's slug with the `<ID>-` prefix stripped; (ii) the check runs before
  `git worktree add`, so `switch` unwinds nothing; (iii) mode comes from Step 1's existing mode
  determination, so autopilot takes §L5's print-and-proceed arm.

Implementation steps:
1. In **Step 1: Read Context**, add `../../references/product-plans.md` to the "Read these files once
   at stage start" list, with the one-line note that it is the governing-plan lookup and plan-order
   check contract and is read on every path (not Linear-only, unlike the adapter reference directly
   above it).
2. In **Step 6**, immediately after the paragraph beginning "**Feature name (derive and normalize
   first).**" and **before** the "**Create the cycle worktree (always).**" paragraph, insert a
   subsection titled **Plan-order check (before anything is created).** Say: run
   `../../references/product-plans.md` §L1 against the normalized `<feature-name>`, then apply §L4's
   outcome and §L5's mode rule. Hold §L1's result for path (C) below — one lookup per stage, not two.

   **`$PRIMARY` must be bound before this subsection reads it.** §L1's read root is `$PRIMARY`, and
   Step 6 currently derives it *inside* the worktree paragraph that now follows
   (`GIT_COMMON=$(git rev-parse --git-common-dir) || { echo "Not a git repository."; exit 1; }` then
   `PRIMARY=$(cd "$(dirname "$GIT_COMMON")" && pwd)`, `spec/SKILL.md:169-170`, verified). **Hoist that
   existing two-line pair above the inserted subsection**, unchanged and with its existing guard
   intact, and have the `git -C "$PRIMARY" fetch origin` / `git -C "$PRIMARY" worktree add …` commands
   below reuse the already-bound value. This is a **move, not a second derivation** — the repo's count
   of guarded `PRIMARY` derivations must not grow. (`dev:fix` needs no equivalent: it binds `PRIMARY`
   at `fix/SKILL.md:35`, well before Task 3's Step 2b.)
3. In that same subsection, state the three site-specific facts the contract does not know. **(i) The
   name checked** is the normalized `<feature-name>` this step just derived — never the raw argument.
   On the **Linear entry path** it is the **`<short-title>` half of §A6's `<ID>-<short-title>` cycle
   slug, with the `<ID>-` prefix stripped**, which is still a value derived from the resolved cycle
   slug (what the spec's entry-adapter edge case requires) rather than the raw argument, and is the
   strict-lowercase form §L1 declares — the ID prefix is uppercase and could never match a plan item.
   **(ii)** The check runs before `git worktree add`, so a `switch` answer stops with nothing created
   and nothing to unwind. **(iii)** A `switch` answer prints §L4's `/dev:spec "<next-item-name>"` line
   and ends the stage.
4. Locate the paragraph beginning "**Product-plan inheritance (path (B) …**" and extend its
   **Precedence (never run both)** sentence so it reads as a three-arm chain: a cycle that is itself
   product-scale takes path (A) and authors its own plan; else a nested cycle under a plan-bearing
   parent inherits at path (B); else a cycle whose name matches an item in **exactly one** plan adopts
   it at path (C); else `product_plan` stays `null`. Keep "never run both" as the governing phrase and
   make it explicit that (C) runs only when (A) and (B) did not.
5. Directly after that paragraph, add **Product-plan adoption (path (C) — this cycle's name is an item
   in exactly one plan).** `(writes: both)` Set `state.json.product_plan` to the `plan-path` held from
   step 2's lookup. State the three cases that do **not** write: no match (`product_plan` stays
   `null`), a §L2 collision (stays `null` — the lookup already returned no plan), and paths (A)/(B)
   having already run. State that this write rides the initial state.json commit at the end of Step 6,
   like path (B)'s, and creates no new commit.
6. Add one sentence to path (C) naming its consumer, so a later reader can see why it exists:
   `dev:done` Step 3 reads this value to check the item's box and bump the plan's cycles-completed
   count, and skips the whole step when it is `null` (`done/SKILL.md:135`, verified).

### Task 3: Add the check to `dev:fix` as Step 2b
What: Make `/dev:fix` run the same plan-order check on its resolved cycle name, after the adapter
resolves and before grounding, so a fast-path cycle that is really a plan item is caught before any
branch exists.
Used by: every `/dev:fix` invocation in lane mode.
Depends on: Task 1 (cites §L1–§L5 by anchor). Independent of Task 2 — the two call sites share no
file and may be built in either order.
Files: modify `plugins/dev/skills/fix/SKILL.md`
Interfaces:
- Consumes: Task 1's `§L1`–`§L5` anchors in `plugins/dev/references/product-plans.md`, and §L1's
  output fields `plan-path`, `item-name`, `item-checked`, `item-milestone`.
- Produces: nothing — terminal task. The lane writes no `state.json`, so this site records no plan
  linkage; its whole effect is the printed outcome and the optional `switch` stop.
- State keys: introduces no new `state.json` key. `dev:fix` writes no `state.json` at all.
- Shared procedure: *plan-order check* — **call site**, not an implementation. Task 1 is canonical.
  This site's divergences from the contract, stated in full at the site: (i) the checked name is
  resolved per dispatch — `<item>` on the `backlog` dispatch, the normalized issue title on the
  `linear` dispatch (the same `<short-title>` value Task 2's Linear path resolves), and the
  normalized raw argument on free text; (ii) it runs after Step 2a and
  before Step 3, so `switch` unwinds nothing; (iii) the lane has no autopilot mode, so §L5's asking
  arm always applies here.

Implementation steps:
1. In **Step 1: Parse the argument**, add `../../references/product-plans.md` to the **Reads** list,
   noting it is read on every dispatch (unlike `docs/dev/config.json` directly below it, which is
   `linear`-only).
2. Insert a new **Step 2b: Plan-order check** between Step 2a and Step 3. Open it by stating the
   placement rule the lane already relies on: it runs after Step 2a's resolve and before Step 3's
   grounding, so everything it can do happens **before Step 5 creates any branch** — the same ordering
   Step 2a states for adapter failures, for the same reason.
3. State that **every dispatch reaches this step**, including free text — Step 2a's "free-text
   dispatch skips this step entirely" applies to Step 2a alone and must not be read forward.
4. Give the name resolution per dispatch, as a three-row table: `backlog` → the normalized `<item>`
   basename bound in Step 2a; `linear` → the issue title normalized by `dev:spec` Step 6's
   construction (lowercase, collapse runs outside `[a-z0-9]` to a single `-`, strip leading/trailing
   `-`) — **the same `<short-title>` value Task 2 checks after stripping the `<ID>-` prefix from
   §A6's slug, so both Linear entry points resolve one name**; free text → the raw argument put
   through that same normalization. Add the one-line reason
   free text is safe to check: normalization of a sentence yields a long hyphenated string that
   matches no plan item, so §L4 returns `unlinked` and prints nothing — which is the spec's
   free-text edge case.
5. State that the resolved name is then passed to §L1 and the outcome applied per §L4, with §L5's
   asking arm — the lane has no autopilot mode. Do not restate §L4's four outcomes here.
6. State what `switch` does in this lane: stop with nothing created, printing §L4's
   `/dev:spec "<next-item-name>"` line. Name the two Step 2a side effects that may already have fired
   on the `linear` dispatch and must be mentioned in that stop rather than silently left: the issue's
   `started` status was set by §A3's Pre-lane hook, and the `config.json` status cache write is still
   deferred (Step 5 performs it, so it never happened). Tell the user the issue was moved to
   `started` so they can move it back if they meant to switch.
7. Close the step with the seam's invariant, in the shape §A1 requires: this check is not an adapter
   hook and alters no adapter behaviour — it changes neither triage, nor the escalation threshold, nor
   PR flow.

### Task 4: Record the autopilot suppression in `dev:autopilot` Step 2
What: Add the plan-order check to `dev:autopilot`'s list of standard-mode behaviours autopilot
overrides, so the suppression is documented where autopilot's overrides are read.
Used by: anyone reading `dev:autopilot` Step 2 to learn what autopilot changes; the Validate reviewer
checking that a behaviour change was recorded everywhere it is documented.
Depends on: Task 1 (uses §L4's outcome names and §L5's rule).
Files: modify `plugins/dev/skills/autopilot/SKILL.md`
Interfaces:
- Consumes: Task 1's `§L4` outcome names (`mismatch`, `already-done`) and `§L5`'s print-and-proceed
  rule.
- Produces: nothing — terminal task.
- State keys: introduces no new `state.json` key.
- Shared procedure: none — this task documents a behaviour defined elsewhere and implements no
  procedure of its own.

Implementation steps:
1. In **Step 2: Autopilot Behavioral Rules**, immediately after the existing **Debt surfacing: print,
   never ask.** bullet (`autopilot/SKILL.md:135`, verified as the adjacent rule of the same class),
   add a bullet **Plan-order check: print, never ask.** Say that `dev:spec` Step 6's plan-order check
   (`../../references/product-plans.md` §L4 — the same depth Tasks 2 and 3 use; `autopilot/SKILL.md`
   carries no existing `references/` citation to pattern-match against, so state the path explicitly) asks for confirmation in standard mode on its `mismatch` and
   `already-done` outcomes; in autopilot it prints the outcome into the run log and continues.
2. State explicitly that this is **not** a stop condition, and do not add it to the `## Purpose`
   "When autopilot stops" list — the check never refuses in any mode, so there is nothing to add
   there.
3. State that the `unlinked` and `on-order` outcomes are unchanged in autopilot — one prints nothing,
   the other prints one line, neither asks in either mode — so the override is scoped to the two
   asking outcomes only.
4. State that path (C)'s `product_plan` write is **not** suppressed: it is a mode-agnostic write in
   the initial state.json commit, exactly like path (B)'s, so an autopilot cycle links to its plan and
   reaches `dev:done` Step 3 with the box ready to tick.

### Task 5: Name path (C) in `dev:done` Step 3's plan-locate paragraph
What: Update Step 3's "Locate the plan (uniform)" paragraph so its account of who sets `product_plan`
includes path (C), keeping the reason the step's single read is sufficient accurate.
Used by: anyone reading `dev:done` Step 3 to understand when the check-off runs.
Depends on: Task 2 (path (C) must exist before it is named as a writer).
Files: modify `plugins/dev/skills/done/SKILL.md`
Interfaces:
- Consumes: Task 2's path (C) — the `product_plan` value it writes, in the same
  `docs/dev/product-plans/<slug>.md` shape paths (A) and (B) write.
- Produces: nothing — terminal task.
- State keys: introduces no new `state.json` key. Step 3 is a **reader** of `product_plan`.
- Shared procedure: none.

Implementation steps:
1. In **Step 3: Update Product Plan + ephemeral deletion**, edit the "**Locate the plan (uniform).**"
   paragraph. It currently justifies the single read by naming two writers — product-scale cycles
   (path (A)) and nested children inheriting (path (B)). Add the third: a cycle whose feature name
   matched exactly one plan item adopts that plan at `dev:spec` Step 6 path (C). Keep the existing
   "no `parentFeature`-based path reconstruction" sentence and the null-skip rule exactly as written.
2. Leave the null-skip behaviour itself **unchanged**: `product_plan` null still skips the step
   entirely. That branch is still correct and still reachable — a standalone cycle, a §L2 collision,
   and a plan not present in the primary checkout all reach `dev:done` with `null`.
3. Add one sentence to step **1. Check off this cycle's item** noting that its "match by feature name"
   is the same match §L1 performed at Spec, so a cycle linked by path (C) is guaranteed to find its
   line item. Do not change the matching procedure.

### Task 6: Buffer the close-intent for the adopted backlog item
What: Write this cycle's `debt-pending.md` buffer with a `## To Close` close-intent for
`debt-plan-item-cycles-never-set-product-plan`, the item the spec adopts and requires be disposed of
explicitly.
Used by: `dev:done` Step 6a, the only in-cycle flusher — it executes each `## To Close` close-intent
against `docs/backlog/`, and Step 7 then deletes the buffer.
Depends on: nothing — independent of Tasks 1–5. (The *reason* the item can close is Task 2's path (C);
the buffer write itself depends on no other task's output.)
Files: create `docs/dev/plan-linkage/debt-pending.md`
Interfaces:
- Consumes: nothing. (`../../references/tech-debt.md` §P4 supplies the buffer template; it is an
  existing contract, not a Task 1 product.)
- Produces: nothing — terminal task. Its effect is realized by `dev:done` Step 6a, outside this plan.
- State keys: introduces no new `state.json` key.
- Shared procedure: none.

Implementation steps:
1. Create `docs/dev/plan-linkage/debt-pending.md` from `../../references/tech-debt.md` §P4's template,
   writing **both** sections — §P4 requires both to be present, and both may be empty.
2. Leave `## To Record` empty. This cycle defers nothing new at plan time; Build, Validate, PR and
   Reflect append their own items here if they find any.
3. Under `## To Close`, write the single §P4-form bullet:
   `- debt-plan-item-cycles-never-set-product-plan — path (C) sets product_plan automatically, so dev:done Step 3's check-off no longer depends on the operator remembering`
4. Verify before committing that `docs/backlog/debt-plan-item-cycles-never-set-product-plan.md` exists
   and its front-matter `status` is `open` — a close-intent naming a missing or already-closed item is
   what `dev:done` Step 8 reports as `(couldn't find: …)`. (Verified at plan time: the file exists in
   `docs/backlog/`.)
5. Do **not** mark the item `promoted` or add a `promoted_to` back-link. The governing plan's
   `## Notes` records that decision for all five of its source items, and its second source is
   explicitly "disposed of, not deferred" — closed by this cycle through the ordinary buffer, which is
   what this task does.

## Edge Cases

| Edge case | Handled in | Approach |
|-----------|-----------|----------|
| Name matches items in two plans | Task 1 (§L2) | Return no plan, print both matches, proceed unlinked; `product_plan` stays `null` |
| Plan item named differently from the cycle | Task 1 (§L1) | Exact match on the item name as written; no match → `unlinked` → behaves exactly as a standalone cycle does today |
| Several unchecked items in the same milestone | Task 1 (§L3, §L4) | "Next" is the first `- [ ]` in file order; any unchecked item in that item's milestone is `on-order`, not a mismatch |
| `dev:fix` invoked with free text | Task 3 step 4 | The raw argument is normalized and looked up; a normalized sentence matches no item → `unlinked` → prints nothing |
| Plan file present but malformed (no checkbox items) | Task 1 (§L1, §L3) | No items parsed → no match → `unlinked`, prints nothing, never errors |
| Plan with every box already ticked | Task 1 (§L3, §L4) | No next unchecked item → `unlinked`, prints nothing |
| Entry-adapter forms (`fix linear`, `fix backlog`, `spec linear`) | Task 3 step 4, Task 2 step 3 | The checked name is the resolved cycle slug — `<item>`, the normalized issue title, or `dev:spec`'s §A6 slug — never the raw argument |
| Name matches an item already checked off | Task 1 (§L4 `already-done`) | Prints its own wording naming the completed item, asks, never refuses |
| No live plan at all / no `product-plans/` directory | Task 1 (§L1) | Returns no plan; not an error; prints nothing |
| Autopilot reaches an asking outcome | Task 1 (§L5), Task 4 | Prints the outcome and proceeds; never asks, never stops |
| Plan merged to `origin/main` but not pulled into the primary checkout | Task 1 (§L1), plan preamble | Lookup reads `$PRIMARY` and finds nothing → `unlinked` → today's behavior exactly; `dev:done` Step 7's fast-forward makes this rare |
| A Linear-sourced cycle name (`<ID>-<short-title>`) | Task 1 (§L1), Tasks 2/3 | Both entry points pass the ID-stripped `<short-title>`, so they resolve one name and produce the same outcome |
| The adopted backlog item must be disposed of explicitly | Task 6 | `## To Close` close-intent in the buffer; `dev:done` Step 6a executes it |
| `switch` answered on `dev:fix linear` after the Pre-lane hook fired | Task 3 step 6 | Stop with nothing created, and say the issue was already moved to `started` so the user can move it back |

## Out of Scope

- Keying the cycle worktree on the governing plan — Milestone 4b (`plan-scoped-worktree`).
- A `## Current Project` section in CLAUDE.md.
- A passive plan line at mid-cycle stages (shape, plan, build, validate, pr).
- Seeding a new worktree's ignored dependency directories from the primary checkout.
- Forcing every cycle to belong to a plan.
- Any change to `dev:done` Step 3's check-off mechanics, completion detection, or Step 3b deletion —
  Task 5 edits that step's prose only.
- The Component Registry entry for the new reference file — `dev:pr` Step 5a owns that table and
  writes it from the merged diff.
