# done-primary-reconcile — Implementation Plan
*Branch: feature/done-primary-reconcile · 2026-07-23*

## Files

| File | Action | Purpose |
|------|--------|---------|
| plugins/dev/skills/done/SKILL.md | Modify | Add the primary-checkout reconciliation block to Step 7 (worktree-cycle teardown) and report its outcome in Step 8 |

## Tasks

### Task 1: Add the primary-checkout reconciliation block to Step 7
What: After the worktree is removed, catch the primary checkout's local `main` up to `origin/main` when it can be done safely; otherwise leave the primary tree byte-for-byte unchanged and record that a manual pull is needed.
Used by: Runs automatically at the tail of `dev:done` Step 7 on the worktree-cycle path; its result is consumed by Task 2's Step 8 report.
Depends on: nothing — first task.
Files: plugins/dev/skills/done/SKILL.md (modify Step 7)
Interfaces:
- Consumes: the existing `PRIMARY`, `WORKDIR`, and `INTEGRATION` variables defined at the top of `dev:done` (Resolve-the-working-directory + Step 2). `WORKDIR` has been removed by the `worktree remove` above this block; the block never references it.
- Produces: shell variable `RECONCILE_MSG` (one of the tokens `ff:<sha>`, `refadvanced:<sha>`, `uptodate`, `reminder`, `reminder-nested`) and shell variable `primary_branch` (the primary checkout's current branch name, empty if detached). Task 2 renders both.

Implementation steps:
1. Insert the block **at the very end of Step 7**, immediately after the existing worktree-removal snippet (`git -C "$PRIMARY" worktree remove --force "$WORKDIR"` / `git -C "$PRIMARY" worktree prune`, currently lines 345–346) and after the parenthetical note about branch deletion (line 349–350). It sits inside the "Otherwise remove the worktree" section, which the legacy in-place path never reaches (legacy returned to Step 8 at the "Step 7 ends here" note above). This placement — not a `worktreePath` check — is what makes the step worktree-cycle-only. State that in the prose so a future edit doesn't "simplify" it by hoisting the block above the legacy return.
2. Add a short prose paragraph introducing the block: after teardown, reconcile the **primary checkout** so the user's `main` folder reflects the just-merged work without a manual `git pull` — but only when it is safe (top-level cycle, primary clean and fast-forwardable). It never mutates a dirty primary tree, never creates a merge commit, never forces an update, and **never STOPs the stage** — every path resolves to a `RECONCILE_MSG` and continues to Step 8.
3. Add this exact embedded shell. It relies on the fact that `push_integration`'s successful `git push origin HEAD:$INTEGRATION` (run repeatedly in Steps 3–7) already advanced the **shared** remote-tracking ref `refs/remotes/origin/main` — remote-tracking refs live in the common git dir and are visible from every worktree, including `$PRIMARY` — so no extra `fetch` is needed for the on-`main` fast-forward; it reads the already-current `origin/main`. (Keep this reasoning in a comment so Build/maintainers don't add a redundant network fetch.)

    ```bash
    # Reconcile the primary checkout's main with origin/main — worktree cycle, top-level only.
    # Never STOPs; each branch sets RECONCILE_MSG for the Step 8 report.
    primary_branch=$(git -C "$PRIMARY" symbolic-ref --quiet --short HEAD || true)   # empty if detached
    if [ "$INTEGRATION" = "main" ]; then
      primary_dirty=$(git -C "$PRIMARY" status --porcelain --untracked-files=no)     # tracked changes only
      local_main=$(git -C "$PRIMARY" rev-parse --verify --quiet refs/heads/main || true)
      # origin/main is already current: push_integration advanced this shared remote-tracking ref.
      origin_main=$(git -C "$PRIMARY" rev-parse --verify --quiet refs/remotes/origin/main || true)

      if [ "$primary_branch" = "main" ]; then
        if [ -n "$primary_dirty" ]; then
          RECONCILE_MSG="reminder"                                   # dirty → never mutate the primary tree
        elif [ "$local_main" = "$origin_main" ]; then
          RECONCILE_MSG="uptodate"                                   # already current → no-op, no reminder
        elif git -C "$PRIMARY" merge-base --is-ancestor "$local_main" "$origin_main" 2>/dev/null; then
          if git -C "$PRIMARY" merge --ff-only origin/main; then
            RECONCILE_MSG="ff:$origin_main"                          # fast-forwarded working tree + ref
          else
            RECONCILE_MSG="reminder"                                 # ff refused (e.g. untracked collision) → defer
          fi
        else
          RECONCILE_MSG="reminder"                                   # diverged → no fast-forward possible → defer
        fi
      else
        # Detached HEAD or a different branch: advance the main ref without a checkout.
        if [ -z "$local_main" ]; then
          RECONCILE_MSG="reminder"                                   # no local main to advance → defer
        elif [ "$local_main" = "$origin_main" ]; then
          RECONCILE_MSG="uptodate"                                   # ref already current → no-op, no reminder
        elif git -C "$PRIMARY" fetch origin main:main 2>/dev/null; then
          RECONCILE_MSG="refadvanced:$origin_main"                   # fetch enforces fast-forward; succeeded
        else
          RECONCILE_MSG="reminder"                                   # non-fast-forward fetch refused → defer
        fi
      fi
    else
      RECONCILE_MSG="reminder-nested"                                # nested cycle (INTEGRATION = parent branch): reminder only
    fi
    ```
4. In prose after the snippet, annotate the two safety-critical design points so they survive future edits:
   - **Check order settles the overlapping cases (spec Open Question).** The three primary-state cases are not mutually exclusive — a primary on another branch whose local `main` has also diverged matches both the "different branch → `fetch origin main:main`" and the "diverged → reminder" descriptions. This block makes the **exit code of `fetch origin main:main` the single authority**: `git fetch` enforces fast-forward on the `main:main` refspec, so a diverged ref makes the fetch exit non-zero and fall to `reminder`, and `refadvanced` is reported **only** when the fetch actually succeeded. The report can therefore never claim "ref advanced" when nothing moved.
   - **`merge --ff-only` / `fetch main:main` are the only mutations, and both are self-guarding.** `--ff-only` updates the working tree only on a clean strict-ahead fast-forward and aborts harmlessly otherwise; `fetch origin main:main` refuses to touch `main` if it is the checked-out branch of any worktree (e.g. a concurrent cycle) and refuses a non-fast-forward — both landing on the `reminder` path. No path mutates a dirty tree, forces a ref, or creates a merge commit.
5. Do **not** add a STOP, an `exit`, or a gate anywhere in this block. It is pure teardown reconciliation; a failure to reconcile is reported as a reminder, not an error. (This is why `dev:autopilot` Step 2 "When autopilot stops" needs no change — the block introduces no new stop condition.)

### Task 2: Report the reconciliation outcome in Step 8
What: Render a single, accurate line in the Step 8 completion display describing what happened to the primary checkout — fast-forwarded, ref advanced, or left for a manual pull — and print nothing when there was nothing to reconcile.
Used by: The user reading the `dev:done` completion output; it tells them whether they still need to `git pull`.
Depends on: Task 1 (consumes `RECONCILE_MSG` and `primary_branch`).
Files: plugins/dev/skills/done/SKILL.md (modify Step 8)
Interfaces:
- Consumes: `RECONCILE_MSG` (`ff:<sha>` | `refadvanced:<sha>` | `uptodate` | `reminder` | `reminder-nested`) and `primary_branch`, both from Task 1. `INTEGRATION` from stage top.
- Produces: nothing — terminal task.

Implementation steps:
1. In Step 8, after the `Tech debt:` line handling (the paragraph ending at current line 366) and before the product-plan prompt block, add a subsection "Primary-checkout reconciliation line" describing that the completion display carries one line derived from `RECONCILE_MSG`, and that the `uptodate` case (already current — a no-op or already-pulled cycle) prints **no** line, per the spec's "nothing to reconcile → no reminder needed."
2. Provide this exact mapping as the mechanism (place it in the block that renders the `✓ <feature> cycle complete` summary, after the tech-debt line):

    ```bash
    case "$RECONCILE_MSG" in
      ff:*)            echo "  Primary checkout fast-forwarded to ${RECONCILE_MSG#ff:} — no manual pull needed." ;;
      refadvanced:*)   echo "  Primary checkout's local main advanced to ${RECONCILE_MSG#refadvanced:} — working tree on ${primary_branch:-a detached HEAD} untouched." ;;
      reminder)        echo "  Primary checkout left unchanged (dirty or diverged) — run \`git pull\` on main when ready." ;;
      reminder-nested) echo "  Primary checkout not auto-reconciled (nested cycle) — run \`git pull\` on $INTEGRATION when ready." ;;
      uptodate)        : ;;  # already current — print no line, no reminder
    esac
    ```
3. Keep the wording consistent with the existing terse two-space-indented display lines (`  PR #N merged…`, `  Decision log: …`). Do not introduce a new heading or blank line — it is one more line in the same summary block.

## Edge Cases
| Edge case | Handled in | Approach |
|-----------|-----------|----------|
| Primary on a non-integration branch | Task 1 (`else`/different-branch path) | `git fetch origin main:main` advances the local `main` ref only; checked-out branch and working tree untouched. Reports `refadvanced`. |
| Primary dirty (tracked changes on `main`) | Task 1 (`primary_dirty` check) | Skip the fast-forward entirely → `reminder`. `--untracked-files=no` scopes dirtiness to tracked changes per spec. |
| `main` diverged from `origin/main` | Task 1 (`merge-base --is-ancestor` false → `reminder`; and fetch-refusal → `reminder`) | No fast-forward possible; defer to manual pull, mutate nothing. |
| Primary already up to date | Task 1 (`local_main == origin_main` → `uptodate`) | No-op; Task 2 prints no line, no reminder. |
| Primary in detached HEAD | Task 1 (`primary_branch` empty → `else` path) | Treated as "not on main"; advance the `main` ref via `fetch origin main:main` if it exists, never check anything out. `primary_branch:-a detached HEAD` in the report. |
| Legacy in-place cycle (`worktreePath` null) | Task 1 (placement) | Block is never reached — legacy path returned to Step 8 before the worktree-removal section. No behavior change. |
| Nested cycle (`INTEGRATION` = parent branch) | Task 1 (`INTEGRATION != main` → `reminder-nested`) | Reminder only; no auto-reconcile of the primary tree. |
| Overlap: different branch AND diverged | Task 1 (fetch exit code decides) | `fetch origin main:main` refuses the non-fast-forward, exits non-zero → `reminder`; report never falsely claims "ref advanced." |
| `merge --ff-only` refused by an untracked-file collision | Task 1 (`|| RECONCILE_MSG="reminder"`) | Falls back to `reminder`; primary tree untouched. |

## Out of Scope
- Nested-cycle auto-reconcile (reminder only, per spec).
- The legacy in-place path (already reconciles via its existing `pull --ff-only`).
- Any change to how stages push to `$INTEGRATION`, or to the worktree model.
- Reconciling any branch other than the integration branch, or any other local branch.
- Adding a network `fetch` for the on-`main` fast-forward — the shared `origin/main` ref is already current from `push_integration`; a redundant fetch is deliberately avoided.
