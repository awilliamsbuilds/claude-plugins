# Debt Pending — reflect-pr-base-explicit-target

Buffered backlog/debt items for this cycle. `dev:done` Step 6a flushes `## To Record` into
`docs/backlog/` and executes each `## To Close` close-intent, then Step 7 deletes this file. Nothing
else reads it.

## To Record

## To Close

- debt-reflect-dogfood-pr-base — this cycle is the fix: step 2 gains an explicit `--repo` on both the dogfood and ask-fallback paths, so a fork's `origin` can no longer let `gh` target its upstream
