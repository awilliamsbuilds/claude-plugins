---
name: pr
description: "Stage 6 of the /dev workflow. Opens a pull request with a description auto-generated from the full artifact chain (spec + design + plan + validation). Stores PR URL and number in state.json."
---

# dev:pr — Pull Request Stage

**Announce:** "I'm using dev:pr to open the pull request."

## Resolve the working directory (do this first)

This stage never relies on the shell's current directory or current branch. Compute the
primary checkout, then locate this cycle's directory:

    GIT_COMMON=$(git rev-parse --git-common-dir) || { echo "Not a git repository."; exit 1; }
    PRIMARY=$(cd "$(dirname "$GIT_COMMON")" && pwd)

Find the cycle directory — first hit wins — by testing for `docs/dev/<feature>/state.json` under:
1. `$PRIMARY/.dev-worktrees/<feature>/`   → active worktree cycle
2. `$PRIMARY/`                            → legacy in-place cycle (worktreePath null)

Set `WORKDIR` to whichever matched. For the rest of this stage: run every git command as
`git -C "$WORKDIR" …`, and read/write all artifacts under `$WORKDIR/docs/dev/<feature>/…`.
Never `cd`, never assume the current branch.

## Purpose

Open the PR with a description that tells the full story of the feature cycle — what was built, how it was designed, and how it was validated.

## Step 1: Artifact Gate

May be invoked with an artifact-path argument (`validation.md` path). If given, derive `<feature>` from the path instead of requiring it already be known from conversation context. If no argument is given, fall back to today's behavior. **Validate before using:** the path must match `docs/dev/<feature>/<artifact>.md` with `<feature>` matching `^[a-z0-9][a-z0-9-]*$` and containing no `..` segments. If it doesn't match, treat the argument as invalid and fall back to today's behavior rather than using the parsed value.

Read `docs/dev/<feature>/state.json`. Confirm `"validate"` is in `completed[]`.

**`linear_issue` is read from that same state file here.** Naming it explicitly matters: until this
stage existed as its reader, the key had **zero readers** — `dev:spec` initialized it and the retired
`dev:linear` wrote it, and nothing ever consumed either write, so the Linear round trip was inert in
both directions. This stage is its first consumer, and the escalated cycle's half of that round trip.

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

**When `state.json.linear_issue` is non-null**, the body opens with the `Closes` line from
`../../references/entry-adapters.md` §A3, exactly `Closes [<id>](<url>)`, read from that object's
`id` and `url` fields. It is the **first line**, above `## What this does`, so Linear's parser sees it
regardless of body length. **Omit the line entirely when `linear_issue` is null** — never emit an
empty or placeholder `Closes`.

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

2. **Version bump** (only when `changelog_versioned: true`; an absent `changelog_versioned` key ⇒ treat as `false`, so skip the version bump):
   - New features present → **minor** bump
   - UX improvements only, no new features → **patch** bump
   - Changes appear major in scope (complete redesign, breaking behavior change, multiple significant features) → ask: `"These changes look substantial — worth a major version bump? (yes / no, use minor)"`
   - Never auto-bump major. Always require explicit confirmation.
   - Parse the current version from the top of the changelog and increment accordingly.

3. Write the entry from the user's perspective — what changed about their experience. Use plain language, no technical jargon. Keep it concise; prefer one clear sentence per item over exhaustive detail.

4. Prepend the new entry to the changelog file (newest at top). Stage and commit:
   ```bash
   git -C "$WORKDIR" add <changelog-path>
   git -C "$WORKDIR" commit -m "chore: update changelog for <feature>"
   ```

5. Note in the exit display: `Changelog updated: <path>` (include new version if versioned).

## Step 4: Open PR

**Duplicated at `dev:fix`.** This step is canonical; `dev:fix`'s PR segment mirrors it for the
artifact-free fast path, which produces no `validation.md` and so cannot enter this stage. A change
here should be reflected there. **The `Closes` lead line is part of what is mirrored** — both sides
emit the identical `Closes [<id>](<url>)` format, but on different transports: this stage reads it
from `state.json.linear_issue`, while the lane holds the values in-turn and never writes a state file
at all. Keep the format in step; do not try to unify the plumbing.

**The `--body` below is a double-quoted interpolation, and this cycle deliberately leaves it that
way.** `dev:fix`'s mirror binds its body through a single-quoted heredoc precisely because the body
carries untrusted input, and that reasoning applies here too. Changing it is out of this cycle's
scope — recorded here so the divergence is visible to whoever picks it up, rather than looking like
an oversight on one side.

Push the branch if not already pushed:
```bash
git -C "$WORKDIR" push -u origin <branch-name>
```

**Determine the target branch:** if `state.json.parentFeature` is set (this is a nested sub-milestone), the target is the parent feature's own branch — read the parent's `docs/dev/<parentFeature>/state.json.branch` field to get its exact name. Otherwise (top-level cycle), the target is `main`, as today.

**If nested, the target branch must exist on the remote before `gh pr create` can target it — push it first if it isn't already there:**
```bash
git -C "$WORKDIR" push origin <parent-branch>   # no-op if already up to date remotely
```
A nested cycle's PR happens before its parent's own `dev:pr` stage runs (the parent hasn't pushed yet at that point), so this step cannot be skipped — assume the parent branch needs pushing rather than checking first.

Open the PR using the `gh` CLI (run inside the worktree with explicit head):
```bash
( cd "$WORKDIR" && gh pr create \
    --title "<feature-name>: [one-sentence summary from spec Intent]" \
    --body "[PR description from Step 2]" \
    --base "<target-branch>" \
    --head "<branch-name>" )
```
`gh` has no `-C` flag; running it inside `$WORKDIR` with an explicit `--head` avoids the wrong-head bug where `gh` infers the head from whatever branch the shared tree happens to be on.

Capture the PR URL from the output.

## Step 5: Update State + Commit

Update state.json:
- Set `artifacts.pr_url` to the PR URL
- Set `artifacts.pr_number` to the PR number (parse from URL or gh output)
- Add `"pr"` to `completed[]`
- Set `stage` to `"done"`
- Record `metrics.stage_timestamps.pr_created` — run `date -u +%Y-%m-%dT%H:%M:%SZ` and write the output in

```bash
git -C "$WORKDIR" add docs/dev/<feature>/state.json
git -C "$WORKDIR" commit -m "pr: open PR for <feature> — [PR URL]"
git -C "$WORKDIR" push
```

In standard mode, display:
```
PR opened: [PR URL]

Review it, get approvals, then run /dev:done when ready to merge.

Safe to /clear now — resume with: /dev:done <feature> [PR URL]
[If worktreePath is set: Worktree: <worktreePath>]
```

**Autopilot mode:** Update state, proceed to done automatically.
