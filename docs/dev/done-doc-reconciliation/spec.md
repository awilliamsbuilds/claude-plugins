# Doc Reconciliation in dev:done
*Branch: feature/done-doc-reconciliation · Confidence: 95% — Ready · 2026-07-23*
*Cycle type: feature · Tier: standard*

## Intent
A `/dev` cycle keeps the `CLAUDE.md` **Component Registry** current (`done` Step 4), but nothing reconciles the rest of the docs. Verified this cycle: `README.md` is only ever *read* (by `init`), never written by any stage; `CLAUDE.md` is only ever written as its `## Component Registry` section (`init`, `shape`, `done` Step 4), always "preserve all other content exactly." So when a merged feature adds a skill, command, flag, config key, or changes a documented workflow, the README and the prose parts of `CLAUDE.md` silently drift out of date. This adds a step to `dev:done` that **checks whether** the merged change made those docs stale and, if so, applies (standard) or records (autopilot) targeted edits — mirroring how the tech-debt system already splits behavior across modes, so both are governed by one convention and change together.

## Scope
- A new step in `dev:done`, immediately after Step 4 (Update Component Registry), that runs on **feature cycles**.
- It **detects** whether this cycle's merged diff (read against `spec.md` / `plan.md` / `validation.md` and the actual changes) created a concrete mismatch with:
  - `README.md`
  - the **prose** of `CLAUDE.md` — everything outside the `## Component Registry` table, which Step 4 owns.
- **Detection is a check, not an assumption.** The common outcome is "no change needed," and in that case the step is silent — no empty proposal, no noise.
- **Conservative detection:** propose only where there is a concrete diff-to-doc mismatch — a new/renamed/removed skill, plugin, command, flag, or config key; a documented workflow step whose description no longer matches. Not style or voice polish.
- **Mode behavior — mirrors the tech-debt system:**
  - **Standard mode:** surface each detected stale spot with a pre-drafted targeted edit; the user **approves / applies / dismisses**. Nothing is auto-applied to prose. Approved edits are applied and committed to `$INTEGRATION` via the existing `push_integration` helper.
  - **Autopilot mode:** print the proposed edits into the run log and **record them durably** (never auto-apply prose). No gate.
- **Durable record = the existing tech-debt mechanism.** A detected-but-**unapplied** mismatch (standard-mode dismiss, or any autopilot detection) is written as a `## To Record` entry in this cycle's `debt-pending.md` buffer, which `done` Step 6a already flushes into `docs/dev/tech-debt.md`. It then shows in `/dev:debt` and is governed by the same convention as all other debt.
- **Missing target file:** the step reconciles only files that exist. If a target is absent (`README.md` or `CLAUDE.md`), it is **not** created — the step emits a one-line note (`no README.md found — skipped`) in the `done` report and durable record, and moves on.
- **Folded-in tech debt (#1 — "The feature slug reaches `git commit -m` with no character allowlist"):** this step adds another `git commit -m "… <feature>"` call site in `done`. Rather than add a sixth unguarded interpolation, close the shape at the source: add feature-name allowlisting in `dev:spec` Step 6 (feature-name derivation) and `dev:fix` Step 3 so `<feature>` matches `^[a-z0-9][a-z0-9-]*$` by construction, making every downstream interpolation safe. Closes that tracker entry (recorded in `debt-pending.md` → `## To Close`).

## Out of Scope
- The `CLAUDE.md` `## Component Registry` table — `done` Step 4 already owns it.
- Rewriting docs for style, tone, or voice — only concrete factual mismatches.
- `AGENTS.md`, `docs/`, or any doc other than `README.md` and `CLAUDE.md`.
- **Creating** a missing `README.md` or `CLAUDE.md`.
- Architecture cycles (like Step 4, this is feature-cycle work).
- Tech-debt items #2 (gate-path state-write sweep) and #3 (hardcoded repo path in reflect) — deferred to later cycles.

## Success Criteria
- After a feature merges, `done` runs a reconciliation check with three possible outcomes, all observable:
  1. **No mismatch:** the step is silent; no prompt, no commit, no debt entry.
  2. **Mismatch, standard mode:** the user is shown each stale spot with a pre-drafted edit and can approve/apply/dismiss; approved edits land in `README.md`/`CLAUDE.md` and are committed to `$INTEGRATION`.
  3. **Mismatch, autopilot or dismissed:** a `docs/dev/tech-debt.md` entry exists after the cycle ("README/CLAUDE.md prose may be stale after `<feature>`") and the proposal appears in the run log/report.
- An absent target file never causes an error and is never created; its skip is noted once.
- The Component Registry table is untouched by this step (Step 4 remains its only writer).
- `<feature>` derivation rejects anything outside `[a-z0-9-]`; all six `git commit -m "… <feature>"` sites in `done` are safe by construction; debt entry #1 is closed.

## Happy Path
1. A feature cycle reaches `dev:done`; the PR merges (Step 2) and the Component Registry updates (Step 4).
2. The new step reviews the cycle's merged diff and artifacts against `README.md` and `CLAUDE.md` prose.
3. **Most common:** no concrete mismatch is found → the step reports nothing and `done` proceeds to Step 5.
4. **If a mismatch is found (standard mode):** the user sees each stale spot with a pre-drafted targeted edit and approves, edits, or dismisses.
5. Approved edits are applied and committed to `$INTEGRATION` via `push_integration`; dismissed ones are recorded to the tech-debt tracker.
6. `done` continues to Step 5 (Decision Log) and onward.

## Edge Cases
- **No mismatch (dominant case):** silent no-op — the step must not manufacture busywork or empty prompts.
- **Autopilot mode:** no gate; detected edits are recorded durably (tracker) and printed, never applied to prose. Mirrors tech-debt's autopilot carve-out (records the decision, doesn't make it).
- **Standard-mode dismiss:** a dismissed mismatch is not lost — it becomes a tracker entry, exactly like a not-folded-in debt item.
- **`README.md` absent:** skip README reconciliation; one-line note; never create.
- **`CLAUDE.md` absent:** normally `init` guarantees it, but if absent, skip with a note; never create.
- **Both absent:** step reconciles nothing, notes both skips, no error.
- **Architecture cycle:** step does not run (feature cycles only).
- **`git commit -m` safety:** a malicious or malformed `<feature>` slug cannot execute via the new (or existing) commit interpolations once the allowlist is in place.

## Audience
`/dev` workflow maintainers and anyone running `/dev` cycles in a repo with a `README.md` / `CLAUDE.md` (agent-facing).

## Technical Constraints
- The step runs in `$WORKDIR`, detached at the merged `$INTEGRATION` tip (the state `done` Steps 3–7 already operate in), and must push via the existing `push_integration` helper — no new push path.
- It must slot after Step 4 and before Step 6a (so any `## To Record` write it makes is flushed by Step 6a's existing flush).
- Detection is agent judgment over the diff, not a mechanical differ; the spec fixes *what* counts as a mismatch, not a parsing algorithm.
- Must not alter the `## Component Registry` table or Step 4's behavior.

## Dependencies
- `push_integration` helper (defined in `done` Step 2) and the detached-`$INTEGRATION` working state.
- The tech-debt buffer→flush mechanism: `debt-pending.md` `## To Record` + `done` Step 6a flush (`plugins/dev/references/tech-debt.md`).
- Slug-allowlist edits touch `dev:spec` Step 6 and `dev:fix` Step 3 in addition to `done`.

## UI Needed
No. Shape stage is skipped; Plan follows Spec directly. (This is a change to skill instructions — no visual interface.)

---
*Auto-filled dimensions: none*
*Grounding inventory: `grep -rn "README" plugins/dev/skills/` → only `init` (read at line 30, prompt line 35, template placeholder line 178); no stage writes README. `grep -rn "CLAUDE.md" plugins/dev/skills/` → writes only in `init` (Create/Update, Component Registry only), `shape` (line 63, registry), `done` Step 4 (`git add CLAUDE.md`, registry table); all else reads. `done` structure mapped (Steps 1–8; `push_integration` defined end of Step 2; Steps 3–5/6a/7 push to `$INTEGRATION`; new step fits after Step 4, before Step 6a). Tech-debt `## Open` cross-checked: 3 entries name `done/SKILL.md`; #1 (slug allowlist) folded into scope, #2/#3 deferred.*
