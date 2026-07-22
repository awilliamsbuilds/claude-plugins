# Tech Debt — Shared Contract

This is the shared contract for `/dev`'s tech-debt tracker — where the files live, what goes in
them, and the four named procedures the stage skills cite. It is a reference, not a skill:
nothing invokes it directly, and skills link here rather than restating any of it, so the
tracker's shape lives in exactly one place.

## Where things live

**The tracker — `docs/dev/tech-debt.md`.** Repo-level, standing, hand-editable. It sits beside
`product-plan.md`, one level *above* the per-cycle directory `docs/dev/<feature>/` that
`dev:done` Step 7 deletes — which is the entire reason it survives cycles.

**The buffer — `docs/dev/<feature>/debt-pending.md`.** Per-cycle scratch, inside the directory
that gets deleted. Created on first write by whichever stage writes first, flushed into the
tracker by `dev:done` Step 6a, and destroyed by Step 7 immediately after. It cannot be a
section inside any one stage's artifact, because `dev:build` runs before `dev:validate` and
both produce entries.

Producing stages (`dev:build`, `dev:validate`, `dev:reflect`, `dev:spec`) only ever **append**
to the buffer. `dev:done` is the only automatic writer of the tracker. `dev:debt` owns all
reads and all manual lifecycle changes.

## The carrying-cost test

Applied by every stage that defers something, to decide whether it is worth recording at all:

> Will this cost us again — does it make future work harder, is it known-wrong behavior that
> will bite, or is it a pattern rather than an instance?

**Yes → record it.** A one-off local cleanup, a cosmetic issue, or anything that gets
fixed-once-and-forgotten → **drop it.** It already died in Validate's fix loop, and recording
it turns the tracker into a P3 landfill.

**Severity is the wrong axis.** Both directions matter:

- A **Nit** that exposes a systemic convention gap — a naming rule nothing enforces, a pattern
  the next five cycles will each rediscover — **qualifies.**
- A **P3** that is a local one-liner in a file nobody else will touch — **does not.**

Classify by what the item will cost the *next* cycle, never by the label the fix loop gave it.

## Tracker file format

Plain Markdown, readable and editable by hand without tooling. An `## Open` section and a
`## Closed` section, both always present, both allowed to be empty. Entries are `###` headings
under one of them.

```markdown
# Tech Debt

Deferred items discovered by `/dev` cycles — recorded rather than fixed, with enough context to
act on later without re-deriving the finding. Written automatically by `dev:done` at the end of
a cycle; read and closed via `/dev:debt`. Entry format: `plugins/dev/references/tech-debt.md`.

## Open

### Autopilot doesn't cross-note the spec grounding gate
*First recorded: 2026-07-21 · Cycles: spec-grounding-and-clock · Recurrence: 1*

**What's wrong:** Autopilot's Step 2 describes its own confidence and auto-fill logic but never
mentions the grounding gate in `dev:spec` Step 7/8, so its "auto-fill remaining dimensions" line
reads as if inference can clear the path to proceed.
**Why deferred:** Raised in code review, judged a documentation gap rather than a blocker —
behavior is safe, since autopilot delegates to `dev:spec` and the gate still fires.
**Done looks like:** A one-line cross-note in autopilot Step 2 pointing at the grounding gate.
**Files:** plugins/dev/skills/autopilot/SKILL.md

### Gate-path state writes are dead in autopilot
*First recorded: 2026-07-21 · Cycles: spec-challenger, tech-debt-tracking · Recurrence: 2*

**What's wrong:** A recurring shape — a `state.json` write specified only on a standard-mode
gate path, silently never executed in autopilot, while `dev:reflect` reads the resulting counter
with no mode qualification.
**Why deferred:** An exhaustive audit of every state write across nine skills is its own scoped
piece of work, not a patch to the cycle that found it.
**Done looks like:** Every `state.json` key written by a `dev:*` skill is traced to the mode(s)
that write it, and gate-only writes are moved pre-gate or duplicated into the autopilot path.
**Files:** plugins/dev/skills/spec/SKILL.md, plugins/dev/skills/autopilot/SKILL.md

## Closed

### Deferred improvements are written into a file that gets deleted
*Closed 2026-07-22 by cycle tech-debt-tracking · First recorded: 2026-07-20 · Recurrence: 1*

**What's wrong:** `dev:build` Step 3 wrote deferred items into `plan.md`, which `dev:done`
Step 7 deletes without any stage reading it first.
**Why deferred:** There was nowhere durable to route them to.
**Done looks like:** Deferred improvements land somewhere that outlives the cycle directory.
**Files:** plugins/dev/skills/build/SKILL.md
```

Rules the example encodes:

- **`Recurrence: N` always equals the number of names in `Cycles:`.** They are maintained
  together; if they disagree, `Cycles:` is authoritative.
- **`**Files:**` is required on every entry** — a comma-separated list of repo-relative paths.
  It is not decoration: `dev:spec`'s Step 7 cross-check keys its matching on this field, so an
  entry without it is invisible at the one moment it would be actionable.
- **`**Possibly related to:** <exact title>`** is optional, and appears only on entries created
  under uncertainty by the recurrence-merge procedure.
- Open and Closed meta lines are different shapes. Open:
  `*First recorded: YYYY-MM-DD · Cycles: <a>, <b> · Recurrence: N*`
  Closed:
  `*Closed YYYY-MM-DD by cycle <name> · First recorded: YYYY-MM-DD · Recurrence: N*`

## Buffer file format

The template a stage copies when creating the buffer. Both sections are always written, and
both are allowed to stay empty.

```markdown
# Debt Pending — <feature>

Buffered tech debt for this cycle. `dev:done` Step 6a flushes this into `docs/dev/tech-debt.md`
and Step 7 deletes it. Nothing else reads it.

## To Record

### <Title>
**What's wrong:** ...
**Why deferred:** ...
**Done looks like:** ...
**Files:** path, path
*Source: <skill> · <cycle>*

## To Close

- <exact tracker entry title> — <why this cycle paid it>
```

`## To Record` holds full entries in the tracker's own entry shape, plus a `*Source:*` line
naming the skill and cycle that wrote it. The flush drops the `*Source:*` line and replaces it
with a proper Open meta line.

`## To Close` holds one bullet per entry: the **exact** tracker entry title, an em dash, and why
the cycle paid it.

## The recurrence-merge procedure

On flush, compare each `## To Record` entry against the existing entries in `## Open`.

A **clear match** means the same underlying problem: the `**Files:**` sets overlap **and** the
described defect is the same defect. Both conditions, not either.

**On a clear match:** append this cycle's name to `Cycles:`, increment `Recurrence:`, and fold
any new detail into `**What's wrong:**` **by appending — never by replacing existing text.**

**When uncertain:** create a new entry carrying `**Possibly related to:** <exact title of the
entry you suspected>`.

The bias is deliberate and it is asymmetric: a duplicate is visible in the list and cheap for a
human to merge by hand, while a wrong merge silently destroys an entry nobody will ever notice
is missing. **Never merge on topic or keyword similarity alone** — two entries both about
"autopilot" or both about "state.json" are not thereby the same entry.

## The silent-degrade rule

When `docs/dev/tech-debt.md` is absent, every **reader** prints **nothing at all** — not an
empty list, not "0 items", not a warning, not an error. The same holds when the file exists but
`## Open` is empty, and when a cross-check finds zero matches.

**Writers** create the file on first write, seeded with the H1 header and both the `## Open` and
`## Closed` headings, then proceed normally.

The one exception is **`dev:debt` invoked directly**, which says so plainly — "No tech debt
tracked in this repo yet." — because the user asked the question and deserves an answer.

## The recurrence ranking

Open entries sort by `Recurrence:` **descending**. Ties break by the **most recent name in
`Cycles:`** — the entry touched by the later cycle ranks first.

## Mode symmetry

Every rule in this file is **self-applied by the writing stage.** Never gate a tracker write on
user confirmation, and never put one on a standard-mode-only path.

This is not a hypothetical. This plugin has three recorded instances of exactly that defect: a
`state.json` write specified only on a standard-mode gate path, silently never executed in
autopilot, with a downstream reader that had no mode qualification. Any new tracker write must
be traceable to a step that runs identically in both modes.

## Calibration

The carrying-cost test above was checked against real history before it shipped — the three
items actually deferred across this repo's first ten `/dev` cycles — rather than asserted:

| Deferred item | Test | Result |
|---|---|---|
| The "locality only" Scoring-Template nit (`name-evaluation-rubric`): two new sections sit after the Scoring Template, so Steps 4 and 9 forward-reference them | Costs nothing again — sections are bold and findable, and no future cycle pays for the ordering. A one-off cosmetic instance | **Does not qualify** |
| The `TMP`-path naming nit (`product-plan-worktree-safe`): Step 2's `TMP` path uses `<feature-name>` before the feature is selected | A single inaccurate token in one path string. Nothing is harder later, nothing is known-wrong at runtime, not a pattern | **Does not qualify** |
| The nested-product-plan-visibility P3 (`product-plan-worktree-safe`): the nested path pushes to `origin/<parent-branch>`, but Step 6 resets the cycle worktree to the *local* parent ref, so a nested plan may not appear in the nested worktree | Known-wrong behavior that will bite the next person who nests a product plan, and it constrains any future change to Step 6 | **Qualifies** |

If a future revision of the test flips any of these three results, the wording is wrong — not
the results.
