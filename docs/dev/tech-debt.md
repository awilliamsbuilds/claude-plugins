# /dev Tech Debt

Deferred items for the `/dev` plugin — things consciously not fixed inline, with enough context
to act on later without re-deriving the finding.

**This file is a temporary holding pen.** Adam wants a proper tech-debt-tracker built into the
`/dev` plugin; until that exists, entries live here. When the tracker ships, migrate these and
delete this file.

Each entry records what's wrong, why it was deferred rather than fixed, and what "done" looks
like. Add new entries at the bottom.

---

## 1. Autopilot doesn't cross-note the spec grounding gate

*Deferred 2026-07-21 · from the spec-grounding-and-clock cycle*

`plugins/dev/skills/autopilot/SKILL.md` (~lines 45–48) describes its own confidence / auto-fill /
stop logic but never mentions the grounding gate added to `dev:spec` Step 7 / Step 8. Its
"auto-fill remaining dimensions" line reads as if inference can clear the path to proceed — which
the gate forbids.

**Behavior is safe.** Autopilot delegates to `dev:spec`, so an unverified as-is claim still
surfaces through autopilot's existing "confidence too low even after auto-fill → STOP" path. The
gate is simply invisible in autopilot's own text.

**Why deferred:** raised as issue #2 in that cycle's code review; judged a documentation gap, not
a blocker.

**Done looks like:** a one-line cross-note in autopilot's Step 2 pointing at the `dev:spec`
grounding gate.

---

## 2. Sweep for gate-path state writes that are dead in autopilot

*Deferred 2026-07-21 · from the spec-challenger cycle*

There is a recurring defect shape in the `/dev` skills: **a `state.json` write specified only on a
standard-mode gate path, silently never executed in autopilot, while `dev:reflect` reads the
resulting counter with no mode qualification.** The counter then reads clean on every autopilot
cycle regardless of what actually happened.

Three confirmed instances so far, all the same shape:

| Counter | Where the write lived | Consequence |
|---|---|---|
| `challenge.applied` | delegated to spec Step 13, whose autopilot branch is a pass-through | autopilot cycles always reported `applied: 0` |
| `challenge.dismissed` | inside Step 13 Path A, gated on "if changes are requested" | a fully-dismissed verdict could never be recorded |
| `metrics.spec_revisions` | spec Step 13's gate path only, while autopilot revises specs via silent backtrack | reflect's self-declared "strongest single signal" pinned at 0 in autopilot |

The first two were caught in spec-challenger's own Validate. The third was pre-existing, predating
that cycle, and **was fixed in the same session** (`autopilot/SKILL.md` backtrack rule now
increments it; `reflect/SKILL.md` wording de-coupled from standard mode).

**What remains:** the sweep. Only two counters were checked beyond the three above —
`metrics.visual_screens_shown` (fine: written in shape Step 10, before the gate) and
`validate.loops_run` (fine: mode-independent). Every other counter across the nine `dev:*` skills
is unverified.

**Why deferred:** the confirmed instance was worth closing immediately; an exhaustive audit of
every state write across nine skills is its own scoped piece of work, not a reflect-gate patch.

**Done looks like:** every `state.json` key written by a `dev:*` skill is traced to the mode(s)
that write it, gate-only writes are either moved pre-gate or duplicated into the autopilot path,
and any counter `dev:reflect` reads without mode qualification is confirmed to be genuinely
mode-independent.

**Prevention (also deferred):** the fix considered and dropped in favour of closing the live
defect — require `dev:plan`'s Interfaces block to name, per state key, which mode writes it, so a
plan spanning gate and no-gate paths cannot leave ownership implicit. Worth revisiting once the
sweep shows how common the shape actually is. Note that spec-challenger *reproduced* this bug in
the very file that already contained an instance of it, which is the argument that a preventive
mechanism is warranted rather than just vigilance.
