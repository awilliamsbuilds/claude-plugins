# Challenger Loop Economics — Decision Log
*2026-08-22 · Branch: feature/challenger-loop-economics · PR #89*
*Handed off to autopilot at Plan*

## What was built

`dev:spec` Step 12a's Blocker definition was tightened so the autopilot revision loop exits when its findings stop being worth another round, together with the three consequences that follow from that change.

## Key decisions

**Blocker becomes a two-member class rather than a narrowed single bar** → tightening to "a builder following this literally ships something broken" alone would have demoted the right-sizing criterion to a Concern, and a Concern can never STOP. That would have silently deleted Step 12a's scope-blocker exception, which bypasses the loop entirely. The right-sizing member is carried over so the exception paragraph keeps working byte-unchanged.

**The exit rule is stated as a consequence, not built as a mechanism** → the loop was already gated on blockers existing, and Step 12a already said concerns never extend it. Once a bookkeeping finding classifies as a Concern, the existing rule ends the loop with no new step, no new counter, and no second severity concept. The spec made "no separate exit test" a success criterion precisely so a backstop couldn't creep back in.

**A mis-classifying reviewer defeating the exit was accepted, deliberately** → the alternative — tightening *and* adding a backstop test — reintroduces the second severity concept. The failure is visible at Reflect instead: high `challenge.blockers` against low `spec_revisions`, persisting across cycles.

**The errored-dispatch STOP is not mode-split** → `dev:validate` already answers the same question with "A reviewer that cannot run stops the stage," and inventing a second answer for the spec challenger would have been a divergence with no reason behind it. A standard-mode STOP is cheap to recover from: `spec.md` is committed and `stage` is still `"spec"`, so re-running `/dev:spec` re-enters at Step 12a through Step 1's existing resume-mid-approval check. Letting the Step 13 gate render without a verdict would instead invite approving a spec that got no cold review at all.

**`null` was chosen over `0` for an errored round's counters** → `0` already means "a round ran and found nothing." Overloading it would have made the two cases indistinguishable at Reflect, which is exactly the reconstruction the value exists to prevent.

**`applied` keeps its meaning and `applied_concerns` is added beside it** → renaming or repurposing `applied` would have broken every `state.json` written before this cycle. Blocker-driven fixes are the subtraction. Purely additive, and `dev:reflect` reads a missing key as "not recorded" rather than `0`.

**`dev:plan` Step 7a's Blocker definition was left byte-unchanged** → grounded in history rather than symmetry: plan-challenger blockers across recorded cycles run 0, 1, 1, 0, 0, never above 1. The runaway is spec-only. Plan's lenses are mechanical where spec's are interpretive, so rewording a precise mechanical test into build-breaking language would only make it vaguer. The divergence is now stated in adjacent prose so a future editor doesn't "reconcile" it away. The counter *shape* change does apply to both — shape symmetry, not severity.

**The deep-tier cap stays at 5** → named as an open judgment in the source item and disposed of here rather than left open. The kind-based exit is now what stops the loop, so the cap is a backstop that rarely binds; lowering it would add a second mechanism doing the same job, and rounds 1–2 of the incident cycle caught load-bearing defects.

**One knowing departure from the approved plan**, made in the fix loop: Task 9 said to place the errored-dispatch bookkeeping "in the same paragraph" as autopilot's spec-challenger rule. It was kept as an adjacent paragraph with a `**Spec challenger — …**` lead instead — folding ~200 words into an already-long paragraph would have hurt readability, and the retitle satisfies what the cross-references actually require.

## Validation notes

- 3 loops run (tier: standard). Final status clean; no P1 at any point.
- **P2** — the reworked verdict-format example left concerns untallied in the header, so a verdict of 0 blockers and 5 concerns could have rendered as four `✅`s above five real findings. Resolved by defining the header rule in prose rather than leaving it inferable only from the example.
- **P2** — autopilot's restatement dropped the canonical's "once per stage, not once per round" qualifier, in the one mode where the distinction bites: a deep-tier run would have granted 5 retries instead of 1. Resolved by restoring the qualifier and stating why the scoping matters there.
- **P3 (defect-class)** — the errored-dispatch paragraph was cited by two files as living in "the spec-challenger section" while sitting as its sibling. Resolved by retitling.
- **P3 (defect-class, from the security reviewer)** — the new rule overlapped the pre-existing **Fallback** rule with no stated precedence; a refused dispatch could have taken the fallback branch and written `run: true` over a review that never returned. Resolved by pinning precedence on whether a verdict came back, and changing the trigger wording that caused the collision.
- **Nits accepted and fixed:** bare counter names mid-clause, two mode-behaviour paragraphs naming only `applied`, a word used in two senses one clause apart, and a stale literal in a registry row.
- **One nit recorded rather than fixed:** `dev:plan` Step 7a has no errored-dispatch rule, so an errored plan-challenger dispatch leaves the previous round's counters standing. Buffered as `plan-challenger-errored-dispatch-undefined` — the spec scoped the rule to the spec challenger deliberately, so fixing it here would have crossed a scope line.
- **Build:** no build system detected (B5/O3). Recorded as such, never as a pass — this surface is prose-only with no test runner.

**Worth recording, since the cycle is about exactly this:** loop 1 carried all the substance; loops 2 and 3 were single nits each, both consequences of loop 1's own edits, and loop 3 spent a full cold dispatch re-reviewing a one-word synonym swap in a registry description no skill executes. That is `dev:validate`'s own loop running its budget on bookkeeping — the same shape this cycle fixed one stage earlier at Spec. Noted rather than acted on: the spec did not scope Validate's loop economics.

## Artifacts (archived)

Spec, plan, and validation committed at: c6e1b89 on branch feature/challenger-loop-economics
