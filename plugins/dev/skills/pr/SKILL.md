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
- `docs/dev/config.json` (for changelog path and versioning config)

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

## Step 3: Update Changelog

Read `docs/dev/config.json`. If the `changelog` key is absent or null, skip this step entirely.

If a changelog path is configured:

**Collect qualifying changes** by reviewing `spec.md`, `design.md` (if exists), and `plan.md`. A change qualifies if it is:
- A new feature or capability
- A removed feature
- A UI/UX improvement (layout, flow, clarity, navigation)

Do **not** include: bug fixes, invisible performance improvements, copy or label changes, config/settings additions, internal refactors.

**If no qualifying changes found:** skip the changelog entry. Append this line to the PR description: `*No user-facing changes in this cycle — changelog not updated.*`

**If qualifying changes exist:**

1. Read the most recent 2–3 entries in the changelog file to extract the style (heading format, bullet style, date/version format). Match it exactly.

2. **Version bump** (only when `changelog_versioned: true`):
   - New features present → **minor** bump
   - UX improvements only, no new features → **patch** bump
   - Changes appear major in scope (complete redesign, breaking behavior change, multiple significant features) → ask: `"These changes look substantial — worth a major version bump? (yes / no, use minor)"`
   - Never auto-bump major. Always require explicit confirmation.
   - Parse the current version from the top of the changelog and increment accordingly.

3. Write the entry from the user's perspective — what changed about their experience. Use plain language, no technical jargon. Keep it concise; prefer one clear sentence per item over exhaustive detail.

4. Prepend the new entry to the changelog file (newest at top). Stage and commit:
   ```bash
   git add <changelog-path>
   git commit -m "chore: update changelog for <feature>"
   ```

5. Note in the exit display: `Changelog updated: <path>` (include new version if versioned).

## Step 4: Open PR

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

## Step 5: Update State + Commit

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
