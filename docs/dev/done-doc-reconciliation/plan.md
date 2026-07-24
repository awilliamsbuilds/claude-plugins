# Doc Reconciliation in dev:done — Implementation Plan
*Branch: feature/done-doc-reconciliation · 2026-07-24*

## Files

| File | Action | Purpose |
|------|--------|---------|
| plugins/dev/skills/spec/SKILL.md | Modify | Step 6: normalize derived feature name to `^[a-z0-9][a-z0-9-]*$` by construction |
| plugins/dev/skills/fix/SKILL.md | Modify | Step 3: normalize the assembled `ENG-123-<short-title>` slug to `^[A-Za-z0-9][A-Za-z0-9-]*$` (uppercase Linear ID preserved) |
| plugins/dev/skills/done/SKILL.md | Modify | Insert new Step 4a (Reconcile Docs Prose) between Step 4 and Step 5 |

## Tasks

### Task 1: Enforce the feature-slug allowlist at both derivation sites
What: Make the `<feature>` slug match a character allowlist *by construction* at the two points it is first derived, so every downstream interpolation (branch names, artifact paths, and all six `git commit -m "… <feature>"` sites in `dev:done` — including the new one Task 2 adds) is injection-safe.
Used by: every stage that interpolates `<feature>`; closes tracked debt entry #1 ("The feature slug reaches `git commit -m` with no character allowlist"), whose `## To Close` bullet already sits in this cycle's `debt-pending.md`.
Depends on: nothing — first task.
Files: plugins/dev/skills/spec/SKILL.md, plugins/dev/skills/fix/SKILL.md
Interfaces:
- Consumes: nothing.
- Produces: the invariant that `<feature>` (from `dev:spec`) matches `^[a-z0-9][a-z0-9-]*$`, and the `dev:fix` cycle slug matches `^[A-Za-z0-9][A-Za-z0-9-]*$` — relied on by Task 2's new commit site for safety.

Implementation steps:
1. **`dev:spec` Step 6, feature-name derivation** (the line "Feature name: derive from the stated intent, kebab-case, 2-4 words."). Append a normalization instruction directly after it: after deriving the kebab-case name, lowercase it, replace every run of characters outside `[a-z0-9]` with a single `-`, and strip leading/trailing `-`, so the result matches `^[a-z0-9][a-z0-9-]*$`. If normalization yields an empty string, STOP and ask the user for a feature name rather than proceeding with an empty slug. State that this makes `<feature>` safe by construction at every downstream interpolation (branch, paths, all `git commit -m` sites).
2. **`dev:fix` Step 3, branch/slug derivation** (around the `short-title` definition and the `worktree add … ENG-123-<short-title>` command). Add: the `short-title` portion is kebab-cased and lowercased as today; the full cycle slug `ENG-123-<short-title>` is then normalized to match `^[A-Za-z0-9][A-Za-z0-9-]*$` — uppercase is permitted **only** so the Linear issue-ID prefix (e.g. `ENG-123`) survives; every other character outside `[A-Za-z0-9-]` collapses to a single `-`, with leading/trailing `-` stripped. This is still injection-safe (no shell metacharacters reach any interpolation). Note explicitly that the uppercase tolerance is scoped to `dev:fix`; `dev:spec` stays strict-lowercase.
3. In the `dev:fix` edit, add a one-line note that `dev:done`/`dev:plan`'s existing bare-slug arg matchers are lowercase-only (`^[a-z0-9][a-z0-9-]*$`) and are intentionally left unchanged this cycle — resolving an uppercase `dev:fix` slug as a *bare positional argument* to those skills is a pre-existing limitation, out of scope here (the slug still resolves via PR-URL and artifact-path forms). This keeps the divergence deliberate and visible rather than silently introduced.

### Task 2: Insert Step 4a — Reconcile Docs Prose — into dev:done
What: Add a new step to `dev:done`, immediately after Step 4 (Update Component Registry) and before Step 5, that checks whether the merged cycle made `README.md` or the **prose** of `CLAUDE.md` stale and, if so, applies (standard) or records (autopilot/dismissed) targeted edits — mirroring the tech-debt system's mode split.
Used by: runs automatically inside `dev:done` on feature cycles, in both standard and autopilot mode.
Depends on: Task 1 — this step adds the sixth `git commit -m "… <feature>"` interpolation in `done`; it is only safe once Task 1's allowlist guarantees `<feature>` cannot carry shell metacharacters.
Files: plugins/dev/skills/done/SKILL.md
Interfaces:
- Consumes: `push_integration` (defined at the end of Step 2); the detached-`$INTEGRATION` working state established by Step 2; the buffer→flush mechanism (`debt-pending.md` `## To Record` + Step 6a flush) documented in `plugins/dev/references/tech-debt.md`; the `<feature>` allowlist invariant from Task 1.
- Produces: nothing later tasks rely on — terminal task.

Implementation steps:
1. Add a new heading **`## Step 4a: Reconcile Docs Prose (feature cycles only)`** between the end of Step 4 and the start of Step 5. Open by stating it runs only when `cycle_type == "feature"` (architecture cycles skip it, exactly like Step 4), and that it slots here deliberately: after Step 4 so the Component Registry is already current, and before Step 6a so any `## To Record` write it makes is flushed by Step 6a's existing flush.
2. **Targets & missing-file rule.** Reconcile only `README.md` and `CLAUDE.md` at `$WORKDIR` (present at the detached `$INTEGRATION` tip). For each target that does **not** exist: never create it, never error — emit a one-line `no <file> found — skipped` note carried into the Step 8 report (see step 8 below). If both are absent, note both and reconcile nothing.
3. **Detection (agent judgment, not a differ).** Against this cycle's merged diff and its `spec.md` / `plan.md` / `validation.md`, judge whether a concrete factual mismatch exists with each target's prose. For `CLAUDE.md`, scope detection to everything **outside** the `## Component Registry` table — Step 4 owns that table and this step must never touch it. Conservative trigger set, stated explicitly: a new/renamed/removed skill, plugin, command, flag, or config key; or a documented workflow step whose description no longer matches the merged behavior. Explicitly exclude style, tone, and voice rewrites.
4. **Dominant outcome — no mismatch:** the step is silent. No prompt, no commit, no debt entry, no Step 8 line. Fall through to Step 5. State this as the common case so no busywork or empty prompt is manufactured.
5. **On a mismatch — standard mode:** surface each stale spot with a pre-drafted targeted edit; the user approves / applies / dismisses each. Apply approved edits to the file(s), then commit to `$INTEGRATION` with a pathspec-scoped commit and push via the existing helper:
   ```bash
   git -C "$WORKDIR" add README.md CLAUDE.md          # stage only the files actually edited
   git -C "$WORKDIR" commit -m "docs: reconcile README/CLAUDE.md prose after <feature>" -- README.md CLAUDE.md
   push_integration
   ```
   The pathspec on the commit is required for the same reason Steps 6a/7 use one: an earlier step's commit may have left the index otherwise-clean, but the pathspec guarantees this commit sweeps in nothing else under a "reconcile prose" message. `<feature>` is safe to interpolate here **because of Task 1's allowlist** — call that dependency out in the step text. Dismissed spots are routed to the durable record (step 7 below).
6. **On a mismatch — autopilot mode:** no gate. Print the proposed edits into the run log and record **all** detected spots durably (step 7). Never auto-apply prose in autopilot. Add an inline note that this step therefore introduces **no new stop condition** — so `dev:autopilot` Step 2's "When autopilot stops" list needs no change, and its "Debt surfacing: print, never ask" self-applied-writes carve-out already covers this write (it is an unconditional `dev:done` debt write, self-applied, identical in both modes except that prose is only *applied* in standard mode). Mirror the phrasing of the Step 7 reconcile block's existing "this is why `dev:autopilot` Step 2 needs no change" note so the reasoning stays visible to future editors.
7. **Durable record (dismissed-in-standard, or any autopilot detection).** Append a single entry to this cycle's `$WORKDIR/docs/dev/<feature>/debt-pending.md` buffer, titled **`README/CLAUDE.md prose may be stale after <feature>`**. Per `references/tech-debt.md`: if the buffer is absent, create it from the contract's template; insert the `###` entry at the **end of the `## To Record` section, immediately before `## To Close`** — never at end-of-file (end-of-file would land it inside `## To Close` and be silently dropped by the flush). Entry body enumerates each unapplied stale spot with its pre-drafted edit; `**Files:**` names whichever of `README.md`, `CLAUDE.md` are affected; close with `*Source: dev:done · <feature>*`. Any Markdown `#` heading copied from a diff into the body must be indented two spaces (the contract's no-`#`-heading-in-a-field rule) so the flush can't mis-parse it. Step 6a's flush then applies its recurrence-merge and turns this into a tracked `## Open` entry; because the title carries `<feature>` it is unique per cycle.
8. **Reporting.** The step's outcome surfaces as **one** line appended to the Step 8 `✓ <feature> cycle complete` summary block (after the tech-debt line), matching the format the reconcile block already uses: e.g. `Docs prose: N spot(s) reconciled` (standard, applied), `Docs prose: N spot(s) recorded to tech debt` (autopilot/dismissed), and/or the `no <file> found — skipped` note(s). Emit **no** line on the silent no-op path. Per the "its skip is noted once" success criterion, the absent-file note appears once (in this report line); if a `## To Record` entry is being written this cycle, include the skip note there too so it is durable, but do not repeat it elsewhere.
9. Add a closing sentence to the step reaffirming its two hard invariants: it never writes the `## Component Registry` table (Step 4 remains the sole writer), and it never creates a missing `README.md`/`CLAUDE.md`.

## Edge Cases
| Edge case | Handled in | Approach |
|-----------|-----------|----------|
| No mismatch (dominant case) | Task 2, step 4 | Silent no-op — no prompt, no commit, no debt entry, no report line |
| Autopilot mode | Task 2, step 6 | No gate; print + record all detected spots durably; never apply prose; no new stop condition |
| Standard-mode dismiss | Task 2, steps 5+7 | Dismissed spot becomes a `## To Record` buffer entry (same as any deferred debt) |
| `README.md` absent | Task 2, steps 2+8 | Skip; one-line `no README.md found — skipped` note; never create; never error |
| `CLAUDE.md` absent | Task 2, steps 2+8 | Skip with a note; never create |
| Both absent | Task 2, steps 2+8 | Note both, reconcile nothing, no error |
| Architecture cycle | Task 2, step 1 | Step does not run (feature cycles only, like Step 4) |
| Component Registry table | Task 2, steps 3+9 | Detection scoped outside the table; step never writes it |
| Malicious/malformed `<feature>` slug | Task 1 | Allowlist at derivation makes every `git commit -m` interpolation (existing five + the new one) safe by construction |

## Out of Scope
- The `CLAUDE.md` `## Component Registry` table — `done` Step 4 already owns it.
- Rewriting docs for style, tone, or voice — only concrete factual mismatches.
- `AGENTS.md`, `docs/`, or any doc other than `README.md` and `CLAUDE.md`.
- Creating a missing `README.md` or `CLAUDE.md`.
- Architecture cycles.
- Broadening `done`/`plan` bare-slug argument matchers to accept uppercase `dev:fix` slugs (pre-existing lowercase-only limitation; left as-is per Task 1 step 3).
- Tech-debt items #2 (gate-path state-write sweep) and #3 (hardcoded repo path in reflect) — deferred to later cycles.
