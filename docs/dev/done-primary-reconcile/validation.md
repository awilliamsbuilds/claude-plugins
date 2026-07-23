# done-primary-reconcile — Validation Report
*Branch: feature/done-primary-reconcile · 2026-07-23*

## Summary
Loops run: 1 / 3
Final status: clean (no open P1/P2/P3)

Reviews were dispatched as two parallel fresh `general-purpose` subagents (code review +
security review), each seeing only the `afec9ba..1dc5971` diff, spec.md's Success Criteria, and
plan.md's task list — deliberately excluding this session's history for objectivity. Neither
found any P1 or P2 issue.

## Issues Resolved
### Loop 1
- **P3 — Stale SHA in the `refadvanced` report** (raised by both reviewers). `origin_main` is
  snapshotted before `git fetch origin main:main`; a concurrent push between the snapshot and the
  fetch would make the Step 8 line name a commit the ref no longer points at. → Fixed: the
  `refadvanced` token now reads the ref's actual post-fetch tip
  (`rev-parse refs/heads/main`, falling back to `$origin_main`), so the reported SHA always
  matches what the ref advanced to. This directly upholds the spec's Open Question intent
  ("reported outcome always matches what actually happened").
- **Nit — Inconsistent output suppression** (code review). `fetch` suppressed its stderr but
  `merge --ff-only` printed its "Updating…/Fast-forward" summary to stdout. → Fixed: added `-q`
  to `merge --ff-only`.

## Issues Remaining
### P1 Open
- None.

### P2 Open
- None.

### P3 Open
- None.

### Nits Surfaced
- **Duplicated `uptodate`/`reminder` ladder** across the on-`main` and off-`main` branches
  (code review). Not applied — the reviewer noted it is "fine as-is for a prose-plus-shell skill
  (readable top-to-bottom)." Local, contained, no carrying cost. Dropped, not recorded as debt.

## Notes
- **A code-review P3 was investigated and rejected as a false positive.** The reviewer proposed
  adding a `*)` default arm to the Step 8 `case` so an "unexpected" `RECONCILE_MSG` still prints a
  reminder. Tracing the full skill shows this would be a regression: on the **legacy in-place
  path**, Step 7's reconcile block is skipped entirely, so `RECONCILE_MSG` is *unset* when Step 8
  runs, and the empty→no-match→prints-nothing behavior is the intended legacy result (legacy
  already reconciled the primary; the spec requires no reminder there). A `*)` reminder default
  would nag every legacy cycle, breaking the "legacy behavior identical to today" success
  criterion. The reviewer lacked the legacy-path context. Rather than change behavior, added an
  anti-regression comment on the `case` explaining why there is deliberately no default arm — so a
  future maintainer (or reviewer) doesn't reintroduce the bug.
- Both reviewers independently confirmed: no command injection (no variable reaches a command
  position; git verbs take only string literals), all `[ … ]` operands quoted, and the three
  safety guarantees (no merge commit, no forced update, no mutation of a dirty/non-`main` tree)
  hold structurally via `--ff-only` and a plain `fetch main:main` refspec.
- Edited shell re-checked with `bash -n` — both the Step 7 reconcile block and the Step 8 `case`
  parse cleanly after the edits.
