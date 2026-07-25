# Debt Pending — harden-validate

Buffer for this cycle's tech-debt writes. `## To Record` holds new entries flushed to the
tracker at `dev:done`; `## To Close` holds bullets naming existing tracker entries this cycle
paid. Format and rules: the `/dev` plugin's `references/tech-debt.md`.

## To Record

## To Close

- "Validate's fix loop never verifies the fixes it writes" — this cycle adds a fix-verification step to Step 4 and states the healthy-path shell exit-code rule once where a fix author reads it.
- "validate's config-contract gate says "every reader" but the convention is "every reader of that key"" — this cycle narrows the gate wording to "every skill that reads that key."
- "validate inherits a stale loops_max that doesn't match the tier" — this cycle derives loops_max from the tier table where it is first written (spec) so validate no longer corrects a stale value.
