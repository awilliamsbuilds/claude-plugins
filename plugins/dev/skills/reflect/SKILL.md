---
name: dev:reflect
description: "Retrospective sub-skill. Reviews the completed /dev cycle, surfaces process improvements, and appends a Retrospective section to the decision log. Called by dev:done automatically. Also available standalone. Requires explicit user confirmation before updating any skill file."
---

# dev:reflect — Retrospective

**Announce:** "I'm using dev:reflect to review this cycle and surface improvements."

## Resolve the working directory (do this first)

This stage never relies on the shell's current directory or current branch. Compute the
primary checkout, then locate this cycle's directory:

    PRIMARY=$(dirname "$(git rev-parse --git-common-dir)")

Find the cycle directory — first hit wins — by testing for `docs/dev/<feature>/state.json` under:
1. `$PRIMARY/.dev-worktrees/<feature>/`   → active worktree cycle
2. `$PRIMARY/`                            → legacy in-place cycle (worktreePath null)

Set `WORKDIR` to whichever matched. For the rest of this stage: run every git command as
`git -C "$WORKDIR" …`, and read/write all artifacts under `$WORKDIR/docs/dev/<feature>/…`.
Never `cd`, never assume the current branch.

When `dev:reflect` is invoked by `dev:done`, `WORKDIR` is already the cycle worktree flipped to the integration branch — this resolution is idempotent and yields the same directory.

## Purpose

Look back at the completed cycle, surface what worked and what didn't, and identify actionable improvements to the /dev plugin itself.

## Step 1: Gather State

Read once:
- `docs/dev/<feature>/state.json` (if still exists) or accept it as passed context from dev:done
- The decision log at `docs/decisions/YYYY-MM-DD-<feature>.md`
- `docs/dev/<feature>/spec.md`, `plan.md`, `validation.md` (if accessible — they may be deleted by done)

Extract key metrics from state.json:
- `metrics.spec_questions_asked`
- `metrics.visual_screens_shown`
- `metrics.files_read_in_build`
- `validate.loops_run` / `validate.loops_max`
- `stage_timestamps` — compute duration per stage
- `confidence.final_score` and `confidence.auto_filled[]`
- `tier`
- Any stage backtracks (stages in completed[] out of typical order)

## Step 2: Review Each Dimension

Analyze the cycle across these dimensions. Note findings briefly — one sentence each unless something is significant:

**Spec quality:**
- Did the confidence score (final_score) reflect actual clarity? (If Build triggered many plan updates → spec was probably overconfident)
- Were auto-filled dimensions `confidence.auto_filled[]` correct? (If they caused problems in Build → auto-fill was wrong)
- Did spec_questions_asked reach the max? (If yes and confidence was still Low → initial request needed more context before starting)

**Shape quality (if ran):**
- Did implementation deviate significantly from design.md?
- Were any components proposed that didn't fit component policy?
- Were visual_screens_shown screens actually useful? (0 clicks on a screen → it wasn't needed)

**Plan quality:**
- Were there unplanned tasks added during Build? (plan.md updated mid-build → plan was underspecified)
- Was the sequence right? (No task ordering problems in Build → good)

**Validate efficiency:**
- Loops run vs. max: `validate.loops_run` / `validate.loops_max`
- If loops_run == loops_max: could Spec or Plan have caught what Validate found?
- P1/P2 issues resolved: patterns in what kinds of bugs slipped through to Validate

**Flow:**
- Was any stage unnecessary for this cycle's complexity?
- Was anything missing that caused friction?
- Was the tier correctly detected? (Micro for something that turned into Standard → under-detected; Standard for something with 0 edge cases → could have been Micro)

**Token efficiency:**
- `files_read_in_build` high → Plan was underspecified, or spec scope was too broad
- `visual_screens_shown` high, few clicks → visual companion over-triggered
- Stage duration outliers (from stage_timestamps) → where time was disproportionately spent
- Backtracks occurred → earlier stage missed something; flag the gap

## Step 3: Generate Retrospective

Write the Retrospective section. Be concise — this is a log, not a report. One sentence per non-trivial finding. Skip dimensions with nothing to note.

Format:
```markdown
## Retrospective
*Reviewed by dev:reflect · YYYY-MM-DD*

**Spec:** [finding or "confidence score matched actual clarity"]
**Shape:** [finding or "design was followed closely" or "Shape skipped"]
**Plan:** [finding or "plan was accurate, no mid-build updates"]
**Validate:** [N loops / max. Finding or "clean after 1 loop"]
**Flow:** [finding or "tier was right, no unnecessary stages"]
**Token efficiency:** [finding or "no outliers detected"]
**Suggestions:** [list of actionable suggestions, or "none"]
```

## Step 4: Append to Decision Log

```bash
cat >> docs/decisions/YYYY-MM-DD-<feature>.md << 'EOF'

## Retrospective
...content from Step 3...
EOF

git -C "$WORKDIR" add docs/decisions/YYYY-MM-DD-<feature>.md
git -C "$WORKDIR" commit -m "docs: append retrospective to <feature> decision log"
git -C "$WORKDIR" push
```

## Step 5: Skill Update Gate

For each actionable suggestion (e.g., "add auth checklist to dev:shape"):

Display one at a time:
```
dev:reflect found a suggestion: [suggestion in one sentence].

Would you like to update [dev:skill-name] based on this? (yes/no)
```

Wait for explicit "yes" before touching any skill file. If "no", record the suggestion as deferred in the decision log.

If "yes": read the current SKILL.md, make the minimal targeted change, show the diff, ask for final confirmation before writing.

**Never update a skill file without two explicit confirmations: one to proceed with the update, one after seeing the diff.**

### Skill edits go through the plugins repo — always

Skill files under `~/.claude/plugins/cache/` are a deployed copy, not the source of truth. Never leave a skill improvement as a local cache-only edit. Once the two confirmations are in and the change is written, port it to the source repo and open a PR — this is the standing process, not a per-cycle choice:

1. Locate the source repo (the `local-plugins` marketplace checkout, e.g. `~/Development/claude-plugins`). The skill lives at `plugins/<plugin>/skills/<skill>/SKILL.md`.
2. Create a feature branch (never commit to `main`), apply the same edit there (copy the finished cache file over, or re-apply the diff), commit, push, and open a PR with `gh`.
3. Keep the deployed cache copy and the repo copy identical so the running skill matches what's under review.
4. Tell the user the PR URL and that changes take effect after merge + `/plugin update`.

If the source repo can't be found, ask the user where it lives rather than leaving the edit cache-only.
