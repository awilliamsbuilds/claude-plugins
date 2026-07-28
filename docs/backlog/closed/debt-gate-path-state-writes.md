---
type: debt
scope: repo
status: closed
first_recorded: 2026-07-21
cycles: [state-write-mode-audit]
recurrence: 2
files:
  - plugins/dev/skills/spec/SKILL.md
  - plugins/dev/skills/shape/SKILL.md
  - plugins/dev/skills/plan/SKILL.md
  - plugins/dev/skills/build/SKILL.md
  - plugins/dev/skills/validate/SKILL.md
  - plugins/dev/skills/pr/SKILL.md
  - plugins/dev/skills/done/SKILL.md
  - plugins/dev/skills/autopilot/SKILL.md
  - plugins/dev/skills/reflect/SKILL.md
closed: 2026-07-25
closed_by: state-write-mode-audit
---

**What's wrong:** There is a recurring defect shape in the `/dev` skills: **a `state.json` write
specified only on a standard-mode gate path, silently never executed in autopilot, while
`dev:reflect` reads the resulting counter with no mode qualification.** The counter then reads
clean on every autopilot cycle regardless of what actually happened. Three confirmed instances
so far, all the same shape:

| Counter | Where the write lived | Consequence |
|---|---|---|
| `challenge.applied` | delegated to spec Step 13, whose autopilot branch is a pass-through | autopilot cycles always reported `applied: 0` |
| `challenge.dismissed` | inside Step 13 Path A, gated on "if changes are requested" | a fully-dismissed verdict could never be recorded |
| `metrics.spec_revisions` | spec Step 13's gate path only, while autopilot revises specs via silent backtrack | reflect's self-declared "strongest single signal" pinned at 0 in autopilot |

The first two were caught in spec-challenger's own Validate. The third was pre-existing,
predating that cycle, and **was fixed in the same session** (`autopilot/SKILL.md` backtrack rule
now increments it; `reflect/SKILL.md` wording de-coupled from standard mode). **What remains is
the sweep.** Only two counters were checked beyond the three above —
`metrics.visual_screens_shown` (fine: written in shape Step 10, before the gate) and
`validate.loops_run` (fine: mode-independent). Every other counter across the nine `dev:*`
skills that touch `state.json` is unverified.

The **plan-challenger** cycle (2026-07-24) is the next data point: it added a cold-review
challenger to `dev:plan` with its own `challenge_plan.*` counters — the same mode-sensitive
shape as `challenge.*` — expanding the surface this sweep must cover. That cycle guarded its own
new counters by construction (`applied` has an autopilot-path writer, `dismissed` is gate-only
*because* its autopilot-correct value is its init default `0`, `loops_run` is autopilot-only), so
no live defect shipped. But it is a further instance of hand-vigilance-per-counter being the only
thing standing between the plugin and this recurring defect, which strengthens the case for the
deferred preventive mechanism (below) over relying on each cycle to re-derive the invariant.
**Why deferred:** The confirmed instance was worth closing immediately; an exhaustive audit of
every state write across nine skills is its own scoped piece of work, not a reflect-gate patch.
**Done looks like:** Every `state.json` key written by a `dev:*` skill is traced to the mode(s)
that write it, gate-only writes are either moved pre-gate or duplicated into the autopilot path,
and any counter `dev:reflect` reads without mode qualification is confirmed to be genuinely
mode-independent. **Prevention (also deferred):** the fix considered and dropped in favour of
closing the live defect — require `dev:plan`'s Interfaces block to name, per state key, which
mode writes it, so a plan spanning gate and no-gate paths cannot leave ownership implicit. Worth
revisiting once the sweep shows how common the shape actually is. Note that spec-challenger
*reproduced* this bug in the very file that already contained an instance of it, which is the
argument that a preventive mechanism is warranted rather than just vigilance.
