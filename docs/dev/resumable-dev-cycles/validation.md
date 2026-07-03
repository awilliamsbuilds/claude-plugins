# Resumable Dev Cycles — Validation Report

*Branch: feature/resumable-dev-cycles · 2026-07-03*

## Summary

Loops run: 2 / 5 (Deep tier)
Final status: clean

Reviews dispatched as fresh `general-purpose`/`feature-dev:code-reviewer` subagents, each given only the diff + `spec.md` + `plan.md`, not this session's conversation history.

## Issues Resolved

### Loop 1

- **P1** (code review): `dev:spec` Step 4 wrote `product-plan.md` but never committed it — if the worktree offer was accepted, the uncommitted file would be silently orphaned in the original directory (worktrees only carry committed history). → Fixed: explicit commit added to Step 4, target (main vs. parent branch) conditioned on nesting state.
- **P1** (code review): `dev:pr`'s nested-cycle PR target branch was never pushed to the remote before `gh pr create --base <parent-branch>` — would fail on every nested PR, the primary recursive scenario this feature is built around. → Fixed: explicit `git push origin <parent-branch>` before PR creation when nested.
- **P2** (code review): `dev:spec` Step 2 (product-scale detection) didn't implement nesting at all, contradicting spec.md's own stated design that both Step 2 and Step 4 should support it. → Fixed: Step 2 now routes through the same Nesting Detection result as Step 4.
- **P2** (code review): `dev:done` Step 7 unconditionally ran `git branch -d`, which fails for any worktree-isolated cycle (branch checked out elsewhere) — exactly the case this feature introduces. → Fixed: deletion now guarded on `worktreePath` being unset, deferring to `ExitWorktree`.
- **P2** (security review): the new artifact-path-argument convention had no input validation, inconsistent with the codebase's existing kebab-case feature-naming guarantee, and a latent injection-adjacent risk if fed an untrusted path. → Fixed: added a validation clause (kebab-case regex, no `..` segments, fallback to today's behavior if invalid) to all 6 files that added the convention.
- **P2** (self-identified while fixing #1): the worktree base-ref fallback ("rebase/reset onto the parent branch") was ambiguous — two semantically different operations, no concrete command. → Resolved to a single unambiguous command (`git reset --hard <parent-branch>`, reasoned: a freshly-created branch has zero unique commits, so there's nothing to replay).
- **Minor** (security review): unquoted `--base <target-branch>` in the `gh pr create` template. → Fixed in the same edit as issue #2.

### Loop 2

Verification-only pass confirming all Loop 1 fixes are correct, complete, and introduced no new issues. All 5 (plus the reset-vs-rebase reasoning) confirmed FIXED.

## Issues Remaining

### P1 Open
None.

### P2 Open
None.

### P3 Open
None.

### Nits Surfaced
None.

## Notes

- One assumption remains open but explicitly documented (not a defect): the `reset --hard` reasoning for the worktree base-ref case assumes `EnterWorktree` itself performs no auto-commit when creating a branch. Both `plan.md`'s own Risks and Unknowns and this validation's loop-2 review flag this as worth confirming against actual harness behavior the first time this path is exercised for real, but it's not blocking — the instructions as written are internally consistent and correct under that assumption.
- Two subagent reviews across this cycle's Validate stage encountered the same benign injected-boilerplate pattern seen in earlier cycles (harness system-reminder-style content unrelated to the task). Both correctly disregarded it without requiring intervention — noted for the record, not a real finding.
