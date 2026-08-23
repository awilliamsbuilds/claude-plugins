# Retro notes — project-scoped-worktree

Observations raised by the user *during* the cycle, recorded here because `dev:reflect` Step 4 asks
for them live at `dev:pr` time — usually a different session. Reflect should fold these into the
retrospective as if raised at Step 4.

## 1. Questions were framed technically instead of as a plain problem and a plain choice

**Dimension:** Spec stage friction.

**What happened.** Across the Spec stage the user rejected three of seven question cards. The
options were written in the repo's own vocabulary — resolution blocks, discovery globs, candidate
ordering, plan slugs — and each question built on the previous answer without restating what was at
stake. On the fourth the user said: *"I don't understand what I'm deciding and why."*

The recovery worked immediately. Same decision, re-framed as: the retro quote describing the real
problem, the one incident where it actually bit (fast-path Milestone 2 built as `entry-adapters`),
the literal output the change would produce, one sentence naming the choice, and a recommendation.
The answer came back in one word.

**The user's own statement of the fix:** *"I want questions to be oriented like that versus being
complex or technical."*

**Cost this cycle:** three discarded question cards, two clarification round-trips, and roughly half
the Spec stage's elapsed time.

**Suggested process fix.** `dev:spec` Step 8's questioning rules say "prefer multiple choice when
options can be enumerated" and "ask about the most impactful unscored dimension first" — neither
constrains *register*. A rule belongs there: lead with the concrete incident, state the choice in
one plain sentence, keep repo vocabulary out of option labels, and recommend one option rather than
presenting a menu when the decision is small. This is a `dev:spec` change, and would apply equally
to `dev:shape` and `dev:plan` gates.

## 2. No way to record a retro observation when it happens

**Dimension:** Reflect stage.

**What happened.** The observation above surfaced at Spec. `dev:reflect` Step 4 collects user
observations by asking live, and runs from `dev:pr` Step 5d — typically a later session, after a
`/clear`. Nothing in the workflow buffers an observation raised mid-cycle, so it survives only if
the human still remembers it at PR time. This file exists because there was nowhere else to put it.

**Cost:** retros capture what the user recalls at PR time, not what actually happened during the
cycle. Silent and unmeasurable — the counters cannot see an observation that was never recorded.

**Suggested process fix.** A per-cycle observations buffer at
`docs/dev/<feature>/retro-notes.md`, written by any stage when the user raises process friction, and
read by `dev:reflect` Step 4 before it asks its question — mirroring how `debt-pending.md` already
buffers close-intent from Spec through to `dev:done` Step 6a. Reflect should weigh this against the
carrying-cost test rather than adopting it automatically.
