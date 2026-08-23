# Debt Pending — retro-inside-pr

Buffered backlog/debt items for this cycle. `dev:done` Step 6a flushes `## To Record` into
`docs/backlog/` and executes each `## To Close` close-intent, then Step 7 deletes this file. Nothing
else reads it.

## To Record

## To Close

- backlog-reflect-before-pr-merge-retire-legacy-commands — the source item for this cycle. Moving the decision log and retrospective into `dev:pr` (pre-merge, post-`gh pr create`) puts both in the cycle's own PR diff, and this cycle additionally moves Steps 4 and 4a so no reviewable content edit lands post-merge. The three merge-tail retro inputs are explicitly dropped with reasons recorded in the spec, satisfying the item's "explicitly deferred or explicitly dropped with a reason."
- debt-autopilot-pr-re-entry-not-idempotent — folded in because this cycle actively worsens it: `dev:pr` gains a decision-log write and a `dev:reflect` invocation, so a re-entry on a cycle whose `artifacts.pr_url` is already set would duplicate `docs/decisions/<file>.md` and append a second `## Retrospective`. The cycle must state one guarded re-entry rule for `dev:pr` regardless, so closing the item is the same work.
- debt-p9-slug-regex-allows-leading-dash — folded in because its fix lands in `reflect/SKILL.md:205`, one of the lines this cycle already edits, and in `fix/SKILL.md`, already in the file surface. Severity P2: §P9's allowlist `^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$` puts `-` inside the class, so `-foo/bar` passes despite both §P9 and `reflect/SKILL.md:205` claiming it rejects a leading dash — an argument-injection vector into `gh --repo`. The anchored form already proven in `dev:fix` becomes canonical in §P9, and `dev:fix` drops its local divergence note.
