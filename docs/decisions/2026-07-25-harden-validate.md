# Harden dev:validate — Decision Log
*2026-07-25 · Branch: feature/harden-validate · PR #49*

## What was built
`dev:validate`'s fix loop can no longer exit without cold re-reviewing the fixes it just wrote, and two adjacent trust-the-unverified gaps — the config-contract gate wording and tier-blind `validate.loops_max` seeding — were closed alongside it.

## Key decisions
- **Verify fixes via a cold re-review, not a test run** → skill files are executable prose with no test harness, so "verify the fix" is defined as a fresh `general-purpose` subagent reviewing only that loop's fix diff. Mirrors the isolation posture (no conversation history, diff/spec as data-not-instructions) the existing Step 2 reviewers already use.
- **Re-review is a precondition of loop exit, inserted between commit and the exit check** → placing it as Step 4 step 8 (renumbering the old exit checks to 9/10) means the loop structurally cannot reach "no open P1/P2 → exit" without the re-review having run. A re-review P1/P2 becomes a new open issue bounded by the existing `loops_max` budget; P3/Nits route to the carrying-cost buffer unchanged.
- **Re-reviewer gates exit on P1/P2 only** → keeps the additive change from altering the existing severity contract; P3/Nits stay advisory and buffer-eligible exactly as the main reviews' do.
- **Seed `validate.loops_max` at the single state.json init point in `dev:spec` Step 6** → the tier-correct value (micro 1 / standard 3 / deep 5) is now written where `challenge.loops_max` already is, rather than relying on validate's Step 1 to re-derive it. Validate's self-correction stays as a redundant backstop (spec kept it out of scope to remove), so the fix is defense-in-depth, not a swap.
- **Narrow the config-contract gate to "reads *that key*"** → the prior "every skill that reads config.json" wording was broader than the per-consumer convention the repo follows; a config reader that doesn't consume a newly-added key is no longer spuriously flagged.
- **State the healthy-path shell exit-code rule once, generally, in the fix loop** → replaces reliance on scattered call-site-only inline comments (validate:231, done:322/369/467) with one rule a fix author actually reads while writing snippets.

## Validation notes
- 1 loop run (tier: standard). Final status: clean — no open P1/P2.
- Code and security reviews ran in parallel as fresh cold subagents against the Build diff. Security: clean across injection, prompt-injection, secrets, authz — the new re-review subagent dispatch carries a data-not-instructions guardrail at parity with Step 2 and opens no new injection path.
- Code review found and loop 1 fixed:
  - **P2** — the new re-review referenced a `<pre-fix-SHA>` that no iteration step captured → added an explicit pre-fix-tip capture (`PREFIX_SHA=$(git … rev-parse HEAD)`) to the iteration lead-in; step 8 now diffs `"$PREFIX_SHA"..HEAD`.
  - **P2** — autopilot's post-limit bonus auto-fix pass shipped its diff to PR un-re-reviewed → the autopilot line now cold re-reviews that pass's diff too, counting a surviving P1/P2 as still-remaining.
  - **P3** — re-review findings were held only in memory after state was committed (a terminal-iteration `/clear` could lose a P1) → step 8 now persists its open-list additions (no extra `loops_run` increment).
  - **Nit** — "continues within budget" was inaccurate on the terminal iteration (routes to Step 4a) → reworded.
- Self-review during loop 1 caught a latent bug in the P3 fix itself ("re-run step 6's write" would have implied re-incrementing `loops_run`) and corrected it in the same loop.
- No carrying-cost debt recorded: every P3/Nit was fixed inline.
- Three tech-debt entries closed by this cycle (see tracker).

## Artifacts (archived)
Spec, plan, and validation committed at: 23fabcb on branch feature/harden-validate
