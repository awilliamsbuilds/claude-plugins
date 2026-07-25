# Debt Pending — state-write-mode-audit

Buffered tech debt for this cycle. `dev:done` Step 6a flushes this into `docs/dev/tech-debt.md`
and Step 7 deletes it. Nothing else reads it.

## To Record

## To Close

- "Sweep for gate-path state writes that are dead in autopilot" — this cycle performs the exhaustive audit (every state.json key traced to the mode(s) that write it, gate-only writes moved pre-gate or duplicated into the autopilot path) and ships the preventive mechanism the entry named as deferred.
