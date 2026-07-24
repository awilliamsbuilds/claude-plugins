# State-Write Mode Audit — Implementation Plan
*Branch: feature/state-write-mode-audit · 2026-07-24*

## Files

| File | Action | Purpose |
|------|--------|---------|
| docs/dev/state-write-mode-audit/audit.md | Create | Cycle-local evidence log: every mode-sensitive counter traced to its writing mode(s), classified against the invariant, with the canonical counter→tag mapping. Deleted by `dev:done`; not a standing file, not a per-key registry (SC5). |
| plugins/dev/skills/spec/SKILL.md | Modify | Tag `challenge.*` (6), `metrics.spec_questions_asked`, `metrics.spec_revisions` write sites; apply any spec-side defect fix the audit flags. |
| plugins/dev/skills/shape/SKILL.md | Modify | Tag `metrics.visual_screens_shown` write site. |
| plugins/dev/skills/build/SKILL.md | Modify | Tag `metrics.files_read_in_build` write site. |
| plugins/dev/skills/validate/SKILL.md | Modify | Tag `validate.loops_run` write site. |
| plugins/dev/skills/plan/SKILL.md | Modify | Tag `challenge_plan.*` (6) write sites; add the write-mode-per-key prevention rule to the `Interfaces:` template, Step 6 self-review, and the Step 7a interface-consistency lens. |
| plugins/dev/references/tech-debt.md | Modify | Extend the existing `## Mode symmetry` section with the per-key write-mode rule (SC3). |

## Tasks

### Task 1: Audit and classify every mode-sensitive counter
What: Trace every mode-sensitive `state.json` counter across the ten writer skills to the mode(s) that actually execute its write, classify each against the load-bearing invariant, and emit the canonical counter→tag mapping the tagging tasks consume.
Used by: Tasks 2–7 (each reads this task's canonical mapping to place its tag / rule); `dev:validate` later reviews `audit.md` as the SC1 evidence.
Depends on: nothing — first task.
Files: create `docs/dev/state-write-mode-audit/audit.md`. This task **edits no skill files** — it only produces evidence and the mapping. Any fix it flags is applied by the owning skill's task (2–6).
Interfaces:
- Consumes: nothing.
- Produces:
  - **Tag vocabulary** — exactly these three byte-fixed strings, reused verbatim everywhere (SC7): `(writes: both)`, `(writes: autopilot-only)`, `(writes: standard; =default 0 in autopilot)`.
  - **Canonical mapping** — for each counter below: its single-source write-site (skill + the description line where its tag belongs), its mode class, and its tag string:

    | Counter | Single-source site | Mode class | Tag |
    |---|---|---|---|
    | `challenge.run` / `.blockers` / `.concerns` | spec Step 12a counter-write semantics | overwritten each dispatch, both modes | `(writes: both)` |
    | `challenge.applied` | spec Step 12a semantics (autopilot loop + Step 13 gate both write) | both (historical fix — confirm no regression) | `(writes: both)` |
    | `challenge.dismissed` | spec Step 12a semantics | standard gate only; 0 in autopilot | `(writes: standard; =default 0 in autopilot)` |
    | `challenge.loops_run` | spec Step 12a semantics | autopilot loop only; 0 in standard | `(writes: autopilot-only)` |
    | `metrics.spec_questions_asked` | spec Step 12 state write | reconciled + written in both modes | `(writes: both)` |
    | `metrics.spec_revisions` | spec Step 13 Path B + autopilot Step 3 writer | both (historical fix — confirm no regression) | `(writes: both)` |
    | `challenge_plan.run` / `.blockers` / `.concerns` | plan Step 7a counter-write semantics | overwritten each dispatch, both modes | `(writes: both)` |
    | `challenge_plan.applied` | plan Step 7a semantics (autopilot loop + Step 8 gate both write) | both | `(writes: both)` |
    | `challenge_plan.dismissed` | plan Step 7a semantics | standard gate only; 0 in autopilot | `(writes: standard; =default 0 in autopilot)` |
    | `challenge_plan.loops_run` | plan Step 7a semantics | autopilot loop only; 0 in standard | `(writes: autopilot-only)` |
    | `metrics.visual_screens_shown` | shape screen-count write | standard only (no browser in autopilot); 0 in autopilot | `(writes: standard; =default 0 in autopilot)` |
    | `metrics.files_read_in_build` | build inline per-read increment | both modes (Build runs identically) | `(writes: both)` |
    | `validate.loops_run` | validate fix-loop increment | both modes (mode-independent loop) | `(writes: both)` |

  - **Untagged-confirmed list** — structural / mode-invariant fields the audit confirms carry no cross-mode reflect risk and leaves untagged (SC2): `stage`, `completed[]`, `skipped[]`, `artifacts.*`, `confidence.*` (incl. `final_score`, `auto_filled[]`), `tier`, `cycle_type`, `stage_timestamps.*`, `linear_issue`, `validate.loops_max`, `validate.p1_open[]`/`p2_open[]`/`p3_open[]`/`nits_open[]`.

Implementation steps:
1. Create `docs/dev/state-write-mode-audit/audit.md` with three sections: `## Counter classification` (the mapping table above), `## Confirmed mode-invariant (untagged)` (the untagged list, each with a one-line reason it carries no cross-mode reflect read), and `## Historical-fix regression check`.
2. For each counter in the table, open its writer skill(s) and confirm the mode class by reading the actual write site — do not carry the table's values on trust; the table is the grounded starting point, and any discrepancy found is resolved in favour of the code and the mapping is corrected here before any tag is placed.
3. Apply the **invariant** as the classification test for every counter: *no counter's non-default autopilot value may depend on a gate write.* A counter passes if it is written in both modes, or is genuinely mode-specific with its autopilot value equal to its init default. A counter that fails — a non-default autopilot value depending on a standard-mode-only gate write — is a **defect**.
4. Regression check the three historical fixes (`challenge.applied`, `challenge.dismissed`, `metrics.spec_revisions`): each must still satisfy the invariant. Record the confirmation in `## Historical-fix regression check` (SC6).
5. **If a fourth (or further) live defect surfaces:** record it in the mapping with the required write-side fix (move the write pre-gate, or give autopilot its own writer — mirroring the three historical fixes). The fix itself is applied by that counter's owning skill task (2–6), never here. If no new defect is found — the expected outcome — state that explicitly in `audit.md`.
6. Confirm `dev:reflect`'s counter reads (its three read sites) remain valid against the final classification, and that no correctly-mode-specific counter is misreported by reflect (spec edge case; expected: none). Record the result.
7. Freeze the tag vocabulary (the three strings) and the mapping. Every tagging task copies its tag string byte-for-byte from this file.

### Task 2: Tag the spec-net and spec metrics write sites in dev:spec
What: Place the single-source mode tag on each `challenge.*`, `metrics.spec_questions_asked`, and `metrics.spec_revisions` write site in `dev:spec`, and apply any spec-side defect fix the audit flagged.
Used by: `dev:reflect` readers (the tag documents the mode the counter is actually written in) and the Step 7a interface-consistency lens (which now enforces tag presence for new keys).
Depends on: Task 1 (canonical mapping + tag vocabulary).
Files: modify `plugins/dev/skills/spec/SKILL.md`.
Interfaces:
- Consumes: Task 1's canonical mapping and the three byte-fixed tag strings.
- Produces: nothing — terminal task (no later task depends on it).

Implementation steps:
1. In the Step 12a "Counter-write semantics" block, append the tag to each counter's description, using the exact string from Task 1's mapping: `challenge.run`/`.blockers`/`.concerns` → `(writes: both)`; `challenge.applied` → `(writes: both)`; `challenge.dismissed` → `(writes: standard; =default 0 in autopilot)`; `challenge.loops_run` → `(writes: autopilot-only)`.
2. Tag `metrics.spec_questions_asked` at its Step 12 state-write description → `(writes: both)`.
3. Tag `metrics.spec_revisions` at its single canonical description (the Step 13 Path B / initial-write description) → `(writes: both)`.
4. Place exactly **one** tag per counter, at its single-source description only — do not scatter the tag across every mention of the counter (the fact must live once so it cannot drift, per Scope 2).
5. Do **not** add tags to autopilot's `challenge.*` writer references — those are cross-references to spec's single-source tag, not independent facts (confirmed in Task 1).
6. If Task 1 flagged a spec-side defect, apply its recorded write-side fix here; otherwise make no behavioural change — tags only.

### Task 3: Tag the shape write site in dev:shape
What: Place the single-source mode tag on the `metrics.visual_screens_shown` write site in `dev:shape`.
Used by: `dev:reflect` readers (documents that the counter is standard-only and honestly 0 in autopilot).
Depends on: Task 1 (canonical mapping + tag vocabulary).
Files: modify `plugins/dev/skills/shape/SKILL.md`.
Interfaces:
- Consumes: Task 1's mapping; the tag string `(writes: standard; =default 0 in autopilot)`.
- Produces: nothing — terminal task.

Implementation steps:
1. Append `(writes: standard; =default 0 in autopilot)` to the `metrics.visual_screens_shown` increment description (the "increment by number of browser screens used" line).
2. Copy the tag string byte-for-byte from Task 1; do not paraphrase it (SC7 byte-consistency).
3. Tags only — no behavioural change.

### Task 4: Tag the build write site in dev:build
What: Place the single-source mode tag on the `metrics.files_read_in_build` write site in `dev:build`.
Used by: `dev:reflect` readers (documents that the counter is written in both modes).
Depends on: Task 1 (canonical mapping + tag vocabulary).
Files: modify `plugins/dev/skills/build/SKILL.md`.
Interfaces:
- Consumes: Task 1's mapping; the tag string `(writes: both)`.
- Produces: nothing — terminal task.

Implementation steps:
1. Append `(writes: both)` to the `metrics.files_read_in_build` increment instruction (the inline per-context-read increment description).
2. Copy the tag string byte-for-byte from Task 1 (SC7).
3. Tags only — no behavioural change.

### Task 5: Tag the validate write site in dev:validate
What: Place the single-source mode tag on the `validate.loops_run` write site in `dev:validate`.
Used by: `dev:reflect` readers (documents that the loop counter is mode-independent).
Depends on: Task 1 (canonical mapping + tag vocabulary).
Files: modify `plugins/dev/skills/validate/SKILL.md`.
Interfaces:
- Consumes: Task 1's mapping; the tag string `(writes: both)`.
- Produces: nothing — terminal task.

Implementation steps:
1. Append `(writes: both)` to the `validate.loops_run` write description — the single-source site (the fix-loop "Increment loops_run" step, or the final-record line, whichever Task 1 designates as canonical; place the one tag there only).
2. Leave `validate.loops_max` and `p1_open[]`/`p2_open[]`/`p3_open[]`/`nits_open[]` untagged — Task 1 confirms them mode-invariant / structural.
3. Copy the tag string byte-for-byte from Task 1 (SC7). Tags only — no behavioural change.

### Task 6: Tag challenge_plan.* and add the write-mode-per-key prevention rule to dev:plan
What: Tag `dev:plan`'s own `challenge_plan.*` write sites, and extend `dev:plan`'s `Interfaces:` task template, Step 6 self-review, and Step 7a interface-consistency lens to require every new `state.json` key to declare its writing mode — the structural prevention (SC4). `dev:plan` self-applying the new rule to its own counters is the self-consistency check.
Used by: future `/dev` cycles adding a new counter (the template forces the declaration; the Step 7a lens catches an omission before Build); `dev:reflect` readers (the `challenge_plan.*` tags).
Depends on: Task 1 (canonical mapping + tag vocabulary — the rule must reference the exact three-string vocabulary).
Files: modify `plugins/dev/skills/plan/SKILL.md`.
Interfaces:
- Consumes: Task 1's mapping and the three byte-fixed tag strings.
- Produces: nothing — terminal task.

Implementation steps:
1. **Tag `challenge_plan.*`** in the Step 7a "Counter-write semantics" block, one tag per counter at its single-source description, using Task 1's mapping: `challenge_plan.run`/`.blockers`/`.concerns` → `(writes: both)`; `challenge_plan.applied` → `(writes: both)`; `challenge_plan.dismissed` → `(writes: standard; =default 0 in autopilot)`; `challenge_plan.loops_run` → `(writes: autopilot-only)`.
2. **Interfaces template (Step 3, the `Produces:` line region and Step 5's plan.md template):** add a required sub-line so that, for each **new** `state.json` key a task introduces, the task's `Interfaces:` block must name which mode(s) write it, using the tag vocabulary from Task 1. Word it to apply only to new state keys (not every interface), so it does not burden tasks that touch no state.
3. **Step 6 self-review (item 6, the `Consumes:`/`Produces:` alignment check):** extend it so the review also confirms that every new `state.json` key declared by a task names its writing mode.
4. **Step 7a interface-consistency lens (the lens table row):** extend the lens brief so it flags a new `state.json` key whose task did not declare its writing mode — reusing the existing interface lens, adding **no** new enforcement machinery (SC4, Out of Scope).
5. Keep every addition additive and consistent with the existing template wording; the `challenge_plan.*` tags placed in step 1 double as the worked example of the rule the same skill now requires.

### Task 7: Extend the Mode symmetry contract with the per-key write-mode rule
What: Add the per-key write-mode rule to the existing `## Mode symmetry` section of the shared `tech-debt.md` contract (SC3), stating that any new `state.json` key must be traceable to the mode(s) that write it and referencing the inline tag vocabulary as where that fact lives.
Used by: the seven `tech-debt.md` consumers (`init`, `build`, `validate`, `reflect`, `done`, `debt`, `spec`) and any future cycle adding a counter.
Depends on: Task 1 (tag vocabulary — the rule cites the three tag strings as the fact's home).
Files: modify `plugins/dev/references/tech-debt.md`.
Interfaces:
- Consumes: Task 1's tag vocabulary.
- Produces: nothing — terminal task.

Implementation steps:
1. In the existing `## Mode symmetry` section (do not create a new section or file — SC5), append a paragraph stating the per-key rule: every new `state.json` key must be traceable to the mode(s) that write it, recorded once as an inline tag at the write site using the vocabulary `(writes: both)` / `(writes: autopilot-only)` / `(writes: standard; =default 0 in autopilot)`, and that the fact lives inline at the single write site — never in a standing registry table (which would drift and lie).
2. Keep the edit purely additive; do not alter the existing three-instance narrative or the calibration table, so the seven consumers stay compatible (Technical Constraints).
3. Cross-reference `dev:plan`'s Step 7a interface lens as the automated enforcer, matching Task 6's wording so the two homes of the rule agree.

## Edge Cases
| Edge case | Handled in | Approach |
|-----------|-----------|----------|
| Legitimately mode-specific counter correct at default (`challenge.dismissed`, `challenge_plan.loops_run`) | Task 1 + Tasks 2/6 | Classified as passing the invariant; tag documents it (`standard; =default 0` or `autopilot-only`); no fix. |
| Genuinely mode-independent counter (`validate.loops_run`, `files_read_in_build`) | Task 1 + Tasks 4/5 | Classified mode-independent; tag `(writes: both)`; no fix. |
| A fourth (or further) live defect surfaces | Task 1 flags; owning skill task (2–6) fixes | Recorded in `audit.md` with a write-side fix mirroring the three historical fixes; applied in the owning skill's task, never in Task 1. |
| Correctly-mode-specific counter that `dev:reflect` misreports | Task 1 step 6 | Audit actively confirms reflect's reads against the final classification; expected none, but confirmed rather than assumed. If found, the read-side reflect change is the one exception recorded and applied. |
| `dev`/`fix` structural writes (`skipped[]`, `linear_issue`, `stage`) | Task 1 untagged-confirmed list | Traced, confirmed no cross-mode reflect read, left untagged. |
| `dev:plan` writes its own `challenge_plan.*` | Task 6 | Its write sites are tagged; the same skill's new rule applied to its own counters is the self-consistency check. |
| `metrics.visual_screens_shown` in autopilot | Task 1 + Task 3 | No browser in autopilot → counter stays at init default 0, which is the honest value; tag `(writes: standard; =default 0 in autopilot)`, no fix. |

## Out of Scope
- The six other open tech-debt entries (autopilot grounding-gate cross-note, hardcoded repo path in `dev:reflect`, nested-product-plan lifetime, validate fix-loop verification, config-contract gate wording, stale `loops_max` derivation) — distinct defects, left open per the spec.
- A validate-stage enforcement check — enforcement is plan-stage only (the Step 7a interface lens).
- Any new standing file or per-key registry table — `audit.md` is cycle-local (deleted by `dev:done`), an evidence log, not a standing registry.
- Runtime code — there is none; all artifacts are `SKILL.md` markdown plus one shared reference.
- Editing `dev:autopilot` — its `challenge.*` writer sites are cross-references to spec's single-source tags, not independent facts; Task 1 confirms consistency, no tag is placed there.
- A read-side `dev:reflect` refactor beyond what a discovered misread counter would require — expected none.

## Risks and Unknowns
- **A fourth defect actually exists.** Mitigation: Task 1's trace is exhaustive by construction (every counter reflect reads, each checked against the invariant at its real write site); if one surfaces, the write-side fix path is already defined (Task 1 flags → owning skill task applies).
- **Tag placement drift** — the same counter tagged at more than one mention, reintroducing the drift the feature exists to prevent. Mitigation: Tasks 2/6 explicitly require exactly one tag at the single-source description and forbid tagging autopilot's cross-reference sites.
- **Byte-inconsistent tags across sites (SC7 self-violation).** Mitigation: Task 1 freezes the three tag strings; every tagging task copies them verbatim rather than paraphrasing; `dev:validate`'s prose-consistency review checks byte-equality across sites.
- **`tech-debt.md` contract breakage** — the edit is loaded by seven consumers. Mitigation: Task 7 is strictly additive to the existing `## Mode symmetry` section, altering no existing narrative or table.
- **Prevention rule over-reaches** — requiring a write-mode declaration for interfaces that touch no state. Mitigation: Task 6 scopes the new template sub-line to *new `state.json` keys only*.
