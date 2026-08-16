---
type: debt
scope: repo
status: open
severity: P3
first_recorded: 2026-08-11
cycles: [autopilot-handoff]
recurrence: 1
files:
  - plugins/dev/skills/dev/SKILL.md
---

**What's wrong:** Three reference lines state flatly that the `no-ui` launch flag skips Shape — all
three now in `dev/SKILL.md`: Step 1's argument line ("set mode to no-ui; Shape stage will be
skipped"), the `/dev no-ui` row in the Invocation Reference, and Step 1a's tier rule "no-ui: Shape
is skipped, for any tier" (which arrived there when `dev:start` was retired into `/dev list`; the
same sentence, same defect, one file instead of two). But `spec/SKILL.md` Step 12 makes the spec's own `## UI Needed` authoritative "whether
or not the cycle was launched with the `no-ui` flag," and `dev/SKILL.md`'s own next-stage logic
already reads `skipped[]` rather than the flag. A user whose spec resolves `UI Needed: Yes` gets
Shape despite having passed `no-ui`.

**Why deferred:** Pre-existing contradiction. The autopilot-handoff cycle brought `dev:autopilot`
into line with the authority (Step 3 now reads `skipped[]`, and its Invocation entry is hedged),
which leaves these three as the remaining stale statements — but editing reference surfaces for
a flag this cycle doesn't otherwise touch is scope creep.

**Done looks like:** All three lines describe `no-ui` as a request that Spec's `## UI Needed`
adjudicates, matching `spec/SKILL.md:478` and `dev:autopilot`'s hedged Invocation entry. A reader
comparing `/dev no-ui` against `/dev:autopilot no-ui` gets one promise, not two.
