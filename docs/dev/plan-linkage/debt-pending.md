# Debt Pending — plan-linkage

Buffered backlog/debt items for this cycle. `dev:done` Step 6a flushes `## To Record` into
`docs/backlog/` and executes each `## To Close` close-intent, then Step 7 deletes this file. Nothing
else reads it.

**One contract divergence, named rather than left to be read as an oversight.**
`../../../plugins/dev/references/tech-debt.md` 's *Who writes what* (under `## Where things live`) scopes `## To Close`
close-intents to `dev:spec`, and its §P4 gives the buffer template, while the one below was written at Build. The **decision** is still
Spec's — `spec.md`'s `## Scope` records this cycle's adoption of the item and requires it be disposed
of explicitly — and this write only transcribes that recorded decision into the buffer the flusher
reads. No producing-stage role is widened: Build originates no close-intent of its own.

## To Record

## To Close

- debt-plan-item-cycles-never-set-product-plan — path (C) sets product_plan automatically, so dev:done Step 3's check-off no longer depends on the operator remembering
