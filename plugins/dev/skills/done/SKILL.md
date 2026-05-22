---
name: dev:done
description: "Stage 7 of the /dev workflow. Merges the PR, generates a decision log, invokes dev:reflect, and cleans up the feature branch and working directory. Requires PR URL in state.json."
---

# dev:done — Completion Stage

**Announce:** "I'm using dev:done to merge, document, and close out the cycle."

## Purpose

Close the feature cycle: merge the PR, create a permanent decision log, run the retrospective, and clean up.

## Step 1: Artifact Gate

Read `docs/dev/<feature>/state.json`. Confirm `artifacts.pr_url` is not null.

If PR URL is missing: STOP — "Done requires an open PR. Run /dev:pr first."

Read once at stage start:
- `docs/dev/<feature>/state.json` — full state including cycle_type, tier, all metrics
- `docs/dev/<feature>/spec.md`
- `docs/dev/<feature>/design.md` (if exists)
- `docs/dev/<feature>/plan.md` (if exists)
- `docs/dev/<feature>/validation.md`

Note the pre-merge commit SHA (used in decision log for artifact archiving).

## Step 2: Merge PR

```bash
gh pr merge <pr-number> --merge --delete-branch
```

This merges with a merge commit and deletes the remote branch.

If the PR can't be auto-merged (conflicts or required reviews pending): STOP and display:

```
PR can't be merged automatically. Reason: [conflict / pending reviews].
Resolve in GitHub, then run /dev:done again.
```

## Step 3: Update Product Plan (if product-scale)

If `state.json.product_plan` is not null:
- Read `docs/dev/product-plan.md`
- Find this feature's line item (match by feature name)
- Change `- [ ]` to `- [x]`
- Update the header: increment cycles completed count
- Commit to main: `chore: mark <feature> complete in product plan`

## Step 4: Update Component Registry (feature cycles only)

If `cycle_type == "feature"` and the feature added or modified components:
- Read `CLAUDE.md`
- Update the `## Component Registry` table: add new components, update modified ones
- Set "Last updated" date to today
- Commit to main: `chore: update Component Registry — <feature>`

For architecture cycles: skip this step.

## Step 5: Generate Decision Log

Write to `docs/decisions/YYYY-MM-DD-<feature>.md` (committed to main):

```markdown
# [Feature Name] — Decision Log
*YYYY-MM-DD · Branch: feature/<name> · PR #N*

## What was built
[One sentence from spec Intent.]

## Key decisions
[From spec.md and plan.md — major choices made. Each as: Decision → reason]

## Design choices
[From design.md — UX decisions and copy choices. Each as: UX decision → rationale]
[Omit section if Shape was skipped.]

## Validation notes
- [N] loops run (tier: [micro/standard/deep])
- [List P1/P2s found and how they were resolved]
- [List any P3/Nits accepted as-is]

## Artifacts (archived)
Spec, design, and plan committed at: <pre-merge-sha> on branch feature/<name>
```

```bash
git add docs/decisions/YYYY-MM-DD-<feature>.md
git commit -m "docs: add decision log for <feature>"
git push
```

## Step 6: Run dev:reflect

Invoke `dev:reflect` with the full state context. dev:reflect appends its output as `## Retrospective` to the decision log.

Pass to dev:reflect:
- The full state.json (all metrics)
- The decision log path
- The spec, plan, and validation artifact paths

## Step 7: Clean Up

Delete the feature's working directory (all committed artifacts travel with the branch which is now merged):

```bash
rm -rf docs/dev/<feature>/
git add -A docs/dev/<feature>/
git commit -m "chore: clean up /dev working directory for <feature>"
git push
```

Delete local branch:
```bash
git branch -d feature/<feature-name>
```

(Remote branch was deleted in Step 2 by `--delete-branch`.)

## Step 8: Display

```
✓ <feature> cycle complete

  PR #N merged and branch deleted
  Decision log: docs/decisions/YYYY-MM-DD-<feature>.md
  Retrospective appended (see decision log)
```

If product-plan.md exists, offer the next cycle:
```
Product plan: 3/8 cycles complete.

Milestone 1: ✓ auth-setup  ✓ data-model  → user-registration
Milestone 2: dashboard  settings

Start user-registration next? Or pick a different cycle.
```
