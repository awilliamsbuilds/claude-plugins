# Fast Path
*Branch: feature/fast-path · Confidence: 92% — Ready · 2026-08-15*
*Cycle type: feature · Tier: standard*
*Milestone 1 of `docs/dev/product-plans/dev-fast-path.md`*

## Intent

`/dev`'s seven stages are correctly weighted for a feature like `backlog-viewer` — 2h43m of spec,
three validate loops, a decision log — and absurdly heavy for a one-line frontmatter fix.

`dev:autopilot` does not close that gap. It removes the **gates**, not the **ceremony**: a micro
cycle run unattended still creates a worktree, writes `spec.md` and `state.json`, dispatches two
challengers, runs a validate fix loop, writes `validation.md`, generates a decision log, and runs a
retrospective. For a typo that is the wrong trade in both directions — slow, and the artifacts it
produces are not worth reading.

The session that produced this spec is the worked example of the target: six PRs merged in one
sitting with **zero** `/dev` artifacts, where rigor came from grounding before acting, running the
suite, verifying in a browser where the suite could not reach, capturing deferred work to
`docs/backlog/`, and reporting honestly. That is not a lower standard — it is the same standard
carried by judgment instead of by paperwork.

This cycle builds that lane and the rule that refuses it.

## Scope

**`/dev:fix "<what you want done>"` — the lane.** Runs unattended through:

1. **Ground** — read the actual files; verify every as-is claim the request makes.
2. **Triage** — count unresolved decisions (see below). Escalate, ask, or proceed.
3. **Branch** — from `origin/<default>`, named for the change.
4. **Change** — the minimal edit that does the job.
5. **Verify** — run the repo's test suite if one exists; verify by whatever means the change
   actually requires, including means the suite cannot reach.
6. **PR** — open it with a real description: what changed, why, what was verified.

Then it **stops**. The PR is the checkpoint.

**`/dev:fix merge` — the tail.** The argument is the bare token `merge` and nothing else; any longer
argument, including one whose first word is `merge`, is a free-text request for the lane. It operates
on the open PR for the branch currently checked out in the primary checkout; if that branch has no
open PR, or more than one resolves, stop and report rather than guessing. Merges the PR, deletes the
remote and local branch, fast-forwards the primary checkout, reports. Nothing irreversible happens
without this second invocation.

**The escalation rule.** After grounding, before changing, count the decisions the lane would be
making *for* the user — points where a reasonable person could choose differently:

| Decisions | Behavior |
|---|---|
| 0 | Proceed, **regardless of size**. A mechanical 14-file rename qualifies. |
| 1 | Ask it inline, then proceed. One question is cheaper than a whole cycle. |
| 2+ | **Stop.** List the decisions, print the `/dev` command, and offer to proceed if the user answers them here. |

Size is deliberately not the trigger. This session's 14-file frontmatter rename was trivially safe;
a one-file change with two defensible answers is not.

**Counting rule.** A decision is countable only if **all three** hold: (a) the request text does not
determine it, (b) no existing repo convention determines it, and (c) reversing it later would
require editing files this change touches. A choice already settled by an established convention
counts as **zero** — that is what lets a large mechanical change proceed. When genuinely unsure
whether something is countable, **count it**: the cost of a false escalation is one `/dev` command,
and the cost of a false proceed is a decision made on the user's behalf that they never saw.

**The rename.** Today's `dev:fix` — Linear issue → the full seven stages — becomes **`/dev:linear`**,
a name that describes what it does. `/dev:fix` is the scarce good name and it goes to the common
case. Linear support is retained, not dropped.

**The rigor floor.** The lane may never skip these, and says which it did in the PR body:
- Ground before acting — no edit from a remembered mental model of the code.
- Run the project's test suite when one exists.
- Never claim unverified success; if something could not be verified, say so.
- Capture anything deferred to `docs/backlog/` rather than dropping it.
- Report what it decided on the user's behalf.

## Out of Scope

- **Backlog-item entry.** `/dev:fix <backlog-slug>` is Milestone 2. This cycle takes a free-text
  request only.
- **Retiring `~/.claude/commands/`.** Milestone 3. Those files are outside this repo; no PR here can
  delete them.
- **Any behavior change to the seven-stage pipeline.** `/dev`, `/dev:autopilot`, and every stage
  skill keep working exactly as they do now. The only edit to an existing stage skill is the
  `dev:fix` → `dev:linear` rename and its reference sites.
- **A second checkpoint before changing.** Considered and rejected: the pre-change approval is where
  most of the wall-clock time goes, and the escalation rule already covers the case where stopping
  is warranted.
- **Auto-merge.** Rejected for this milestone — merging is the one irreversible step, and it stays
  behind a human yes. Milestone 2 may revisit it for backlog runs, where "as little interaction as
  possible" is the explicit goal.
- **A shared-logic refactor of `dev:pr` / `dev:done`.** See Technical Constraints — the duplication
  is real and is managed by explicit divergence, not by extracting a shared module this cycle.

## Success Criteria

1. A 0-decision request reaches an open PR with **no user turn** between invocation and the PR
   report.
2. A request carrying 2+ unresolved decisions **stops before changing any file**, lists the
   decisions, and prints the `/dev` command. It never proceeds silently.
3. A mechanical multi-file change — the shape of this session's 14-file rename — **proceeds without
   escalating**. Size alone never triggers escalation.
4. `/dev:fix merge` leaves: PR merged, remote branch gone, local branch gone, primary checkout on
   the default branch and fast-forwarded, working tree clean.
5. The lane never opens a PR without having run the repo's test suite when one exists, and the PR
   body states the result.
6. `/dev`, `/dev:autopilot`, and stages `spec`/`shape`/`plan`/`build`/`validate`/`pr`/`done` are
   byte-identical after this cycle except for `dev:fix` → `dev:linear` rename references **and, in
   `dev/SKILL.md` only, one added invocation-table row plus a description mention for the new
   `/dev:fix` lane**. Without that carve-out the criterion forbids the discoverability edit the Scope
   requires — the invocation table is where commands are advertised.
7. Every reference to `dev:fix` resolves to the skill that actually does what the reference claims —
   verified by sweeping **all 9 sites** in `plugins/dev/`, not by recall, **plus the three
   out-of-plugin references** (`README.md`, `CLAUDE.md`, `plugins/plugin-manager/skills/add-plugin/SKILL.md`).
   Historical records under `docs/decisions/` are **excluded**: they describe what was true when
   written and must not be rewritten.
8. `grep -rn '/Users/\|awilliamsbuilds\|adam' plugins/dev/` still returns zero.
9. The new `/dev:fix` lane is discoverable everywhere the repo advertises `dev` skills: its own
   Component Registry row in `CLAUDE.md` beside the renamed `dev:linear` row, an entry in
   `README.md:13`'s skill list, in `add-plugin/SKILL.md:25`'s table, and in both `dev:start` lists
   (`start/SKILL.md:52` and `:68`) beside `dev:linear`. The twelve sites are swept for the rename
   **and** for the addition — a pure rename that leaves the lane unlisted fails this criterion.

## Happy Path

1. Run `/dev:fix "drop the redundant plugin prefix from the dev skill names"` from anywhere in the
   repo.
2. The lane reads the frontmatter of every `dev` skill and of one other plugin's skills, confirming
   the prefix claim against real files.
3. Triage: 0 unresolved decisions — the fix is mechanical and the convention is already established
   elsewhere in the repo. Proceed.
4. Branch, edit 14 files, run the suite.
5. PR opened. The lane reports what it changed, what it verified, and stops.
6. User reviews, runs `/dev:fix merge`. Merged, cleaned up, main fast-forwarded.

## Edge Cases

- **Dirty working tree.** The lane operates in the primary checkout, not a worktree. Refuse before
  branching, naming the modified files — never stash, never branch over uncommitted work.
- **No test suite in the repo.** Say so explicitly in the PR body rather than implying tests passed.
  An absent suite raises the bar on other verification, it does not lower the bar overall.
- **Mid-flight discovery.** Grounding said 0 decisions; implementation reveals a real fork. **Stop
  and escalate at that point** rather than deciding to keep momentum. The count is a prediction, and
  a prediction that turns out wrong is a reason to stop, not a commitment to honor.
- **Nothing to change.** The request is already satisfied. Say so and open no PR — an empty PR is
  worse than no PR.
- **Default branch is not `main`.** Detect it; never assume.
- **Branch name already exists** locally or on the remote. Disambiguate rather than reusing or
  force-pushing.
- **PR is not mergeable at `/dev:fix merge`** — conflicts, failing checks, or a mergeability the API
  still reports as `UNKNOWN`. Stop and report; never force, and never delete a branch whose PR did
  not merge.
- **`gh` unavailable or unauthenticated.** Fail before branching, with the reason.
- **No `docs/backlog/` in the repo.** Deferred-work capture degrades silently rather than erroring —
  the same rule the tech-debt contract already applies (P7).
- **Invoked while a `/dev` cycle is in flight.** A modern cycle lives in its own worktree, so it does
  not contend with the lane's use of the primary checkout. **A legacy in-place cycle
  (`worktreePath: null`) does contend** — it occupies the primary checkout on its own feature branch,
  and a clean-tree check will not catch it because a committed in-place cycle leaves the tree clean.
  Detect that case explicitly — scan `$PRIMARY/docs/dev/*/state.json` for a cycle whose
  `worktreePath` is null and whose `stage` is not `done` — and refuse rather than branching over it.

## Audience

Single operator — the repo owner, running this many times a day across several repos. The plugin is
distributed via the `local-plugins` marketplace and must stay installable by anyone, so nothing may
hardcode a personal path, username, or machine-specific location.

## Technical Constraints

- **No build tooling.** The repo ships markdown skills. This cycle must not introduce a build step.
- **The lane cannot reuse `dev:pr` or `dev:done`.** Verified: `dev:pr` STOPs without `validation.md`,
  `dev:done` STOPs without `pr_url` in `state.json`, `dev:validate` STOPs without a completed build,
  `dev:build` STOPs without a plan unless tier is micro. Every stage gates on the prior artifact, so
  a lane that produces no artifacts cannot enter the chain anywhere. **This is the cycle's central
  design tension:** the lane must therefore implement its own PR and merge segments, which
  duplicates logic that `dev:pr` and `dev:done` already hold. The duplication is accepted
  deliberately for this milestone and must be *named in the skill file* at both sites, so a future
  edit to one is not silently missed at the other. Extracting a shared reference is a candidate for
  a later cycle, not this one.
- **`dev:fix` has 9 reference sites** in `plugins/dev/`: `skills/validate`, `skills/done`,
  `skills/spec`, `skills/start`, `skills/plan`, `skills/dev`, `skills/fix` itself,
  `skills/debt/viewer.py`, and **`references/tech-debt.md`** — the last of which a `skills/`-only
  sweep misses. Three further references live outside the plugin and would go stale: `README.md:13`,
  `CLAUDE.md:35` (the Component Registry row, owned by `dev:done` Step 4), and
  `plugins/plugin-manager/skills/add-plugin/SKILL.md:25`. The rename must sweep all twelve; the same
  twelve are the addition surface for the new lane (Success Criterion 9).
  `docs/decisions/*.md` also mention `dev:fix` and are **deliberately excluded** — a decision log
  records what was true on its date, and editing one to match the present destroys the record.
- **`PRIMARY` derivation must reuse the existing precedent**, not invent one. The lane runs "from
  anywhere in the repo" while operating on the primary checkout, so it needs the derivation
  `dev:build` Step 0 and `debt/viewer.py` already use (`git rev-parse --git-common-dir`, then
  `dirname`, with a non-empty guard). `debt-primary-cd-failure-unchecked` records that 13 existing
  sites lack the guard; this cycle writes a new site and must carry it rather than grow the count.
- **Skills are auto-discovered** — `plugins/dev/.claude-plugin/plugin.json` has no skills array, so
  adding `dev:linear` and reshaping `dev:fix` touches no plugin.json and no marketplace entry.
- **The installed plugin is a snapshot of `main`.** Nothing this cycle writes is live until the PR
  merges and `/plugin update` runs — so the lane cannot be verified end-to-end through its own
  invocation during Build. Verify at the file level and by walking the procedure manually, and say
  which is which.
- **Frontmatter `name:` must stay bare** (`fix`, not `dev:fix`) or slash-command autocomplete renders
  `/dev:dev:fix`. Established this session.

## Dependencies

- Depends on nothing external — no new runtime, no new tool.
- **Blocks Milestone 2** (`fast-path-backlog`), which is an entry adapter onto this lane, and
  **Milestone 3** (`retire-legacy-commands`), which cannot decide what to retire until the
  replacement exists.
- Consumes the `docs/backlog/` contract in `plugins/dev/references/tech-debt.md` for deferred-work
  capture. The lane is a consumer of that schema and must not fork it.

## UI Needed

**No.** Terminal output only; no visual surface. The lane's copy — the PR-stop report, the
escalation message, the merge confirmation — is short enough to settle in this spec and the plan.
Shape would add a stage for little gain, which would be a poor advertisement for a cycle about not
spending time on ceremony.

---
*Auto-filled dimensions: none — `ui_needed` and `dependencies` were decided by the author with
reasoning stated rather than asked, and are subject to the approval gate.*
*Grounding inventory: stage artifact gates read directly — `pr/SKILL.md:36` (STOP without
validation.md), `done/SKILL.md:45` (STOP without pr_url), `validate/SKILL.md:40` (STOP without
build), `build/SKILL.md:42` (STOP without plan unless micro); this is what rules out reusing the
chain and is the spec's most load-bearing claim. Micro-tier reachability: no *invocation* form exists
(`dev/SKILL.md` and `autopilot/SKILL.md` carry no micro argument), but the tier **is** requestable
interactively — `spec/SKILL.md:123` displays the detected tier and offers "Override?". The corrected
claim is that micro cannot be reached without entering Spec, and that reaching it changes only the
stage list, not the artifact set: a micro cycle still writes every artifact, which is what the
Intent actually rests on. Negative space swept for an existing fast lane
(`grep -rln "quick\|fast.path\|fast lane"` across `skills/`) → two hits, both incidental prose
("quick reference", "quick no"), confirming none exists. `dev:fix` consumers enumerated by sweep,
not recall: `skills/{validate,done,spec,start,plan,dev,fix}`, `skills/debt/viewer.py`, and
`references/tech-debt.md` = **9 sites** in `plugins/dev/`. A first pass scoped to `skills/` found
only 8 and missed `references/tech-debt.md`; the corrected sweep is 9, plus the three out-of-plugin
sites (`README.md:13`, `CLAUDE.md:35`, `add-plugin/SKILL.md:25`) = 12 total. Legacy commands
located and read at `~/.claude/commands/{fix,merge,pr,security-review,security-review-diff}.md` —
confirmed outside this repo and therefore outside any PR's reach. Autopilot's weight confirmed from
its own description and Step 2 stop list: it removes gates, not artifacts. Open-debt cross-check run
against the P5 corpus intersected with this cycle's surface — 16 nominal matches, narrowed to 4
genuinely coupled, 3 folded into scope (see debt-pending.md).*
