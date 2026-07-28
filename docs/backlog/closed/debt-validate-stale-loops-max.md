---
type: debt
scope: repo
status: closed
first_recorded: 2026-07-23
cycles: [harden-validate]
recurrence: 1
files:
  - plugins/dev/skills/validate/SKILL.md
closed: 2026-07-25
closed_by: harden-validate
---

**What's wrong:** On this deep-tier cycle, `state.json`'s `validate.loops_max` was `3` at validate stage entry, but the deep tier's max is `5`. `dev:validate` self-corrected it per the tier table before reviewing, so there was no visible breakage — but the mismatch means some earlier stage (or a config/template default) seeds `loops_max` without reference to the tier, and every non-micro cycle silently relies on validate to re-derive it. If validate's self-correction ever regresses, a deep cycle would cap at 3 loops without anyone noticing.
**Why deferred:** Surfaced by dev:reflect; the user declined the skill change this cycle, and validate already self-heals so there is no immediate breakage.
**Done looks like:** `loops_max` is derived from the tier table at the point it is first written (tier detection in spec), so validate reads a value already consistent with the tier rather than correcting a stale one — and the self-correction becomes a redundant backstop rather than a load-bearing fix.
