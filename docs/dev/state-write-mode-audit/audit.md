# State-Write Mode Audit — Evidence Log
*Branch: feature/state-write-mode-audit · 2026-07-24*

Cycle-local evidence for the state-write-mode-audit cycle. Every mode-sensitive `state.json`
counter that `dev:reflect` reads is traced here to the mode(s) that actually execute its write,
classified against the load-bearing invariant, and assigned its canonical single-source tag.
This file is deleted by `dev:done` — it is an evidence log, not a standing registry (SC5).

**Load-bearing invariant** (inherited verbatim from `plan-challenger` SC5):
> *No counter's non-default autopilot value may depend on a gate write.*

A counter **passes** if it is written in both modes, **or** is genuinely mode-specific with its
autopilot value equal to its init default. A counter **fails** — is a **defect** — if it has a
non-default autopilot value that depends on a standard-mode-only gate write. Every tag string is
frozen here and copied byte-for-byte by Tasks 2–7 (SC7).

**Frozen tag vocabulary** — exactly these three strings, reused verbatim everywhere:
- `(writes: both)`
- `(writes: autopilot-only)`
- `(writes: standard; =default 0 in autopilot)`

## Counter classification

Each row was confirmed by reading the actual write site in code (not carried from the plan's
table on trust). The "Confirmed at" column cites the grounded line(s) verified during this audit.

| Counter | Single-source site (tag home) | Confirmed at | Mode class | Tag |
|---|---|---|---|---|
| `challenge.run` / `.blockers` / `.concerns` | spec Step 12a "Counter-write semantics", the "overwritten by each dispatch" bullet | spec:513 | Overwritten each dispatch; dispatch runs in both modes | `(writes: both)` |
| `challenge.applied` | spec Step 12a, the cumulative `applied`/`dismissed` bullet | spec:514, autopilot:71 | Standard gate writes it (Step 13); autopilot revision loop writes it — both modes | `(writes: both)` |
| `challenge.dismissed` | spec Step 12a, same cumulative bullet | spec:514, spec:557 | Standard gate only; stays `0` (= init default) in autopilot | `(writes: standard; =default 0 in autopilot)` |
| `challenge.loops_run` | spec Step 12a, the `loops_run` bullet | spec:515, spec:504 | Autopilot revision loop only; `0` (= init default) in standard | `(writes: autopilot-only)` |
| `metrics.spec_questions_asked` | spec Step 12 state-write list | spec:437, spec:429 | Reconciled in Step 11 and written in Step 12 — runs in both modes | `(writes: both)` |
| `metrics.spec_revisions` | spec Step 12 initial-write description (the both-modes lifecycle line naming Step 13's increment and autopilot's Step 3 writer) | spec:441 (tag home); confirmed at spec:551, autopilot:60 | Standard: Path B gate increment. Autopilot: Step 3 writes it on silent backtrack — both modes | `(writes: both)` |
| `challenge_plan.run` / `.blockers` / `.concerns` | plan Step 7a "Counter-write semantics", the "overwritten by each dispatch" bullet | plan:236 | Overwritten each dispatch; dispatch runs in both modes | `(writes: both)` |
| `challenge_plan.applied` | plan Step 7a, the cumulative `applied`/`dismissed` bullet | plan:237, autopilot:73 | Standard gate writes it (Step 8); autopilot revision loop writes it — both modes | `(writes: both)` |
| `challenge_plan.dismissed` | plan Step 7a, same cumulative bullet | plan:237, plan:277 | Standard gate only; stays `0` (= init default) in autopilot | `(writes: standard; =default 0 in autopilot)` |
| `challenge_plan.loops_run` | plan Step 7a, the `loops_run` bullet | plan:238, plan:231 | Autopilot revision loop only; `0` (= init default) in standard | `(writes: autopilot-only)` |
| `metrics.visual_screens_shown` | shape "Increment by number of browser screens used" line | shape:211 | Standard only (no browser in autopilot); stays `0` (= init default) in autopilot | `(writes: standard; =default 0 in autopilot)` |
| `metrics.files_read_in_build` | build inline per-context-read increment | build:138 | Build runs identically in both modes | `(writes: both)` |
| `validate.loops_run` | validate fix-loop "Increment loops_run" step | validate:123 | Mode-independent fix loop; both modes | `(writes: both)` |

**Canonical tag placement, one per counter (Tasks 2–6 consume this):**
- spec:513 `challenge.run`/`.blockers`/`.concerns` → `(writes: both)`
- spec:514 `challenge.applied` → `(writes: both)`; `challenge.dismissed` → `(writes: standard; =default 0 in autopilot)`
- spec:515 `challenge.loops_run` → `(writes: autopilot-only)`
- spec:437 `metrics.spec_questions_asked` → `(writes: both)`
- spec:441 `metrics.spec_revisions` → `(writes: both)` (the both-modes lifecycle line; the standard-only Path B increment at spec:551 is a cross-reference, left untagged)
- plan:236 `challenge_plan.run`/`.blockers`/`.concerns` → `(writes: both)`
- plan:237 `challenge_plan.applied` → `(writes: both)`; `challenge_plan.dismissed` → `(writes: standard; =default 0 in autopilot)`
- plan:238 `challenge_plan.loops_run` → `(writes: autopilot-only)`
- shape:211 `metrics.visual_screens_shown` → `(writes: standard; =default 0 in autopilot)`
- build:138 `metrics.files_read_in_build` → `(writes: both)`
- validate:123 `validate.loops_run` → `(writes: both)`

Line numbers are the grounding snapshot for this cycle; each tagging task re-locates its site by
the quoted anchor text (line numbers drift as prose is edited) and places **exactly one** tag at
that single-source description. Autopilot's `challenge.*` / `challenge_plan.*` / `spec_revisions`
mentions (autopilot:60, 71, 73) are **cross-references** to spec's/plan's single-source semantics,
not independent facts — no tag is placed there (SC — Out of Scope: editing `dev:autopilot`).

## Confirmed mode-invariant (untagged)

These fields carry no cross-mode reflect read and are written by every stage in both modes by
construction (or are pure structure). Each is confirmed to carry no defect shape and is left
untagged (SC2):

- `stage`, `completed[]` — written by every stage's completion step, both modes.
- `skipped[]` — written by `dev` (`skip` command, dev:99) and spec (records the UI decision); structural, no counter read.
- `linear_issue` — written by `fix` (fix:99); structural, no cross-mode reflect read.
- `artifacts.*` (spec/design/plan/validation/pr_url/pr_number) — path/URL pointers, written as each stage produces its artifact in both modes.
- `confidence.*` incl. `final_score`, `final_level`, `dimensions.*`, `auto_filled[]` — written by spec in both modes; `dev:reflect` reads `final_score` but cross-checks it against churn, and the value is produced identically in both modes.
- `tier`, `cycle_type` — set once by spec in both modes.
- `metrics.stage_timestamps.*` — each stage stamps its own start/end in both modes.
- `validate.loops_max` — set from tier; mode-invariant cap.
- `validate.p1_open[]` / `p2_open[]` / `p3_open[]` / `nits_open[]` — the fix-loop's open-issue lists, written on the mode-independent validate path.
- `challenge.loops_max` / `challenge_plan.loops_max` — set from tier by spec (spec:212, spec:214); mode-invariant caps.

## Historical-fix regression check

The three already-fixed instances (the tech-debt entry this cycle pays) each re-confirmed against
the invariant at their real write site — none regressed (SC6):

- **`challenge.applied`** — standard mode writes it at the Step 13 gate; autopilot writes it inside the Step 12a revision loop (autopilot:71). Its non-default autopilot value does **not** depend on a gate write. **Passes.**
- **`challenge.dismissed`** — standard gate only (spec:557); in autopilot nothing is declined, so it stays at init default `0`, which is the honest value. Mode-specific with autopilot value = default. **Passes.**
- **`metrics.spec_revisions`** — standard mode increments it at the Path B gate (spec:551); autopilot Step 3 writes it on each silent backtrack (autopilot:60–62, whose own comment notes that without it `spec_revisions` "is structurally always 0"). Written in both modes. **Passes.**

`challenge_plan.applied` and `challenge_plan.dismissed` mirror the spec pair (autopilot:73 writes
`applied`; `dismissed` is standard-gate-only and honestly `0` in autopilot) — same result.

## Fourth-defect sweep result

**No fourth (or further) live defect found — the expected outcome.** Every mode-sensitive counter
`dev:reflect` reads (spec:40–45 read list) resolves to one of two passing classes:

1. **Written in both modes** — `challenge.run/blockers/concerns`, `challenge.applied`, `spec_questions_asked`, `spec_revisions`, `challenge_plan.run/blockers/concerns`, `challenge_plan.applied`, `files_read_in_build`, `validate.loops_run`.
2. **Mode-specific with autopilot value = init default `0`** — `challenge.dismissed`, `challenge.loops_run`, `challenge_plan.dismissed`, `challenge_plan.loops_run`, `visual_screens_shown`.

No counter has a non-default autopilot value that depends on a standard-mode-only gate write, so
no write-side fix is required in Tasks 2–6. Tasks 2–6 place tags only.

## Reflect read-surface confirmation

`dev:reflect`'s counter reads (reflect:40–45, 56–94) were checked against the final classification.
Every mode-specific counter reflect reads sits at its honest init default in the mode where it is
not written (`challenge.dismissed`/`loops_run`, `challenge_plan.dismissed`/`loops_run`,
`visual_screens_shown` all read `0` in the mode they don't apply to — the correct value). No
correctly-mode-specific counter is misreported by reflect, so **no read-side `dev:reflect` change
is required** (SC6; the spec's expected-none edge case is confirmed, not assumed). Reflect already
guards the one genuinely different case — a *missing* `challenge`/`challenge_plan` block reads as
"did not run," not zero (reflect:41–42).
