# Telemetry Schema — Implementation Plan
*Branch: feature/telemetry-schema · 2026-09-09*

## Files

| File | Action | Purpose |
|------|--------|---------|
| `plugins/dev/references/telemetry.md` | Create | Canonical ledger contract — path, envelope, both record shapes, the append procedure (T1–T6) |
| `plugins/dev/skills/pr/SKILL.md` | Modify | Capture `pr_start`; write `pr_start`/`pr_end` into `state.json` (new Step 5e stamps `pr_end`) |
| `plugins/dev/skills/reflect/SKILL.md` | Modify | One clause on Step 1's `stage_timestamps` bullet: an absent `pr_end` means the PR stage is still running |
| `plugins/dev/skills/done/SKILL.md` | Modify | Capture `done_start`; new Step 6b appends the cycle record before Step 7's `rm -rf` |
| `plugins/dev/skills/fix/SKILL.md` | Modify | Derive lane values inside the merge fence; new `### Telemetry record` segment appends the lane record; Report line |
| `plugins/dev/skills/autopilot/SKILL.md` | Modify | Add the ledger-append failure to `## Purpose`'s "When autopilot stops" list |
| `docs/dev/product-plans/dev-observability.md` | Modify | Collapse Milestone 2 to one item, correct the `_start` claim, fix the header count |

No file is created under `docs/telemetry/` by this cycle. The ledger is created writer-side on first
append (Task 1, T1), which is what Success Criterion 7 asks for; committing an empty or seeded
`runs.jsonl` here would make the create-if-absent branch unexercised on this repo.

## Tasks

### Task 1: Write the telemetry ledger contract reference

What: Define, in one canonical place, where the ledger lives, what one record looks like in each of
its two kinds, and the exact procedure a writer follows to append one.

Used by: Task 3 (`dev:done` Step 6b) and Task 4 (`dev:fix`'s `### Telemetry record`) cite it as their
append procedure; Milestone 3's `lifecycle-viewer` reads it as the format it renders.

Depends on: nothing — first task.

Files: create `plugins/dev/references/telemetry.md`.

Interfaces:
- Consumes: nothing.
- Produces:
  - `LEDGER_PATH` — the repo-relative constant string `docs/telemetry/runs.jsonl`.
  - **§T-envelope** — the shared outer record shape (field names and types below).
  - **§T-cycle** — the cycle-record-only fields.
  - **§T-lane** — the lane-record-only fields.
  - **§T-append (T1–T6)** — the six-step append procedure, named so callers can cite it.
  - **§T-stagemap** — the rule mapping `state.json` stamps onto the record's `stages` object.
- State keys: none — this task introduces no `state.json` key.
- Shared procedure: **the ledger append.** This task is the **canonical** implementation. Tasks 3 and
  4 are *call sites*, not mirrors: they cite §T-append rather than restating it, the same way
  `dev:spec` Step 6 and `dev:fix` Step 2b cite `references/product-plans.md` §L1 rather than
  restating the lookup. Each call site names only its own divergences (identity field, push helper,
  guard set) — enumerated in that task's own `Shared procedure:` line.

Implementation steps:

1. Create the file with the repo's reference-doc shape: an H1 title, a one-paragraph purpose, then
   the named sections below. It is a reference, not a skill — no frontmatter `name:`/`description:`,
   matching `plugins/dev/references/product-plans.md` and `tech-debt.md`.

2. State the **path and why it is that path**, as §T-path:
   - `docs/telemetry/runs.jsonl` — repo-relative, resolved against the writer's own tree root
     (`$WORKDIR` for `dev:done`, `$PRIMARY` for `dev:fix`).
   - **Not** `docs/dev/telemetry/`: a future cycle whose slug were `telemetry` would put
     `dev:done` Step 7's `rm -rf "$WORKDIR/docs/dev/<feature>/"` (`done/SKILL.md:364`) directly on
     top of the ledger.
   - Named `runs`, not `cycles`: the file holds both kinds, and naming it after one is the exact
     conflation the `kind` field exists to prevent.
   - One JSON object per line, no trailing commas, newline-terminated, append-only. Never rewrite,
     reorder, or delete a line — a correction is a new line, not an edit.

3. Define **§T-envelope** — present on every record, in this key order:

   | Field | Type | Meaning |
   |---|---|---|
   | `schema` | int | Format version. `1` for this cycle. A reader that does not recognise the value skips the line rather than guessing. |
   | `kind` | `"cycle"` \| `"lane"` | **Success Criterion 5's distinguishing field.** A reader must filter on it before averaging anything. |
   | `id` | string | Identity within the kind: the cycle's `state.json.feature` for `"cycle"`; the merged branch name for `"lane"`. |
   | `pr_number` | int \| null | The PR this run merged. Null only where the writer genuinely had none. |
   | `start` | ISO-8601 UTC string \| null | When the run began, per `basis`. Null only when underivable. |
   | `end` | ISO-8601 UTC string | When the run finished. Never null — a record is only written after the run ended. |
   | `basis` | string | **What `start` measures.** One of `"spec_start"` (cycle), `"first_commit"` (lane), `"unavailable"` (lane, squash merge). Named because a lane's `start` is its first commit — after grounding and triage — and comparing it against a cycle's `spec_start` as though they measured the same thing is a real misreading, not a hypothetical one. |
   | `note` | string \| null | Free text naming why an underivable field is null. Null when everything derived. |

   State plainly that a reader **must** branch on `kind` and **must not** compare a `"first_commit"`
   `start` against a `"spec_start"` one.

4. Define **§T-cycle** — added to the envelope when `kind == "cycle"`, all read from `state.json`
   except `stages.done`:

   | Field | Type | Source |
   |---|---|---|
   | `tier` | string | `state.json.tier` |
   | `cycle_type` | string | `state.json.cycle_type` |
   | `mode` | string | `state.json.mode` |
   | `handoff_at` | string \| null | `state.json.handoff_at`; **absent key reads as null**, per `dev:autopilot` Step 1's read contract |
   | `stages` | object | Per §T-stagemap |
   | `metrics` | object | `spec_questions_asked`, `spec_revisions`, `visual_screens_shown`, `files_read_in_build` — copied from `state.json.metrics`, each defaulting to `0` if absent |
   | `validate` | object | `{loops_run, loops_max}` from `state.json.validate` |
   | `challenge` | object | `{run, blockers, concerns, applied, applied_concerns, dismissed, loops_run}` from `state.json.challenge` |
   | `challenge_plan` | object | The same seven keys from `state.json.challenge_plan` |
   | `confidence` | object | `{final_score, final_level, auto_filled: <length of state.json.confidence.auto_filled>}` |
   | `product_plan` | string \| null | `state.json.product_plan` |
   | `linear_issue` | string \| null | `state.json.linear_issue.id`, or null when `linear_issue` is null |

   `challenge.blockers` and `challenge.concerns` may legitimately be `null` rather than an integer —
   `dev:spec` Step 12a's errored-dispatch rule sets them to a third value distinct from `0`. Copy
   the value through unchanged; never coerce a `null` to `0`.

5. Define **§T-lane** — added to the envelope when `kind == "lane"`:

   | Field | Type | Source |
   |---|---|---|
   | `commits` | int \| null | `git rev-list --count <sha>^1..<sha>^2` |
   | `churn` | object \| null | `{files, insertions, deletions}` parsed from `git diff --shortstat <sha>^1 <sha>^2` |
   | `merge_sha` | string \| null | The merge commit's full SHA — the basis every other lane value was derived from. Null **only** when the merge commit could not be identified at all (see the third branch below) |

   State the derivation set as the four commands the spec grounded against merged PR #94, all
   merge-commit-relative and none branch-relative (the branch is deleted before a record can be
   written — `fix/SKILL.md:1137` deletes it inside the merge fence):

   ```
   start   git log --format=%cI <sha>^1..<sha>^2 | tail -1
   end     git log -1 --format=%cI <sha>
   commits git rev-list --count <sha>^1..<sha>^2
   churn   git diff --shortstat <sha>^1 <sha>^2
   ```

   **Parsing `--shortstat` — the omitted clauses are `0`, not missing.** `git diff --shortstat`
   drops a clause entirely when its count is zero (`1 file changed, 3 deletions(-)` — no
   insertions clause) and prints an **empty line** for an empty diff. A deletions-only lane run is
   not rare: a `/dev:fix` that removes text produces exactly that shape. So: an absent clause
   parses to `0`, never to a missing key; empty output yields
   `{"files": 0, "insertions": 0, "deletions": 0}`. A parser written literally to the field table
   above, without this rule, crashes or emits a partial object on the commonest real input.

   **There are three branches, not two, and the difference between the last two is load-bearing.**
   A record is written on all three — skipping one would silently under-count lane work.

   | Branch | Condition | Record |
   |---|---|---|
   | **Derived** | a merge SHA is known and `<sha>^2` resolves | every field derived; `basis: "first_commit"`, `note: null` |
   | **Squash** | a merge SHA is known but `<sha>^2` does not resolve | `merge_sha` set; `start: null`, `basis: "unavailable"`, `commits: null`, `churn: null`, `note: "squash merge — no second parent; start, commits and churn underivable"`. `end` is read from the merge commit itself |
   | **No SHA** | the merge commit could not be identified **or could not be read in the writer's tree** — a transient `gh pr view --json mergeCommit` failure, auth loss, or a commit `gh` reports that `git` cannot fetch (the two do not share credentials). Reachable even with `RECONCILED=1` | `merge_sha: null`; `start: null`, `basis: "unavailable"`, `commits: null`, `churn: null`, `note: "merge commit not available locally (no mergeCommit from gh, or the commit could not be fetched); start, commits and churn underivable"`. `end` is the wall-clock time of the append |

   **Never collapse the third branch into the second.** They differ in what actually happened: one
   is a genuine squash, the other is a tooling failure on a merge that may well have had two
   parents. Writing the squash `note` on a no-SHA run asserts a merge shape nobody observed — the
   same class of misreading the `basis` field exists to prevent. **The squash arm may only be
   entered with the commit readable in the writer's tree**; an unreadable SHA belongs to the third
   branch, not the second. `end` and `pr_number` are known on all three branches.

   **The three branches are the shapes a *written* record can take; they are not a claim that every
   merged lane run produces one.** The caller carries its own guard above this contract: `dev:fix`
   skips the append entirely when its checkout is not reconciled, because a commit there would be
   unpushable (Task 4 step 3). That skip is the caller's, not §T-lane's, and it is reported rather
   than recorded.

6. Define **§T-stagemap** — how `stages` is built:
   - The stage list is `spec`, `shape`, `plan`, `build`, `validate`, `pr`, `done`, in that order.
   - **A stage named in `state.json.skipped[]` is omitted from the object entirely** — not present
     with nulls (Success Criterion 3).
   - For `spec`…`pr`, each present stage emits `{"start": <stage>_start, "end": <stage>_end}` read
     from `state.json.metrics.stage_timestamps`. A stamp absent from a legacy state file emits
     `null` for that side rather than omitting the stage.
   - `pr` additionally emits `"created": pr_created`, preserving the existing key `dev:reflect`
     Step 1 reads (`reflect/SKILL.md:49`).
   - **`done` is the one stage whose stamps do not come from `state.json`.** `dev:done` holds
     `done_start`/`done_end` in-run and writes them straight into the record. Say why, so a later
     edit does not "fix" it by routing them through state: `dev:done` writes no `metrics.*` today,
     and `state.json` is deleted seconds later by that same stage's Step 7, so a state round-trip
     would add a writer to a file already being torn down, for no reader.
   - `done` is never in `skipped[]`, so it is always present on a cycle record.

7. Define **§T-append (T1–T6)** — the procedure, in the writer's own tree (`$ROOT` below stands for
   `$WORKDIR` in `dev:done`, `$PRIMARY` in `dev:fix`):

   - **T1 — create if absent.** `mkdir -p "$ROOT/docs/telemetry"`. The ledger file itself is created
     by the append. Its absence is never an error and never fails the run (Success Criterion 7).
   - **T2 — dedup, and it is per-kind.** Read every existing line; if any parses as JSON with
     `kind` equal to the kind about to be written **and** `id` equal to the id about to be written,
     **append nothing and report "already recorded"** (Success Criterion 6). A line that fails to
     parse is skipped by the dedup scan rather than aborting it — a hand-corrupted line must not
     block a legitimate append. Note explicitly that matching on `id` **within the kind** is what
     keeps a lane record whose branch happened to equal a feature slug from suppressing that
     feature's cycle record.
   - **T3 — serialize.** Build the object and emit exactly one line with
     `json.dumps(record, separators=(",", ": "), sort_keys=False)` followed by `\n`, appended in
     `"a"` mode. Key order follows §T-envelope then the kind-specific section. Use `python3` only —
     stdlib, no `jq`, no new runtime dependency (spec Technical Constraints).
   - **T4 — verify the write landed.** Re-read the last line of the file and confirm it parses and
     carries the expected `kind` and `id`. A silent partial write must not be reported as success.
   - **T5 — commit under the ledger's own pathspec**, never a widened one:
     ```bash
     git -C "$ROOT" add docs/telemetry/
     git -C "$ROOT" diff --cached --quiet -- docs/telemetry/ || \
       git -C "$ROOT" commit -m "<message>" -- docs/telemetry/
     ```
     Both the `add` and the `commit` carry the pathspec. State why in one line: an unpathspec'd
     `--quiet` sees anything else already staged and the commit that follows sweeps it in — the same
     reasoning `dev:done` Step 6a and Step 7 already give for their own pathspecs. The `--quiet`
     guard is what makes T2's "already recorded" path exit cleanly instead of failing on an empty
     index.
   - **T6 — push, and treat failure as the caller's stop.** The push itself is the caller's (the two
     call sites use different helpers — see each task's `Shared procedure:` line). §T-append's rule
     is only this: **a failed append or a failed push is reported and stops the caller; it is never
     pushed past.** For `dev:done` that is load-bearing — Step 7 destroys the only copy of the data
     the append failed to save (Success Criterion 2).

8. Close the file with a **Consumers** section naming `dev:done` Step 6b, `dev:fix`'s
   `### Telemetry record`, and Milestone 3's `lifecycle-viewer` (not yet built), so a later editor
   knows both ends to keep in step.

---

### Task 2: `dev:pr` — capture `pr_start` and `pr_end`

What: Give the PR stage the start/end stamp pair every other instrumented stage already has, so
Success Criterion 3 holds for `pr`.

Used by: Task 3's record builder reads both keys through §T-stagemap; nothing else consumes them.

Depends on: Task 1 (§T-stagemap is what defines these two keys as required inputs).

Files: modify `plugins/dev/skills/pr/SKILL.md`, `plugins/dev/skills/reflect/SKILL.md`.

Interfaces:
- Consumes: Task 1's §T-stagemap (as the contract these keys satisfy).
- Produces: `state.json.metrics.stage_timestamps.pr_start` and
  `state.json.metrics.stage_timestamps.pr_end`, both ISO-8601 UTC strings from
  `date -u +%Y-%m-%dT%H:%M:%SZ`.
- State keys: `metrics.stage_timestamps.pr_start` `(writes: both)`,
  `metrics.stage_timestamps.pr_end` `(writes: both)`. `dev:pr` **does** mode-split — Step 5b's
  docs-prose reconciliation branches at `pr/SKILL.md:276`/`:290`, and `### Push and display`
  branches again at `:398`/`:419` — but neither key sits inside a split arm: `pr_start` is written
  in Step 5's unconditional state write, and `pr_end` in Step 5e, which precedes
  `### Push and display`. Both keys are therefore written on every path — `(writes: both)`. Do not
  place Step 5e inside either mode arm.
- Shared procedure: none.

Implementation steps:

1. After the `## Resolve the working directory (do this first)` block and before `## Purpose`, add
   the first-action capture line, worded to match `dev:plan`'s existing one verbatim in shape:

   > **First action, before anything else:** run `date -u +%Y-%m-%dT%H:%M:%SZ` and hold onto the
   > output — this is `pr_start`, recorded in Step 5. Capturing it now, before any other work, keeps
   > it accurate to when the stage actually began.

2. In **Step 5**'s bullet list (`pr/SKILL.md:222`), add one bullet directly above the existing
   `pr_created` bullet:

   > - Record `metrics.stage_timestamps.pr_start` — the value captured at the very top of this
   >   skill, before Step 1. **On re-entry, leave the existing value alone**, for the same reason
   >   `pr_created` does: it marks when the stage first began, and re-stamping it would report the
   >   resume time instead.

3. Add a new sub-step **`### Step 5e: Stamp pr_end`**, placed **after `### Step 5d: Run dev:reflect`
   and before Step 5's single push at the end.** Its body:
   - Run `date -u +%Y-%m-%dT%H:%M:%SZ` and write it to `metrics.stage_timestamps.pr_end`.
   - **On re-entry, leave an existing `pr_end` alone** — write-once, the same rule as `pr_start` and
     `pr_created`. State the three as one rule so a later editor does not have to infer it: *the
     three `pr` stamps are write-once; a second entry re-runs the stage but does not re-date it.*
   - Commit under the state.json pathspec, guarded for an empty stage exactly as Step 5's own state
     commit is:
     ```bash
     git -C "$WORKDIR" add docs/dev/<feature>/state.json
     git -C "$WORKDIR" diff --cached --quiet -- docs/dev/<feature>/state.json || \
       git -C "$WORKDIR" commit -m "pr: stamp pr_end for <feature>" -- docs/dev/<feature>/state.json
     ```
   - State the placement reason in one sentence: `pr_end` must cover Steps 5a–5d, which are the bulk
     of the stage's work, so it cannot be stamped in Step 5's own state write; and it must be
     *before* the push so its commit rides into PR #N's diff like every other 5x commit
     (`pr/SKILL.md:239`).

4. Extend Step 5's existing "Sub-steps 5a–5d sit here deliberately" paragraph to read **5a–5e**, and
   add one clause naming why 5e is last in the block: it dates the end of the stage, so anything
   that ran before it is inside the span and anything after it is only the push.

5. **Extend `dev:reflect` Step 1's `stage_timestamps` bullet** (`reflect/SKILL.md:49`) with one
   clause, because this task creates a stamp that is legitimately unpaired at read time:
   `dev:reflect` runs at `dev:pr` Step 5d, so `pr_start` is on disk by then and `pr_end` — stamped
   in Step 5e, after — is not. Add: *an absent `pr_end` means the PR stage is still running at the
   moment Reflect reads it (Step 5e stamps it afterwards); report `pr` as in-progress rather than
   computing a duration from a missing end.* Without this, every retrospective from this cycle
   onward reads an unpaired `pr` stamp and has no rule for it. This is a one-clause edit to an
   existing bullet — do not restructure Step 1.

6. Do **not** touch `pr_created`. It keeps its existing meaning and its existing reader
   (`dev:reflect` Step 1, `reflect/SKILL.md:49`); §T-stagemap carries it through as
   `stages.pr.created` alongside the new pair.

---

### Task 3: `dev:done` — capture `done_start`/`done_end` and append the cycle record

What: Write one cycle record into the ledger before Step 7 destroys `state.json`, and give the Done
stage the start/end pair it has never had.

Used by: the ledger is the only durable consumer; Milestone 3's viewer reads what this writes.

Depends on: Task 1 (cites §T-append, §T-envelope, §T-cycle, §T-stagemap), Task 2 (`stages.pr`
requires the two keys Task 2 introduces).

Files: modify `plugins/dev/skills/done/SKILL.md`.

Interfaces:
- Consumes: Task 1's `LEDGER_PATH`, §T-envelope, §T-cycle, §T-stagemap, §T-append (T1–T6); Task 2's
  `metrics.stage_timestamps.pr_start` / `pr_end`.
- Produces: one `kind: "cycle"` line in `docs/telemetry/runs.jsonl`, committed and pushed to
  `$INTEGRATION`.
- State keys: **none.** `done_start` and `done_end` are held in-run and written straight into the
  record — they are deliberately **not** `state.json` keys. Do not add them to `state.json`: that
  file is deleted by this same stage's Step 7 and has no reader for them (spec Scope 2).
- Shared procedure: **the ledger append.** This is a **call site** of Task 1's canonical §T-append,
  cited rather than restated. Its three divergences from the generic procedure, named here so the
  two call sites cannot drift silently:
  - **D1 — `$ROOT` is `$WORKDIR`**, which Step 2 left detached at the merged `$INTEGRATION` tip. On
    a legacy in-place cycle `$WORKDIR` *is* `$PRIMARY`; the path is repo-relative either way, so
    the legacy lane needs no special case (spec Edge Cases asked this be confirmed rather than
    assumed — it is confirmed here by the resolution block at `done/SKILL.md:10`, which sets
    `WORKDIR` to the primary tree on that lane).
  - **D2 — the push is `push_integration`**, the helper defined at the end of Step 2, targeting
    `HEAD:$INTEGRATION` so it works from the detached HEAD. `dev:fix`'s call site has no such helper.
  - **D3 — T6's stop is a hard STOP for the stage.** A failed append or push must not fall through
    to Step 7.

Implementation steps:

1. After the `## Resolve the working directory (do this first)` block (which ends with the
   `INTEGRATION` definition) and before `## Purpose`, add the first-action capture line:

   > **First action, before anything else:** run `date -u +%Y-%m-%dT%H:%M:%SZ` and hold onto the
   > output — this is `done_start`, written into the telemetry record in Step 6b. It is **not**
   > written to `state.json`. Capturing it now, before the merge, keeps it accurate to when the
   > stage actually began.

2. Add a new **`## Step 6b: Append the telemetry record`**, positioned **after Step 6a and before
   Step 7**. Open it with the position rationale, in the same voice Step 6a uses for its own:

   > **The position of this step is load-bearing.** After Step 6a, so a flush that STOPped never
   > reaches an append that would then be followed by Step 7's teardown; and before Step 7, so the
   > record is written while `state.json` still exists. Step 7's `rm -rf` is what makes this the
   > last possible moment. Do not move it.

3. Body of Step 6b, in order:
   - Run `date -u +%Y-%m-%dT%H:%M:%SZ` — this is `done_end`.
   - Read `$WORKDIR/docs/dev/<feature>/state.json` (already read at Step 1; re-read it here so the
     record reflects every write this stage has made since).
   - Build the record per §T-envelope + §T-cycle + §T-stagemap, with:
     `kind: "cycle"`, `id: <state.json.feature>`, `pr_number: <state.json.artifacts.pr_number>`,
     `start: <metrics.stage_timestamps.spec_start>`, `end: <done_end>`, `basis: "spec_start"`,
     `note: null`, and `stages.done = {"start": <done_start>, "end": <done_end>}`.
   - Run §T-append T1–T5 with `$ROOT = "$WORKDIR"` and commit message
     `chore: record telemetry for <feature>`.
   - Push with `push_integration`.
   - **STOP on any failure** — append, verify, commit, or push — with the message:
     `STOP: telemetry record for <feature> did not land — do not run Step 7 (it deletes state.json).`
     Word the surrounding sentence so the reason is unmissable: Step 7 destroys the data this step
     failed to save.

4. State the pathspec relationship to its neighbours explicitly, since three consecutive steps now
   commit with three different pathspecs: Step 6a commits `-- docs/backlog/`, Step 6b commits
   `-- docs/telemetry/`, Step 7 commits `-- docs/dev/<feature>/`. None widens; each stages only its
   own tree. Add the same "do not widen this pathspec" note Step 7 already carries.

5. In **Step 7**, extend the existing mid-rebase guard's prose to name Step 6b beside Step 6a: a
   push conflict from *either* step leaves `$WORKDIR` mid-rebase, and the guard's `exit 1` covers
   both. The guard's code is unchanged — only the sentence explaining what it protects.

6. In **Step 8**'s display block, add one line: `Telemetry: cycle record appended to
   docs/telemetry/runs.jsonl` — or, on T2's already-recorded path,
   `Telemetry: already recorded (re-entry)`. A single two-space-indented line, matching the block's
   existing shape.

   **Pin the order explicitly, because that slot is already claimed.** `done/SKILL.md:513–516`
   places the primary-checkout reconciliation line "right after the tech-debt line (or in its place
   when both debt counts are zero)" — the exact position this line would otherwise take, and the
   `RECONCILE_MSG` `case` block is what actually prints it. So the block's order becomes: tech-debt
   line (when non-zero) → **telemetry line** → reconciliation line. Reword the reconciliation
   paragraph's "or in its place when both debt counts are zero" to say **after the telemetry line**,
   which is unconditional and therefore always present. Leave the `case` block's code unchanged —
   only its placement sentence moves.

7. Do **not** change Step 3, Step 6a, or Step 7's commit blocks. The record is a fourth commit, not
   a widening of an existing one — spec Technical Constraints states Step 7's pathspec scoping is
   load-bearing and must stay.

---

### Task 4: `dev:fix` — derive and append the lane record

What: Record a `/dev:fix merge` run in the same ledger, with every value derived from the merge
commit, so the lane writes no state while it works.

Used by: the ledger; Milestone 3's viewer renders lane records beside cycle records.

Depends on: Task 1 (cites §T-append, §T-envelope, §T-lane).

Files: modify `plugins/dev/skills/fix/SKILL.md`.

Interfaces:
- Consumes: Task 1's `LEDGER_PATH`, §T-envelope, §T-lane, §T-append (T1–T6); the merge fence's
  `PR_NUMBER`, `BRANCH`, `PRIMARY`, `DEFAULT_BRANCH`.
- Produces: one `kind: "lane"` line in `docs/telemetry/runs.jsonl`, committed and pushed to
  `$DEFAULT_BRANCH`.
- State keys: none — the lane writes no `state.json` at all (`fix/SKILL.md:16`), and this task does
  not change that. Every value is derived from git.
- Shared procedure: **the ledger append.** This is a **call site** of Task 1's canonical §T-append,
  cited rather than restated. Its three divergences, named here to match Task 3's list:
  - **D1 — `$ROOT` is `$PRIMARY`.** The lane never creates a worktree, so there is only the in-place
    shape.
  - **D2 — there is no `push_integration` helper.** The lane targets `$DEFAULT_BRANCH` directly, so
    T6's push reuses the fetch/rebase/re-push **shape** the closeout hook already uses
    (`fix/SKILL.md:1161` ff.), not the helper.
  - **D3 — T6's stop is a report, not an exit.** Nothing downstream destroys data here, so a failed
    push leaves the record committed-but-unpushed and the Report says so in those words — the same
    treatment the closeout hook gives its own failed push. This is the deliberate opposite of Task
    3's D3, and the asymmetry is the point: `dev:done` has a teardown behind it, the lane does not.

Implementation steps:

1. **Derive inside the merge fence.** In `### Merge, then clean up` (`fix/SKILL.md:1106`), after the
   existing `delete_feature_branch || exit 1` line, append a derivation block to the *same* fenced
   script — the fence is where `PR_NUMBER`, `BRANCH` and the merge are all still in hand:

   ```bash
   # Telemetry derivation — merge-commit-relative, per references/telemetry.md §T-lane.
   MERGE_SHA=$(gh pr view "$PR_NUMBER" --repo "$SLUG" --json mergeCommit -q '.mergeCommit.oid')
   git -C "$PRIMARY" fetch --quiet origin "$DEFAULT_BRANCH" 2>/dev/null || true
   # A SHA GitHub knows but this checkout cannot read is a fetch failure, not a squash.
   if [ -n "$MERGE_SHA" ] && ! git -C "$PRIMARY" cat-file -e "${MERGE_SHA}^{commit}" 2>/dev/null; then
     git -C "$PRIMARY" fetch --quiet origin "$MERGE_SHA" 2>/dev/null || true
     git -C "$PRIMARY" cat-file -e "${MERGE_SHA}^{commit}" 2>/dev/null || MERGE_SHA=""
   fi
   echo "TELEMETRY branch=$BRANCH pr=$PR_NUMBER sha=${MERGE_SHA:-none}"
   if [ -n "$MERGE_SHA" ] && git -C "$PRIMARY" rev-parse --verify --quiet "$MERGE_SHA^2" >/dev/null; then
     echo "TELEMETRY start=$(git -C "$PRIMARY" log --format=%cI "$MERGE_SHA^1..$MERGE_SHA^2" | tail -1)"
     echo "TELEMETRY end=$(git -C "$PRIMARY" log -1 --format=%cI "$MERGE_SHA")"
     echo "TELEMETRY commits=$(git -C "$PRIMARY" rev-list --count "$MERGE_SHA^1..$MERGE_SHA^2")"
     echo "TELEMETRY churn=$(git -C "$PRIMARY" diff --shortstat "$MERGE_SHA^1" "$MERGE_SHA^2")"
   elif [ -n "$MERGE_SHA" ]; then
     echo "TELEMETRY end=$(git -C "$PRIMARY" log -1 --format=%cI "$MERGE_SHA")"
     echo "TELEMETRY squash=1"
   else
     echo "TELEMETRY end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
     echo "TELEMETRY nosha=1"
   fi
   ```

   Annotate three things in prose beneath it:
   - **Why it is inside the fence.** `BRANCH` and `PR_NUMBER` cannot be re-derived afterwards — the
     fence deletes both branches and moves the checkout, and a re-run of the resolution block would
     bind `BRANCH` to `$DEFAULT_BRANCH` and exit on its own guard (`fix/SKILL.md:1218` already
     states this for `ITEM`/`BRANCH_MERGED`; the same reasoning applies here).
   - **Why the `fetch` is `|| true`, and why an unreadable SHA is demoted rather than tolerated.**
     The merge commit must be present locally for `git log` / `rev-list` / `rev-parse` to read it.
     On the healthy path `pull --ff-only` above already brought it in; the fetch covers the
     `RECONCILED=0` paths. But `gh` and `git` do not share credentials — `gh` speaks HTTPS with its
     own token while the remote may be SSH — so a SHA GitHub happily reports can be one this
     checkout cannot read. Left unguarded, `rev-parse "$MERGE_SHA^2"` fails for the *wrong reason*,
     the squash arm runs `git log -1` against an object git does not have, `end` comes back **empty**
     (violating §T-envelope's "never null"), and the record asserts a squash that may never have
     happened. The `cat-file -e` probe plus the targeted second fetch is what settles it: a commit
     that still cannot be read blanks `MERGE_SHA`, which routes the run to the no-SHA arm — the arm
     that already handles "we could not identify the merge" and takes a wall-clock `end`.
   - **Why `gh pr view --json mergeCommit` rather than `rev-parse HEAD`.** `HEAD` is only the merge
     commit when reconciliation succeeded; on the `--detach` fallback it is not. Asking GitHub for
     the merge commit is correct on every path.
   - **Why `commits` and `churn` are absent on the squash branch.** No `^2` exists, so the range
     `^1..^2` is unresolvable. `end` is still read from the merge commit itself.
   - **Why there is a third `else` and not two branches.** `MERGE_SHA` can come back empty — a
     transient `gh pr view --json mergeCommit` failure or auth loss, reachable even when
     `RECONCILED=1`. That is a *tooling failure*, not a squash, and folding it into the squash arm
     would emit `merge_sha: ""` (a type violation of §T-lane) plus a `note` asserting a merge shape
     nobody observed. The `nosha=1` arm takes wall-clock time as `end`, since no commit is
     available to read one from, and Task 4 step 3 gives it its own record arm.

2. Add a new segment **`### Telemetry record`**, placed **after `### Merge, then clean up` and
   before `### Closeout hook`**. State the ordering reason in one line: the closeout hook is
   conditional and its script `exit 0`s on the common non-backlog path, so a telemetry block placed
   after it inside the same invocation would never run — this block goes first, and uses `if`/`fi`
   rather than `exit` so that concatenating it with anything is safe.

3. Body of `### Telemetry record`:
   - Open with the same three-classes-of-value note the closeout hook carries: `BRANCH_MERGED`,
     `PR_NUMBER`, `MERGE_SHA` and the four derived values are **substituted literals** read from the
     derivation block's `TELEMETRY …` output, because this block runs in a later shell invocation
     and the fence's variables are gone. `PRIMARY` is `:?`-asserted, because it has a re-runnable
     derivation at the top of the skill.
   - Build the record per §T-envelope + §T-lane, with `kind: "lane"`,
     `id: <BRANCH_MERGED>`, `pr_number: <PR_NUMBER>`, `merge_sha: <MERGE_SHA>`, and either:
     - **derived branch** — `start: <derived start>`, `basis: "first_commit"`, `commits`, `churn`,
       `note: null`; or
     - **squash branch** (`squash=1`) — `merge_sha` set; `start: null`, `basis: "unavailable"`,
       `commits: null`, `churn: null`,
       `note: "squash merge — no second parent; start, commits and churn underivable"`; or
     - **no-SHA branch** (`nosha=1`) — `merge_sha: null`; `start: null`, `basis: "unavailable"`,
       `commits: null`, `churn: null`,
       `note: "merge commit not available locally (no mergeCommit from gh, or the commit could not be fetched); start, commits and churn underivable"`.
       `end` is the wall-clock stamp the derivation block emitted. Never write the squash `note` on
       this branch — the two are distinguished by which marker the derivation printed.
   - Guard on reconciliation before committing, re-deriving it from observable state exactly as the
     closeout hook does (`fix/SKILL.md:1225`) rather than inheriting the fence's `RECONCILED`:
     ```bash
     : "${PRIMARY:?re-run this skill's PRIMARY derivation, above}" \
       "${DEFAULT_BRANCH:?re-run this skill's default-branch derivation, above}"
     RECONCILED=0
     CMP_REF="origin/$DEFAULT_BRANCH"
     git -C "$PRIMARY" rev-parse --verify --quiet "$CMP_REF" >/dev/null || CMP_REF="$DEFAULT_BRANCH"
     if [ "$(git -C "$PRIMARY" branch --show-current)" = "$DEFAULT_BRANCH" ] \
        && git -C "$PRIMARY" merge-base --is-ancestor "$CMP_REF" HEAD 2>/dev/null; then
       RECONCILED=1
     fi
     ```
     When `RECONCILED=0`, **do not append** — print
     `Telemetry skipped: checkout not reconciled — no lane record written.` and continue. The
     checkout is detached or unadvanced, so a commit here would land somewhere unpushable. This is
     a skip, never a stop.
   - When `RECONCILED=1`, run §T-append T1–T5 with `$ROOT = "$PRIMARY"` and commit message
     `chore: record telemetry for <BRANCH_MERGED>`, then push with the fetch/rebase/re-push shape.
   - T2's dedup is keyed on `kind == "lane"` **and** `id == <BRANCH_MERGED>`. The `pr_number` is
     also carried and could serve as the key — `id` is chosen because it is the same field the
     cycle record deduplicates on, so one dedup rule covers both kinds.
   - **State the re-entry reality plainly, because it is the opposite of `dev:done`'s and a reader
     will otherwise assume symmetry.** By the time this segment runs, the merge fence has deleted
     the feature branch and moved the checkout to `$DEFAULT_BRANCH`, so a re-invoked
     `/dev:fix merge` STOPs in `### Resolve the branch and PR` (`fix/SKILL.md:966–985`) long before
     reaching here. Two consequences, both deliberate:
     - Success Criterion 6's lane half is **delivered by that guard**, not by T2. T2 remains, as
       defence in depth against a hand-run of this segment.
     - **A failed append here is not recoverable by re-running the tail.** Say so in the Report
       rather than advising a re-run: the remedy is to append the line by hand or to accept the
       gap. This is the deliberate counterpart to Task 3's D3, where recovery matters *because*
       an irreversible teardown follows; here nothing is destroyed, so a missing lane record costs
       one under-counted run and nothing else.

4. In **`### Report`**, add the telemetry outcome as an additional line, sitting **beside** the
   existing backlog-closeout fifth line rather than replacing it — one of: the lane record appended
   and pushed; the record appended but unpushed after a failed retry (name the file, and say the
   remedy is a push); the record skipped because the checkout was not reconciled; or the append
   failed. On that last one, **do not advise re-running `/dev:fix merge`** — the resolve guard will
   STOP before reaching this segment. Say the record is missing and that the remedy is a manual
   append. Keep the section's existing rule: read each state from the command that produced it, do
   not assert it.

5. Do **not** change the merge fence's control flow, `delete_feature_branch`, the mergeability
   check, or the closeout hook. The derivation block in step 1 is an addition at the end of the
   fence's script; nothing above it moves.

---

### Task 5: `dev:autopilot` — record the new stop condition

What: Add `dev:done`'s ledger-append failure to the one place that enumerates where an autopilot run
halts.

Used by: an operator reading `## Purpose` to know what can stop a run; `dev:autopilot` Step 4's
blocker report.

Depends on: Task 3 (it introduces the STOP this task documents).

Files: modify `plugins/dev/skills/autopilot/SKILL.md`.

Interfaces:
- Consumes: Task 3's Step 6b STOP.
- Produces: nothing other tasks read.
- State keys: none.
- Shared procedure: none.

Implementation steps:

1. In `## Purpose`'s **"When autopilot stops"** sentence (`autopilot/SKILL.md:14`), add one item to
   the existing comma-separated list, directly after the Validate entries and before the Step 1
   resolution entry: `a telemetry record that fails to land at Done (see dev:done Step 6b)`.

2. Change nothing else. The three checks that this is the *complete* ripple:
   - Step 6b introduces exactly one STOP. **`dev:done` Step 6a's flush STOP is absent from that
     list today** — verified this stage by reading `autopilot/SKILL.md:14`, which names stops from
     Spec, Build, Validate, PR-merge and Step 1 and none from the debt flush. Adding Step 6b anyway
     is deliberate and the difference is stated in the edit: Step 6b's failure sits immediately
     before an irreversible `rm -rf`, so an operator who does not know it can halt a run cannot
     recover the data; the flush STOP leaves the buffer on disk and is re-runnable. Do **not** also
     add the flush STOP — that is a separate finding, not this cycle's scope.
   - Task 4's telemetry skip is a **skip, not a stop**, and `/dev:fix` is not an autopilot stage —
     no entry for it.
   - Task 2 introduces no stop. Its `dev:reflect` edit changes how an absent `pr_end` is *reported*,
     not whether the stage halts, so it is not a behaviour this list covers.

---

### Task 6: Update the governing product plan

What: Collapse Milestone 2's two items into the one cycle that is actually shipping, correct the
false `_start` claim, and make the header count match.

Used by: `dev:done` Step 3, which checks off the item matching `state.json.feature`
(`telemetry-schema`) and increments the header count.

Depends on: nothing — independent of Tasks 1–5. Sequenced last only so the plan edit lands in the
same PR as the work it describes.

Files: modify `docs/dev/product-plans/dev-observability.md`.

Interfaces:
- Consumes: nothing.
- Produces: a `- [ ] telemetry-schema (feature)` line that `dev:done` Step 3 will match on
  `state.json.feature` unchanged (no ID-strip retry needed — `linear_issue` is null on this cycle).
- State keys: none.
- Shared procedure: none.

Implementation steps:

1. Replace Milestone 2's two checkbox lines:
   ```
   - [ ] telemetry-schema (architecture)
   - [ ] telemetry-instrumentation (feature)
   ```
   with the single line:
   ```
   - [ ] telemetry-schema (feature)
   ```
   The slug must remain exactly `telemetry-schema` — `dev:done` Step 3 matches on
   `state.json.feature`, which is that string.

2. Replace Milestone 2's two prose paragraphs with one that states what grounding actually found:
   - `metrics.stage_timestamps` already carries **both** `_start` and `_end` for `spec`, `shape`,
     `plan`, `build` and `validate`; the plan's claim that "only `spec` has one today" was false.
   - The real gaps are `pr` (which records only `pr_created`), `done` (which records nothing), and
     — the blocking one — that all of it is deleted by `dev:done` Step 7 before anything outside the
     cycle can read it.
   - Token/cost estimation and `/dev:debt` invocation counting are dropped, with the spec's reasons
     in one clause each.
   - Say in one sentence why the architecture cycle collapsed into a feature cycle: the contract
     turned out to be one file format with two writers, not a decision needing ADRs.

3. Change the header from `*Created: 2026-08-13 · Cycles completed: 1/4*` to
   `*Created: 2026-08-13 · Cycles completed: 1/3*`. Three items remain in the plan after step 1
   (`backlog-viewer`, `telemetry-schema`, `lifecycle-viewer`), one of which is `[x]`.
   `dev:done` Step 3 will increment this to `2/3` when this cycle merges — do **not** pre-increment
   it here.

4. Leave Milestone 1 and Milestone 3 untouched. Milestone 3's "Depends on Milestone 2" line stays
   true and needs no edit.

## Edge Cases

| Edge case | Handled in | Approach |
|-----------|-----------|----------|
| Ledger append fails (disk, bad `state.json`) | Task 1 (T4, T6) + Task 3 step 3 | T4 verifies the line landed; T6 makes failure the caller's stop; `dev:done` STOPs before Step 7's `rm -rf`, so nothing is torn down |
| `dev:done` re-entry double-appends | Task 1 (T2) + Task 3 | Dedup on `kind == "cycle"` and `id == <feature>`; the T5 `--quiet` guard makes the no-op path exit cleanly |
| `/dev:fix merge` re-entry double-appends | Task 4 step 3 (primary) + Task 1 (T2, defence in depth) | **The re-run never reaches the segment**: the merge fence has already deleted the branch and moved the checkout, so `### Resolve the branch and PR` binds `BRANCH` to `$DEFAULT_BRANCH` and STOPs (`fix/SKILL.md:966–985`) before any telemetry code runs. T2's `kind`+`id` dedup is a second line of defence, not the mechanism. Named honestly because the consequence is real — see the note in Task 4 step 3 |
| Squash merge — no second parent | Task 1 (§T-lane) + Task 4 steps 1, 3 | Record written with `start`/`commits`/`churn` null, `basis: "unavailable"`, and a `note` naming why; never skipped |
| Merge commit not identified (`gh pr view` returns no `mergeCommit`) | Task 1 (§T-lane, third branch) + Task 4 steps 1, 3 | Own record arm: `merge_sha: null`, `end` from wall clock, its own `note`. Never written as a squash — that would assert a merge shape nobody observed |
| `--shortstat` omits a zero clause, or the diff is empty | Task 1 (§T-lane parse rule) | An absent clause parses to `0`, never a missing key; empty output yields all-zero churn. A deletions-only lane run is the common case, not an exotic one |
| `pr_end` absent when `dev:reflect` reads `stage_timestamps` | Task 2 step 5 | Reflect runs at Step 5d, Step 5e stamps `pr_end` after it — so `pr` is reported in-progress rather than given a duration from a missing end |
| Two cycles finish near-simultaneously | Task 1 (§T-path) + Task 3 D2/D3 | Append-only, one line each; a push conflict is resolved by keeping **both** lines, never by picking a side. `push_integration`'s fetch/rebase retry handles the ordinary case; a conflict that survives it is Task 3's STOP, and `dev:done` Step 7's existing mid-rebase guard catches the state |
| Lane run whose PR is never merged | Task 4 (placement) | `/dev:fix merge` never runs, so the segment is never reached — no record. Correct: unmerged work is not a completed run |
| Lane `start` is not comparable to a cycle `start` | Task 1 (§T-envelope `basis`) | The record names its own basis; the reference states the reader must not compare across bases |
| Legacy in-place cycle (`worktreePath: null`) | Task 3 (D1) | `$WORKDIR` resolves to the primary checkout and the ledger path is repo-relative — confirmed against `done/SKILL.md`'s resolution block, no special case |
| `docs/telemetry/` does not exist | Task 1 (T1) | `mkdir -p` writer-side on every append; absence never fails a run |
| `/dev:fix merge` on a non-reconciled checkout | Task 4 step 3 | Re-derive `RECONCILED`; skip the append with a printed line rather than committing somewhere unpushable. A skip, not a stop |
| A hand-corrupted ledger line | Task 1 (T2) | The dedup scan skips unparseable lines instead of aborting, so one bad line cannot block every future append |
| `challenge.blockers` is `null`, not `0` | Task 1 (§T-cycle) | Copied through unchanged; never coerced — `dev:spec` Step 12a's errored-dispatch rule makes `null` a meaningful third value |

## Out of Scope

- Token and cost estimation, and `/dev:debt` invocation counts — spec Out of Scope.
- New per-stage instrumentation beyond `pr` and `done` — the other five stages already stamp both sides.
- Backfilling past cycles. The ledger starts empty and grows forward.
- The viewer that renders the ledger — Milestone 3 (`lifecycle-viewer`).
- Any change to `dev:reflect`. It keeps reading `state.json.metrics` in-cycle; the ledger is a second,
  later reader of the same data, not a replacement.
- Any change to `pr_created`'s meaning, or to the commit pathspecs in `dev:done` Steps 3, 6a and 7.
