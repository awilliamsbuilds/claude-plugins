# Debt Pending — autopilot-resume-stage

Buffered backlog/debt items for this cycle. `dev:done` Step 6a flushes `## To Record` into
`docs/backlog/` and executes each `## To Close` close-intent, then Step 7 deletes this file. Nothing
else reads it.

## To Record

## To Close

- debt-autopilot-handoff-stage-not-explicit — this cycle is the fix: it settles the resume-stage
  interface so a handoff cannot re-run an approved stage, which is exactly the item's "Done looks
  like."
