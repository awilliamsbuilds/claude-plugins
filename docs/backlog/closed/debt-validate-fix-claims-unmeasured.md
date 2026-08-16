---
type: debt
scope: repo
status: closed
closed: 2026-08-16
closed_by: retire-legacy-commands
severity: P3
first_recorded: 2026-08-01
cycles: [reflect-pr-base-explicit-target]
recurrence: 1
possibly_related_to: debt-validate-fix-loop-verification
files:
  - plugins/dev/skills/validate/SKILL.md
---

**What's wrong:** `dev:validate` Step 4's fix loop has no rule requiring that a factual claim about
command or tool behavior written into a fix be **measured** before the loop exits. Fixes assert
behavior instead of running the command, and the assertion then ships as skill prose that a later
reader treats as verified. In `reflect-pr-base-explicit-target` this fired in three consecutive
loops: loop 1's fix asserted "`$PRIMARY` is never `$WORKDIR`" (false on a legacy in-place cycle,
where the header's second resolution case makes them the same directory — a P1); loop 1 also wrote
"`gh` never resolves the repo from the git remotes" (false — without `--repo` it does exactly that,
and the very next clause described the resolution it denied — a P2); loop 2's rationale for
`git rev-parse --git-common-dir` was backwards and stood until loop 3 actually ran the command and
measured it (absolute from a linked worktree, relative from the primary checkout). Each was caught
only by the *next* loop's cold re-review of the fix diff, which is one loop of latency and, at the
loop cap or on a micro tier, no catch at all.

This is the successor to the closed `debt-validate-fix-loop-verification` (closed 2026-07-25 by
`harden-validate`), which added the cold re-review of each loop's own fix diff. That mechanism works
— it caught all three of these. What is still missing is the cheaper upstream rule: the fix author
should measure the claim rather than rely on a reviewer to disprove it.

**Why deferred:** Surfaced at `dev:reflect` Step 6; the user chose to record rather than patch. The
edit is a rule in `dev:validate` Step 4 and wants designing once — it needs a definition of which
claims are in scope (claims about *observable command behavior*, not claims about intent or design)
so it does not become a blanket "run everything" that the fix loop learns to skip.

**Done looks like:** `dev:validate` Step 4 states that any claim about what a command or tool does,
written into a fix, must be verified by running it and recording the observed result — with the
scope of "claim" defined narrowly enough to be followed. A fix that asserts wrong tool behavior is
caught by the loop that wrote it, not by the next one.
