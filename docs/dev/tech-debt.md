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
*First recorded: 2026-07-21 · Cycles: spec-challenger, plan-challenger · Recurrence: 2*

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

### Validate's fix loop never verifies the fixes it writes
*First recorded: 2026-07-22 · Cycles: tech-debt-tracking · Recurrence: 1*

**What's wrong:** `dev:validate` Step 4 fixes issues, commits, and closes the loop. Nothing
verifies the fix itself — a defect introduced by a fix is caught only if another loop happens to
run and re-review the whole diff. In the tech-debt-tracking cycle this fired twice in a row:
loop 1's renumbering left a dangling cross-reference and put a guard after the operation it
guarded; loop 2's guard rewrite shipped `git rebase --show-current-patch … && { … }`, which
**exits 128 on the healthy path**, as the first command of `dev:done` Step 7 — every normal
cycle's teardown would have read as a failure. Loop 3 caught it by running the snippet. On a
`micro` tier (1 loop) or any cycle that goes clean early, neither would have been caught at all.

Two distinct gaps sit underneath. **(a)** There is no self-check step: the loop's exit condition
is "no open P1/P2," which says nothing about the fixes just written. **(b)** The specific rule
that would have caught the concrete defect — *a shell snippet written into a skill must exit 0 on
its healthy path, so `&&` chains and bare guard blocks don't read as failure* — **exists nowhere
in the plugin.** Verified by grep across all `dev:*` skills on merged `main`: zero hits. That
cycle's own `validation.md` asserted the rule was "already codified in `dev:validate` Step 6";
that claim was false and is recorded here so the next reader doesn't inherit it.

**Why deferred:** The user chose to record rather than patch. The concrete defect was already
fixed in-cycle; what remains is the missing mechanism, and this plugin's own history argues the
prevention is worth designing once rather than bolting a single rule onto Step 4 — see
*Sweep for gate-path state writes that are dead in autopilot*, which reaches the same conclusion
about a different recurring shape. Note that a diff of executable prose has no test harness, so
"verify the fix" cannot mean "run the tests"; it needs its own definition.
**Done looks like:** `dev:validate` Step 4 cannot close a loop without checking the fixes it just
wrote, and the healthy-path exit-code rule for shell snippets is stated once somewhere a fix
author will read it. A fix that breaks a sibling skill's happy path is caught by the loop that
wrote it, not by the next one.
**Files:** plugins/dev/skills/validate/SKILL.md

### validate's config-contract gate says "every reader" but the convention is "every reader of that key"
*First recorded: 2026-07-23 · Cycles: init-rerun-hardening · Recurrence: 1*

**What's wrong:** `dev:validate`'s Config-contract review gate reads "if this cycle adds a new key to config.json, verify every skill that reads config.json has that key in its Step 1 read list." Taken literally that is broader than the actual convention this repo follows: only a skill that reads *that specific key* needs it in its read list. Every existing key is handled per-consumer, and this cycle added `component_policy`/`schema_version` to just their consumers (shape, reflect; migration for schema_version) while spec/autopilot/pr read config.json for other keys and were correctly left alone. A strict future run of the gate as worded would flag those as violations — a false positive that each config-touching cycle will rediscover.
**Why deferred:** Editing `validate`'s checklist was explicitly out of scope for this cycle; the implementation correctly followed the per-consumer intent, so no diff change was warranted here.
**Done looks like:** The gate wording is narrowed to "every skill that reads that key" (or equivalent), so the literal reading matches the per-consumer convention and stops producing false positives.
**Files:** plugins/dev/skills/validate/SKILL.md

### validate inherits a stale loops_max that doesn't match the tier
*First recorded: 2026-07-23 · Cycles: init-rerun-hardening · Recurrence: 1*

**What's wrong:** On this deep-tier cycle, `state.json`'s `validate.loops_max` was `3` at validate stage entry, but the deep tier's max is `5`. `dev:validate` self-corrected it per the tier table before reviewing, so there was no visible breakage — but the mismatch means some earlier stage (or a config/template default) seeds `loops_max` without reference to the tier, and every non-micro cycle silently relies on validate to re-derive it. If validate's self-correction ever regresses, a deep cycle would cap at 3 loops without anyone noticing.
**Why deferred:** Surfaced by dev:reflect; the user declined the skill change this cycle, and validate already self-heals so there is no immediate breakage.
**Done looks like:** `loops_max` is derived from the tier table at the point it is first written (tier detection in spec), so validate reads a value already consistent with the tier rather than correcting a stale one — and the self-correction becomes a redundant backstop rather than a load-bearing fix.
**Files:** plugins/dev/skills/validate/SKILL.md

## Closed

### dev:spec's product-plan procedure pushes straight to origin/main
*Closed 2026-07-23 by cycle init-rerun-hardening · First recorded: 2026-07-22 · Recurrence: 1*

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

### The feature slug reaches git commit -m with no character allowlist
*Closed 2026-07-24 by cycle done-doc-reconciliation · First recorded: 2026-07-22 · Recurrence: 1*

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
