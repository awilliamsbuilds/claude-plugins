# Debt Pending — spec-review-autoloop

Buffered backlog/debt items for this cycle. `dev:done` Step 6a flushes `## To Record` into
`docs/backlog/` and executes each `## To Close` close-intent, then Step 7 deletes this file. Nothing
else reads it.

## To Record

## To Close

- debt-plan-challenger-errored-dispatch-undefined — the plan challenger now loops in gated mode too, so Step 7a gains the errored-dispatch rule as a marked mirror of dev:spec Step 12a (spec Scope 7)
- debt-plan-end-excludes-challenger-loop — plan_end is re-stamped after Step 7a's loop exits (spec Scope 8)
