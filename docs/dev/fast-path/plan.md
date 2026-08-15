# Fast Path — Implementation Plan
*Branch: feature/fast-path · 2026-08-15*

## Files

| File | Action | Purpose |
|------|--------|---------|
| `plugins/dev/skills/fix/SKILL.md` | Move → `plugins/dev/skills/linear/SKILL.md` | Today's Linear-issue entry point, renamed to describe what it does |
| `plugins/dev/skills/linear/SKILL.md` | Modify | Frontmatter `name: linear`, description reworded, self-references updated |
| `plugins/dev/skills/fix/SKILL.md` | Create | The new fast-path lane (written fresh at the freed name) |
| `plugins/dev/skills/dev/SKILL.md` | Modify | Rename refs (`:3`, `:179`) + one new invocation-table row + description mention |
| `plugins/dev/skills/start/SKILL.md` | Modify | Rename refs (`:52`, `:68`) + new `dev:fix` lane entries in both lists |
| `plugins/dev/skills/spec/SKILL.md` | Modify | Rename refs only (`:301`, `:509`) |
| `plugins/dev/skills/plan/SKILL.md` | Modify | Rename ref only (`:212`) |
| `plugins/dev/skills/validate/SKILL.md` | Modify | Rename ref only (`:64`) |
| `plugins/dev/skills/done/SKILL.md` | Modify | Rename ref (`:256`) + duplication pointer at Step 2 and Step 7 |
| `plugins/dev/skills/pr/SKILL.md` | Modify | Duplication pointer at Step 4 |
| `plugins/dev/references/tech-debt.md` | Modify | Rename refs only (`:137`, `:428`) |
| `plugins/dev/skills/debt/viewer.py` | Modify | Rename ref only (comment, `:367`) |
| `README.md` | Modify | Rename ref + new `dev:fix` entry in the skill list (`:13`) |
| `CLAUDE.md` | Modify | Registry row renamed to `dev:linear` + new `dev:fix` row (`:35`) |
| `plugins/plugin-manager/skills/add-plugin/SKILL.md` | Modify | Rename ref + new `dev:fix` entry (`:25`) |
| `docs/backlog/debt-primary-cd-failure-unchecked.md` | Modify | Path-only edit: its `files:` entry follows the renamed skill (count stays 13) |

**Not touched, deliberately:** `docs/decisions/*.md` (historical records — SC7), and the working
artifacts `docs/backlog/backlog-fix-as-short-bug-round-trip.md` and
`docs/dev/product-plans/dev-fast-path.md` (see Task 1's exclusion rule).

## Tasks

### Task 1: Rename `dev:fix` → `dev:linear`

What: Free the `dev:fix` name by moving today's Linear entry point to `dev:linear`, and sweep every
reference so none goes stale.
Used by: Task 2, which writes the new lane at the freed `skills/fix/` path — this must land first or
the two skills collide on one directory.
Depends on: nothing — first task.
Files: `plugins/dev/skills/fix/SKILL.md` → `plugins/dev/skills/linear/SKILL.md`; rename-only edits to
`skills/{dev,start,spec,plan,validate,done}/SKILL.md`, `references/tech-debt.md`,
`skills/debt/viewer.py`, `README.md`, `CLAUDE.md`, `add-plugin/SKILL.md`; path-only edit to
`docs/backlog/debt-primary-cd-failure-unchecked.md`.
Interfaces:
- Consumes: nothing
- Produces: the skill `dev:linear` at `plugins/dev/skills/linear/SKILL.md` with frontmatter
  `name: linear`; a vacant `plugins/dev/skills/fix/` path for Task 2

Implementation steps:
1. `git -C "$WORKDIR" mv plugins/dev/skills/fix plugins/dev/skills/linear`.
2. In `linear/SKILL.md`: set frontmatter to `name: linear` — **bare, not `dev:linear`**, or
   autocomplete renders `/dev:dev:linear` (spec §Technical Constraints). Reword the `description:`
   to open with "Linear-aware entry point into the full seven-stage /dev workflow" and change the
   example invocation to `/dev:linear ENG-123`.
3. In `linear/SKILL.md` body, update the four self-references: the `# dev:fix —` H1 (`:6`), the
   Announce line (`:8`), and the two Step 3 mentions of the `dev:fix` slug allowlist (`:82`, `:84`).
4. Sweep the remaining 11 files. The exact lines, verified by sweep at plan time:
   `dev:3`, `dev:179`, `start:52`, `start:68`, `spec:301`, `spec:509`, `plan:212`, `validate:64`,
   `done:256`, `tech-debt.md:137`, `tech-debt.md:428`, `viewer.py:367`, `README.md:13`,
   `CLAUDE.md:35`, `add-plugin/SKILL.md:25`. Every one of these describes the *Linear* behavior, so
   every one becomes `dev:linear`. **One of them needs more than a token swap:** `done:256` also says
   "(or `^[A-Za-z0-9][A-Za-z0-9-]*$` **for a fix cycle**)". A token-level sweep leaves that reading
   "`dev:linear` Step 3's allowlist … for a fix cycle", pointing at the new lane — which runs no cycle
   and has no such allowlist. Reword it to "for a Linear cycle".
5. **Two further references are *path* strings, not `dev:fix` strings — the `dev:fix` grep will not
   surface them**, because the path contains `skills/fix`:
   - `CLAUDE.md:35`'s Path column becomes `plugins/dev/skills/linear/SKILL.md`. Without this, Task 7's
     new `dev:fix` row and this renamed `dev:linear` row would both point at the lane's file, failing
     SC7 and SC9.
   - `docs/backlog/debt-primary-cd-failure-unchecked.md`'s `files:` entry
     `plugins/dev/skills/fix/SKILL.md` becomes `plugins/dev/skills/linear/SKILL.md`. The count stays
     **13** — the renamed file is still unguarded, and the new lane at `skills/fix/` carries the
     guard. Without this the item would name the guarded new lane while the real unguarded site went
     unlisted, silently falsifying Task 2 step 2's own "does not grow the count to 14" reasoning.
   - `docs/backlog/closed/debt-feature-slug-allowlist.md` and
     `docs/backlog/closed/debt-primary-path-relative-in-dev-headers.md` keep the old path — closed
     items are historical records, like decision logs.
6. **Exclusion rule — do not edit:** `docs/decisions/*.md` (SC7: a decision log records what was true
   on its date). Also do not edit `docs/backlog/backlog-fix-as-short-bug-round-trip.md` or
   `docs/dev/product-plans/dev-fast-path.md` — both use `dev:fix` in its pre-rename sense as a record
   of what was asked, and both are ephemeral cycle artifacts that `dev:done` closes or deletes. This
   settles the spec's open question about the exclusion set beyond `docs/decisions/`.
7. Re-run `grep -rn 'dev:fix' plugins/ README.md CLAUDE.md` and confirm every surviving hit is either
   an intentional reference to the *new* lane (none yet at this task) or in the exclusion set. Then
   run the path sweep `grep -rn 'skills/fix' .` for the same reason — step 5's references are invisible
   to the first grep.

### Task 2: Lane skill — header, `PRIMARY`, argument parse, preflight refusals

What: Create `plugins/dev/skills/fix/SKILL.md` and write everything that runs before the lane touches
a file: working-directory resolution, the `merge`-vs-free-text argument split, and the four refusals.
Used by: every later segment of the lane; `/dev:fix <anything>` enters here.
Depends on: Task 1 (the path must be vacant and the name freed).
Files: create `plugins/dev/skills/fix/SKILL.md`
Interfaces:
- Consumes: nothing
- Produces: `$PRIMARY` (absolute path to the primary checkout, guaranteed non-empty); `$DEFAULT_BRANCH`;
  the parsed mode `lane | tail`; a preflight that has either passed or STOPped
- State keys: **none.** The lane writes no `state.json` and creates no `docs/dev/<feature>/` directory
  — producing no cycle artifacts is the feature, not an omission. No `(writes: …)` declaration applies
  to any task in this plan.

Implementation steps:
1. Frontmatter: `name: fix` (bare). Description rich with trigger phrases — "fast path", "quick fix",
   "small change", "just do this", "open a PR for" — plus an explicit line steering full-cycle work to
   `/dev` and Linear work to `/dev:linear`.
2. **`PRIMARY` derivation, with the guard.** Write the shape used at `build/SKILL.md:26-27`, plus the
   non-empty check none of the 13 shell sites carries:
   ```bash
   GIT_COMMON=$(git rev-parse --git-common-dir) || { echo "Not a git repository."; exit 1; }
   PRIMARY=$(cd "$(dirname "$GIT_COMMON")" && pwd)
   if [ -z "$PRIMARY" ]; then echo "Could not resolve the primary checkout."; exit 1; fi
   ```
   The lane operates in `$PRIMARY` throughout — it never creates a worktree. Add one sentence naming
   `debt-primary-cd-failure-unchecked` and stating that this site carries the guard so it does not
   grow that item's count to 14.
3. **Default branch detection** (spec edge case — never assume `main`):
   `DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)`, falling back to
   `git -C "$PRIMARY" symbolic-ref --short refs/remotes/origin/HEAD | sed 's|^origin/||'`. STOP if both
   fail. Note in the file that `dev:done` hardcodes `main` (`done/SKILL.md:26`) and that the lane
   deliberately does not copy that.
4. **Argument parse.** The argument is the bare token `merge` and nothing else → tail mode (Task 5).
   Any longer argument, including one whose first word is `merge`, is a free-text lane request. State
   this rule explicitly with the worked example `/dev:fix merge the two config loaders` → lane, not
   tail. Empty argument → ask what to do; do not guess.
5. **Preflight refusals — the first three run in both modes, before any branch is created, in this
   order:**
   - `gh` unavailable or unauthenticated (`gh auth status`) → STOP with the reason. Checked first
     because it is the cheapest and the lane cannot finish without it.
   - Dirty working tree in `$PRIMARY` (`git -C "$PRIMARY" status --porcelain`) → STOP, naming the
     modified files. Never stash, never branch over uncommitted work.
   - A legacy in-place `/dev` cycle occupying `$PRIMARY`: scan `$PRIMARY/docs/dev/*/state.json` for a
     cycle whose `worktreePath` is null and whose `stage` is not `done` → STOP naming that feature.
     Explain why the clean-tree check above does not catch it: a committed in-place cycle leaves the
     tree clean. A modern worktree cycle does not contend and must not trigger this.
   - **Lane mode only — the currently checked-out branch already has an open PR**
     (`gh pr list --head "$(git -C "$PRIMARY" branch --show-current)" --state open`) → STOP and report
     it. **In tail mode (`/dev:fix merge`) this same condition is the expected precondition, not a
     refusal: skip this check entirely and dispatch to the merge tail.** Running it in both modes
     would make `/dev:fix merge` always STOP while offering `/dev:fix merge` as the exit — an
     infinite loop that puts Success Criterion 4 out of reach. This is the lane's own leftover
     state: the lane stops at PR and leaves `$PRIMARY` on that feature branch, so a second *lane*
     invocation would otherwise branch off `$DEFAULT_BRANCH` and strand the first PR, which
     `/dev:fix merge` (defined as operating on the current branch) could then no longer reach. Offer
     the two exits: `/dev:fix merge`, or switch branches manually.

### Task 3: Lane skill — Ground, Triage, Branch

What: Write the lane's first three segments — verify the request's as-is claims against real files,
count the unresolved decisions and route on that count, then create the branch.
Used by: Task 4, which changes files only after Triage says proceed.
Depends on: Task 2 (`$PRIMARY`, `$DEFAULT_BRANCH`, preflight passed).
Files: modify `plugins/dev/skills/fix/SKILL.md` (append segments)
Interfaces:
- Consumes: `$PRIMARY`, `$DEFAULT_BRANCH`, lane mode, passed preflight (Task 2)
- Produces: a grounding inventory (the files actually read and what each confirmed); a decision count
  `0 | 1 | 2+` with the route taken; a created-and-checked-out feature branch in `$PRIMARY`

Implementation steps:
1. **Ground.** Read the actual files the request names or implies, and verify every as-is claim it
   makes. Prohibit editing from a remembered mental model. Record what was read — this becomes the
   "what I verified" section of the PR body (Task 4).
2. **Triage — the escalation rule.** Reproduce the spec's table verbatim (0 → proceed regardless of
   size; 1 → ask inline, then proceed; 2+ → stop). Reproduce the three-part counting rule: countable
   only if (a) the request text does not determine it, (b) no repo convention determines it, and
   (c) reversing it later would require editing files this change touches. A choice settled by
   convention counts as **zero**. When genuinely unsure, **count it**.
3. **State the observable difference between the 1 and 2+ rows**, since both may end in proceeding:
   the 2+ path *always prints the `/dev` command* before asking, and never begins changing files in
   the same turn as the question. That printed command is the marker Success Criterion 2 tests. The
   1-decision path asks inline and proceeds in the same turn without printing it.
4. Give one worked example per row, drawn from spec §Happy Path and §Scope: the 14-file frontmatter
   rename as the canonical 0-decision case (size is never the trigger), and a one-file change with two
   defensible answers as the 2+ case.
5. **Branch.** `git -C "$PRIMARY" fetch origin`, then
   `git -C "$PRIMARY" checkout -b <name> "origin/$DEFAULT_BRANCH"`. Name the branch
   `fix/<kebab-summary>`. **The allowlist applies to `<kebab-summary>` alone, not to the full branch
   name** — `dev:spec` Step 6 (`spec/SKILL.md:135`) normalizes a bare feature slug, and a prefixed
   `fix/…` can never match the anchored `^[a-z0-9][a-z0-9-]*$` because the `/` would be collapsed.
   Normalize by Step 6's construction — collapse every non-`[a-z0-9]` run to a single `-`, strip
   leading/trailing `-` — and carry its STOP: if the result is empty, ask for a name rather than
   proceeding.
6. **Branch-name collision.** Check both `git -C "$PRIMARY" rev-parse --verify` (local) and
   `git -C "$PRIMARY" ls-remote --exit-code --heads origin <name>` (remote). On either hit,
   disambiguate with a `-2`, `-3` suffix. Never reuse an existing branch, never force-push. Both
   checks run **before** step 5's `checkout -b` — resolve the final name first, then create the
   branch once.
7. **Nothing to change.** If grounding shows the request is already satisfied, say so, open no PR, and
   do not create a branch — an empty PR is worse than no PR. This check belongs before step 5.

### Task 4: Lane skill — Change, Verify, PR

What: Write the segments that make the edit, verify it, and open the PR — where the lane stops.
Used by: the user, who reviews the PR and then invokes Task 5's tail.
Depends on: Task 3 (a branch exists and Triage said proceed).
Files: modify `plugins/dev/skills/fix/SKILL.md` (append segments)
Interfaces:
- Consumes: the branch, grounding inventory, and decision count from Task 3
- Produces: an open PR URL, reported to the user; `$PRIMARY` left checked out on the feature branch
- Shared procedure: `open PR` — this is a **mirror** of `dev:pr` Step 4 (`pr/SKILL.md:115-140`), not
  the canonical implementation. Restating its branch structure in full: (a) push the branch with
  `git -C "$PRIMARY" push -u origin <branch>` — the `-C` is required, not optional, since the lane may
  be invoked from anywhere in the repo including inside a `.dev-worktrees/<feature>` tree; (b)
  determine the base branch — `dev:pr` reads
  `state.json.parentFeature` and falls back to `main`, whereas **the lane has no state.json and always
  targets `$DEFAULT_BRANCH`**; (c) `dev:pr`'s nested-cycle push of the parent branch has **no lane
  equivalent** and is deliberately absent — the lane never nests; (d) run `gh pr create` from inside
  the working directory with an explicit `--head`, because `gh` has no `-C` flag and would otherwise
  infer the head from whatever branch the tree is on. Task 6 adds the pointer at the `dev:pr` end.

Implementation steps:
1. **Change.** The minimal edit that does the job. Commit with a conventional-commit message.
2. **Verify.** Run the repo's test suite if one exists; detect it rather than assuming (`package.json`
   scripts, `pytest`, `Makefile`, a `test_*.py` convention). Then verify by whatever means the change
   actually requires, **including means the suite cannot reach** — reading rendered output, walking a
   procedure manually. Record each result verbatim for the PR body.
3. **The rigor floor, stated as a checklist the lane may never skip**, with the PR body naming which
   applied: grounded before acting; ran the suite when one exists; never claimed unverified success;
   captured deferred work; reported decisions made on the user's behalf.
4. **No suite in the repo** → say so explicitly in the PR body rather than implying tests passed. Add
   the sentence that an absent suite raises the bar on other verification rather than lowering the bar
   overall.
5. **Mid-flight discovery.** If implementation reveals a real fork that grounding missed, stop and
   escalate at that point rather than deciding to keep momentum. **Working-tree disposition on this
   stop, stated so the next invocation is not blocked:** commit the partial work to the feature branch
   and report the branch name and what is on it. Do not leave the tree dirty (Task 2's preflight would
   then refuse the follow-up invocation with a confusing "modified files" message) and do not revert
   (that discards real work over a question). Open no PR.
6. **Deferred-work capture.** Anything noticed and not done goes to `docs/backlog/` per
   `plugins/dev/references/tech-debt.md` — the lane is a consumer of that schema and must not fork it.
   Per §P7's writer-side rule, create `docs/backlog/` (and `closed/`) when absent and proceed; degrade
   silently rather than erroring when the store cannot be written. Spec §Audience has the lane running
   across several repos, so a `scope: plugin` item captured **off** the plugin repo routes per §P9 —
   cite that section rather than restating it, and carry its degrade-to-local branch
   (`routing: pending`) so a failed route buffers instead of dropping.
7. **PR body template.** Three required sections: what changed, why, and what was verified (including
   what could not be). Plus a "Decisions made for you" section, which prints the 1-decision question
   and its answer when Triage took that route, and states "none" otherwise.
8. **Stop.** Report the PR URL and end the turn. State plainly in the file that the PR is the
   checkpoint and that the lane never merges.
9. **Name the duplication at the lane's end.** In the PR segment, write one line: *This mirrors
   `dev:pr` Step 4 (`pr/SKILL.md:115-140`), which is canonical. It is duplicated because the lane
   produces no `validation.md` and so cannot enter that stage; a change to either side should be
   reflected at the other.* Task 6 adds the matching pointer at the `dev:pr` end. Both halves are
   required — spec §Technical Constraints says the duplication must be named at **both ends**, and
   the `Shared procedure:` line above is plan metadata that never reaches the shipped file.

### Task 5: Lane skill — the `merge` tail

What: Write the `/dev:fix merge` segment — merge the PR, delete both branches, fast-forward the
primary checkout, report.
Used by: the user, as the deliberate second invocation.
Depends on: Task 4 (an open PR exists for the current branch) and Task 2 (argument parse routes the
bare token `merge` here).
Files: modify `plugins/dev/skills/fix/SKILL.md` (append segment)
Interfaces:
- Consumes: `$PRIMARY`, `$DEFAULT_BRANCH` (Task 2); the open PR on the currently checked-out branch
- Produces: merged PR; remote and local branch deleted; `$PRIMARY` on `$DEFAULT_BRANCH`, fast-forwarded,
  working tree clean
- Shared procedure: `merge and clean up` — a **mirror** of `dev:done` Step 2 (`done/SKILL.md:56-131`),
  not the canonical implementation. Restating its branch structure in full: (a) a mergeability
  precheck via `gh pr view --json mergeable,mergeStateStatus`, which STOPs on a definite conflicting
  or blocked state but **not** on `UNKNOWN` — GitHub computes mergeability asynchronously, so re-query
  after a few seconds; (b) a `delete_feature_branch` guard that refuses to delete anything unless
  `gh pr view --json state` reads `MERGED`, then removes remote and local idempotently; (c) `dev:done`
  forks on `worktreePath` into a **worktree** branch (detached HEAD, because git forbids one branch in
  two worktrees) and a **legacy in-place** branch (plain checkout) — **the lane has only the in-place
  shape**, since it never creates a worktree, so the detached-HEAD branch is deliberately absent;
  (d) `gh pr merge --merge` with **no** `--delete-branch`, and deletion done with explicit git
  plumbing; (e) `dev:done`'s `push_integration` helper (end of Step 2) has **no lane equivalent** and
  is deliberately absent — the lane makes no post-merge commits, so it never pushes to the integration
  branch. Task 6 adds the pointer at the `dev:done` end.

Implementation steps:
1. Resolve the target PR: the open PR for the branch currently checked out in `$PRIMARY`. If that
   branch has no open PR, or more than one resolves, stop and report rather than guessing.
2. Mergeability precheck per the branch structure above. Never force, and never delete a branch whose
   PR did not merge.
3. `gh pr merge <n> --merge` from inside `$PRIMARY`. Carry `dev:done`'s explicit warning about
   `--delete-branch` and why it is not used — the lane is a mirror, and a future reader must not
   "simplify" it back.
4. `git -C "$PRIMARY" checkout "$DEFAULT_BRANCH"` (frees the feature branch for deletion), then
   `git -C "$PRIMARY" pull --ff-only origin "$DEFAULT_BRANCH"`, then the guarded branch deletion.
   Ordering matters: the local branch cannot be deleted while it is checked out.
5. Report: PR merged, branches gone, primary checkout on `$DEFAULT_BRANCH` at the merged tip, tree
   clean — the four states Success Criterion 4 tests.
6. **Name the duplication at the lane's end.** In the merge tail, write one line: *This mirrors
   `dev:done` Step 2 (`done/SKILL.md:56-131`), which is canonical. It is duplicated because the lane
   writes no `state.json` and so cannot enter that stage; a change to either side should be reflected
   at the other.* Task 6 adds the matching pointer at the `dev:done` end. Both halves are required,
   for the same reason given in Task 4 step 9.

### Task 6: Duplication pointers in `dev:pr` and `dev:done`

What: Add the one-line pointers at the canonical end of each duplicated procedure, so a future edit to
`dev:pr` or `dev:done` is not silently missed at the lane.
Used by: any future editor of those two stage skills.
Depends on: Tasks 4 and 5 (the lane's mirror sites must exist to point at).
Files: modify `plugins/dev/skills/pr/SKILL.md`, `plugins/dev/skills/done/SKILL.md`
Interfaces:
- Consumes: the lane's PR segment (Task 4) and merge tail (Task 5) as pointer targets
- Produces: nothing later tasks rely on — terminal except for Task 8's verification
- Shared procedure: this task is the **other end** of the two mirrors declared in Tasks 4 and 5. It
  adds pointers only; it does not restate or alter either procedure.

Implementation steps:
1. `pr/SKILL.md` Step 4 (`:115`): one line — `dev:fix`'s PR segment mirrors this step for the
   artifact-free lane; changes here should be reflected there.
2. `done/SKILL.md` Step 2 (`:56`): the same, naming `dev:fix`'s merge tail.
3. `done/SKILL.md` Step 7 (`:471`): the same, for the cleanup half.
4. Keep each to a single sentence. These three lines are carve-out (c) of Success Criterion 6 — the
   only non-rename edits permitted in `pr/SKILL.md` and `done/SKILL.md`.

### Task 7: Discoverability — advertise the new lane

What: Add the new `/dev:fix` lane everywhere the repo advertises `dev` skills, so a pure rename does
not leave it invisible.
Used by: the user, who finds the lane without being told it exists.
Depends on: Task 1 (the `dev:linear` rows exist to sit beside) and Task 2 (the lane's description is
written and can be quoted).
Files: modify `README.md`, `CLAUDE.md`, `plugins/plugin-manager/skills/add-plugin/SKILL.md`,
`plugins/dev/skills/start/SKILL.md`, `plugins/dev/skills/dev/SKILL.md`
Interfaces:
- Consumes: `dev:linear` (Task 1); the lane's frontmatter description (Task 2)
- Produces: nothing later tasks rely on — terminal except for Task 8's verification

Implementation steps:
1. **Exactly five sites list skills and receive the addition** — the other seven of the twelve are
   injection-guardrail prose with nothing to add, and Success Criterion 6 forbids touching them beyond
   the rename:
   - `README.md:13` — add `dev:fix` to the `dev` plugin's skill list beside `dev:linear`.
   - `CLAUDE.md:35` — a new Component Registry row for `dev:fix` (the fast-path lane) beside the
     renamed `dev:linear` row.
   - `add-plugin/SKILL.md:25` — add `dev:fix` to that table's `dev` skill list.
   - `start/SKILL.md:52` — a `dev:fix` bullet in the Step 4 FYI list, beside `dev:linear`.
   - `start/SKILL.md:68` — a `dev:fix` bullet in the fallback minimal-description list.
2. `dev/SKILL.md`: one added invocation-table row after `:179` —
   `| /dev:fix "<what you want done>" | Fast path — grounded change to open PR, no cycle artifacts |`
   — plus a second row for `| /dev:fix merge | Merge that PR and clean up |`, and a description
   mention. These are carve-out (b) of Success Criterion 6.
3. Each entry must distinguish the lane from `/dev` in one clause, so the reader can tell which to
   reach for: the lane stops at a PR and writes no cycle artifacts.

### Task 8: Verification sweep

What: Verify the four mechanically checkable success criteria before the cycle leaves Build.
Used by: `dev:validate`, which inherits a repo already known to satisfy them.
Depends on: Tasks 1–7 (every edit must have landed).
Files: none — read-only verification
Interfaces:
- Consumes: the full working tree after Tasks 1–7
- Produces: nothing — terminal task

Implementation steps:
1. **SC7/SC8:** `grep -rn 'dev:fix' plugins/ README.md CLAUDE.md` — every hit must refer to the *new*
   lane, and `grep -rn 'dev:linear' …` must cover every Linear reference. Then the path sweep
   `grep -rn 'skills/fix' . --exclude-dir=docs/dev` — the exclusion is required, not cosmetic: this
   cycle's own `spec.md` and `plan.md` quote both the old and new paths throughout, so an unscoped
   sweep returns ~18 self-hits and can never come back clean. Every surviving hit must name the *new*
   lane or sit in the exclusion
   set of Task 1 **steps 5–6** (the two `closed/` items, `backlog-fix-as-short-bug-round-trip.md`, and
   `product-plans/dev-fast-path.md`), since the `dev:fix` grep structurally cannot see path strings.
   Also confirm `fix/SKILL.md` carries both mirror-pointer lines (Task 4 step 9, Task 5 step 6), so
   the "both ends" requirement is verified from both directions rather than only from
   `dev:pr`/`dev:done`. Then
   `grep -rn '/Users/\|awilliamsbuilds\|adam' plugins/dev/` must still return zero.
2. **SC6:** `git -C "$WORKDIR" diff --stat main -- plugins/dev/skills/{spec,shape,plan,build,validate,pr,done,autopilot,dev}` and
   inspect each hunk — every one must be a rename reference, one of the three Task 6 pointers
   (carve-out c), or in `dev/SKILL.md` only, Task 7's two invocation rows and description mention
   (carve-out b), and nothing else. `plugins/dev/skills/{shape,build,autopilot}/SKILL.md` should show
   **no diff at all**. `autopilot` is in the pathspec because SC6 names `/dev:autopilot` explicitly;
   it holds no `dev:fix` reference today, so any diff there is a defect.
3. **SC9:** confirm all five discoverability sites from Task 7 list the new lane.
4. **Skill loading:** confirm `plugins/dev/.claude-plugin/plugin.json` still has no skills array (both
   skills are auto-discovered, so no plugin.json or marketplace edit is needed — spec §Technical
   Constraints), and that both `fix/SKILL.md` and `linear/SKILL.md` carry a **bare** frontmatter
   `name:`.
5. **State honestly what could not be verified.** The installed plugin is a snapshot of `main`, so the
   lane cannot be exercised through its own invocation during Build. Verify at the file level and by
   walking the procedure manually against the real repo, and label which is which — do not report a
   manual walkthrough as an end-to-end run.

## Edge Cases

| Edge case | Handled in | Approach |
|-----------|-----------|----------|
| Dirty working tree | Task 2 | Preflight refusal naming the modified files; never stash, never branch over |
| No test suite in the repo | Task 4 | Say so explicitly in the PR body; absent suite raises the bar elsewhere |
| Mid-flight discovery of a real fork | Task 4 | Stop and escalate; commit partial work to the branch, open no PR |
| Nothing to change | Task 3 | Say so, create no branch, open no PR |
| Default branch is not `main` | Task 2 | `gh repo view` with a `symbolic-ref` fallback; STOP if both fail |
| Branch name already exists (local or remote) | Task 3 | Check both, disambiguate with a suffix; never reuse or force-push |
| PR not mergeable at `merge` (incl. `UNKNOWN`) | Task 5 | Re-query on `UNKNOWN`; STOP on definite block; never delete an unmerged branch |
| `gh` unavailable or unauthenticated | Task 2 | First preflight check; fail before branching, with the reason |
| No `docs/backlog/` in the repo | Task 4 | §P7 writer-side rule — create on first write, degrade silently |
| Legacy in-place `/dev` cycle in `$PRIMARY` | Task 2 | Scan `docs/dev/*/state.json` for null `worktreePath` + stage ≠ `done`; refuse |
| Lane re-invoked before merging the last PR | Task 2 | Open-PR-on-current-branch preflight; report it rather than stranding it |
| `merge` as the first word of a free-text request | Task 2 | Bare-token-only parse rule, with the worked example |

## Out of Scope

- Extracting a shared reference for the `dev:pr` / `dev:done` duplication — named at both ends
  (Tasks 4, 5, 6) and deferred deliberately to a later cycle.
- Backlog-item entry (`/dev:fix <backlog-slug>`) — Milestone 2.
- Retiring `~/.claude/commands/` — Milestone 3; those files are outside this repo.
- Auto-merge — merging stays behind the second invocation.
- Narrowing Task 7's `dev/SKILL.md` addition to a single invocation row. SC6 carve-out (b) reads "one
  added invocation-table row"; the lane genuinely has two invocation forms (`/dev:fix "<request>"` and
  `/dev:fix merge`), so Task 7 adds both and Task 8 validates both. Recorded here so a literal SC6
  check at Validate reads the pair as the one authorized addition rather than as an unapproved edit.
- Correcting the spec footer's "a micro cycle still writes every artifact" sentence. Carried from the
  cold review as a concern: micro sets `skipped: ["shape", "plan"]` (`spec/SKILL.md:126`), so
  `design.md` and `plan.md` are never written. The Intent's argument is unaffected — worktree,
  `spec.md`, `state.json`, both challengers, the validate loop, `validation.md`, the decision log and
  the retrospective are all still produced on micro — so this is a spec-prose inaccuracy with no build
  action, recorded here rather than silently fixed.
