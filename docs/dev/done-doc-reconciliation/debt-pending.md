# Debt Pending — done-doc-reconciliation

Buffered tech debt for this cycle. `dev:done` Step 6a flushes this into `docs/dev/tech-debt.md`
and Step 7 deletes it. Nothing else reads it.

## To Record

## To Close

- "The feature slug reaches git commit -m with no character allowlist" — this cycle adds another `git commit -m "… <feature>"` call site in dev:done, so it closes the shape at the source: an allowlist in dev:spec Step 5 and dev:fix Step 3 makes every downstream interpolation (the existing five plus the new one) safe by construction.
