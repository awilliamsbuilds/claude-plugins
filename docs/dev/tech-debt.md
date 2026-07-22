# Tech Debt

Deferred items discovered by `/dev` cycles — recorded rather than fixed, with enough context to
act on later without re-deriving the finding. Written automatically by `dev:done` when a cycle
completes; read, ranked, and closed via `/dev:debt`. Format and rules: the `/dev` plugin's
`references/tech-debt.md`.

## Open

### Autopilot doesn't cross-note the spec grounding gate
*First recorded: 2026-07-21 · Cycles: spec-grounding-and-clock · Recurrence: 1*

**What's wrong:** `plugins/dev/skills/autopilot/SKILL.md` (~lines 45–48) describes its own
confidence / auto-fill / stop logic but never mentions the grounding gate added to `dev:spec`
Step 7 / Step 8. Its "auto-fill remaining dimensions" line reads as if inference can clear the
path to proceed — which the gate forbids. **Behavior is safe:** autopilot delegates to
`dev:spec`, so an unverified as-is claim still surfaces through autopilot's existing "confidence
too low even after auto-fill → STOP" path. The gate is simply invisible in autopilot's own text.
**Why deferred:** Raised as issue #2 in that cycle's code review; judged a documentation gap,
not a blocker.
**Done looks like:** A one-line cross-note in autopilot's Step 2 pointing at the `dev:spec`
grounding gate.
**Files:** plugins/dev/skills/autopilot/SKILL.md

### Sweep for gate-path state writes that are dead in autopilot
*First recorded: 2026-07-21 · Cycles: spec-challenger · Recurrence: 1*

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
**Files:** plugins/dev/skills/spec/SKILL.md, plugins/dev/skills/shape/SKILL.md, plugins/dev/skills/plan/SKILL.md, plugins/dev/skills/build/SKILL.md, plugins/dev/skills/validate/SKILL.md, plugins/dev/skills/pr/SKILL.md, plugins/dev/skills/done/SKILL.md, plugins/dev/skills/autopilot/SKILL.md, plugins/dev/skills/reflect/SKILL.md

### Hardcoded repo path in dev:reflect
*First recorded: 2026-07-22 · Cycles: tech-debt-tracking · Recurrence: 1*

**What's wrong:** `plugins/dev/skills/reflect/SKILL.md:166` hardcodes `~/Development/claude-plugins`
as the source-repo location and names the `local-plugins` marketplace directly. Found by the
tech-debt-tracking cycle's negative-space sweep, which grepped the whole plugin for
person-, company-, and environment-specific strings: this is the **only** repo-specific string
in the entire `/dev` plugin. It directly violates the portability property that cycle was built
around — a `/dev` installed in any other repo follows an instruction pointing at a directory
that doesn't exist there.
**Why deferred:** Found by that cycle's grounding sweep and explicitly placed out of scope in
its spec. Best fixed by a later cycle already working in that file — which is the behavior this
tracker exists to enable.
**Done looks like:** The source repo is discovered (from the git remote, or from where the
plugin cache resolves) or asked for, with no path and no marketplace name hardcoded anywhere in
the skill.
**Files:** plugins/dev/skills/reflect/SKILL.md

### dev:spec's product-plan procedure pushes straight to origin/main
*First recorded: 2026-07-22 · Cycles: tech-debt-tracking · Recurrence: 1*

**What's wrong:** `dev:spec` Step 4's product-plan procedure mandates a direct push to
`origin/main`. That conflicts with the standing "never commit directly to `main`" convention —
a repo with branch protection on `main` will simply reject the push, and a repo without it gets
an unreviewed commit on its default branch.
**Why deferred:** Found by the tech-debt-tracking cycle's grounding sweep and explicitly placed
out of scope in its spec. Best fixed by a later cycle already working in that file — which is
the behavior this tracker exists to enable.
**Done looks like:** The product plan lands on `main` through the same branch-and-PR path every
other change uses, or the procedure documents explicitly why this one file is exempt.
**Files:** plugins/dev/skills/spec/SKILL.md

### A nested product plan cannot outlive its parent
*First recorded: 2026-07-22 · Cycles: tech-debt-tracking · Recurrence: 1*

**What's wrong:** A nested product plan lives at `docs/dev/<parent>/product-plan.md` — inside
the parent's own cycle directory. `dev:done` Step 7 runs `rm -rf "$WORKDIR/docs/dev/<feature>/"`,
so the moment the parent cycle completes, its nested plan is deleted along with everything else
in that directory. A nested plan structurally cannot outlive the parent it decomposes. This is
the same disease the tech-debt tracker was built to treat: a record meant to be durable, stored
inside a directory designed to be destroyed.
**Why deferred:** Found by the tech-debt-tracking cycle's grounding sweep and explicitly placed
out of scope in its spec. Best fixed by a later cycle already working in those files — which is
the behavior this tracker exists to enable.
**Done looks like:** A nested product plan survives its parent's `dev:done`, either by living
one level up (as `docs/dev/tech-debt.md` does) or by being archived into `docs/decisions/`
before Step 7's cleanup.
**Files:** plugins/dev/skills/spec/SKILL.md, plugins/dev/skills/done/SKILL.md

### The feature slug reaches git commit -m with no character allowlist
*First recorded: 2026-07-22 · Cycles: tech-debt-tracking · Recurrence: 1*

**What's wrong:** `dev:done` interpolates `<feature>` into five double-quoted
`git commit -m "… <feature>"` strings (Steps 3, 4, 5, 6a, 7), where `$(…)` and backticks
execute. The slug is only validated against `^[a-z0-9][a-z0-9-]*$` on the argument-derived path;
the common path takes it from conversation context, and `dev:fix` derives it by kebab-casing a
Linear issue title with no character allowlist stated. Other stages have the same shape.
**Why deferred:** Found by the tech-debt-tracking cycle's security review. The right fix is at
the source — one allowlist in `dev:fix` Step 3 and `dev:spec` Step 5 closes every call site at
once — which means editing skills this cycle's spec put out of scope. Patching only the one new
call site would leave four identical ones and imply the shape was reviewed and accepted.
**Done looks like:** Feature-name derivation strips everything outside `[a-z0-9-]` after
kebab-casing and rejects a result that doesn't match `^[a-z0-9][a-z0-9-]*$`, so every downstream
interpolation is safe by construction rather than by convention.
**Files:** plugins/dev/skills/fix/SKILL.md, plugins/dev/skills/spec/SKILL.md, plugins/dev/skills/done/SKILL.md

## Closed
