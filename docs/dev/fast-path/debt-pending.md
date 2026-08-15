# Debt Pending — fast-path

Buffered backlog/debt items for this cycle. `dev:done` Step 6a flushes `## To Record` into
`docs/backlog/` and executes each `## To Close` close-intent, then Step 7 deletes this file. Nothing
else reads it.

## To Record

## To Close

- backlog-reflect-before-pr-merge — this cycle has to decide where reflection sits for a lane that merges in one motion; answering it for the fast path settles the open question
- debt-dev-stage-jump-has-no-new-session-path — the fast path adds an invocation form to `dev:dev` Step 5a's surface, so it either inherits the inconsistency or fixes it while it is there
- debt-state-advancement-commit-durability — the lane's state model is decided here; whichever way it goes, the durability question is answered rather than left dangling
