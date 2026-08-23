# Plan Linkage — Validation
*Branch: feature/plan-linkage · 2026-08-23 · Base: 234b224*

## Summary

Final status: **passed**
Loops run: 3 of 3 (standard tier)
Reviewers: `/dev:review diff` + `/dev:secure diff`, dispatched cold and in parallel; each fix loop's
own diff cold re-reviewed before the loop could exit.

| Severity | Found | Resolved | Open |
|---|---|---|---|
| P1 | 0 | — | 0 |
| P2 | 2 | 2 | 0 |
| P3 | 12 | 12 | 0 |
| Nit | 11 | 11 | 0 |

## Build

No build system: no `package.json`, `Makefile`, `pyproject.toml`, `Cargo.toml`, or `go.mod` in the
repo (B1–B5 all miss). The repo is markdown skills plus one stdlib-only Python tool, so the
substitutes actually run were:

- `python3 -m py_compile plugins/dev/skills/debt/viewer.py` — clean
- `python3 plugins/dev/skills/debt/test_viewer.py` — **89 tests, OK (2 skipped)**
- every tracked `*.json` parsed with `json.load` — all valid

Nothing this cycle touched is executable, so the suite is a regression guard rather than a check of
the change itself.

## P2 — both fixed

**1. Path (C) linked a cycle to an already-checked item, or to a finished plan.** (code review)
`dev:spec` Step 6 path (C) enumerated three non-writing cases and did not exclude
`item-checked == true` or `next-item-name == null`. Consequences: `/dev:spec "<an already-ticked
item>"` would set `product_plan`, and `dev:done` Step 3 would bump the cycles-completed count with no
box to tick; on a plan whose every box is already `[x]`, Step 3's completion detection would fire and
Step 3b would **delete the plan file and close the promoted source item** on a cycle that completed
nothing — the unrecoverable direction. Fixed by adding a fourth non-writing case at the writer, using
two fields §L1 already returns (no second lookup). `dev:done`'s mechanics were out of scope, so the
guard belongs at the writer, not the reader.

**2. `plan-path` came from an unallowlisted filesystem name and reaches an interpolated `git rm -f`.**
(security review) Paths (A) and (B) guarantee `product_plan`'s slug matches `^[a-z0-9][a-z0-9-]*$` by
construction; path (C) was the first producer to populate the key from a globbed filename. That value
reaches `dev:done` Step 3b as `git rm -f "<plan-path>"` (double-quoted — `$(…)` still expands) and
Step 3a as an **unquoted** `git add <plan-path>`, and is grepped against backlog front-matter where
regex metacharacters could false-match an unrelated item. Fixed in two places: §L1 now requires the
matched file's stem to satisfy the same allowlist and skips a file that does not, so path (C) can
never write a value paths (A)/(B) could not have; and `done/SKILL.md`'s `git add` is now quoted.

## P3 and Nits — all resolved

Fix loop 1 (`3e10698`) also closed: §L4's cross-plan examples contradicting the same-plan rule it
states; §L4's "exactly one applies" being false for an all-ticked plan (now first-match ordering);
§L4 printing a plan display name §L1 never produced (now a `plan-name` field); `dev:done`'s Linear
strip rule not naming `<ID>`'s source and applying unconditionally (now `linear_issue.id` verbatim,
unchanged-match first); `dev:spec` Step 6's "create the branch before asking any questions" opening
contradicting the new asking check; `dev:fix`'s unattended claim vs Step 2b's question; the `PRIMARY`
derivation claiming a guard it lacked; and `cycles-completed` being echoed "as written".

Fix loop 2 (`c457aa0`) reconciled the count drift that fix caused — adding the guard to `dev:spec`
falsified "the 12 stage-header sites carry no guard" in `dev:fix` and `dev:secure` and staled
`debt-primary-cd-failure-unchecked` — and specified §L4's rendering when `cycles-completed` is `null`.

Fix loop 3 (`50dc5c0`) plus `e0f6bb4` corrected path (C)'s consequence sentence (copied from the §L2
collision case, it told the operator to tick a box that by definition does not exist), `dev:review`'s
"fourth guarded derivation" enumeration, and a `dev:fix` sentence that asserted a question count
falsified two hundred lines above it.

## Notes

**One planned wording deviated, deliberately.** `plan.md` Task 2 step 4 said to keep "never run both"
as `dev:spec` Step 6's precedence phrase. The built text reads **"never run more than one"** — with
path (C) the chain has three arms and "both" is no longer true. `spec.md`'s Technical Constraints
still quotes the old phrase, as the record of what was specified.

**A security P3 was closed by the P2 fix rather than separately.** The security review noted that path
(C) extends `dev:done` Step 3b's delete-and-close authority to cycles that did not author the plan.
With P2 #1 fixed, an adopted cycle can only reach Step 3b's project-complete path by *itself*
completing the plan's last unchecked item — which is the intended behavior, not the blast-radius
widening the finding described. No debt recorded.

**Carried to `dev:pr` Step 5a, not fixed here.** `CLAUDE.md`'s Component Registry describes `dev:review`
as carrying "the repo's fourth guarded `PRIMARY` derivation" (now one of five) and does not record that
`dev:spec` Step 6 gained the guard. The registry is regenerated at PR, which is where those belong.

**`debt-primary-cd-failure-unchecked` was partially paid.** `dev:spec` Step 6's derivation gained the
non-empty guard because the plan-order check made it a *reader* of `$PRIMARY` before any
`git -C "$PRIMARY"` command — without it, an empty value degrades a safety check to silence instead of
failing loudly. The item's `files:` list and body were updated to 11 remaining sites; independently
recounted by the reviewer as 5 guarded / 11 unguarded.
