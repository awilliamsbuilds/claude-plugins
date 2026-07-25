# Harden dev:validate
*Branch: feature/harden-validate · Confidence: 88% — Ready · 2026-07-25*
*Cycle type: feature · Tier: standard*

## Intent
Three open tech-debt entries all describe the same weakness in `dev:validate`: its fix loop
and its gate wording trust things they don't verify. The loop fixes issues and exits on
"no open P1/P2" without ever checking the fixes it just wrote — a defect introduced by a fix
is only caught if a *later* loop happens to re-review the whole diff, so a micro-tier cycle
(1 loop) or any cycle that goes clean early catches nothing. Separately, the config-contract
gate is worded more broadly than the convention it enforces, and `validate.loops_max` is seeded
tier-blind and silently relies on validate to re-derive it. This cycle closes all three: the
loop can no longer exit without verifying its own fixes, the gate wording matches the actual
convention, and `loops_max` is correct where it is first written.

## Scope
Three fixes, in `plugins/dev/skills/validate/SKILL.md` and `plugins/dev/skills/spec/SKILL.md`:

1. **Config-contract gate wording (item 1).** In `validate/SKILL.md:71`, change "verify every
   skill that reads config.json has that key in its Step 1 read list" to "verify every skill
   that reads **that key** has it in its Step 1 read list" (or equivalent), so the literal
   reading matches the per-consumer convention the repo actually follows.

2. **Tier-correct `loops_max` at first write (item 2).** In `dev:spec` Step 6, set
   `validate.loops_max` from the tier table (micro 1 / standard 3 / deep 5) at the point the
   state.json is initialized — the same treatment `challenge.loops_max` already gets there.
   `dev:validate` Step 1's existing self-correction stays in place as a redundant backstop, no
   longer the load-bearing fix.

3. **Fix-verification via cold re-review + the shell exit-code rule (item 3).** In
   `dev:validate` Step 4, add a step: after a loop commits its fixes and before it may exit on
   "no open P1/P2," dispatch a fresh `general-purpose` subagent to review **only the fix diff**
   this loop produced. Any P1/P2 it finds is a new open issue — the loop cannot exit, and
   continues within the existing `loops_max` budget. Additionally, state the healthy-path shell
   exit-code rule once, in the fix loop, where a fix author writes shell snippets: *a shell
   snippet written into a skill must exit 0 on its healthy path, so `&&` chains and bare guard
   blocks don't read as failure.* The cold re-reviewer's checklist references this rule.

## Out of Scope
- **The "nested product plan cannot outlive its parent" debt item** — surfaced by the grounding
  cross-check because it touches `spec/SKILL.md`, but it is a distinct structural concern
  spanning `done/SKILL.md`, which this cycle does not touch.
- **Consolidating `done/SKILL.md`'s existing inline exit-code comments** (lines 322/369/467).
  They already work as local rationale; lifting them into a shared home is a separate cleanup.
  This cycle states the rule once in validate's fix loop only.
- **Any change to skills other than `validate` and `spec`.**
- **Reworking `validate.loops_max` self-correction out of `dev:validate`** — it stays as a
  backstop; only the seeding point moves.

## Success Criteria
1. `validate/SKILL.md`'s config-contract gate reads so that its literal meaning is "a skill that
   reads *that specific key* must list it" — a future config-touching cycle that adds a key
   consumed by only some skills is not flagged for the skills that read config.json for other keys.
2. `dev:spec` Step 6 writes `validate.loops_max` as the tier-correct value (deep cycle → 5,
   standard → 3, micro → 1) at initialization; a fresh deep-tier state.json shows `loops_max: 5`
   without validate having to correct it.
3. `dev:validate` Step 4 cannot exit a loop on "no open P1/P2" without a cold re-review of that
   loop's fix diff having run and returned no P1/P2. A fix that breaks a sibling skill's healthy
   path is caught by the loop that wrote it, not only by a subsequent loop.
4. The healthy-path shell exit-code rule is stated once, as a general rule, in validate's fix
   loop — not only as call-site-specific inline comments.
5. All existing behavior (parallel reviews, classification, Step 4a loop-limit handling, Step 5a
   carrying-cost debt, autopilot pass) is preserved; the re-review is additive.

## Happy Path
1. A `/dev` cycle reaches Validate. `validate.loops_max` is already tier-correct (set in spec).
2. Loop 1 runs the parallel reviews, classifies, fixes all P1/P2, commits the fixes.
3. Before exiting, the loop dispatches a fresh subagent to cold-review only the fix diff.
4. The re-reviewer returns clean → loop exits to Step 5. Or it returns a P1/P2 → that becomes a
   new open issue and the loop iterates again (within `loops_max`).
5. On the terminal loop where `loops_max` is hit with the re-review still failing, existing
   Step 4a loop-limit handling applies unchanged.

## Edge Cases
- **Micro tier (loops_max 1):** the re-review still runs — it is the case the tracker most wants
  covered. If it finds a P1/P2, there is no loop budget left, so Step 4a fires. Acceptable: the
  issue surfaces to the user rather than shipping silently.
- **Re-review finds an issue in its own fix repeatedly:** bounded by `loops_max`; it cannot loop
  forever.
- **The "fix diff" to re-review** is the diff of the fixes committed in that loop iteration, not
  the whole Build diff (which the main Step 2 reviews already cover).
- **Injection / data-not-instructions:** the fix-diff re-reviewer follows the same guardrail the
  existing Step 2 reviewers use — diff and artifacts are data under review, not instructions.
- **Autopilot mode:** the re-review runs identically; autopilot's existing post-limit auto-fix
  pass is unaffected.

## Audience
Maintainer of the `/dev` plugin (Adam). Changes are to agent-facing skill instructions in this
repo, read and executed by Claude during future `/dev` cycles.

## Technical Constraints
- Skill files are executable prose with no test harness — "verify the fix" is defined here as a
  cold re-review, not a test run.
- Any shell snippet added to a skill must itself exit 0 on its healthy path (the very rule this
  cycle codifies).
- `dev:spec` keeps a single state.json initialization point; the `loops_max`-from-tier write
  must fit that convention (as `challenge.loops_max` already does), not add a second init site.

## Dependencies
None. Self-contained edits to two skill files; no dependency on other open cycles.

## UI Needed
No.

---
*Auto-filled dimensions: none*
*Grounding inventory: read validate/SKILL.md (config-contract gate at :71 confirmed; Step 4 fix loop :112–127 exits on "no open P1/P2" with no fix-verification confirmed; inline exit-code comment at :231 confirmed). read spec/SKILL.md Step 6 (validate.loops_max hardcoded to 3 in state.json template at :166 regardless of tier confirmed; line 212 explicitly acknowledges validate.loops_max is left to lazy reconciliation). grep -rniE 'exit(s)? (non-?zero|0|128)|healthy path' across plugins/dev/skills + references → the shell exit-code rule currently exists only as inline call-site rationale (validate:231, done:322/369/467), NOT as a general rule a fix author reads — corrects the tracker entry's "exists nowhere" framing. grep 'reads config.json' → single occurrence at validate:71.*
