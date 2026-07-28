# Unified Backlog Store — Format Cutover — Implementation Plan
*Branch: feature/unified-backlog-store · 2026-07-28*

Cycle 1 of the ADR (`docs/decisions/2026-07-28-backlog-debt-model.md`): rewrite the shared
contract for the per-item `docs/backlog/` store and cut over the 7 consuming skills. No routing,
no migration, no capture, no promotion — those are cycles 2–4 (see Out of Scope).

**Sequencing law.** Task 1 rewrites the contract (`references/tech-debt.md`), the single source of
truth every skill links to. Tasks 2–8 update the skills and depend only on Task 1's definitions;
they are mutually independent (each links to the contract, none to another skill) and may run in
any order or in parallel after Task 1. **No task introduces a new `state.json` key** — this cycle
changes file formats and skill prose only — so no task carries a `State keys:` line.

## Files

| File | Action | Purpose |
|------|--------|---------|
| plugins/dev/references/tech-debt.md | Modify | Rewrite the contract for the per-item `docs/backlog/` store — the definitions Tasks 2–8 cite |
| plugins/dev/skills/init/SKILL.md | Modify | Seed `docs/backlog/` tree (with `closed/` + `README.md`) instead of `tech-debt.md`; idempotent re-run |
| plugins/dev/skills/build/SKILL.md | Modify | Append a front-matter'd `type: debt` item to the buffer under the same carrying-cost trigger |
| plugins/dev/skills/validate/SKILL.md | Modify | Step 5a: front-matter'd items to the buffer; the `Source`/severity tag becomes a front-matter field |
| plugins/dev/skills/reflect/SKILL.md | Modify | In-cycle → buffer; standalone → write item file(s) directly into `docs/backlog/` (create dir if absent) |
| plugins/dev/skills/spec/SKILL.md | Modify | Step 7 cross-check scans `docs/backlog/` item front-matter `files:`; fold-in records a close-intent |
| plugins/dev/skills/done/SKILL.md | Modify | Flush writes one file per buffered item + runs recurrence-merge + executes close-intent; creates store on first write |
| plugins/dev/skills/debt/SKILL.md | Modify | Read the directory, rank by front-matter `recurrence:`, close by editing `status:` + moving to `closed/` |

## Tasks

### Task 1: Rewrite the contract — `references/tech-debt.md`
What: Replace the aggregate-file contract with the per-item `docs/backlog/` store contract — the
definitions every skill in Tasks 2–8 links to.
Used by: All 7 consuming skills link here via `../../references/tech-debt.md`; nothing invokes it
directly. **Keep the filename `tech-debt.md`** (the spec says rewrite in place) so the seven
`references/tech-debt.md` links stay valid and Tasks 2–8 touch no reference paths.
Depends on: nothing — first task.
Files: plugins/dev/references/tech-debt.md (modify — substantial rewrite)
Interfaces:
- Consumes: nothing (the ADR is the input, read at plan time; not a code dependency)
- Produces: the named definitions the skills cite by section — **(P1)** the front-matter schema;
  **(P2)** the file-naming/identity rule; **(P3)** the lifecycle states; **(P4)** the redesigned
  buffer format incl. the close-intent section; **(P5)** the active-item corpus glob; **(P6)** the
  retargeted recurrence-merge procedure; **(P7)** the retargeted silent-degrade rule; **(P8)** the
  retargeted recurrence ranking. Later tasks reference these by the P-number below.

Implementation steps:
1. **Where things live** — replace the "tracker file / buffer" prose. The store is the directory
   `docs/backlog/`: active items flat as `docs/backlog/<type>-<slug>.md`; closed items archived to
   `docs/backlog/closed/<type>-<slug>.md`; the one and only file move happens on close (Decision 1).
   The buffer stays `docs/dev/<feature>/debt-pending.md` (per-cycle scratch, redesigned in step 5).
   Keep the "who appends vs. who flushes vs. who reads" role paragraph, retargeted: producing stages
   (`dev:build`, `dev:validate`, `dev:reflect`, `dev:spec`) append to the buffer; `dev:done` is the
   only in-cycle flusher; standalone `dev:reflect` writes item files directly into `docs/backlog/`;
   `dev:debt` owns reads + manual lifecycle.
2. **(P1) Front-matter schema.** Add a section defining the **complete** YAML front-matter block —
   every Decision 3 field, so the on-disk format is forward-stable: `type` (`debt|backlog`), `scope`
   (`repo|plugin`, default `repo`), `status` (`open|in-progress|promoted|closed`), `first_recorded`,
   `cycles` (list), `recurrence` (int), `files` (list, **required** — the field `dev:spec`'s
   cross-check keys on; may be legitimately empty only for a not-yet-built backlog intention),
   `possibly_related_to` (optional slug), `routing` (optional), `promoted_to` (optional), `closed`
   (optional), `closed_by` (optional), and `severity` (optional, `P3|Nit` — informational, written by
   `dev:validate` per Task 4, preserved verbatim by the flush; not a routing/lifecycle field). State the
   invariant `recurrence == len(cycles)`, `cycles`
   authoritative on disagreement. Body follows the front-matter in the current bold-label prose:
   debt uses `**What's wrong:** / **Why deferred:** / **Done looks like:**`; backlog uses
   `**What:** / **Why:** / **Done looks like:**`. **Document the schema fields in full, but only the
   *procedures* this cycle implements** — write NO routing or promotion procedure (Out of Scope):
   `scope`, `routing`, `promoted_to` are documented as reserved schema fields with a one-line
   "handled by a follow-on cycle" note, not as behaviors.
3. **(P2) File naming / identity.** Slug is a stable kebab-case identity fixed at creation. Filename
   `<type>-<slug>.md`, `type ∈ {debt, backlog}`; encodes type, not status (status lives in
   front-matter and, terminally, in `closed/`). Slugs unique within the tree; on collision append the
   first cycle name → `<type>-<slug>-<first-cycle>.md` (reuse the old title-collision instinct). The
   slug is what `possibly_related_to:` points at, so it survives the close move.
4. **(P3) Lifecycle states.** Document `open`, `in-progress`, `closed` as the states this cycle's
   flows use, and the transitions this cycle carries: `open → in-progress → closed`, `open → closed`
   (paid-directly / dropped). `promoted` is documented as a **reserved** state value (backlog-only,
   cycle 4) with no procedure here. `closed` is terminal and is the only state whose entry triggers
   the archival move to `docs/backlog/closed/`.
5. **(P4) Redesigned buffer format.** Replace the old `## To Record` / `## To Close` template. The
   buffer keeps two sections:
   - `## To Record` — holds one entry per deferred item, each as a `### <slug>` heading followed by
     the item's **complete file content** (front-matter + body) inside a fenced ```` ```markdown ````
     block. Storing the item in its final on-disk form means the flush lifts it verbatim (after
     recurrence-merge) with no format translation. Use a **4-backtick** outer fence so a 3-backtick
     fence inside a quoted body cannot close it early; state that rule explicitly. The
     no-`#`-heading-inside-a-value escape survives for body prose (bodies still quote Markdown), and
     the fence is the primary guard.
   - `## To Close` — the close-intent section, one bullet per item this cycle agreed to pay:
     `- <type>-<slug> — <why this cycle pays it>`. **The bullet names the item's filename slug**
     (stable identity, P2), which `dev:done`'s flush resolves directly to `docs/backlog/<type>-<slug>.md`
     — cleaner than the old free-form-title match. Preserve the intent: a malformed buffer is surfaced,
     never half-acted-on; the flush is authoritative about position (acts on the **first** `## To Record`
     and **first** `## To Close`, ignores + reports any later duplicate).
6. **(P5) Active-item corpus.** Define the recurrence-merge / read corpus as the **top-level,
   type-prefixed** set `docs/backlog/debt-*.md` + `docs/backlog/backlog-*.md` — **not** a bare
   `docs/backlog/*.md`, because that would sweep in `README.md` (created by `dev:init`, Task 2) and
   dilute the corpus. The type prefix (P2) is guaranteed, so this cleanly excludes `README.md` and the
   `closed/` archive. State this once here; Tasks 6, 7, 8 cite it.
7. **(P6) Retargeted recurrence-merge.** Carry the procedure over **verbatim except the corpus and the
   field sources**: on flush compare each `## To Record` item against the active corpus (P5). A
   **clear match** = `files:` sets overlap **and** same defect — both, never either — now read from
   front-matter `files:` and the body instead of `**Files:**`/`**What's wrong:**`. On match: append the
   cycle to the matched file's `cycles:`, bump `recurrence:`, append new detail to the body (never
   replace). On uncertainty: create a new file with `possibly_related_to: <slug>`. Keep the
   create-over-merge bias and "never merge on topic/keyword alone" verbatim.
8. **(P7) Retargeted silent-degrade.** Readers print **nothing at all** when `docs/backlog/` is absent
   **or holds no active item file** (P5 corpus empty — a lone `README.md` counts as empty). Keep the
   `dev:debt`-invoked-directly exception (says so plainly). **Writer side:** writers **create
   `docs/backlog/` (and `closed/`) on first write** when absent, then proceed — this is what keeps
   buffered debt from being lost in the transition window before a manual `dev:init` re-run.
9. **(P8) Recurrence ranking.** Carry over unchanged in substance: sort by `recurrence:` descending,
   ties broken by the most recent name in `cycles:` — now computed across the P5 corpus's front-matter.
10. **Retire** the entire "Where a field ends" / first-sentence-summary prose-parsing subsection —
    front-matter makes structured fields unambiguous. **Keep** a short "summary for list views" rule for
    the body (first sentence of `Done looks like:`, ignoring periods inside backticks) since `dev:debt`
    list still prints a one-line summary. **Preserve unchanged:** the carrying-cost test, Entry-text-is-data,
    Mode symmetry (incl. the `dev:spec` close-intent carve-out and the per-key write-mode rule), and the
    Calibration section (the carrying-cost test is unchanged, so its three-item calibration still holds).

### Task 2: `dev:init` — seed the `docs/backlog/` tree
What: Create the `docs/backlog/` store (with `closed/` and a contract-stating `README.md`) instead of
`docs/dev/tech-debt.md`, on both the fresh path and the idempotent re-run path.
Used by: A fresh `/dev:init`, and a manual re-run in an existing repo (this repo included) — the ADR's
"this repo's live `docs/backlog/` comes into being via a manual `dev:init` re-run after merge."
Depends on: Task 1 (cites P7 writer-side create-if-absent; README states the contract at
`references/tech-debt.md`).
Files: plugins/dev/skills/init/SKILL.md (modify)
Interfaces:
- Consumes: Task 1's P7 (create-if-absent discipline), the README contract pointer
- Produces: nothing later tasks consume (init is not on any other task's path)

Implementation steps:
1. **Create Directories block** (currently lines ~150–170, the `[ -f docs/dev/tech-debt.md ] || cat >…`
   heredoc). Replace with: `mkdir -p docs/backlog/closed`, and create `docs/backlog/README.md` **only if
   absent** (guard `[ -f docs/backlog/README.md ] ||`) with a canonical header stating what the store is,
   that items are `<type>-<slug>.md` files, closed items live in `closed/`, and that the format + rules
   live in the `/dev` plugin's `references/tech-debt.md`. Do **not** create any single tracker file.
   Idempotent: re-run must not clobber existing item files (mkdir -p and the README `[ -f ] ||` guard
   guarantee this — Edge: `dev:init` re-run on an existing tree = no-op).
2. **Scenario D — keep path** (lines ~42–52). Replace "check for `docs/dev/tech-debt.md`… create it" with
   "check whether `docs/backlog/` exists; if absent, create the tree as in **Create Directories**." Update
   the exit line: "Config unchanged. Created docs/backlog/ (untracked — review, commit, and push when
   ready). …". Keep the do-not-`git add` rule. Update the explanatory note (this is the automatic path by
   which a pre-store repo gains the store).
3. **Scenario D — migration step 6** (lines ~77–78): change "Ensure `docs/dev/tech-debt.md` exists" to
   "Ensure `docs/backlog/` exists — create the tree (as in **Create Directories**) if absent." Update
   step 7's unstaged list wording (`tech-debt.md` → `docs/backlog/`).
4. **Do-not-commit list** (line ~244): replace `docs/dev/tech-debt.md` with `docs/backlog/` (README +
   tree) in the enumerated unstaged-files list.
5. **Exit Display** (lines ~255, 266): replace `Created: docs/dev/tech-debt.md` with
   `Created: docs/backlog/ (README + closed/)`; update the "Omit the … line if it already existed" note to
   key on the directory's prior existence.

### Task 3: `dev:build` — front-matter'd buffer item
What: When Build defers an improvement that passes the carrying-cost test, append a front-matter'd
`type: debt` item to the buffer's `## To Record` section in the new format.
Used by: `dev:build`'s "improvement larger than this cycle" branch (currently lines ~113–119).
Depends on: Task 1 (P4 buffer format, P1 schema).
Files: plugins/dev/skills/build/SKILL.md (modify)
Interfaces:
- Consumes: Task 1's P4 (buffer `## To Record` entry shape) and P1 (front-matter fields)
- Produces: buffer items in the P4 format — consumed by Task 7's flush (via the contract, not directly)

Implementation steps:
1. In the **Qualifies** bullet, replace "append an entry at the end of the `## To Record` section…" with:
   append a `### <slug>` entry in the P4 buffer format — a fenced ```` ```markdown ```` block holding the
   item's front-matter (`type: debt`, `scope: repo`, `status: open`, `first_recorded:` from
   `date -u +%Y-%m-%d`, `cycles: [<feature>]`, `recurrence: 1`, `files: [<the files the improvement
   touches>]`) plus the `**What's wrong:** / **Why deferred:** / **Done looks like:**` body. Create the
   buffer from the contract's template if absent.
2. Keep the "you know the files precisely; `dev:spec`'s cross-check keys on `files:`" note, retargeted to
   the front-matter `files:` field. Drop the old `*Source: dev:build*` tag line — provenance is now the
   `cycles:` field (the flush no longer strips a `*Source:*` line; see Task 4 for validate's severity tag).
3. Keep and retarget the escape note to the P4 fence rule (4-backtick outer fence; escape `#` headings in
   quoted body text).

### Task 4: `dev:validate` — front-matter'd buffer item + severity as a field
What: Step 5a appends surviving P3/Nit debt to the buffer as front-matter'd items; the old
`*Source: dev:validate (P3|Nit)*` tag becomes a front-matter field.
Used by: `dev:validate` Step 5a (lines ~191–225).
Depends on: Task 1 (P4 buffer format, P1 schema).
Files: plugins/dev/skills/validate/SKILL.md (modify)
Interfaces:
- Consumes: Task 1's P4 and P1
- Produces: buffer items in the P4 format (consumed by Task 7's flush via the contract)

Implementation steps:
1. Step 5a item 2: replace the "append an entry at the end of the `## To Record` section" instruction with
   the P4 buffer format (as Task 3) — front-matter `type: debt`, `status: open`, `first_recorded:` from
   the clock, `cycles: [<feature>]`, `recurrence: 1`, `files: [<paths the finding names>]`, plus the debt
   body. **Carry the fix-loop severity** as a front-matter field: add `severity: P3` or `severity: Nit`
   (the field replacing the old `*Source: dev:validate (P3|Nit)*` tag). State that `severity` is an
   informational field the flush preserves verbatim (it is not one of the routing/lifecycle fields).
2. Retarget the parenthetical about `## To Close` being last/parsed-as-bullets to the P4 structure and the
   4-backtick fence escape rule. Keep the Mode rule (unconditional, self-applied, no state counter) and the
   "buffer receives only what survives the fix loop" note unchanged.
3. Confirm the Step 6 commit block (lines ~236–244) still `git add`s the buffer path unchanged — the buffer
   filename is unchanged, so no edit needed there; note this in the task so Build doesn't touch it.

### Task 5: `dev:reflect` — buffer in-cycle, direct-to-`docs/backlog/` standalone
What: In-cycle deferrals append a front-matter'd item to the buffer; standalone invocation (no buffer)
writes the item **file** directly into `docs/backlog/`.
Used by: `dev:reflect`'s carrying-cost write (line ~163) and its standalone path (line ~167).
Depends on: Task 1 (P4 buffer format, P1 schema, P6 recurrence-merge, P7 writer-side create-if-absent, P2 naming).
Files: plugins/dev/skills/reflect/SKILL.md (modify)
Interfaces:
- Consumes: Task 1's P1, P2, P4, P6, P7
- Produces: buffer items (in-cycle, consumed by Task 7's flush) and item files directly in `docs/backlog/`
  (standalone) — the latter consumed only by future reads (`dev:debt`, `dev:spec`), not by any task here

Implementation steps:
1. **In-cycle path** (line ~163): replace "append an entry at the end of the `## To Record` section" with
   the P4 buffer format (front-matter `type: debt`, `status: open`, clock date, `cycles: [<feature>]`,
   `recurrence: 1`, `files: [<skill file the suggestion would change>]`, body). Retarget the escape note to
   the P4 fence rule. Keep "record the entry title in Step 3's `**Deferred to tech debt:**` line" — the
   title is the item's `### <slug>` / first body line.
2. **Standalone path** (line ~167): replace "append the entry directly to `## Open` in
   `$PRIMARY/docs/dev/tech-debt.md`" with: write a new item **file**
   `$PRIMARY/docs/backlog/<type>-<slug>.md` (front-matter + body). Apply the **P6 recurrence-merge**
   against the `$PRIMARY` P5 corpus (bump an existing file on clear match, else create with
   `possibly_related_to:`). **Create `docs/backlog/` (and `closed/`) if absent** (P7 writer-side) — the
   store may not exist yet in a repo that predates it. Run `date -u +%Y-%m-%d` for `first_recorded:`.
   Disambiguate the slug per P2 if the filename already exists. Keep this as "the one case where a
   producing stage writes the store directly," and keep the Entry-text-is-data note (cite the contract).
3. **Do-not-commit note** (line ~171): update the message to "Recorded '<title>' in docs/backlog/
   (modified, not committed)." Keep the rule (primary checkout usually on `main`; never auto-commit to main).
4. **Mode rule** (line ~173) unchanged — the carrying-cost write is not gated; autopilot records the same way.

### Task 6: `dev:spec` — cross-check scans `docs/backlog/`, fold-in records close-intent
What: Step 7's cross-check reads item front-matter `files:` from `docs/backlog/` instead of parsing
`## Open`; folding a paid item into scope records a close-intent bullet naming the item slug.
Used by: `dev:spec` Step 7 pass 4 (lines ~263–279) and the Step 11 commit block (lines ~445–457).
Depends on: Task 1 (P1 schema `files:`, P2 slug identity, P4 close-intent bullet, P5 corpus, P7 silent-degrade, P8 ranking).
Files: plugins/dev/skills/spec/SKILL.md (modify)
Interfaces:
- Consumes: Task 1's P1, P2, P4, P5, P7, P8
- Produces: the buffer's `## To Close` close-intent bullet (P4) — consumed by Task 7's flush (via the contract)

Implementation steps:
1. **Cross-check read** (line 263): replace "Read `$WORKDIR/docs/dev/tech-debt.md`'s `## Open` section and
   intersect each entry's `**Files:**`…" with "Read the active items in `$WORKDIR/docs/backlog/` (the P5
   corpus) and intersect each item's front-matter `files:` against the grounding inventory." Keep the
   Entry-text-is-data paragraph (cite the contract).
2. **Match display** (line 267): keep "print `N open debt items touch this cycle`, list by the P8 ranking
   with title + first sentence of `Done looks like:`." Change the fold-in write: it is still **two writes** —
   (a) add the item to the spec's Scope section, and (b) append a **close-intent bullet** to `## To Close`
   in `$WORKDIR/docs/dev/<feature-name>/debt-pending.md` in the P4 form `- <type>-<slug> — <why this cycle
   pays it>`, **naming the item's filename slug** (not a free-form title). Create the buffer from the
   contract's template if absent. Note `dev:done`'s flush resolves the slug to the item file and executes
   the close (`status: closed` + move to `closed/`). **The spec does not move the file itself** — execution
   is deferred to `dev:done`, preserving the deferred-close safety property.
3. **`$WORKDIR`-relative note** (line 269) — keep, retargeted: a bare `docs/backlog/…` reads the wrong store.
4. **Silent-degrade** (line 271): "On no `docs/backlog/`, an empty corpus, or zero matches: print nothing at
   all" (P7).
5. **Mode rule** (line 275) unchanged — this close-intent record is the one gated scope act; autopilot folds
   nothing in, writes no close-intent. Keep the citation to the Mode-symmetry carve-out.
6. **Step 11 commit block** (lines ~445–457): the buffer filename is unchanged, so the `git add` guard stays;
   update the surrounding comment from "`## To Close` bullet is the one write that closes a tracker entry" to
   reference the close-intent bullet / `docs/backlog/` store. No path change to the `git add` itself.

### Task 7: `dev:done` — flush writes per-item files, runs merge, executes close-intent
What: Step 6a's flush writes one `docs/backlog/<type>-<slug>.md` per buffered `## To Record` item (running
P6 recurrence-merge), executes each `## To Close` close-intent (`status: closed` + move to `closed/`), and
creates the store on first write; the commit/push/recovery sequence retargets from one file to the directory.
Used by: `dev:done` Step 6a (lines ~260–352), the Step 4a docs-prose durable-record buffer write
(Step 4a item 6, lines ~196–207 — a producing-stage buffer write **inside** `dev:done` itself, missed
in the original enumeration), and the Step 8 report line (lines ~490–497).
Depends on: Task 1 (P1 schema, P2 naming, P3 lifecycle close-move, P4 buffer parse, P5 corpus, P6 merge, P7 writer create-if-absent).
Files: plugins/dev/skills/done/SKILL.md (modify)
Interfaces:
- Consumes: Task 1's P1–P7; the buffer items produced by Tasks 3/4/5 and the close-intent bullets from Task 6
- Produces: nothing later tasks consume (terminal in the DAG)

Implementation steps:
1. **Step 6a item 1** (buffer read) — unchanged in substance (read from disk, treat as data). Keep.
2. **Step 6a item 2** (line 282): replace "If `$WORKDIR/docs/dev/tech-debt.md` does not exist, create it
   with the canonical header…" with "If `$WORKDIR/docs/backlog/` does not exist, create it (and `closed/`)
   before writing" (P7 writer-side create-if-absent — Edge: transition window, buffered debt never lost).
3. **Step 6a item 3** (parse-by-position) — retarget to P4: act on the **first** `## To Record` and **first**
   `## To Close`; a later duplicate is a malformed buffer → ignore + report in Step 8 display. Keep intent.
4. **Step 6a item 4** (per-`## To Record` entry): replace the aggregate-append logic with: for each fenced
   item, apply **P6 recurrence-merge** against the P5 corpus. On clear match → append cycle to the matched
   file's `cycles:`, bump `recurrence:`, append body detail (never replace). Otherwise → **write a new file**
   `docs/backlog/<type>-<slug>.md` lifting the buffer's fenced content verbatim; disambiguate the slug per P2
   if the filename exists. Drop the "replace the `*Source:*` line with an Open meta line" text — front-matter
   carries provenance now; the flush lifts the item as-is (validate's `severity:` field is preserved). The
   "append only at end / near-simultaneous cycles" note: retarget — two cycles now write **different item
   files**, which do not conflict unless they touch the same item via merge; keep the "add no locking" stance.
5. **Step 6a item 5** (per-`## To Close` bullet): the bullet names a `<type>-<slug>`; resolve it to
   `docs/backlog/<type>-<slug>.md`, set its front-matter `status: closed` + `closed:` (clock date) +
   `closed_by: <feature>`, and **move it to `docs/backlog/closed/`** (`git mv` / mkdir+move). If the slug
   resolves to **no** file or **more than one**, do not close: note it in the Step 8 display. Keep "a
   stale-open item is recoverable; a wrongly-closed one disappears."
6. **Step 6a item 6** (empty `## To Close` is normal) — keep, wording retargeted (a later cycle that fixes an
   item incidentally leaves it open until `/dev:debt` closes it).
7. **Step 6a item 7 — commit/push guard** (the bash block, lines ~324–342). Retarget end-to-end:
   - Guard: replace `[ -f "$WORKDIR/docs/dev/tech-debt.md" ]` with `[ -d "$WORKDIR/docs/backlog" ]` (assert
     the flush wrote where expected; else STOP before `git add` so the no-change branch can't destroy the buffer).
   - `git -C "$WORKDIR" add docs/backlog/` (the directory pathspec stages new item files **and** the close
     moves — a `git mv` shows as delete-from-active + add-to-`closed/`, both under `docs/backlog/`).
   - `git -C "$WORKDIR" diff --cached --quiet -- docs/backlog/ || { commit -m "chore: record backlog items
     from <feature>" -- docs/backlog/ && push_integration; } || { STOP; }` — keep the pathspec-on-both-commands
     discipline and the "nothing staged exits non-zero" guard rationale.
   - Keep "do not add the buffer file — Step 7's `git add -A docs/dev/<feature>/` stages its deletion."
8. **Push-conflict recovery** (lines ~344–352): retarget the prose from "conflict inside `## Open` of one
   file" to "conflict inside `docs/backlog/` — now rarer, since two cycles usually write different item files;
   a real conflict means both touched the same item file (via merge)." Keep the recovery discipline verbatim
   (re-read `origin/$INTEGRATION`'s `docs/backlog/`, re-apply this cycle's writes so **both** cycles' items
   survive, push again; STOP if it still fails; buffer is still on disk). Keep the Step 7 mid-rebase guard
   (lines ~356–364) — the buffer is still the only copy; wording change only.
9. **Step 4a durable-record buffer write** (Step 4a item 6, lines ~196–207) — *added during Build: a
   producing-stage buffer write inside `dev:done` that the original enumeration missed.* It must emit the
   **P4** format like Tasks 3/4/5, not the old `###` + `**Files:**` + `*Source:*` shape: a `### <slug>`
   entry whose fenced ```` ```markdown ```` block holds front-matter (`type: debt`, `scope: repo`,
   `status: open`, `first_recorded:` from the clock, `cycles: [<feature>]`, `recurrence: 1`,
   `files: [README.md, CLAUDE.md as affected]`) + the debt body; drop the `*Source:*` line. Retarget the
   following prose paragraph from "turns this into a tracked `## Open` entry / increments `Recurrence:`" to
   P6 against the P5 corpus (merge keys on front-matter `files:` overlap + same defect; a repeat bumps the
   matched file's `recurrence:`). Escape note → P4 fence rule.
10. **Step 8 report line** (lines ~490–497): keep the `Tech debt: N recorded, M closed` line format and the
   anomaly-append discipline (unmatched close, ambiguous, malformed buffer). Optionally reword "Tech debt:"
   → keep as-is for continuity (the store still holds debt items); update the malformed-buffer anomaly text
   to the P4 structure. Do **not** touch the docs-prose or primary-checkout reconciliation lines.

### Task 8: `dev:debt` — read the directory, rank, close-and-move
What: Read `docs/backlog/` item files, rank by front-matter `recurrence:`, and close by editing
`status:` + moving the file to `closed/` — reads/rank/close only (no `add`, no routing; those are cycle 3).
Used by: The user, on demand (`/dev:debt`, `list`, `show`, `closed`, `close`).
Depends on: Task 1 (P1 schema, P2 naming/identity, P5 corpus, P7 silent-degrade exception, P8 ranking, P3 close-move).
Files: plugins/dev/skills/debt/SKILL.md (modify)
Interfaces:
- Consumes: Task 1's P1, P2, P3, P5, P7, P8
- Produces: nothing later tasks consume

Implementation steps:
1. **Front-matter `description`** (line 3) and **Purpose** (line 12): replace "Reads docs/dev/tech-debt.md" /
   "on-demand surface for `docs/dev/tech-debt.md`" with the `docs/backlog/` directory. Keep trigger phrases.
2. **Step 1 (Locate)** (lines ~34–50): the store is `$PRIMARY/docs/backlog/` (the P5 active corpus + `closed/`).
   The say-so-plainly exception fires when `docs/backlog/` is absent **or holds no active item files** (P5
   corpus empty, README-only counts as empty): "No tech debt tracked in this repo yet." Keep the note that this
   is the one place silent-degrade doesn't apply.
3. **Step 3 (List open)** (lines ~61–89): parse the P5 corpus, read front-matter, rank by **P8** (`recurrence:`
   desc, ties by most recent `cycles:` name). Print index, title, `recurrence`, `cycles`, `files`, and the
   first sentence of the body `Done looks like:` (keep the summary rule kept in Task 1 step 10). Update the
   "empty open but closed exists" branch to read the `closed/` archive.
4. **Step 4 (Show)** (lines ~91–95): print one item file verbatim — front-matter + full body incl.
   `possibly_related_to:` — indices are positions in Step 3's ranked list.
5. **Step 5 (List closed)** (lines ~97–107): read `docs/backlog/closed/`, print newest-first by front-matter
   `closed:` date, each showing `closed_by`.
6. **Step 6 (Close)** (lines ~109–158): resolve the item by Step 3 index or slug/title (exact match; on 0 or
   >1, list candidates and ask — never fuzzy-match). Resolve the paying cycle (the two-location scan is
   unchanged). Confirm before writing (echo item + cycle). **Write:** set the file's front-matter
   `status: closed`, `closed:` (`date -u +%Y-%m-%d`), `closed_by: <cycle>`, and **move the file to
   `docs/backlog/closed/`** (P3). Keep the do-not-commit rule + message (update path to `docs/backlog/`).
7. **Invocation** (lines ~160–167): keep the list/show/closed/close verbs; **do not** add `add` or convert
   (Out of Scope — cycle 3).

## Edge Cases
| Edge case | Handled in | Approach |
|-----------|-----------|----------|
| Store absent / empty (fresh repo, or this repo pre-init-rerun) | Task 1 (P7) + Tasks 6, 8 (readers) + Task 7 (writer) | Readers print nothing (P7); `dev:debt` keeps its say-so exception; writers create the store on first write |
| Malformed buffer at flush | Task 1 (P4) + Task 7 (item 3) | Act on first `## To Record`/`## To Close`; ignore + report any later duplicate in the Step 8 display |
| Recurrence-merge uncertainty | Task 1 (P6) + Task 7 (item 4) | Create a new file with `possibly_related_to: <slug>` — never a silent merge; create-over-merge bias preserved |
| Slug collision on write | Task 1 (P2) + Task 7 (item 4), Task 5 (standalone) | Append the first cycle name → `<type>-<slug>-<first-cycle>.md` |
| `dev:init` re-run on an existing `docs/backlog/` | Task 2 (steps 1–2) | `mkdir -p` + `[ -f README ] ||` guards → idempotent no-op; never clobbers item files |
| Transition window (flush with `docs/backlog/` absent) | Task 7 (item 2) + Task 1 (P7) | Flush creates the tree and writes (writer-side degrade) — buffered debt never lost |
| `README.md` diluting the merge corpus | Task 1 (P5) | Corpus is the type-prefixed glob (`debt-*.md`/`backlog-*.md`), which excludes `README.md` and `closed/` |

## Out of Scope
- **`dev:autopilot`** — not a contract consumer, writes no debt, and this cycle adds no new STOP/gate/state
  key its Step 2 documents. No task (ADR-confirmed). Cross-skill-ripple check: nothing else needs an autopilot edit.
- **Cross-repo routing** (`scope: plugin`, `gh issue create`, intake dedup, `routing: pending`, convert verb) —
  Decision 5, cycle 3. Schema fields `scope`/`routing` are *documented* (Task 1 P1) but carry no procedure here.
- **`/dev:debt add` / capture flow** — Decision 6, cycle 3. Task 8 keeps read/rank/close only.
- **Promotion + `promoted` state procedures, product-plan deletion** — Decisions 4/7, cycle 4. `promoted` is a
  documented reserved state value (Task 1 P3), no procedure.
- **Data migration** — moving the 13 existing items and retiring `tech-debt.md` / top-level `product-plan.md`
  (Decision 8), cycle 2. This cycle changes formats and skills only; existing `docs/dev/tech-debt.md` is left
  on disk, unread (transition-window edge).
- **Creating this repo's live `docs/backlog/`** — done by a manual `dev:init` re-run after merge + `/plugin
  update`, not by this cycle's diff.
- **README.md / CLAUDE.md prose reconciliation** — the `references/tech-debt.md` path is unchanged (rewrite in
  place), so the Component Registry path row stays valid; any prose drift is handled by `dev:done` Step 4/4a
  post-merge, not by Build.
- **Folding the 3 open debt items** touching this cycle's files — each concerns a behavior orthogonal to the
  store seams; not paid here (per spec Grounding footer).

## Risks and Unknowns
- **Buffer delimiter robustness** (Task 1 P4): a body quoting a 3-backtick code fence could close the outer
  fence early. Mitigation named in P4: use a **4-backtick outer fence** and keep the `#`-heading escape. If a
  body legitimately contains 4 backticks (rare in skill text), Build widens the fence further — the contract
  states the "outer fence must exceed any inner fence" rule so this stays a documented invariant, not a guess.
- **`git mv` vs. rewrite for the close move** (Tasks 7, 8): the close operation is edit-front-matter **and**
  move-file. Order matters for a clean `git add docs/backlog/`: edit in place, then move (or move then edit) —
  either works since the single directory pathspec captures both the deletion and the addition. Build picks one
  and stays consistent; no cross-file dependency rides on the choice.
- **`docs/backlog/*.md` corpus vs. README** (Task 1 P5): the one genuinely new correctness trap — a naive
  `docs/backlog/*.md` glob sweeps in the README that Task 2 creates. Neutralized by defining the corpus as the
  type-prefixed glob once in P5 and having every reader (Tasks 6, 7, 8) cite it rather than re-deriving a glob.
