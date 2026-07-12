---
name: dev:shape
description: "Stage 2 of the /dev workflow. Produces design.md — user flows, component inventory, copy, and wireframes. Presents 2-3 alternatives before committing to full design. Runs per-section approval in standard mode. Requires spec.md."
---

# dev:shape — Design Stage

**Announce:** "I'm using dev:shape to create the design document."

**First action, before anything else:** run `date -u +%Y-%m-%dT%H:%M:%SZ` and hold onto the output — this is `shape_start`, recorded in Step 10. Capturing it now, before any other work, keeps it accurate to when the stage actually began.

## Purpose

Produce a `design.md` that gives Build everything it needs to implement the feature without guessing. Embeds UX design and copywriting judgment — no external skill dependencies.

This skill supersedes `superpowers:brainstorming`'s design phase for the duration of the `/dev` session — do not invoke it separately.

**Anti-Pattern: "There's No UI, Skip Shape."**
Shape is skipped via `no-ui` mode or auto-routing from Spec. It is not skipped because "the UI will be simple." If the spec says `UI Needed: Yes`, Shape runs.

## Step 1: Artifact Gate

May be invoked with an artifact-path argument (e.g. `docs/dev/<feature>/spec.md`). If given, derive `<feature>` from the path instead of requiring it already be known from conversation context. If no argument is given, fall back to today's behavior (feature already known from orchestration or an existing in-progress session). **Validate before using:** the path must match `docs/dev/<feature>/<artifact>.md` with `<feature>` matching `^[a-z0-9][a-z0-9-]*$` and containing no `..` segments. If it doesn't match, treat the argument as invalid and fall back to today's behavior rather than using the parsed value.

<HARD-GATE>
Read `docs/dev/<feature>/state.json` to find the feature name and locate `spec.md`. If `artifacts.spec` is null or the file does not exist, STOP:

"Shape requires spec.md. Run /dev:spec first to create the specification."
</HARD-GATE>

**Resume-mid-approval check:** if `design.md` already exists for this feature and `state.json.stage` is still `"shape"`, skip straight to Step 11 to re-display it for approval rather than re-running the full design flow.

Read these files once at stage start:
- `docs/dev/<feature>/state.json`
- `docs/dev/<feature>/spec.md` — full content, work from this throughout

## Step 2: Check Mode

From state.json `mode`:
- **standard:** visual companion available, per-section approval runs, browser used for design exploration
- **autopilot:** no browser, no approval gates, self-review only

## Step 3: Existing Codebase Scan

Before proposing anything new, understand what already exists.

1. Check `CLAUDE.md` → `## Component Registry` first. If present and dated recently (within this /dev session): use it directly. No directory scan needed.
2. If Component Registry is absent or stale: scan `components/`, `src/components/`, `app/`, `src/app/` directories. Note component names, paths, and inferred purposes. Update the registry in CLAUDE.md.
3. Read `docs/dev/config.json` → component policy (existing only vs. can propose new).

Present results before any design questions:
```
Based on your existing components, here's what I'm working with:
[component list from registry or scan]
Component policy: [existing only / can propose new]

Correct anything off, or say "looks good" to continue.
```

Wait for confirmation.

## Step 4: Visual Companion Offer (Standard mode only)

When layout or visual questions are ahead, offer the visual companion. This message contains ONLY this offer — nothing else:

> "Some of what we're designing might be easier to see than read. I can put together mockups, wireframes, and visual comparisons in a browser as we go. Want to try it? (Requires opening a local URL)"

Wait for the response before continuing. If declined, proceed text-only. If accepted, use the visual companion for layout/spatial questions throughout this stage.

**Target device(s) — required before any prototype.** Whenever a prototype or mockup will be produced — whether you propose one or the user asks for one — first ask which device(s) it targets (e.g. iPhone 17 · 393×852 pt, or a specific web breakpoint). Build every mockup at that device's real point dimensions and aspect ratio (1:1), never a shrunken or arbitrary frame, so Build implements at true size. If multiple devices, mock the primary one at true size and note the others. Record the answer in design.md's Design Status block (Step 8).

**Autopilot mode:** Skip this step entirely.

## Step 5: Design Alternatives

Before producing a full design, present 2–3 structural approaches.

Each option includes:
- Layout/structure at high level (1-2 sentences)
- Trade-offs (what it's good for, what it sacrifices)
- One option marked "**My recommendation:**" with brief reasoning

**Standard mode with visual companion:** Show options side by side in the browser if layout is meaningfully different between options. Text terminal if options differ conceptually but look similar.

**Standard mode, no browser:** Present as labeled options (A/B/C) in the terminal.

**Autopilot mode:** Auto-select the recommended option. State the selection and reasoning — it will appear in design.md as "Design decision."

Wait for user to pick one direction (standard mode). Produce the full design for that direction only.

## Step 6: Comprehension Check (Standard mode only)

After the alternative is selected, before going deep on copy and wireframes, open the browser and show the chosen structural layout:

"Here's the skeleton before I fill in details — confirm this is the right structure."

This prevents spending time on copy and wireframes for a fundamentally wrong structure. If user requests changes, revise and re-show before proceeding.

**Autopilot mode:** Skipped.

## Step 7: Per-Section Design (Standard mode)

Produce design sections in order. After each section in standard mode, ask: "Does this look right before I continue?"

**Section 1 — User Flows**
Entry → success state, with all error paths named. Format as numbered flows:
```
Flow 1: [Happy Path]
1. User [action]
2. System [response]
3. User reaches [success state]

Error: If [condition] → [what happens]
```

**Section 2 — Component/Screen Inventory**
Table of what exists vs. what's new:
```
| Component | Status | Notes |
|-----------|--------|-------|
| Button | Existing | Use Button variant="primary" |
| NewWidget | New | Component policy allows; justified because [reason] |
```

**Section 3 — Copy**
Every interactive element needs copy. For each:
- Button labels (action words — "Save changes" not "Submit")
- Headings and subheadings
- Error messages (specific, not generic — "Name can't be empty" not "Invalid input")
- Empty state messages
- Loading state labels
- Confirmation messages

**Section 4 — Wireframes**
ASCII wireframes where layout matters — not for every screen, only where structure is ambiguous. Higher fidelity in browser if user accepted visual companion and look-and-feel drives the decision.

**Visual companion design rules (when browser is active):**
- Fidelity matches the question: structural → rough wireframes; look-and-feel → higher fidelity
- Render at target-device dimensions: every mockup uses the real point size and aspect ratio of the target device captured in Step 4 (1:1, not scaled down), so on-device implementation doesn't need to resize
- 2–4 options max per screen
- Use real content: real component names, real copy strings, real data shapes
- Iterate before advancing: if feedback changes the current screen, write a new version before moving on
- Read click event stream: check `$STATE_DIR/events` after browser interaction. A→B→A click pattern signals hesitation — ask before moving on
- Push a waiting screen when returning to terminal for a text question

**Autopilot mode:** Write all four sections, then run artifact self-review. No per-section stops.

## Step 8: Write design.md

Write to `docs/dev/<feature>/design.md`:

```markdown
# [Feature Name] — Design
*Branch: feature/xxx · YYYY-MM-DD*

## Design Status
[**Locked** — Plan and Build must adhere to these dimensions, copy, and layout exactly. | **Directional** — conveys intent; Plan/Build may adapt specifics.]
Target device(s): [e.g. iPhone 17 · 393×852 pt]. Any prototype/mockup was built at these dimensions (1:1).

## Design Decision
[Which alternative was selected and why]

## User Flows
[From Section 1]

## Component/Screen Inventory
[From Section 2]

## Copy
[From Section 3]

## Wireframes
[From Section 4 — omit if not needed]

## UX Decisions
[Any design choices made during this stage with rationale]
```

Scale length to complexity. A simple form addition may need 20 lines. A multi-screen flow may need 150.

## Step 9: Artifact Self-Review

After writing design.md:
1. Does every user flow have a defined error path?
2. Is every new component justified by the component policy?
3. Is copy present for every interactive element?
4. Are any sections contradicted by the spec?
5. Is Design Status set (Locked or Directional), and — if a prototype/mockup exists — does it name the target device it was built at?

Fix any issues inline. No need to re-review after fixing.

## Step 10: Update State + Commit

Update state.json:
- Set `artifacts.design` to the path
- Increment `metrics.visual_screens_shown` by number of browser screens used
- Record `metrics.stage_timestamps.shape_start` (the value captured at the very top of this skill, before Step 1) and `metrics.stage_timestamps.shape_end` (run `date -u +%Y-%m-%dT%H:%M:%SZ` now)

```bash
git add docs/dev/<feature>/design.md docs/dev/<feature>/state.json
git commit -m "shape: write design for <feature>"
```

## Step 11: User Review Gate (Standard mode)

```
Design written and committed to docs/dev/<feature>/design.md.

Please review it and let me know if you'd like any changes before we move to Plan.

Safe to /clear now — resume with: /dev:plan docs/dev/<feature>/design.md
[If worktreePath is set: Worktree: <worktreePath>]
```

Confirm **Design Status** before moving on: is this design **locked** (Plan and Build must follow it exactly) or **directional** (Plan may adapt specifics)? Record it in the Design Status block so Plan knows how strictly to follow it.

Wait for explicit user approval. If changes requested: update design.md, re-run Step 9, re-commit.

When approved: update state.json — add `"shape"` to `completed[]`, set `stage` to `"plan"`. Commit state update.

**Autopilot mode:** No gate. After self-review, update state and proceed.
