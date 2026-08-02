# Autopilot Handoff at Pre-Execution Gates
*Branch: feature/autopilot-handoff · Confidence: 90% — Ready · 2026-08-02*
*Cycle type: feature · Tier: standard*

## Intent

A `/dev` cycle in standard mode runs every stage behind an approval gate. But the gates stop
being useful at a predictable point: once the spec is approved and the design (if any) is
settled, the remaining stages — Plan, Build, Validate, PR, Done — are mechanical execution of
decisions already made. Today the only way to get autopilot's speed for that stretch is to have
launched the whole cycle in autopilot from the start, forfeiting the gates that were valuable
during definition.

The machinery to switch already exists and is unused: `dev:autopilot` Step 1 (autopilot/SKILL.md:20–31)
already detects an in-progress session, announces `Resuming from <current-stage> in autopilot mode`,
and sets `mode: "autopilot"` in state.json. What is missing is the *offer* — nothing anywhere in
`plugins/dev/` tells the user this is possible.

A naive fix would flip `mode` in-session and keep going. That squanders the second benefit: by the
time Shape is approved, the session context is carrying the entire spec and design conversation, and
the stages that follow read their inputs from committed artifacts, not from that conversation. The
handoff is therefore a `/clear` boundary — the offer's payload is a runnable command, not a mode flip.

## Scope

1. **An autopilot offer at each pre-execution gate.** A "pre-execution gate" is an approval gate
   whose next stage is the cycle's first execution stage — Plan for standard/deep, Build for micro.
   Concretely:
   - `dev:spec` Step 13, **only** when the next stage is Plan (`"shape" ∈ skipped[]`) or Build
     (micro tier). Never when the next stage is Shape.
   - `dev:shape` Step 11, on approval.
2. **The offer is printed, not asked.** Each of those gates already prints a `Safe to /clear now —
   resume with: …` line; the offer adds a second command beside it — `/clear`, then
   `/dev:autopilot <artifact>`. There is **no yes/no prompt, no session-ending path, and no state
   write at the gate.** A user who wants the gated flow ignores the extra line, so existing gate
   behaviour is untouched by construction rather than by a guarded branch. This is what keeps the
   feature from needing a second code path anywhere in the eleven stage skills or the orchestrator.
3. **`dev:autopilot` accepts the artifact-path argument form** — `/dev:autopilot docs/dev/<feature>/<artifact>.md`
   (`spec.md` from the Spec gate, `design.md` from the Shape gate) — deriving `<feature>` from the
   path, then resolving `WORKDIR` with the same working-directory block the eleven stage skills
   already open with: compute `PRIMARY`, then take the first hit of
   `$PRIMARY/.dev-worktrees/<feature>/docs/dev/<feature>/state.json` (worktree cycle) or
   `$PRIMARY/docs/dev/<feature>/state.json` (legacy in-place). `worktreePath` is **not** the
   resolver — it is written once by `dev:spec` Step 6 and read only as a set/null predicate. This
   matches the resume convention every stage skill already implements (`dev:dev` Invocation
   Reference, `dev/SKILL.md:173`; header block at `plan/SKILL.md:10–23`). `dev:autopilot` is
   currently the only orchestrator with neither, and the printed command must work cold or the
   feature does not work at all. On this form it also reads `tier` and `stage` from the resolved
   `state.json` rather than inferring them from an initial request — a pasted command carries no
   request to infer from, and without `tier` a micro cycle cannot select its stage sequence
   (`autopilot/SKILL.md:79` currently says tier is detected "from the initial request").
4. **A handoff marker in `state.json`** recording the stage the cycle handed off at
   `(writes: autopilot-only)` — written by `dev:autopilot` Step 1 at the moment it flips a cycle
   whose `mode` is `"standard"` over to `"autopilot"`. That flip *is* the handoff, so the marker
   records an observed event rather than a stated intention; nothing is written at the gate. A cycle
   that was autopilot from the start never flips from `"standard"`, so the marker stays absent there.
   Two readers: `dev:reflect` Step 4 runs the user-observation turn when the marker is set even though
   `mode` is `"autopilot"`; `dev:done` Step 5's decision-log template gains one line when the marker
   is set — `*Handed off to autopilot at <stage>*` under the date/branch/PR header — and is
   byte-identical when it is absent.
5. **Folded-in debt — `debt-primary-path-relative-in-dev-headers` (P3).** `PRIMARY` is derived by
   relative `dirname "$(git rev-parse --git-common-dir)"` across eleven skills, yielding `.` when run
   from the repo root. This cycle's core path is a command pasted into a cleared session running from
   the primary checkout, so absolute `PRIMARY`/`WORKDIR` resolution is directly load-bearing here.
6. **Folded-in debt — `debt-autopilot-grounding-gate`.** A one-line cross-note in autopilot's Step 2
   pointing at the `dev:spec` grounding gate. This cycle is already editing `autopilot/SKILL.md`
   Steps 1–2.

## Out of Scope

- Extracting a shared "canonical WORKDIR block" that all skills reference. Two files cite one
  (`autopilot/SKILL.md:54`, `dev/SKILL.md:64`) and it does not exist as a defined artifact — a real
  gap, but its own cycle. This cycle does not create that shared artifact; it inlines correct
  resolution at each site. (Distinct from Scope item 5, which fixes the *`PRIMARY` derivation*
  one-liner in all eleven existing stage headers, and from item 3, which gives `dev:autopilot` a
  resolution block it currently lacks entirely.)
- Making `dev:reflect` Step 4 unconditional for all modes. Wider blast radius than the problem.
- Any handoff in the reverse direction (autopilot → gated mode).
- An offer at the Validate or PR gates. Those sit past the point where a handoff saves meaningful
  context, and `dev:dev` Step 5 already lets the user drive them.
- The two other matched debt items (`debt-state-advancement-commit-durability`,
  `debt-spec-grounding-citation-unverified`) — neither is in this cycle's edit path.

## Success Criteria

1. The `dev:shape` Step 11 gate prints, beside its existing `/dev:plan` resume command, a `/clear`
   instruction plus a runnable `/dev:autopilot` command and the worktree path.
2. That command, pasted into a cleared session started from the primary checkout, resumes the cycle
   at Plan in autopilot mode from the correct worktree — with no `cd` asked of the user.
3. A no-UI standard cycle gets the same offer at its Spec gate; a UI cycle does **not** (its next
   stage is Shape).
4. A micro cycle gets the offer at its Spec gate, handing off to Build.
5. A user who ignores the offer takes the existing approval path unchanged — no extra prompt, no
   state write, and no change to the printed next-stage command.
6. After a handed-off cycle completes, `dev:reflect` still runs its Step 4 user-observation turn,
   and the decision log reflects that the cycle was mixed-mode rather than pure autopilot.
7. Every `/dev` skill computing `PRIMARY` yields an absolute path when invoked from the repo root.
8. A cycle run in autopilot end-to-end finishes with the marker **absent**: `dev:reflect` skips its
   Step 4 turn and the decision log is byte-identical to today's. This is the counterpart to
   criterion 6 — the marker has to distinguish the two, not fire on both.

## Happy Path

1. User runs `/dev`, works through Spec and Shape with gates — answering questions, correcting the
   design.
2. `dev:shape` Step 11 gate renders: design committed, Design Status confirmed, and — beside the
   existing `/dev:plan` resume command — a `/clear` + `/dev:autopilot docs/dev/autopilot-handoff/design.md`
   alternative, the worktree path, and a one-line preview of which stages will run unattended.
3. User approves the design through the existing gate flow, then runs `/clear` and pastes the
   autopilot command.
4. `dev:autopilot` derives the feature from the path, resolves `WORKDIR` by the two-location
   `state.json` test, reads `tier` and `stage` from it, sees `mode` is `"standard"`, records
   `handoff_at` for the stage it is resuming at, sets `mode: "autopilot"`, and runs
   Plan → Build → Validate → PR → Done with no gates.
5. At Done, `dev:reflect` sees the handoff marker and asks the user for observations before closing out.

## Edge Cases

- **Spec gate in a UI cycle.** The next stage is Shape, not an execution stage — no offer. This is the
  distinction that keeps the rule stateable in one sentence.
- **Spec gate re-displayed after a revision** (Step 13 Path A or Path B). The offer re-renders with the
  gate; it is static text carrying no state of its own, so re-display is idempotent.
- **User never runs the offered command.** Nothing to reconcile — the offer recorded nothing, so the
  cycle continues down the gated path with no residue and no stale marker.
- **User pastes the command without clearing first.** Works identically; only the context benefit is
  lost. Not an error to guard against.
- **Cycle already in autopilot mode.** Autopilot has no gates, so the offer never renders — no mode
  check needed at the offer site. The marker is likewise never written, because `mode` is already
  `"autopilot"` and no `"standard"` → `"autopilot"` flip occurs.
- **Handoff at a stage past Shape.** No offer is printed at the Validate or PR gates (Out of Scope),
  but a user who types `/dev:autopilot` there still flips a standard cycle, so the marker records
  that stage accurately. The marker's value domain is therefore any stage name, not just
  `spec`/`shape` — which is the correct behaviour for criterion 6, since such a cycle is genuinely
  mixed-mode.
- **Legacy in-place cycle** (`worktreePath: null`). `WORKDIR` resolves to the primary tree, matching
  `dev:dev` Step 3's existing worktree-first-else-primary rule.
- **Standalone stage invocation** (`/dev:shape docs/dev/<f>/spec.md`, outside the `dev:dev`
  orchestrator). The offer still renders, because it lives in the stage skill's own gate rather than
  in `dev:dev` Step 5's sequencing prompt.

## Audience

Solo developer running `/dev` on personal plugin and product repos. Comfortable in the terminal;
the cost being optimized is attention and context window, not clicks.

## Technical Constraints

- **Mode-symmetry contract** (`references/tech-debt.md:467–472`): every new `state.json` key declares
  its writing mode at its single write site, using the vocabulary `(writes: both)` /
  `(writes: autopilot-only)` / `(writes: standard; =default … in autopilot)`. The handoff marker has
  exactly one write site — `dev:autopilot` Step 1, on the `"standard"` → `"autopilot"` flip — and is
  therefore tagged `(writes: autopilot-only)`. Because the gates write nothing, there is no
  standard-mode writer to keep symmetric, and the marker cannot go stale against a mode that never
  changed. Its readers must treat an absent marker as today's behavior: `dev:reflect` Step 4 skips
  the user turn, `dev:done` Step 5 emits the unchanged template.
- **Ten skill files branch on mode.** The handoff must not require touching all ten; it works by
  letting `dev:autopilot` Step 1 set `mode` exactly as it does today, adding only the marker.
- These are Markdown skill files with no test harness. Verification is by reading the edited
  procedures against the success criteria, plus at least one real end-to-end handoff.

## Dependencies

- `dev:autopilot` Step 1 must gain the artifact-path form, explicit `WORKDIR` resolution, and the
  `tier`/`stage` read before the printed command is trustworthy. Scope item 3 is a hard prerequisite
  for criteria 1–4, not a parallel nicety. It is now also where the marker (item 4) is written, so it
  is a prerequisite for criteria 6 and 8 as well — item 3 carries the whole mechanism, and the gate
  edits are only the two printed lines that point at it.
- Nothing outside `plugins/dev/`. No config schema change (`docs/dev/config.json` is untouched).

## UI Needed

No. All surfaces are terminal text inside skill procedures. Gate copy still needs care — it is the
whole user-facing artifact of this feature — but there is no visual design work, so Shape is skipped.

---
*Auto-filled dimensions: none*
*Grounding inventory (all verified by grep/read during this stage, not recalled):*
- *"No mid-cycle mode switch exists" — `grep -rn 'switch to autopilot\|run the rest\|remaining stages\|hand off\|handoff' plugins/dev/` → zero hits. Net-new.*
- *"Autopilot already resumes an in-progress session and sets mode" — read `autopilot/SKILL.md:20–31`.*
- *"Autopilot Step 1 has no worktree-aware scan" — `grep -n 'PRIMARY\|worktree\|WORKDIR\|state.json' autopilot/SKILL.md` → only lines 31, 52, 54, 59; no `$PRIMARY/.dev-worktrees/*` sweep, unlike `dev/SKILL.md` Step 3.*
- *"The cited canonical WORKDIR block does not exist" — `grep -rn 'canonical block\|Canonical WORKDIR\|WORKDIR=' plugins/dev/` → only `fix:90`, `dev:64`, `spec:156`; the citation in `autopilot:54` and `dev:64` resolves to nothing.*
- *"`dev:dev:94` is the only options-bearing sequencing prompt" — `grep -rn 'yes / skip / stop\|Continue? (' plugins/dev/skills/*/SKILL.md` → single hit.*
- *"Ten skill files branch on mode" — `grep -rln 'Autopilot mode\|autopilot mode\|mode.*autopilot' plugins/dev/skills/*/SKILL.md` → build, dev, autopilot, pr, done, reflect, shape, plan, validate, spec.*
- *"`dev:shape` reads `state.json.mode` directly" — `shape/SKILL.md:54`.*
- *"Reflect Step 4 is standard-mode-only and autopilot skips it" — read `reflect/SKILL.md:117,132`.*
- *"`visual_screens_shown` is declared standard-only" — `shape/SKILL.md:211`.*
- *"`worktreePath` is not a WORKDIR resolver" — `grep -rn 'worktreePath' plugins/dev/` → written once at `spec/SKILL.md:230`, read only as a set/null predicate (`dev/SKILL.md:66–69`, `done/SKILL.md:95,106,496`). The stage skills resolve `WORKDIR` by a two-location `state.json` existence test (`plan/SKILL.md:10–23`, identical in shape/build/validate/pr/done/reflect). Corrected via cold review.*
- *"Mode-symmetry per-key rule" — `references/tech-debt.md:467–472`; the `(writes: …)` vocabulary itself at 471–472.*
- *"The decision-log template has no mode field" — read `done/SKILL.md:295–318`.*
- *"The `PRIMARY=` one-liner appears in exactly eleven skills, and not in autopilot" — build:26, debt:41, dev:39, done:15, fix:87, plan:15, pr:15, reflect:15, shape:15, spec:141, validate:15; `autopilot/SKILL.md` has no `PRIMARY` line.*
- *"`PRIMARY` derives relative" — reproduced live this stage: `dirname "$(git rev-parse --git-common-dir)"` returned `.` from the repo root; matches `debt-primary-path-relative-in-dev-headers`.*
- *Debt cross-check: intersected the P5 corpus front-matter `files:` against the above inventory → 4 matches; 2 folded into scope (buffered in `debt-pending.md` `## To Close`), 2 declined as out of path.*
