# State-Write Mode Audit — Decision Log
*2026-07-25 · Branch: feature/state-write-mode-audit · PR #48*

## What was built
An exhaustive audit that traces every mode-sensitive `state.json` counter across the ten `/dev` writer skills to the mode(s) that actually write it, tags each write site inline, and adds a plan-stage rule so a future counter cannot reintroduce the "gate-only write that's dead in autopilot" defect class.

## Key decisions
- **Fix write-side, not read-side** → the recurring defect is a gate-path write that never runs in autopilot; the honest fix moves the write pre-gate or gives autopilot its own writer, mirroring the three historical fixes (`challenge.applied`, `challenge.dismissed`, `metrics.spec_revisions`). No `dev:reflect` refactor was needed — the invariant makes a correctly-mode-specific-but-misread counter not exist.
- **Facts live inline at the single write site, never in a registry table** → a per-key registry is a second copy of a fact that already lives in the skills; it drifts on every state-key change and "a drifted safety-doc lies." Explicitly rejected a new standing file (SC5).
- **Frozen three-string tag vocabulary** → `(writes: both)` / `(writes: autopilot-only)` / `(writes: standard; =default 0 in autopilot)`, copied byte-for-byte at every site. Byte-consistency (SC7) is the very interface property the feature enforces, so the tags had to model it.
- **Prevention is plan-stage only** → the write-mode-per-key rule lands in `dev:plan`'s `Interfaces:` template, Step 6 self-review, and the Step 7a interface-consistency lens — reusing existing enforcement machinery, adding none. A validate-stage check was deliberately excluded.
- **Contract edit is strictly additive** → `references/tech-debt.md`'s existing `## Mode symmetry` section gained one parallel paragraph, altering no existing narrative or table, keeping all seven consumers compatible.
- **Writer set grounded from code, not recalled** → ten writers (`spec`, `shape`, `plan`, `build`, `validate`, `pr`, `done`, `autopilot`, plus `dev` for `skipped[]` and `fix` for `linear_issue`/`stage`); `dev:reflect` is the counter *reader*, traced as the read surface.

## Validation notes
- 1 loop run (tier: deep). Both code and security reviews ran as fresh cold subagents on the Build-onward diff, given only the diff, spec Success Criteria, and the plan task list.
- Security: clean, no findings.
- Code review: no P1/P2/P3. One Nit fixed in loop 1 — `metrics.spec_revisions` tag placement diverged from `audit.md`'s canonical mapping; reconciled so spec:441 (the both-modes lifecycle line) is the tag home, spec:551 recorded as the confirming standard-mode write site.
- One Nit accepted as-is: spec:441's clarifying clause about autopilot's Step 3 writer — prose clarification, not a behavioural change, verified accurate; left in as an improvement.
- No carrying-cost debt recorded.

## Artifacts (archived)
Spec, plan, audit, and validation committed at: 5836e51890d1f496dcdb17e1b8bfa0c2d1d1af6d on branch feature/state-write-mode-audit
