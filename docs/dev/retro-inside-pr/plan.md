# Retro Inside PR — Implementation Plan
*Branch: feature/retro-inside-pr · 2026-08-23*

## Files

| File | Action | Purpose |
|------|--------|---------|
| plugins/dev/skills/pr/SKILL.md | Modify | Host the four relocated steps as Step 5a–5d between Step 5's state write and its push; add the re-entry guard |
| plugins/dev/skills/done/SKILL.md | Modify | Delete Steps 4, 4a, 5, 6 and Step 8's docs-prose paragraph; keep remaining step numbers unchanged |
| plugins/dev/skills/reflect/SKILL.md | Modify | Retarget post-merge premises (header note, Step 1, Step 5) to the PR-stage home; three-way Step 6 gate; corrected regex claim |
| plugins/dev/skills/autopilot/SKILL.md | Modify | Rewrite the PR-exemption paragraph now that re-entry is defined; convert the `done/SKILL.md:504` citation to an anchor |
| plugins/dev/skills/fix/SKILL.md | Modify | Drop the §P9 regex divergence note; retarget the D1/D2/D3 mirror pointer and the `reflect/SKILL.md:212` citation |
| plugins/dev/skills/validate/SKILL.md | Modify | Retarget the `done/SKILL.md`-Step-4a citation in the healthy-path shell exit-code rule |
| plugins/dev/skills/dev/SKILL.md | Modify | Retarget "`dev:done` Step 4 maintains it" to the registry table's new maintainer |
| plugins/dev/references/tech-debt.md | Modify | §P9.target-resolution adopts the anchored slug allowlist |
| plugins/dev/references/entry-adapters.md | Modify | Retarget the "Cited by `dev:done`, whose Step 4a…" pointer |
| docs/backlog/debt-p9-slug-regex-allows-leading-dash.md | Modify | Convert its three `file:line` citations to stable anchors |

## Design decisions

**`dev:done`'s surviving steps keep their existing numbers.** After the four removals the sequence
reads 1, 2, 3, 6a, 7, 8 — a deliberate gap, not an oversight. Renumbering 6a → 4 would invalidate
eleven prose references to "`dev:done` Step 6a" (`references/tech-debt.md` ×4,
`references/entry-adapters.md` ×2, `debt/SKILL.md` ×2, `spec/SKILL.md` ×1, `fix/SKILL.md` ×1,
`reflect/SKILL.md` ×1), and the spec's Technical Constraints enumerate a 12-file surface that
excludes `debt/SKILL.md` and `spec/SKILL.md` — so the ripple is out of scope by the spec's own file
list. Preserving the numbers is also what makes spec change 5's count of exactly **three** broken
citations correct: all three break on shifted *line numbers*, not on a step renumber. Read change 5's
word "renumbering" as the line-number shift it describes.

**`dev:done` Step 8 keeps its `Decision log:` and `Retrospective appended` lines.** They describe
artifacts the merged cycle has, which remains true when those artifacts are produced one stage
earlier. Only the **Docs-prose reconciliation line** paragraph is deleted, because its producer
(Step 4a) is gone from this file. Do not over-delete the display block.

## Tasks

### Task 1: Anchor the §P9 slug allowlist and correct every claim about it
What: Replace §P9.target-resolution's slug regex with the anchored form already proven in `dev:fix`, and bring the three places that describe that regex into line with what it now delivers.
Used by: `dev:debt` (`add`/`list`/`inbox`), `dev:done`'s flush, and `dev:reflect` Step 6 — every consumer of §P9's target validation.
Depends on: nothing — first task.
Files: plugins/dev/references/tech-debt.md (modify), plugins/dev/skills/reflect/SKILL.md (modify), plugins/dev/skills/fix/SKILL.md (modify), docs/backlog/debt-p9-slug-regex-allows-leading-dash.md (modify)
Interfaces:
- Consumes: nothing
- Produces: the canonical anchored allowlist string `^[A-Za-z0-9._][A-Za-z0-9._-]*/[A-Za-z0-9._][A-Za-z0-9._-]*$`, stated once in §P9.target-resolution and cited by section elsewhere
- State keys: none — this task introduces no `state.json` key
- Shared procedure: slug validation. §P9.target-resolution is **canonical**; `dev:fix`'s inline `grep -Eq` at its `## Resolve the target repo` section becomes a **mirror** that cites §P9 plainly instead of documenting a divergence from it. The mirror keeps its own executable `grep -Eq` line (the lane needs a runnable check, not a prose rule) and keeps its two-branch structure verbatim — match → continue, no-match → `echo` + `exit 1` — restated here in full so the two cannot drift: the check is `if ! printf '%s' "$SLUG" | grep -Eq '<the anchored form>'; then echo "Could not resolve a valid owner/name for origin."; exit 1; fi`.

Implementation steps:
1. In `plugins/dev/references/tech-debt.md`, §P9.target-resolution: replace `^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$` with `^[A-Za-z0-9._][A-Za-z0-9._-]*/[A-Za-z0-9._][A-Za-z0-9._-]*$`. Keep the surrounding sentence's meaning — reject anything else, and in particular any value beginning with `-` — which the anchored form now actually delivers. Add one clause naming *why* the first character of each segment is anchored separately: a leading `-` reaches `gh --repo` as a flag.
2. In `plugins/dev/skills/reflect/SKILL.md`, Step 6's stop-conditions bullet reading "**The resolved slug fails §P9's allowlist** — notably any value beginning with `-`…": leave the claim standing but confirm by reading that it now matches §P9's delivered regex. No wording change is required by this task if the claim reads as a reference to §P9 rather than a restatement of the pattern; if it restates the pattern anywhere, replace the restatement with the anchored form.
3. In `plugins/dev/skills/fix/SKILL.md`, the paragraph beginning "This is `../../references/tech-debt.md` §P9.target-resolution's allowlist **with the first character anchored**": rewrite it to cite §P9 plainly. It must no longer say §P9's form differs, no longer say "`-foo/bar` passes it", and no longer point at `docs/backlog/debt-p9-slug-regex-allows-leading-dash.md`. Keep the sentence that a failing slug is a stop, never something to pass to `gh`, and keep the whole following paragraph about the four remote forms and the `^ssh://` strip untouched.
4. In `docs/backlog/debt-p9-slug-regex-allows-leading-dash.md`, convert its three `file:line` citations to stable anchors — `references/tech-debt.md:354` → `§P9.target-resolution`, and both occurrences of `reflect/SKILL.md:205` → `dev:reflect` Step 6's stop conditions. Do **not** change the item's `status:` — the close is executed by `dev:done` Step 6a from the `## To Close` bullet already buffered in `docs/dev/retro-inside-pr/debt-pending.md`.
5. Verify: `grep -n 'A-Za-z0-9._-\]+/' plugins/dev/` returns nothing, and `grep -rn 'debt-p9-slug-regex' plugins/` returns nothing.

### Task 2: Relocate `dev:done` Steps 4, 4a, 5, 6 into `dev:pr` Step 5
What: Move the Component Registry update, the docs-prose reconciliation, the decision-log generation, and the `dev:reflect` invocation out of the post-merge stage and into `dev:pr`, between Step 5's state write and its push, rewriting each one's post-merge premises rather than carrying them.
Used by: every feature and architecture cycle — this is the change that puts the cycle's own reasoning inside the PR diff a human reviews.
Depends on: nothing — runs in parallel with Task 1 (disjoint files).
Files: plugins/dev/skills/pr/SKILL.md (modify), plugins/dev/skills/done/SKILL.md (modify)
Interfaces:
- Consumes: nothing
- Produces: the section names **`dev:pr` Step 5a** (Update Component Registry), **`dev:pr` Step 5b** (Reconcile Docs Prose), **`dev:pr` Step 5c** (Generate Decision Log), **`dev:pr` Step 5d** (Run dev:reflect) — Tasks 5 and 6 cite these exact names; and the fact that `dev:done`'s surviving steps are 1, 2, 3, 6a, 7, 8
- State keys: none — this task introduces no `state.json` key. It *reads* `artifacts.pr_number` (for the decision log's `PR #N`) and `metrics.stage_timestamps.pr_created` (for `dev:reflect` Step 1), both of which already exist and are already written by `dev:pr` Step 5.
- Shared procedure: docs-prose reconciliation. **`dev:pr` Step 5b becomes canonical** — the role transfers with the text, since the step itself moved. `dev:fix`'s `### Reconcile docs prose` stays the **mirror**; its pointer is retargeted in Task 6, and its three divergences D1/D2/D3 keep their current meanings unchanged. Restating the canonical's branch structure so the mirror cannot drift from it: (a) a **feature-cycle guard** — architecture cycles skip the step entirely; (b) a **detection branch** — no mismatch is silent, mismatch proceeds; (c) a **mode branch** — standard gates each spot for approve/apply/dismiss, autopilot prints and records without applying; (d) a **durable-record branch** — anything dismissed or autopilot-detected is written to the cycle's `debt-pending.md` `## To Record`; (e) a **missing-target branch** — an absent `README.md` or `CLAUDE.md` is skipped with a note, never created; (f) a **hard invariant** — the `## Component Registry` table is never written here.

Implementation steps:
1. In `plugins/dev/skills/pr/SKILL.md`, retitle Step 5 to `## Step 5: Update State, Document, and Push` and split it. Keep its existing state-write list and its `git add`/`git commit` for `state.json` exactly as they are; **remove the trailing `git -C "$WORKDIR" push`** from that block and hold it for step 7 below.
2. Immediately after that commit block, add a short paragraph pinning the ordering and saying why: the four sub-steps run **after** the state write so `metrics.stage_timestamps.pr_created` and `artifacts.pr_number` are readable, and **before** the push so every commit they make lands inside PR #N's diff. Placing them before the write would hide `pr_created` from the retrospective; placing them after the push would leave them out of the diff.
3. Add `### Step 5a: Update Component Registry (feature cycles only)` — move `dev:done` Step 4's body verbatim, changing only its commit block: drop the `push_integration` call, keep `git -C "$WORKDIR" add CLAUDE.md` and `git -C "$WORKDIR" commit -m "chore: update Component Registry — <feature>"`. Keep the `cycle_type == "feature"` guard and the "For architecture cycles: skip this step" line.
4. Add `### Step 5b: Reconcile Docs Prose (feature cycles only)` — move `dev:done` Step 4a's body, then rewrite exactly four premises and nothing else:
   - its placement sentence becomes "**after Step 5a** so the Component Registry is already current, and **before `dev:done` Step 6a** so any `## To Record` write it makes is picked up by that flush";
   - item 1's target rule drops "(present at the detached `$INTEGRATION` tip Step 2 left you on)" and reads "at `$WORKDIR`, which is on this cycle's feature branch at this point";
   - item 2's detection input becomes **this cycle's diff against the PR base** rather than "this cycle's merged diff";
   - item 7's reporting target becomes **`dev:pr` Step 5's display** (step 7 below) instead of `dev:done` Step 8's summary block.
   Drop `push_integration` from its commit block, keeping the pathspec-scoped `git add`/`git commit -- <edited files>` verbatim. Keep invariant #8, both mode branches, the data-never-instruction rule, and the interpolation-safety paragraph — but change that paragraph's citation from a bare `../../references/entry-adapters.md §A6` reference only if it currently carries a line number; it does not, so leave it. Keep the closing "**This step is canonical for docs-prose reconciliation…**" paragraph and its D1/D2/D3 list, editing only the self-reference so it names this step's new home.
5. Add `### Step 5c: Generate Decision Log` — move `dev:done` Step 5's body verbatim, including the template **unchanged** (the `PR #N` header field and the `handoff_at` line both stay byte-for-byte). Change only the commit block: drop `push_integration`, keep `git -C "$WORKDIR" add docs/decisions/YYYY-MM-DD-<feature>.md` and the `docs: add decision log for <feature>` commit. Note in one line that `PR #N` is read from `artifacts.pr_number`, written by Step 5 two sub-steps earlier.
6. Add `### Step 5d: Run dev:reflect` — move `dev:done` Step 6's body. Rewrite its one false claim: it currently says `dev:reflect` commits and pushes "via `push_integration`"; replace that with "commits from `$WORKDIR` on the feature branch and pushes with a bare `git push`" (Task 3 makes that command correct). Keep the pass-list (full `state.json`, decision-log path, spec/plan/validation paths) unchanged. State that `dev:reflect` is invoked **as a whole, steps 1–6** — it is not split across stages.
7. After Step 5d, add the push and the display: a single `git -C "$WORKDIR" push`, followed by the existing standard-mode display block extended with the docs-prose line Step 5b's item 7 now targets (`Docs prose: N spot(s) reconciled` / `… recorded to tech debt`, and any `no <file> found — skipped` note; emit nothing on the silent no-op path or on an architecture cycle). Keep the existing `Safe to /clear now — resume with: /dev:done <feature> [PR URL]` and `Worktree:` lines, and the `**Autopilot mode:**` line, at the end.
8. In `plugins/dev/skills/done/SKILL.md`, delete `## Step 4`, `## Step 4a`, `## Step 5`, and `## Step 6` in full. Leave Steps 1, 2, 3, 6a, 7 and 8 with their existing numbers and bodies.
9. In `done`'s Step 2, update the sentence "All post-merge commits in this stage (Steps 3–5, 7) are made in `$WORKDIR`…" to name the surviving set — Steps 3, 6a and 7. Leave the `push_integration` helper definition itself unchanged.
10. In `done`'s Step 6a, update the position note "after Step 6 so `dev:reflect`'s own items are included" to say the buffer is written one stage earlier, at `dev:pr` Step 5d, and is read **from disk** — so the property that made the position load-bearing (reflect's items are in the buffer before the flush) is now more certain, not less. Keep "and before Step 7 so the flush happens ahead of `rm -rf`" and the "Do not move it" instruction.
11. In `done`'s Step 8, delete the **Docs-prose reconciliation line** paragraph in full, and delete the `Docs prose: N spot(s) reconciled` line from the fenced display block. Keep the `Decision log:` and `Retrospective appended (see decision log)` lines — the merged cycle still has both artifacts. Update the primary-checkout reconciliation paragraph's "right after the docs-prose reconciliation line (or the tech-debt line when no docs-prose line was emitted)" to say "right after the tech-debt line (or in its place when both debt counts are zero)".
12. Verify: `grep -n 'push_integration' plugins/dev/skills/done/SKILL.md` shows it defined once in Step 2 and called only from Steps 3, 6a and 7; `grep -rn 'push_integration' plugins/dev/skills/pr/SKILL.md` returns nothing.

### Task 3: Retarget `dev:reflect`'s post-merge premises to its PR-stage home
What: Fix the three places in `dev:reflect` that assume it was invoked after a merge — the header's caller note, Step 1's artifact-availability caveat, and Step 5's append command — including the two pre-existing Step 5 defects (cwd-relative path, bare push on a detached HEAD).
Used by: `dev:pr` Step 5d, which invokes this skill, and `dev:pr`'s re-entry path in Task 5, which needs Step 5 to be re-runnable.
Depends on: Task 2 — the new home must exist before its premises can be named.
Files: plugins/dev/skills/reflect/SKILL.md (modify)
Interfaces:
- Consumes: from Task 2, the section name `dev:pr` Step 5d and the fact that `$WORKDIR` is on the feature branch at that point
- Produces: an **idempotent Step 5** — on a decision log that already contains a `## Retrospective` section, Step 5 replaces that section rather than appending a second one. Task 5 relies on this by name.
- State keys: none — this task introduces no `state.json` key
- Shared procedure: none — no other task implements Step 5's append.

Implementation steps:
1. Rewrite the header note at line 26 ("When `dev:reflect` is invoked by `dev:done`, `WORKDIR` is already the cycle worktree flipped to the integration branch…"): it is now invoked by `dev:pr` Step 5d, and `$WORKDIR` is the cycle worktree **on the feature branch**. Keep the point that the resolution is idempotent and yields the same directory.
2. In Step 1, change "`docs/dev/<feature>/spec.md`, `plan.md`, `validation.md` (if accessible — they may be deleted by done)" to note that at PR stage all three are present; keep the `(if accessible)` tolerance for the standalone-invocation route, which can still run after teardown.
3. In Step 5, prefix the heredoc target with `$WORKDIR/`: `cat >> "$WORKDIR/docs/decisions/YYYY-MM-DD-<feature>.md" << 'EOF'`. State in one line why — every sibling command in the file uses `$WORKDIR`, and a cwd-relative redirect silently appends in whatever directory the shell happens to be in.
4. In Step 5, make the append idempotent. Replace the bare `cat >>` with a two-branch rule, stated in full because Task 5 depends on it: **if** the file already contains a `## Retrospective` heading, delete from that heading to end-of-file and then append the new section; **otherwise** append directly. Both branches end at the same commit. This is what makes a second `dev:pr` entry produce exactly one `## Retrospective`.
5. In Step 5, leave `git -C "$WORKDIR" push` as a bare push and add one sentence saying it is now correct: at PR stage `$WORKDIR` is on the feature branch, where a bare push has an upstream (set by `dev:pr` Step 4's `push -u`). The detached-HEAD failure this command used to hit belonged to the post-merge home it no longer has.
6. Verify: `grep -n 'cat >>' plugins/dev/skills/reflect/SKILL.md` shows the `$WORKDIR/`-prefixed form only; `grep -n 'push_integration' plugins/dev/skills/reflect/SKILL.md` returns nothing.

### Task 4: Make `dev:reflect` Step 6's skill-update gate three-way
What: Replace Step 6's yes/no gate with three named choices — `backlog`, `debt`, `fix now` — where the first two record and act on nothing, and rewrite the two Step 6 premises the relocation invalidates.
Used by: the standard-mode user at the end of every cycle; the carrying-cost write below it runs unconditionally in both modes.
Depends on: Task 1 (its §P9 claim correction lives in this same step — do not undo it) and Task 3 (Step 5's new commit position is referenced here).
Files: plugins/dev/skills/reflect/SKILL.md (modify)
Interfaces:
- Consumes: from Task 1, the corrected §P9 stop-condition claim; from Task 3, the fact that Step 5's commit has already run when Step 6 writes the buffer
- Produces: the three-way gate's choice vocabulary — `backlog`, `debt`, `fix now` — and a buffer write that branches on the chosen type
- State keys: none — this task introduces no `state.json` key
- Shared procedure: the carrying-cost test. `references/tech-debt.md`'s *State the cost, or don't record it* is **canonical**; this step is a **mirror** that applies it. Restating the canonical's branch structure: an item qualifies only if its body names what the next cycle pays; a body that can only say "would be tidier" fails; the test binds at every capture site regardless of the finding's review label; and the sentence goes in `**Why deferred:**` for a `debt` item or `**Why:**` for a `backlog` item.

Implementation steps:
1. Replace Step 6's display block with the three-way prompt from the spec, verbatim, including the two lines stating that `backlog` and `debt` act on nothing at the time and the three lines describing what `fix now` does (a direct edit under two confirmations, through no `/dev` stages).
2. Route each choice: `backlog` → a buffer entry with `type: backlog`; `debt` → a buffer entry with `type: debt`; `fix now` → today's "yes" path verbatim, including both confirmations, the `### Skill edits go through the plugins repo — always` sub-section, and every stop condition in it.
3. Gate **both** recording choices on the carrying-cost test, not `debt` alone — cite the contract's "It applies at **every** capture site". Branch the hardcoded body shape: `type: debt` keeps `**What's wrong:** / **Why deferred:** / **Done looks like:**`; `type: backlog` uses `**Why:**` in place of `**Why deferred:**`. Everything else in the front-matter (`scope: repo`, `status: open`, `first_recorded:`, `cycles:`, `recurrence: 1`, `files:`) is unchanged.
4. Keep the **Mode rule** paragraph's substance: the gate is standard-mode-only, including on a handed-off cycle, and the carrying-cost write below it is unconditional. Update its sentence naming where `handoff_at` changes behavior — "Step 4 above and `dev:done` Step 5" becomes "Step 4 above and `dev:pr` Step 5c". On a cycle that never reaches the gate, the unconditional write records `type: debt`, exactly as today.
5. Rewrite the **Where the buffer goes, and when** paragraph. Its premise "`dev:reflect` runs from `dev:done` Step 6, and the flush is Step 6a — immediately after" is now false: reflect runs at `dev:pr` Step 5d, and the flush is `dev:done` Step 6a, one stage later. State what still holds — the buffer is written to `$WORKDIR/docs/dev/<feature>/debt-pending.md`, `dev:done` Step 6a reads it **from disk** rather than from git, and `dev:done` Step 2's `checkout --detach` preserves it (untracked files survive a checkout; a tracked-and-committed buffer arrives at the merged tip through the PR). Keep "Do **not** add a commit for the buffer here" and the reason: Step 5's commit has already run.
6. Rewrite the reason attached to the `<source-repo-path> == $WORKDIR` stop condition. The claim "a skill edit committed there would land on `$INTEGRATION`" no longer describes the hazard — at PR stage `$WORKDIR` pushes to the feature branch. The hazard that now applies: the edit would land in **this cycle's own PR**, mixing an unrelated skill change into a diff opened for something else. Keep the stop itself, keep the absolute-path comparison rule, and keep the legacy-in-place note that `$PRIMARY` and `$WORKDIR` are the same directory there.
7. Verify: `grep -n 'fix now' plugins/dev/skills/reflect/SKILL.md` finds the gate; `grep -n 'Why:' plugins/dev/skills/reflect/SKILL.md` finds the `backlog` body branch.

### Task 5: Give `dev:pr` an idempotent re-entry rule and rewrite `dev:autopilot`'s PR exemption
What: Define what a second `dev:pr` entry does on a cycle whose `artifacts.pr_url` is already set — resume idempotently, never stop — and replace the `dev:autopilot` paragraph that currently defers the question to `docs/backlog/`.
Used by: `dev:autopilot` Step 3's Start stage rule, which executes every row stage from the resolved entry point onward, PR included.
Depends on: Task 2 (Step 5a–5d must exist to be made re-enterable) and Task 3 (Step 5's replace branch is what makes the retrospective single).
Files: plugins/dev/skills/pr/SKILL.md (modify), plugins/dev/skills/autopilot/SKILL.md (modify)
Interfaces:
- Consumes: from Task 2, the section names `dev:pr` Step 5a–5d; from Task 3, `dev:reflect` Step 5's replace-if-present branch
- Produces: the stated rule "**idempotent resume, never a stop**", cited by `dev:autopilot`
- State keys: none — this task introduces no `state.json` key. It reads `artifacts.pr_url` and `artifacts.pr_number`, both already written by Step 5.
- Shared procedure: none

Implementation steps:
1. In `plugins/dev/skills/pr/SKILL.md` Step 4, add a re-entry branch at the top: if `state.json.artifacts.pr_url` is already set, **skip `gh pr create`** and reuse the stored `artifacts.pr_number` / `artifacts.pr_url`. The branch push above it still runs on every path — state why in one line: the feature branch is published in exactly one place, and skipping the push would let `dev:done` merge a stale remote head and then force-delete the branch, discarding the run's work.
2. In Step 5, state the three re-entry consequences explicitly: the state write is a no-op re-write of the same values (do not re-stamp `pr_created` — `dev:reflect` Step 1 reads it as the moment the PR was opened); Step 5c **overwrites** `docs/decisions/YYYY-MM-DD-<feature>.md` rather than appending to it; and Step 5d re-runs `dev:reflect`, whose Step 5 replaces the existing `## Retrospective` per Task 3's branch. Step 5's final push still runs.
3. State the rule as a named property — **idempotent resume, never a stop** — and say what it buys: every path reaching `dev:done` has a pushed branch, and no new stop condition is introduced, which is what keeps this consistent with autopilot's rule that from the resolved entry point onward no stage is exempted.
4. Guard the commit in Step 5 against an empty stage on re-entry: if the state write produced no diff, `git commit` exits non-zero. Use the same `git diff --cached --quiet || { … }` shape `dev:done` Step 6a already uses, so a no-change re-entry does not fail the stage.
5. In `plugins/dev/skills/autopilot/SKILL.md` Step 3, replace the paragraph beginning "**No stage is exempted from that rule here** — including PR, whose `gh pr create` is not idempotent…" in full. The rule that no stage is exempted **stands unchanged**; what changes is the reason attached to PR. New text: PR is safely re-enterable — `dev:pr` Step 4 skips `gh pr create` when `artifacts.pr_url` is set, Step 5c overwrites the decision log, Step 5d's retrospective replaces rather than duplicates, and the branch push runs on every path. Delete the "Tracked in `docs/backlog/` rather than guessed at" sentence.
6. In the same file, convert the `done/SKILL.md:504` citation in the "**When the resolved start stage is Done,**" paragraph to a stable anchor — `dev:done` Step 7. Leave the paragraph's argument intact.
7. Leave `dev:autopilot`'s `## Purpose` stop list **unchanged** — this cycle adds no stop condition. Confirm by reading rather than editing.
8. Verify: `grep -n 'pr_url' plugins/dev/skills/pr/SKILL.md` shows the re-entry read in Step 4; `grep -n 'SKILL.md:' plugins/dev/skills/autopilot/SKILL.md` no longer matches `done/SKILL.md:504`.

### Task 6: Repair the remaining cross-file consumer prose and citations
What: Update the four files outside the relocation that name `dev:done` Step 4, Step 4a, or a `file:line` inside a file this cycle edited, so no pointer names a step at a stage that no longer holds it.
Used by: readers of `dev:fix`, `dev:validate`, `dev:dev`, and `references/entry-adapters.md` — each of whom is currently sent to the wrong stage.
Depends on: Task 2 (final section names) and Task 5 (which already owns `autopilot/SKILL.md`, so this task must not touch it).
Files: plugins/dev/skills/fix/SKILL.md (modify), plugins/dev/skills/validate/SKILL.md (modify), plugins/dev/skills/dev/SKILL.md (modify), plugins/dev/references/entry-adapters.md (modify)
Interfaces:
- Consumes: from Task 2, the section names `dev:pr` Step 5a / Step 5b / Step 5c and the fact that `dev:done` no longer has a Step 4, 4a, 5 or 6
- Produces: nothing — terminal for the citation surface
- State keys: none — this task introduces no `state.json` key
- Shared procedure: none — this task only retargets pointers; the mirrored procedures themselves are settled in Tasks 1 and 2.

Implementation steps:
1. `plugins/dev/skills/fix/SKILL.md`, the `## Resolve the target repo` section: convert the citation `dev:reflect` guards exactly this (`reflect/SKILL.md:212`) to a stable anchor — `dev:reflect` Step 6's `### Skill edits go through the plugins repo — always`, step 2. This is spec change 5's `fix/SKILL.md:60`.
2. `plugins/dev/skills/fix/SKILL.md`, the `### Reconcile docs prose` mirror block: retarget "**This is a marked mirror of `dev:done` Step 4a, which stays canonical**" to **`dev:pr` Step 5b**, and retarget D1's "`dev:done` Step 6a later flushes" (still correct — leave it) and D3's "`dev:done` Step 4a must never touch the table because `dev:done` **Step 4** owns it two steps earlier" to name `dev:pr` **Step 5b** and `dev:pr` **Step 5a**. The three divergences keep their meanings; only the stage names change.
3. `plugins/dev/skills/validate/SKILL.md`, the healthy-path shell exit-code rule: its closing parenthetical cites "`done/SKILL.md`'s Step 4a gives for citing its mirror by name". Retarget to `dev:pr` Step 5b. The reasoning it borrows — line numbers across files go stale silently — is unchanged and is what this cycle is acting on.
4. `plugins/dev/references/entry-adapters.md`, the **Loaded by / Cited by** line: "**Cited by** `dev:done`, whose Step 4a interpolation-safety argument rests on §A6's allowlist" becomes `dev:pr`, whose Step 5b argument rests on it.
5. `plugins/dev/skills/dev/SKILL.md` Step 1a item 1: "`dev:done` Step 4 maintains it on every feature cycle" becomes `dev:pr` **Step 5a**. Leave the fallback behavior and the rest of the item unchanged.
6. Verify: `grep -rn 'done.*Step 4a\|dev:done.*Step 4\b\|dev:done.*Step 5\b\|dev:done.*Step 6\b' plugins/dev/ docs/backlog/` returns nothing outside `dev:done`'s own file, and `grep -rn 'SKILL\.md:[0-9]' plugins/dev/skills/fix/SKILL.md plugins/dev/skills/autopilot/SKILL.md docs/backlog/debt-p9-slug-regex-allows-leading-dash.md` no longer matches the three spec-named sites.

### Task 7: Consistency sweep against the Success Criteria
What: Run the grep-and-read checks that verify each of the spec's seven Success Criteria, and fix anything they surface.
Used by: `dev:validate`, which reviews this cycle's diff against the plan — a criterion checked here is one the fix loop does not have to rediscover.
Depends on: Tasks 1–6, all of them.
Files: none created or modified by the sweep itself; fixes land in whichever file a check fails.
Interfaces:
- Consumes: the finished state of every file in the Files table
- Produces: nothing — terminal task
- State keys: none — this task introduces no `state.json` key
- Shared procedure: none

Implementation steps:
1. **SC1** — `grep -n 'push_integration' plugins/dev/skills/done/SKILL.md`: every call site must be in Step 3, 6a or 7, and none of those stages stages `docs/decisions/`, `CLAUDE.md` or `README.md`. Read each of the three to confirm.
2. **SC2** — read `dev:pr` Step 5c's template and confirm the `PR #N` header field is byte-identical to the pre-cycle version, and that Step 5d runs before Step 5's push so the retrospective commit is inside the diff.
3. **SC3** — trace the re-entry path by reading: Step 4 skips create, Step 5c overwrites, Step 5d's reflect replaces, the push runs. One decision log, one `## Retrospective`, branch pushed.
4. **SC4** — `grep -n 'backlog\|debt\|fix now' ` over `dev:reflect` Step 6: three named choices present, neither recording choice edits a skill file or opens a PR, and the `backlog` body branch carries `**Why:**`.
5. **SC5** — `grep -rn 'SKILL\.md:[0-9]'` over the three spec-named sites returns nothing.
6. **SC6** — `grep -rn 'A-Za-z0-9._-\]+/' plugins/dev/` returns nothing, and no prose in `plugins/dev/` claims a validation property the anchored regex does not deliver.
7. **SC7** — read `dev:done` Step 6a: it still reads the buffer from disk at `$WORKDIR/docs/dev/<feature>/debt-pending.md`, and the position note explains why a buffer written one stage earlier is still present.
8. Fix anything a check surfaces, in the owning task's file, and re-run that check.

## Edge Cases

| Edge case | Handled in | Approach |
|-----------|-----------|----------|
| Architecture cycle | Task 2 | Steps 5a and 5b keep their `cycle_type == "feature"` guards verbatim; 5c and 5d run on every cycle type, as Steps 5 and 6 did |
| `dev:pr` re-entry with `pr_url` set | Task 5 | Idempotent resume: skip create, overwrite the log, replace the retrospective, still push. No stop condition |
| Autopilot handed-off cycle | Tasks 2, 4 | `dev:reflect` Step 4's user-observation pause now happens at PR stage instead of Done. Still a pause, not a stop; `dev:autopilot`'s stop list is untouched (Task 5 step 7) |
| `fix now` chosen mid-cycle | Task 4 | Accepted and named: the second PR branches from a `$PRIMARY` `main` lacking this cycle's unmerged edits, producing an ordinary stale-branch conflict a reviewer resolves |
| Legacy in-place cycle (`worktreePath` null) | Tasks 3, 4 | `$WORKDIR` is the primary tree; the `$WORKDIR/` prefix in Task 3 is correct there too, and Task 4 keeps `dev:reflect`'s `<source-repo-path> == $WORKDIR` stop, which still fires |
| Cycle abandoned after `dev:pr`, before `dev:done` | Task 2 | The decision log and retrospective exist only on the unmerged branch and die with it — accepted, and strictly better than today |
| `debt-pending.md` must survive PR → Done | Task 4 step 5 | The flush reads it from disk; `dev:done` Step 2's `checkout --detach` preserves an untracked file, and a tracked-and-committed buffer arrives at the merged tip through the PR |
| Both `README.md` and `CLAUDE.md` absent | Task 2 | Step 5b's missing-file rule moves unchanged: never create, never error, carry a `no <file> found — skipped` note into Step 5's display |
| Empty state diff on `dev:pr` re-entry | Task 5 step 4 | `git diff --cached --quiet || { … }` guard, matching `dev:done` Step 6a's shape, so a no-op commit does not fail the stage |

## Out of Scope

- **`CLAUDE.md` and `README.md` content updates.** They are in the spec's file surface because `dev:done` Step 4 / Step 4a will edit them for *this* cycle, running under the currently-deployed skill version. Build must not pre-empt those stages by editing either file directly.
- **The plugin-wide `file:line` → anchor conversion.** 35 citation-bearing lines across six files; a follow-on cycle that must run after this one merges so the sweep sees final line numbers. `debt-cross-file-line-citations-go-stale-silently` stays open.
- **Renumbering `dev:done`'s surviving steps.** See Design decisions above — the eleven-reference ripple falls outside the spec's stated file surface.
- **`dev:fix`'s lane structure.** It gains only the edits Tasks 1 and 6 require.
- **`review`, `secure`, `migrate-tracker`.** Their citations belong to the follow-on sweep.
- **Closing the three buffered backlog items.** `docs/dev/retro-inside-pr/debt-pending.md` already carries all three `## To Close` bullets; `dev:done` Step 6a executes them. Build writes no `status: closed`.

## Risks and Unknowns

- **`dev:reflect` Step 4's pause now lands mid-`dev:pr`.** On a handed-off cycle the stage stops for a human answer between its state commit and its push, leaving the branch unpushed until the user replies. Mitigated by Task 5's re-entry rule — a resumed `dev:pr` completes the push — but the window is real. Verify in Task 7 step 3 that the resume path is stated, not assumed.
- **Step 5b's detection input changes from a merged diff to a diff against the PR base.** The set of changes it sees is the same for a linear feature branch, but a branch with merge commits from `main` would show more. Accepted: the reconciliation is judgment-based and over-inclusion is visible in the PR, where under-inclusion at the old post-merge site was not.
- **A tracked, locally-modified `debt-pending.md` at `dev:done` Step 2's `checkout --detach`.** Git carries local modifications through a checkout when the target has the same base content, which holds here because the PR merged that base. If it ever did not, the checkout would refuse and the stage would stop loudly rather than lose the buffer. Confirm the reasoning is written into Task 4 step 5 rather than left implicit.
- **`dev:done` Step 8's display now describes artifacts produced by an earlier stage.** Kept deliberately (see Design decisions), but a reader could take `Retrospective appended` as something Done just did. Task 2 step 11 should leave the lines' wording as-is; if Validate flags the ambiguity, the fix is one clarifying clause, not a deletion.

## Grounding for cross-skill claims

Every task instruction below is justified by a claim about another skill's behavior. Each was
checked against the file before this plan was committed, at the line named:

- **Task 3 step 5** — "a bare push has an upstream at PR stage." `dev:pr` Step 4 runs
  `git -C "$WORKDIR" push -u origin <branch-name>` (`pr/SKILL.md:142`), so the upstream is set before
  Step 5 ever runs. Verified.
- **Task 4 step 5** — "`dev:done` Step 6a reads the buffer from disk, not from git." Step 6a item 1
  states it explicitly and gives the reason (`done/SKILL.md`, Step 6a item 1, "Read the buffer **from
  disk, not from git**"). Verified.
- **Task 5 step 4** — "`dev:done` Step 6a already uses a `git diff --cached --quiet` guard against an
  empty stage." Present at `done/SKILL.md:452`, with the reason stated in the sentence above it.
  Verified.
- **Task 5 step 1** — "the feature branch is published in exactly one place." `pr/SKILL.md:142` is the
  only `push -u origin <branch-name>` in the pipeline; `dev:pr` Step 5's push is a bare push to that
  upstream. Verified, and it is the same finding `debt-autopilot-pr-re-entry-not-idempotent` records
  as the reason its obvious one-line fix was wrong.
- **Task 2 step 10** — "Step 6a's position note is load-bearing twice over." The note names both
  halves (`done/SKILL.md`, Step 6a, "**The position of this step is load-bearing twice over**"), and
  only the first half — reflect's items being in the buffer — is affected by this cycle. Verified.
- **Design decisions, the eleven-reference count** — measured by grep, not estimated:
  `references/tech-debt.md` lines 20, 29, 234, 287; `references/entry-adapters.md` 434, 457;
  `debt/SKILL.md` 16, 223; `spec/SKILL.md` 356; `fix/SKILL.md` 591; `reflect/SKILL.md` 172.
