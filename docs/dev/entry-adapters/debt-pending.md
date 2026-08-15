# Debt Pending — entry-adapters

Buffered backlog/debt items for this cycle. `dev:done` Step 6a flushes `## To Record` into
`docs/backlog/` and executes each `## To Close` close-intent, then Step 7 deletes this file. Nothing
else reads it.

## To Record

## To Close

- debt-fix-tail-guard-stale-when-offline — this cycle rewrites `skills/fix/SKILL.md`'s argument parse and is already in the merge tail; capturing the fetch exit status is a few lines with a pre-written fix
- debt-fix-tail-multiple-open-prs-unchecked — same file, same edit session; the tail's prose already promises the multiple-open-PR stop that the snippet does not implement
