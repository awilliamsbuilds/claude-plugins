# Tech Debt Tracking — Implementation Plan
*Branch: feature/tech-debt-tracking · 2026-07-22 · Tier: deep · no-ui (Shape skipped)*

**No test harness.** This repo is prose `SKILL.md` files; there is no runner and Build must
not invent one. TDD's red phase does not apply. Verification is per-task greps plus Task 12's
two sweeps — Build should treat those as the "tests pass" condition in its Step 6 gate.

**No `state.json` keys are added by this cycle.** Nothing here writes a counter, so Success
Criterion 3's mode-symmetry trace has no counter to follow. If Build finds it needs one, that
is a Backtrack Trigger (build Step 4), not a silent addition — and Task 12's trace must then
cover it.

**No `docs/dev/config.json` keys are added.** The tracker path is fixed at
`docs/dev/tech-debt.md`. `dev:validate`'s config-contract check therefore has nothing to
enforce for this diff.

## Files

| File | Action | Purpose |
|------|--------|---------|
| `plugins/dev/references/tech-debt.md` | Create | Single source of truth for the tracker format, buffer format, carrying-cost test, and recurrence-merge procedure |
| `plugins/dev/skills/init/SKILL.md` | Modify | Create `docs/dev/tech-debt.md` at init; backfill it on an already-initialized repo |
| `plugins/dev/skills/validate/SKILL.md` | Modify | Step 4/5 — apply the carrying-cost test to surviving P3/Nits, append to the buffer |
| `plugins/dev/skills/build/SKILL.md` | Modify | Step 3 — route `## Deferred Improvements` to the buffer instead of plan.md |
| `plugins/dev/skills/reflect/SKILL.md` | Modify | Step 6 — give the "record as deferred" branch a real destination |
| `plugins/dev/skills/done/SKILL.md` | Modify | New Step 6a — flush the buffer into the tracker *before* Step 7's `rm -rf` |
| `plugins/dev/skills/debt/SKILL.md` | Create | New `dev:debt` skill — list open, show closed, close by hand |
| `plugins/dev/skills/start/SKILL.md` | Modify | Step 4 — add `dev:debt` to both the FYI list and the hardcoded fallback list |
| `plugins/dev/skills/spec/SKILL.md` | Modify | Step 7 — surface open debt intersecting the grounding inventory |
| `plugins/dev/skills/autopilot/SKILL.md` | Modify | Step 2 — debt surfacing prints, never asks, never folds in |
| `CLAUDE.md` | Modify | Component Registry — add the `dev:debt` row (`dev:start` reads descriptions from here) |
| `docs/dev/tech-debt.md` | Modify | Migrate the two holding-pen entries; delete the preamble; seed three new entries |

## Tasks

### Task 1: Write the shared tech-debt contract

What: Define, in one file, every format and rule the other eleven tasks depend on, so the
tracker's shape lives in exactly one place instead of being restated in six skills.

Used by: Read by `dev:init`, `dev:validate`, `dev:build`, `dev:reflect`, `dev:done`,
`dev:debt`, and `dev:spec` — each links to it rather than restating its content.

Depends on: nothing — first task.

Files: create `plugins/dev/references/tech-debt.md`

Interfaces:
- Consumes: nothing
- Produces:
  - Reference path `plugins/dev/references/tech-debt.md`, cited from any skill as
    `../../references/tech-debt.md` (matches the `plugins/writing/references/` convention
    already used by `writing:email` and `writing:linkedin`)
  - Tracker path constant: `docs/dev/tech-debt.md`
  - Buffer path constant: `docs/dev/<feature>/debt-pending.md`
  - Section headings: tracker `## Open` / `## Closed`; buffer `## To Record` / `## To Close`
  - Entry field labels: `**What's wrong:**`, `**Why deferred:**`, `**Done looks like:**`,
    `**Files:**`, `**Possibly related to:**`
  - Open meta line: `*First recorded: YYYY-MM-DD · Cycles: <a>, <b> · Recurrence: N*`
  - Closed meta line: `*Closed YYYY-MM-DD by cycle <name> · First recorded: YYYY-MM-DD · Recurrence: N*`
  - Four named procedures, cited by name from other tasks: **the carrying-cost test**,
    **the recurrence-merge procedure**, **the silent-degrade rule**, **the recurrence ranking**

Implementation steps:
1. Create `plugins/dev/references/tech-debt.md`. Open with one line stating it is the shared
   contract for `/dev`'s tech-debt tracker and is not itself a skill.
2. Section `## Where things live` — the tracker is `docs/dev/tech-debt.md`, one level above
   the per-cycle directory `dev:done` Step 7 deletes, which is why it survives. The buffer is
   `docs/dev/<feature>/debt-pending.md`, created on first write by whichever stage writes
   first, flushed and destroyed at Done.
3. Section `## The carrying-cost test` — state the test verbatim as the spec words it: *will
   this cost us again — does it make future work harder, is it known-wrong behavior that will
   bite, or is it a pattern rather than an instance?* Yes → record. Then state the negative
   explicitly: a one-off local cleanup, a cosmetic issue, or anything fixed-once-and-forgotten
   → drop it. Add the sentence "Severity is the wrong axis" with both directions spelled out —
   a Nit exposing a systemic convention gap qualifies; a P3 that is a local one-liner does not.
4. Section `## Tracker file format` — give a complete worked example containing `## Open` with
   two entries and `## Closed` with one, using the exact meta lines and field labels in
   Produces. State that `Recurrence: N` equals the number of names in `Cycles:` and that
   `**Files:**` is a comma-separated list of repo-relative paths, present on every entry
   because Task 9's Spec-time matching keys on it.
5. Section `## Buffer file format` — give the complete template a stage copies when creating
   the buffer: an H1 `# Debt Pending — <feature>`, a one-line note that `dev:done` flushes and
   deletes it, then `## To Record` and `## To Close`, both present and both allowed to be
   empty. `## To Record` holds full entries plus a `*Source: <skill> · <cycle>*` line.
   `## To Close` holds one bullet per entry — the exact tracker entry title, an em-dash, and
   why the cycle paid it.
6. Section `## The recurrence-merge procedure` — on flush, compare each `## To Record` entry
   against existing `## Open` entries. A **clear match** means the same underlying problem: the
   `**Files:**` sets overlap *and* the described defect is the same one. On a clear match,
   append the cycle name to `Cycles:`, increment `Recurrence:`, and fold any new detail into
   `**What's wrong:**` **by appending — never by replacing existing text**. When uncertain,
   create a new entry carrying `**Possibly related to:** <exact title>`. State the reason
   plainly: a duplicate is visible and cheap to merge by hand; a wrong merge silently destroys
   an entry. Forbid merging on topic or keyword similarity alone.
7. Section `## The silent-degrade rule` — when `docs/dev/tech-debt.md` is absent, every
   *reader* prints nothing at all: not an empty list, not a warning, not an error. Writers
   create the file (with `## Open` and `## Closed` headings) on first write. The one exception
   is `dev:debt` invoked directly, which says so plainly.
8. Section `## The recurrence ranking` — open entries sort by `Recurrence:` descending, ties
   broken by the most recent name in `Cycles:`.
9. Section `## Mode symmetry` — every rule here is self-applied by the writing stage. Never
   gate a tracker write on user confirmation, and never put one on a standard-mode-only path.
   This plugin has three recorded instances of that exact defect.
10. **Verify the rule against real history before finishing this task** (Success Criterion 4).
    Apply the §3 test as written to the three items actually deferred across this repo's ten
    cycles: the "locality only" Scoring-Template nit → must not qualify; the `TMP`-path naming
    nit → must not qualify; the nested-product-plan-visibility P3 → must qualify. If the wording
    gets any of the three wrong, fix the wording, not the expected result. Record the three
    outcomes as a `## Calibration` section at the end of the file so a future reader can see
    the rule was tested rather than asserted.

---

### Task 2: Create the tracker at init

What: Make `dev:init` produce `docs/dev/tech-debt.md` so a fresh repo is ready to receive its
first entry, and backfill the file into a repo initialized before this shipped.

Used by: Every other tracker touchpoint — this is what guarantees the file exists in a repo
that ran init after this ships.

Depends on: Task 1 (needs the tracker format).

Files: modify `plugins/dev/skills/init/SKILL.md`

Interfaces:
- Consumes: from Task 1 — `docs/dev/tech-debt.md`, the `## Open` / `## Closed` headings, and
  the tracker file format
- Produces: a `docs/dev/tech-debt.md` guaranteed to exist in any repo that has run `dev:init`
  since this shipped

Implementation steps:
1. In the `### Create Directories` block, after the two `touch` lines, add creation of
   `docs/dev/tech-debt.md` — only when absent, so re-running init never clobbers real entries.
   Seed it with the H1, a two-line description of what the file is and who writes it, and both
   `## Open` and `## Closed` headings with nothing under them. Point the reader at
   `../../references/tech-debt.md` for the entry format. Do not use `touch` — an empty file is
   not "ready to receive its first entry" (Success Criterion 7).
2. Add `docs/dev/tech-debt.md` to the `### Commit` block's `git add` list.
3. In **Scenario D — Already initialized**, add a line to the `If keep` branch: before exiting,
   if `docs/dev/tech-debt.md` is absent, create it exactly as in step 1 and mention it in the
   exit line. This is the only automatic path by which a repo initialized before this shipped
   ever gets the file — `dev:init` is auto-triggered only when `config.json` is missing, which
   is false for those repos.
4. Add a `Created: docs/dev/tech-debt.md` line to the `## Exit Display` block.

---

### Task 3: dev:validate appends surviving P3/Nits to the buffer

What: Make the stage that produces the most debt apply the carrying-cost test to what its fix
loop consciously chose not to fix, and write the survivors somewhere that outlives the cycle.

Used by: `dev:done` Step 6a (Task 6) reads what this writes.

Depends on: Task 1.

Files: modify `plugins/dev/skills/validate/SKILL.md`

Interfaces:
- Consumes: from Task 1 — `docs/dev/<feature>/debt-pending.md`, the `## To Record` heading,
  the buffer template, the entry field labels, and the carrying-cost test
- Produces: `## To Record` entries in the buffer, each carrying `*Source: dev:validate (P3|Nit) · <feature>*`

Implementation steps:
1. Add a new **Step 5a: Record Carrying-Cost Debt**, placed after Step 5 (write validation.md)
   and before Step 6 (update state + commit). Put it after validation.md so `p3_open[]` and
   `nits_open[]` are final, and before the commit so the buffer lands in the same commit.
2. Step 5a body: for each item in the final `### P3 Open` and `### Nits Surfaced` lists, apply
   the carrying-cost test from `../../references/tech-debt.md`. Say explicitly that both lists
   are eligible and that classification is by carrying cost, not by P3-vs-Nit.
3. For each qualifying item, append an entry to `$WORKDIR/docs/dev/<feature>/debt-pending.md`
   under `## To Record`, using the field labels from the contract, with `**Files:**` set to the
   paths the finding actually names. Create the buffer from the contract's template first if it
   does not exist.
4. State the mode rule inline: this step is unconditional and self-applied — it runs identically
   in standard and autopilot mode, is never gated on user confirmation, and writes no
   `state.json` counter.
5. Add `docs/dev/<feature>/debt-pending.md` to Step 6's `git add` line, guarded so a cycle that
   recorded nothing does not fail on a missing path.
6. Leave Steps 3 and 4 untouched. The fix loop must keep fixing P3s and Nits inline — the buffer
   receives only what genuinely survives it (spec Out of Scope).

---

### Task 4: dev:build routes deferred improvements to the buffer

What: Stop `## Deferred Improvements` from being written into `plan.md`, which `dev:done`
Step 7 deletes without ever reading it — today this content is lost outright.

Used by: `dev:done` Step 6a (Task 6) reads what this writes.

Depends on: Task 1.

Files: modify `plugins/dev/skills/build/SKILL.md`

Interfaces:
- Consumes: from Task 1 — `docs/dev/<feature>/debt-pending.md`, the `## To Record` heading,
  the buffer template, the entry field labels, and the carrying-cost test
- Produces: `## To Record` entries in the buffer, each carrying `*Source: dev:build · <feature>*`

Implementation steps:
1. In **Step 3: Targeted Adjacent Improvements**, replace the final sentence — "note it in
   plan.md under a `## Deferred Improvements` section" — with: apply the carrying-cost test
   from `../../references/tech-debt.md`; if it qualifies, append an entry under `## To Record`
   in `$WORKDIR/docs/dev/<feature>/debt-pending.md`, creating the buffer from the contract's
   template if absent; if it does not qualify, drop it.
2. Set `**Files:**` on the entry to the files the improvement would touch — Build knows them
   precisely, and Task 9's matching depends on them.
3. Remove the `## Deferred Improvements` name entirely so no future reader looks for it in
   plan.md. Grep `plugins/dev/` for `Deferred Improvements` afterward and confirm zero hits.
4. Keep the first half of Step 3 unchanged: in-scope adjacent fixes are still fixed inline and
   still update plan.md. Only the *deferred* branch changes destination.
5. State the mode rule inline: unconditional, self-applied, identical in both modes, no
   `state.json` counter.
6. Do not add the buffer to a new commit of its own — Build already commits per task; instruct
   it to include the buffer in the commit for the task that produced the finding.

---

### Task 5: dev:reflect's deferred branch gets a real destination

What: Give Step 6's "record the suggestion as deferred in the decision log" an actual
destination — today the Retrospective template in Step 3 has no field for it, so the
instruction names a place that does not exist.

Used by: `dev:done` Step 6a (Task 6) reads what this writes.

Depends on: Task 1.

Files: modify `plugins/dev/skills/reflect/SKILL.md`

Interfaces:
- Consumes: from Task 1 — `docs/dev/<feature>/debt-pending.md`, the `## To Record` heading,
  the buffer template, the entry field labels, and the carrying-cost test
- Produces: `## To Record` entries in the buffer, each carrying `*Source: dev:reflect · <feature>*`

Implementation steps:
1. In **Step 6: Skill Update Gate**, change the "If 'no', record the suggestion as deferred in
   the decision log" sentence to: apply the carrying-cost test from
   `../../references/tech-debt.md`; if it qualifies, append an entry under `## To Record` in
   `$WORKDIR/docs/dev/<feature>/debt-pending.md`, creating the buffer from the contract's
   template if absent. Set `**Files:**` to the skill file the suggestion would have changed.
2. Handle the ordering hazard explicitly, in the skill text: `dev:reflect` runs from
   `dev:done` Step 6, and Task 6's flush is Step 6a — immediately after. So a buffer written
   here is still flushed before Step 7's `rm -rf`. If `dev:reflect` is invoked **standalone**
   after the cycle directory is already gone, the buffer path does not exist; in that case
   append directly to `docs/dev/tech-debt.md`'s `## Open` section instead, applying the
   recurrence-merge procedure. Name both paths — do not leave the standalone case implicit.
   Do **not** add a commit for the buffer here: Step 5's commit has already run by this point,
   and Task 6's flush reads the buffer from disk rather than from git, so an uncommitted buffer
   flushes correctly. Step 7's `git add -A docs/dev/<feature>/` then stages its deletion.
3. Add a `**Deferred to tech debt:**` line to the Retrospective format block in **Step 3**, so
   the log records that the suggestion went somewhere. Value is the entry title, or "none".
4. State the mode rule inline: Step 6's gate is standard-mode-only, but the carrying-cost
   write is not conditional on the user's answer — a "yes" that gets implemented records
   nothing, a "no" records, and autopilot (which skips Step 4's user turn) still reaches
   Step 6's suggestions and records them the same way.

---

### Task 6: dev:done flushes the buffer before deleting the cycle directory

What: Move the cycle's buffered debt into the durable tracker, and close any entry this cycle
paid — the single behavior that makes Success Criterion 1 true.

Used by: The tracker itself. This is the only automatic writer of `docs/dev/tech-debt.md`.

Depends on: Task 1.

Files: modify `plugins/dev/skills/done/SKILL.md`

Interfaces:
- Consumes: from Task 1 — the tracker path and format, `## Open` / `## Closed`, the buffer
  path and its `## To Record` / `## To Close` headings, the recurrence-merge procedure, the
  Open and Closed meta lines. From Tasks 3/4/5 — `## To Record` entries. From Task 9 —
  `## To Close` bullets (which may legitimately not exist yet)
- Produces: the flushed `docs/dev/tech-debt.md` on `$INTEGRATION`, and the guarantee that the
  buffer is consumed before it is deleted

Implementation steps:
1. Insert a new **Step 6a: Flush Tech Debt**, positioned after Step 6 (`dev:reflect`) and
   before Step 7 (Clean Up). This ordering is load-bearing twice over: after Step 6 so
   `dev:reflect`'s own entries are included, before Step 7 so the flush happens ahead of
   `rm -rf "$WORKDIR/docs/dev/<feature>/"`. State both reasons in the step text.
2. If `$WORKDIR/docs/dev/<feature>/debt-pending.md` does not exist, skip the whole step
   silently — most cycles will defer nothing. Read the buffer **from disk, not from git** —
   `dev:reflect` (Task 5) writes to it after its own commit has already run, so the buffer can
   legitimately be uncommitted or dirty at this point.
3. If `$WORKDIR/docs/dev/tech-debt.md` does not exist, create it with the H1 and both
   headings before writing (a repo initialized before this shipped, per Task 2's Scenario D
   note — this is the write-side half of the same edge case).
4. For each `## To Record` entry: apply the recurrence-merge procedure from
   `../../references/tech-debt.md`. New entries append **at the end of the `## Open` section**
   — state that append-only-at-the-end is deliberate, because `/dev` runs cycles in separate
   worktrees and two can finish near-simultaneously; combined with `push_integration`'s
   existing fetch/rebase/retry, an append at the end is the shape that rebases cleanly. Add no
   new locking machinery.
5. For each `## To Close` bullet: locate the named entry in `## Open`, move it verbatim to
   `## Closed`, and rewrite its meta line to the Closed form — stamping today's date and this
   cycle's feature name as the payer. If the named entry is not found, leave a note in the
   Step 8 display rather than failing the stage.
6. Handle the absent-`## To Close` case explicitly: Task 9 (Spec-time surfacing) is the only
   writer of that section and ships second, so until it does, the section will routinely be
   missing or empty. That is not an error — nothing closes automatically. Cross-reference the
   spec's decision that a stale-open entry is recoverable and a wrongly-closed one is not.
7. Commit and push through the existing helper, matching Steps 3–5's shape exactly:
   ```bash
   git -C "$WORKDIR" add docs/dev/tech-debt.md
   git -C "$WORKDIR" commit -m "chore: record tech debt from <feature>"
   push_integration
   ```
   Trace the prerequisites before writing this: `push_integration` is defined at the end of
   Step 2 and `$WORKDIR` is detached at the merged `$INTEGRATION` tip by then, so both hold at
   Step 6a. Do not add the buffer file to this `git add` — it is deleted by Step 7's
   `git add -A docs/dev/<feature>/` in the very next step.
8. Add a `Tech debt: N recorded, M closed` line to the Step 8 display, omitted entirely when
   both are zero.

---

### Task 7: The dev:debt skill

What: The on-demand read surface — list open entries ranked by recurrence, show closed ones,
and close an entry by hand.

Used by: The user, directly, via `/dev:debt`. Also the fallback for the edge case where a
later cycle fixes a debt item incidentally without folding it in.

Depends on: Task 1.

Files: create `plugins/dev/skills/debt/SKILL.md`

Interfaces:
- Consumes: from Task 1 — the tracker path and format, `## Open` / `## Closed`, both meta line
  forms, the recurrence ranking, and the silent-degrade rule's `dev:debt` exception
- Produces: skill name `dev:debt`, and the three sub-commands `list`, `closed`, `close` —
  Task 8 registers this name in two places

Implementation steps:
1. Create `plugins/dev/skills/debt/SKILL.md` with frontmatter `name: dev:debt` and a
   trigger-rich `description` covering: view tech debt, list tech debt, what debt do we have,
   show deferred items, close a debt item, mark debt paid, tech debt tracker. No manifest edit
   is needed — `plugins/dev/.claude-plugin/plugin.json` carries no skills array and skills are
   auto-discovered.
2. Add the **Announce** line and a Purpose stating this skill owns all *reads* and all
   *manual* lifecycle changes; `dev:done` owns automatic closing; producing stages only append.
3. Resolve the tracker location using the canonical block the other stage skills already use
   (`PRIMARY=$(dirname "$(git rev-parse --git-common-dir)")`), reading
   `$PRIMARY/docs/dev/tech-debt.md`. Do not `cd`.
4. `/dev:debt` and `/dev:debt list` — print open entries ranked by the recurrence ranking, each
   as: index, title, `Recurrence: N`, the `Cycles:` list, `**Files:**`, and the one-line
   `**Done looks like:**`. Do not dump `**What's wrong:**` in full; offer `/dev:debt show <n>`
   for that.
5. `/dev:debt closed` — print `## Closed` entries newest-first by close date, each showing the
   paying cycle.
6. `/dev:debt close <n|title>` — move the entry to `## Closed` and rewrite its meta line to the
   Closed form. The paying cycle: use the active cycle's feature name if a `docs/dev/*/state.json`
   with `stage != "done"` exists, otherwise ask. Confirm the entry title back to the user before
   writing — a wrong close is the destructive direction.
7. **Do not commit.** Write the file and tell the user it is modified-but-uncommitted, so they
   can fold it into their next commit. `dev:debt` is invoked outside a cycle, usually with the
   primary checkout on `main`, and this repo's standing convention is never to commit directly
   to `main`. State that reason in the skill so it is not "fixed" later.
8. Absent or empty tracker: say so plainly — "No tech debt tracked in this repo yet." — and
   exit 0. This is the one place the silent-degrade rule does not apply, because the user asked
   directly.
9. Close with an `## Invocation` section listing all four forms, matching `dev:start`'s style.

---

### Task 8: Register dev:debt in the discovery surfaces

What: Make `dev:debt` findable — `dev:start` hardcodes two skill lists, and it reads its
descriptions from `CLAUDE.md`'s Component Registry.

Used by: A user running `/dev:start` to find out what exists.

Depends on: Task 7 (the skill must exist and its purpose line must be settled).

Files: modify `plugins/dev/skills/start/SKILL.md`, `CLAUDE.md`

Interfaces:
- Consumes: from Task 7 — the skill name `dev:debt` and its one-line purpose
- Produces: nothing — terminal task

Implementation steps:
1. In `start/SKILL.md` **Step 4**, add a `- dev:debt` line to the `FYI — other skills` block,
   in the same `— [registry description] — <when to use it>` shape as its neighbours. Keep the
   column alignment of that block intact.
2. In the same step's **fallback** bullet list (the one used when the Component Registry table
   or a row is missing), add `` `dev:debt` — view and close tracked tech debt ``. Both lists are
   hardcoded and both must be updated — this is called out in the spec's Technical Constraints.
3. In `CLAUDE.md`'s `## Component Registry` table, add a row:
   `| \`dev:debt\` | plugins/dev/skills/debt/SKILL.md | On-demand tech debt tracker — list open entries, show closed, close by hand |`
   Place it in `dev:*` alphabetical position (between `dev:build` and `dev:dev`) to match the
   table's existing ordering.
4. Update the registry's `*Last updated by /dev · <date>*` line to today.
5. Grep `plugins/dev/skills/start/SKILL.md` for `dev:debt` and confirm exactly two hits.

---

### Task 9: Spec-time surfacing of intersecting debt

What: Surface open debt at the one moment it is actionable — when `dev:spec`'s grounding sweep
is already reading the files the debt lives in.

Used by: A user at Spec deciding what to fold into the cycle about to start. Its `## To Close`
output is consumed by Task 6's flush.

Depends on: Task 1 and Task 7. Built after `dev:debt` deliberately — the spec sequences the two
surfaces so a long Build still ships something coherent.

Files: modify `plugins/dev/skills/spec/SKILL.md`, `plugins/dev/skills/autopilot/SKILL.md`

Interfaces:
- Consumes: from Task 1 — the tracker path, `## Open`, `**Files:**`, the recurrence ranking,
  the silent-degrade rule, and the buffer's `## To Close` format
- Produces: `## To Close` bullets in `docs/dev/<feature>/debt-pending.md` — the section Task 6
  reads

Implementation steps:
1. In `spec/SKILL.md`, add a fourth pass to **Step 7: Ground the Spec in the Codebase**, after
   the three existing passes: **Cross-check open tech debt.** Read `docs/dev/tech-debt.md`'s
   `## Open` section and intersect each entry's `**Files:**` against the grounding inventory
   just built.
2. On one or more matches, print `N open debt items touch this cycle`, list them by the
   recurrence ranking with title and `**Done looks like:**`, and ask whether to fold any into
   scope. Folding one in means: add it to the spec's Scope section, and append a bullet to
   `## To Close` in `docs/dev/<feature>/debt-pending.md` (creating the buffer from the
   contract's template if absent) naming the exact tracker entry title.
3. Handle the buffer-timing prerequisite explicitly: `docs/dev/<feature>/` and `state.json` are
   created in Step 6, which runs before Step 7 — so the buffer's parent directory exists by the
   time this pass writes. State this in the skill text so a future reordering of Step 6/7 is
   visibly load-bearing.
4. State the degrade behavior inline and precisely: no `docs/dev/tech-debt.md`, an empty
   `## Open`, or zero matches → **print nothing at all**. Not an empty list, not "0 items", not
   a warning (Success Criterion 6).
5. State that matching is best-effort: at Spec there is no plan and no definitive file list,
   only the grounding inventory. A missed match costs nothing — `/dev:debt` remains available.
   Do not widen the match to compensate.
6. State that this pass never blocks the grounding gate. The gate in Step 8 caps confidence on
   unverified **as-is claims**; a surfaced debt item is not an as-is claim and must not cap
   anything.
7. In `autopilot/SKILL.md` **Step 2**, add a rule — **Debt surfacing: print, never ask.** In
   autopilot the Step 7 cross-check prints its matches into the run log and folds nothing in;
   scope changes need a human. This is not a stop condition, so leave the "When autopilot stops"
   list in Step 2's header untouched. Without this rule, a new user-facing question lands on
   autopilot's no-gate path — the exact cross-skill ripple this plugin has been bitten by before.

---

### Task 10: Migrate this repo's holding pen

What: Convert the two hand-written entries in `docs/dev/tech-debt.md` into the new format and
remove the preamble that declares the file temporary.

Used by: The tracker's own first readers — and it is the only proof the format can carry real
content written before the format existed.

Depends on: Task 1.

Files: modify `docs/dev/tech-debt.md`

Interfaces:
- Consumes: from Task 1 — the tracker format, `## Open` / `## Closed`, the Open meta line, and
  the entry field labels
- Produces: a `docs/dev/tech-debt.md` in canonical format holding two open entries — the file
  Task 11 appends to

Implementation steps:
1. Replace the current preamble (the "temporary holding pen" paragraph and the "Add new entries
   at the bottom" line) with the standard header Task 2 seeds into fresh repos, so a migrated
   file and an init-created file are indistinguishable.
2. Add the `## Open` heading, and an empty `## Closed` heading at the end.
3. Convert entry 1, *Autopilot doesn't cross-note the spec grounding gate*, keeping its
   what / why-deferred / done-looks-like content intact (Success Criterion 8). Meta line:
   `*First recorded: 2026-07-21 · Cycles: spec-grounding-and-clock · Recurrence: 1*`.
   `**Files:**` `plugins/dev/skills/autopilot/SKILL.md`. Fold the "Behavior is safe" paragraph
   into `**What's wrong:**` — do not drop it, it is why the item is open rather than urgent.
4. Convert entry 2, *Sweep for gate-path state writes that are dead in autopilot*, the same
   way. Meta line: `*First recorded: 2026-07-21 · Cycles: spec-challenger · Recurrence: 1*`.
   `**Files:**` — the nine `dev:*` skill files it names as the sweep surface. Preserve its
   three-row table and its "Prevention (also deferred)" paragraph inside `**What's wrong:**`
   and `**Done looks like:**` respectively; both carry reasoning that is expensive to
   re-derive.
5. Drop the numeric prefixes (`## 1.`, `## 2.`) from the titles — entry identity is the title
   text, since `dev:debt`'s indices are positional and would drift.
6. Re-read the migrated file against the pre-migration content and confirm no
   what / why-deferred / done-looks-like sentence was lost.

---

### Task 11: Seed the three defects this cycle found

What: Record — not fix — the three defects this cycle's own grounding sweep turned up, as the
tracker's first auto-captured-shape entries.

Used by: A later cycle that finds itself in those files.

Depends on: Task 10 (writes the same file; the format and `## Open` heading must exist first).

Files: modify `docs/dev/tech-debt.md`

Interfaces:
- Consumes: from Task 10 — the migrated file with `## Open` populated and `## Closed` present
- Produces: nothing — terminal task

Implementation steps:
1. Append three entries at the end of `## Open`, each with meta line
   `*First recorded: 2026-07-22 · Cycles: tech-debt-tracking · Recurrence: 1*`.
2. Entry: **Hardcoded repo path in dev:reflect** — `reflect/SKILL.md:166` hardcodes
   `~/Development/claude-plugins` and the `local-plugins` marketplace name. `**Files:**`
   `plugins/dev/skills/reflect/SKILL.md`. `**What's wrong:**` note it is the *only*
   repo-specific string in the entire plugin, found by the negative-space sweep, and that it
   directly violates the portability property this cycle was built around.
   `**Done looks like:**` the source repo is discovered or asked for, with no path or
   marketplace name hardcoded.
3. Entry: **dev:spec's product-plan procedure pushes straight to origin/main** — Step 4's
   procedure mandates a direct push to `origin/main`, conflicting with the standing "never
   commit directly to `main`" convention. `**Files:**` `plugins/dev/skills/spec/SKILL.md`.
4. Entry: **A nested product plan cannot outlive its parent** — a nested plan lives at
   `docs/dev/<parent>/product-plan.md`, inside the parent's cycle directory, so `dev:done`
   Step 7 deletes it when the parent completes. `**Files:**`
   `plugins/dev/skills/spec/SKILL.md`, `plugins/dev/skills/done/SKILL.md`.
   `**Why deferred:**` say plainly that this is the same disease this cycle treats — a durable
   record living inside a directory that gets deleted.
5. Set `**Why deferred:**` on all three to the same substance: found by this cycle's grounding
   sweep, explicitly out of scope per the spec, and best fixed by a later cycle already working
   in those files — which is the behavior this feature exists to enable.
6. Do not touch any of the three files. This task records; it does not repair.

---

### Task 12: Verify portability and mode symmetry across the diff

What: Run the two sweeps Success Criteria 2 and 3 specify by *presence*, and record what they
returned.

Used by: `dev:validate`, which checks the build against the spec's Success Criteria.

Depends on: all of Tasks 1–11.

Files: none — verification only; findings go into the commit message and are carried into
`dev:validate`

Interfaces:
- Consumes: the complete diff produced by Tasks 1–11
- Produces: nothing — terminal task

Implementation steps:
1. **Portability sweep (Success Criterion 2).** Run against the diff, not from memory:
   `git -C "$WORKDIR" diff main...HEAD | grep -niE "claude-plugins|awilliamsbuilds|adam|/Users/|local-plugins|~/Development"`.
   Expected hits are confined to Task 11's entry text, which *quotes* the existing hardcoded
   string as the content of a debt entry, and to `CLAUDE.md`. Any hit in
   `plugins/dev/references/` or in a new/modified skill instruction is a real failure — fix it.
   Record the hit list.
2. **Mode-symmetry trace (Success Criterion 3).** For every tracker write introduced by Tasks
   3, 4, 5, 6, and 9, name the skill and step that performs it and confirm that step is not on
   a standard-mode-only gate path. The expected result: validate Step 5a (unconditional),
   build Step 3 (unconditional), reflect Step 6 (write is not conditional on the gate's
   answer), done Step 6a (unconditional), spec Step 7 pass 4 (prints in both modes; folds in
   only on a human answer, with autopilot's behavior pinned by Task 9 step 7). Record the trace.
3. Confirm no `state.json` key was added by the diff:
   `git -C "$WORKDIR" diff main...HEAD | grep -n "state.json"` — every hit should be an
   existing key or a `git add` line. If Build did add a counter, extend step 2's trace to it.
4. Confirm no `docs/dev/config.json` key was added, so `dev:validate`'s config-contract check
   has nothing to enforce.
5. Grep for the reference-path convention: every skill citing the contract must use
   `../../references/tech-debt.md`, not an absolute or repo-relative path.
   `grep -rn "references/tech-debt.md" plugins/dev/skills/` — all hits must match that form.
6. Commit the findings as `verify: portability and mode-symmetry sweeps for tech-debt-tracking`
   with the recorded lists in the commit body, so `dev:validate` can check them without
   re-running.

## Edge Cases

| Edge case | Handled in | Approach |
|-----------|-----------|----------|
| Two cycles flush at Done near-simultaneously | Task 6 | Append-only at the end of `## Open`; `push_integration`'s existing fetch/rebase/retry absorbs the non-fast-forward. No new machinery |
| Mode asymmetry — a write that is dead in autopilot | Tasks 1, 3, 4, 5, 6, 9; verified in 12 | Every write is self-applied and unconditional; no `state.json` counter is added; Task 12 traces each write to its step |
| Repo initialized before this ships (no tracker file) | Tasks 2, 6, 9 | Init Scenario D backfills on re-invocation; Done's flush creates the file on first write; Spec surfacing no-ops silently |
| Empty or absent tracker at Spec | Task 9 | Prints nothing at all — not an empty list, not a warning |
| Empty or absent tracker in `dev:debt` | Task 7 | Says so plainly and exits 0 — the one exception to the silent-degrade rule, because the user asked directly |
| Spec-time matching is approximate | Task 9 | Best-effort against the grounding inventory's file set; a miss costs nothing and `/dev:debt` remains available. Do not widen the match |
| A cycle fixes a debt item incidentally | Tasks 6, 7 | Never auto-closed — Done closes only what `## To Close` names. Stale-open is recoverable; wrongly-closed is not |
| `dev:reflect` invoked standalone, after the cycle dir is gone | Task 5 | Buffer path is absent; append directly to the tracker's `## Open` using the recurrence-merge procedure |
| A `## To Close` entry title that no longer matches | Task 6 | Report it in the Step 8 display rather than failing the stage |
| Cycle deferred nothing at all | Tasks 3, 6 | Buffer is never created; Step 6a skips silently; the `git add` is guarded against the missing path |

## Out of Scope

- Backfilling the tracker from `docs/decisions/*.md` history — deferred to `debt-backfill`.
- `/dev:debt promote <id>` creating a Linear issue — deferred to `debt-linear-promotion`.
- Fixing the three defects recorded in Task 11. They are recorded, not repaired.
- Changing `dev:validate`'s fix loop. Steps 3 and 4 are untouched; P3s and Nits still get
  fixed inline, and the tracker receives only survivors.
- Changing `dev:done` Step 5's decision-log template. Its "[List any P3/Nits accepted as-is]"
  line stays as-is — the tracker supersedes it in practice, but rewriting the log format is a
  separate concern.
- Archiving completed product-plan milestones.
- Any `state.json` or `config.json` schema change.

## Risks and Unknowns

- **Twelve tasks across ten files, all prose, with no test harness.** The failure mode is
  format drift — Task 6's merge procedure reading a field Task 3 spells differently. Mitigated
  structurally: Task 1 owns every name, and Tasks 2–11 cite it rather than restating it. If
  Build finds itself retyping a format, that is the signal the contract is missing something —
  update Task 1's file, not the local copy.
- **Task 9 modifies `dev:spec` Step 7, which this very cycle's spec depends on.** The change
  ships in the same PR that the spec was written under. No self-reference problem at build
  time (skills load from the plugin cache, and changes take effect only after merge +
  `/plugin update`), but it does mean this cycle cannot dogfood its own Spec surfacing. Accept
  it; the next cycle is the real test.
- **`dev:reflect`'s standalone path (Task 5, step 2) has no natural caller to exercise it.**
  It will be verified by reading, not running. Low cost if wrong — the branch only triggers on
  a standalone invocation after cleanup, and the worst case is one lost suggestion.
- **Recurrence-merge is judgment, not string matching.** The contract deliberately biases
  toward creating duplicates. Investigate after ~5 real cycles: if the tracker fills with
  `Possibly related to:` chains that a human keeps merging by hand, the match rule is too
  conservative and the threshold should tighten. Not tunable in advance without real entries —
  which is precisely the argument the spec makes for deferring `debt-backfill`.
