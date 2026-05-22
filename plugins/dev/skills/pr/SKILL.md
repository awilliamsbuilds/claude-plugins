---
name: dev:pr
description: "Stage 6 of the /dev workflow. Opens a pull request with a description auto-generated from the full artifact chain (spec + design + plan + validation). Stores PR URL and number in state.json."
---

# dev:pr — Pull Request Stage

**Announce:** "I'm using dev:pr to open the pull request."

## Purpose

Open the PR with a description that tells the full story of the feature cycle — what was built, how it was designed, and how it was validated.

## Step 1: Artifact Gate

Read `docs/dev/<feature>/state.json`. Confirm `"validate"` is in `completed[]`.

If validation is not complete: STOP — "PR requires validation.md. Run /dev:validate first."

Read once at stage start:
- `docs/dev/<feature>/state.json`
- `docs/dev/<feature>/spec.md`
- `docs/dev/<feature>/design.md` (if it exists — Shape may have been skipped)
- `docs/dev/<feature>/plan.md` (if it exists — Micro uses spec Implementation Note)
- `docs/dev/<feature>/validation.md`

## Step 2: Build PR Description

Generate a PR description from the artifact chain. Do not repeat information verbatim — synthesize into a readable narrative.

**PR description format:**

```markdown
## What this does
[1–2 sentences from spec.md Intent and Scope]

## Why
[1 sentence from spec.md Intent — the problem being solved]

## Design decisions
[Key choices from design.md — which alternative was selected and why. Omit if Shape was skipped.]

## Implementation notes
[Summary of approach from plan.md — what was built, key architectural choices. 2–4 bullet points.]

## Validation
[From validation.md: loops run, what was found and fixed, any remaining open issues with their severity]

## Checklist
- [ ] Tests pass
- [ ] No open P1/P2 issues (or: N P1/P2 issues noted above — proceeding by choice)
```

If validation has open P1/P2 issues (user chose to proceed anyway), add a prominent note at the top:

```markdown
> ⚠️ **Open issues:** N P1/P2 issues remain. See Validation section. Reviewed and accepted by author.
```

## Step 3: Open PR

Push the branch if not already pushed:
```bash
git push -u origin <branch-name>
```

Open the PR using the `gh` CLI:
```bash
gh pr create \
  --title "<feature-name>: [one-sentence summary from spec Intent]" \
  --body "[PR description from Step 2]" \
  --base main
```

Capture the PR URL from the output.

## Step 4: Update State + Commit

Update state.json:
- Set `artifacts.pr_url` to the PR URL
- Set `artifacts.pr_number` to the PR number (parse from URL or gh output)
- Add `"pr"` to `completed[]`
- Set `stage` to `"done"`
- Record `stage_timestamps.pr_created`

```bash
git add docs/dev/<feature>/state.json
git commit -m "pr: open PR for <feature> — [PR URL]"
git push
```

In standard mode, display:
```
PR opened: [PR URL]

Review it, get approvals, then run /dev:done when ready to merge.
```

**Autopilot mode:** Update state, proceed to done automatically.
