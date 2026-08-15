# Retire Legacy Commands

*Branch: feature/retire-legacy-commands · Confidence: 88% — Ready · 2026-08-15*
*Cycle type: feature · Tier: deep*
*Milestone 3 of `docs/dev/product-plans/dev-fast-path.md`*

## Intent

Five commands in `~/.claude/commands/` predate the `dev` plugin and overlap it. They cannot simply be
deleted: two of them hold capabilities `/dev` does not have, and one of the two — the security
review — turns out to be missing from the very path this project spent two cycles building.

**`/dev:fix` opens pull requests, unattended, with no security review of any kind.** A sweep for
`security` across `plugins/dev/skills/fix/SKILL.md` returns zero hits. The seven-stage pipeline is
covered — `dev:validate` Step 2 dispatches a security review as a parallel subagent on every feature
cycle — but the fast path this project exists to promote has none. That is the gap that makes
retiring `security-review-diff.md` a loss rather than a consolidation.

So this cycle closes the capability gaps first, then retires what `/dev` genuinely replaces. The rule
it establishes is one sentence: **every route to a PR runs the same two checks.**

## Scope

**1. A new `dev:security` skill — on-demand, outside the pipeline.**

Two verbs, sibling to `dev:debt` in shape (no stage gate, no `state.json`, no cycle artifacts):

| Verb | Behavior |
|---|---|
| `/dev:security` | Whole-project audit — the replacement for `security-review.md` |
| `/dev:security diff` | Current-diff audit — the replacement for `security-review-diff.md` |

**Report only. It writes nothing.** Findings are printed, severity-classified, and the skill stops.
It does not write to `docs/backlog/`, does not prompt, and does not modify a single file. This keeps
the new skill's blast radius at zero and makes retiring `security-review.md` an exact trade rather
than an expansion. (Chosen over offer-to-capture and auto-capture; the store's writer set stays as the
tech-debt contract defines it.)

**2. `/dev:fix` gains a security review — by calling `/dev:security diff`, not by growing its own.**

The lane runs the diff audit before it opens a PR. It **calls the new skill's `diff` verb** rather
than restating the checklist, so there is one canonical implementation and no mirror to drift. This is
the seam the two-verb design exists to create.

**On a P1/P2 finding the lane fixes it inline, once, then re-reviews before proceeding.** Bounded
exactly:

1. Attempt the fix in the same unattended run.
2. **Cold re-review the fix diff** — a fresh subagent seeing only that diff, the pattern `dev:validate`
   Step 4 step 8 already uses.
3. Clean → open the PR. **Any finding on the re-review → stop, commit the work, open no PR.**

One round only. This is `dev:validate`'s fix loop with `loops_max` pinned to 1.

*Recorded because the alternative was argued and lost:* the spec author recommended **stopping before
the PR on any finding**, matching what `pr.md` did and what the lane's own mid-flight escalation does.
The user chose bounded inline fixing, on the grounds that a single round with a cold re-review keeps
the fast path fast without letting an unreviewed fix through. The bound is what carries that argument —
without the one-round cap and the re-review, this would be the lane making security decisions
unattended and unchecked.

**3. Verification failure stops the lane — for the build *and* the suite.**

`/dev:fix` and `dev:validate` gain a build check: detect a build system (`package.json` `build`
script, `Makefile` target, `cargo build`, `go build`), run it, and **stop before the PR if it fails**.
No build system detected → skip, and say so.

**This also settles an existing ambiguity rather than adding a second inconsistent rule.** The lane
today runs the test suite and says only "Record each result verbatim for the PR body" — it never
states what a *failing* suite does. Adding a build check that blocks while a failing suite merely gets
reported would read as an oversight. So one rule covers both: **a failing build or a failing suite
stops the lane before the PR** — commit the work, report, open nothing, exactly as Step 6's mid-flight
escalation already does. This changes existing suite behavior, deliberately.

**4. Retire four commands, and document the manual step.**

`fix.md`, `pr.md`, `security-review.md`, `security-review-diff.md` — each with its replacement named:

| Command | Replaced by |
|---|---|
| `fix.md` | `/dev:fix linear <id>` (shipped by `entry-adapters`) |
| `pr.md` | `dev:pr` + `dev:fix`'s PR segment, plus this cycle's build check |
| `security-review.md` | `/dev:security` |
| `security-review-diff.md` | `/dev:security diff` |

**No PR in this repo can delete them** — they live in the user's home directory. This cycle documents
the exact removal step and states plainly that the keystroke is the user's.

**5. Three debt items, folded in at the Step 7 cross-check.**

- `debt-validate-fix-claims-unmeasured` — **closed.** `dev:validate` Step 4 gains the rule that a fix
  asserting what a command or tool does must verify it by running it. Directly earned: this cycle
  writes build-detection shell into two skills, which is exactly that class of claim.
- `debt-bare-reference-paths-do-not-resolve` — **closed.** The two remaining bare `references/` paths
  in `init/SKILL.md` and `done/SKILL.md` gain the `../../` prefix that resolves.
- `debt-primary-cd-failure-unchecked` — **not closed, and deliberately so.** `dev:security` is a new
  skill needing its own `PRIMARY` derivation. This cycle guards *that one site* so the item's count
  does not grow 12 → 13 and its body does not go stale on merge. The other 12 sites stay unguarded and
  the item stays `status: open`. This is the same forced-bookkeeping shape `entry-adapters` hit.

## Out of Scope

- **Security review on architecture cycles.** `dev:validate` excludes them by an explicit rule, and
  they still reach `dev:pr` and open PRs. **The user was shown this hole and chose to keep the
  carve-out**, on the grounds that architecture cycles produce committed decision documents rather
  than code. This cycle documents the reasoning in `dev:validate` so it reads as a decision rather
  than an oversight — but "every PR gets a security review" therefore carries one named exception, and
  the spec says so rather than overclaiming.
- **`branches.md`.** It restarts a launchd service for a personal app and has nothing to do with
  `/dev`. The product plan's command list never named it; it is excluded rather than swept up.
- **Whole-project audit on every PR.** `/dev:security` is ad hoc. Running a full-project scan per PR
  would re-report the same findings every cycle; the per-PR check is the diff audit.
- **Writing audit findings to `docs/backlog/`.** Considered and declined — see Scope §1.
- **Retiring `~/.claude/commands/` as a mechanism.** Only these four files are addressed.
- **Closing the remaining 12 unguarded `PRIMARY` derivations.** See Scope §5.
- **A fix loop on the fast path beyond one round.** The single round is the bound; a second finding
  stops rather than iterating.

## Success Criteria

1. `/dev:security` exists at `plugins/dev/skills/security/SKILL.md` and its whole-project verb prints
   a severity-classified report while creating, modifying, and deleting **zero** files —
   `git status --porcelain` is byte-identical before and after a run.
2. `/dev:security diff` audits only the current diff against the default branch, and its findings use
   the same P1/P2/P3/Nit vocabulary `dev:validate` Step 3 already defines — not a second severity
   scheme.
3. `/dev:fix` invokes `/dev:security diff` before opening a PR. **The lane does not restate the
   security checklist** — `grep -c 'injection\|XSS\|CSRF' plugins/dev/skills/fix/SKILL.md` returns
   zero, proving the call is a call and not a copy.
4. On a P1/P2 the lane fixes once, cold re-reviews **that fix's diff**, and opens the PR only on a
   clean re-review. A finding on the re-review leaves the work committed on the branch with no PR
   opened, and the report says which finding stopped it.
5. A failing build **or** a failing test suite stops `/dev:fix` before the PR, with the work committed
   and reported. Both are covered by a single stated rule, not two.
6. A repo with no detectable build system runs the lane unchanged and says in the PR body that no
   build was found — distinguishable from "the build passed."
7. `~/.claude/commands/{fix,pr,security-review,security-review-diff}.md` each have a named `/dev`
   replacement documented in the repo, and the manual removal step is written down as the user's to
   perform. `branches.md` is not mentioned as a retirement target.
8. `plugins/dev/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` are **unchanged** —
   verified against `origin/main`. Adding a skill to an existing plugin touches only a new `SKILL.md`
   (`CLAUDE.md:11`), and a diff to either file means that rule was misread.
9. `docs/backlog/debt-validate-fix-claims-unmeasured.md` and
   `docs/backlog/debt-bare-reference-paths-do-not-resolve.md` are in `docs/backlog/closed/` with
   `status: closed`, and `grep -rn '](references/' plugins/dev/skills/` returns zero.
10. `docs/backlog/debt-primary-cd-failure-unchecked.md` still reads `status: open` with **12** entries
    in `files:` and body counts agreeing. `dev:security` carries a guarded derivation, so it is not a
    13th site.
11. `/dev`, `/dev:autopilot`, and stages `shape`/`plan`/`build`/`spec`/`done` are byte-identical
    except where a retired command is referenced. `dev:fix`, `dev:validate`, `dev:pr`, `dev:init` and
    `dev:done` change as the Scope requires.

## Happy Path

1. `/dev:fix "drop the redundant prefix from the dev skill names"` in a repo with a build script.
2. Preflight passes; the lane grounds, triages at 0 unresolved decisions, branches, and makes the edit.
3. **Verify:** the build runs and passes; the test suite runs and passes. Both results recorded verbatim.
4. **Security:** the lane calls `/dev:security diff`. One P2 is found — an unquoted variable reaching a
   shell command.
5. The lane fixes it, then cold re-reviews that fix's diff. The re-review is clean.
6. PR opened. The body carries the build result, the suite result, and the security review's outcome
   including the P2 that was found and fixed.
7. `/dev:fix merge` merges and cleans up.

## Edge Cases

- **No build system detected.** Skip the build check and say so explicitly in the PR body — never
  imply a build passed. Mirrors the existing no-test-suite rule.
- **Build passes, suite fails.** Stop. One rule covers both; neither outranks the other.
- **Security review's subagent dispatch unavailable.** Fall back to running the checklist in-session,
  the same fallback `dev:validate` Step 2 already specifies. Never skip the review silently.
- **The inline fix introduces a *new* finding.** The re-review catches it; the lane stops rather than
  attempting a second round. This is the bound.
- **The inline fix cannot be made** (the finding is a design problem, not a line). Stop, commit, report
  — do not open the PR with a known P1.
- **`/dev:security` run in a repo with no git remote or on a detached HEAD.** The whole-project verb
  needs neither; the `diff` verb does need a base to diff against, and stops naming the reason when it
  cannot resolve one.
- **`/dev:security diff` with an empty diff.** Say so and stop; do not report "no findings," which
  reads as an audit that ran.
- **A retired command is still invoked** after this merges but before the user deletes the files. The
  command still exists on their machine and still runs — this cycle cannot prevent that, and the
  documentation says so rather than implying the retirement is enforced.
- **`dev:validate` already ran a security review; the lane's is separate.** A cycle that goes through
  the full pipeline is not double-reviewed by the lane — the lane and the pipeline are different
  routes to a PR and each runs exactly one.

## Audience

Single operator — the repo owner, running `/dev` across several repos with different build systems
(and some with none). The plugin is distributed via the `local-plugins` marketplace and must stay
installable by anyone, so build detection cannot assume a stack and the security skill cannot assume a
language.

## Technical Constraints

- **`~/.claude/commands/` is outside this repo.** No PR here can delete those files. The deliverable
  is documentation plus the replacement capability; deletion is a manual step.
- **Adding a skill to an existing plugin touches only a new `SKILL.md`** — verified at `CLAUDE.md:11`,
  and `plugins/dev/.claude-plugin/plugin.json` carries only `name`/`description`/`author` with no
  skill list, so there is nothing there to update.
- **`pr.md` already references a command that does not exist.** Its step 3 says run
  `/security-review-pr`; the files on disk are `security-review-diff.md` and `security-review.md`. Its
  security gate has been a dangling reference, which is worth stating in the retirement note.
- **No build tooling in this repo.** The repo ships markdown skills; this cycle must not introduce a
  build step, and its own build check will correctly detect nothing here.
- **Frontmatter `name:` must stay bare** (`security`, not `dev:security`) or autocomplete renders
  `/dev:dev:security`.
- **Severity vocabulary is already defined** at `dev:validate` Step 3 (P1/P2/P3/Nit). The new skill
  consumes it rather than defining a second scheme.

## Dependencies

- **Depends on** `/dev:fix` as shipped by `fast-path` and extended by `entry-adapters` — the security
  call and the build check attach to its Verify and PR segments.
- **Depends on** `dev:validate` Step 2's existing security-review checklist as the content the new
  skill's audit is built from; the skill is where that checklist becomes reusable.
- **Unblocks** nothing further — this is Milestone 3, the last item in `dev-fast-path`.
- **Completes the product plan.** On merge, all three milestones are `[x]`, so `dev:done` Step 3b will
  delete `docs/dev/product-plans/dev-fast-path.md` and close its promoted source item
  `backlog-fix-as-short-bug-round-trip`.

## UI Needed

**No.** Terminal output only — the audit report, the build/suite results, and the retirement
documentation. Copy settles in this spec and the plan.

---
*Auto-filled dimensions: none — every dimension was answered directly or derived from a verified
grounding result, with the derivation stated.*

*Grounding inventory: The request's central as-is claim ("if it's not already there") was checked
rather than assumed and came back **partly there**. `grep -n 'Security review' validate/SKILL.md` →
Step 2 dispatches one for feature cycles; `grep -i security fix/SKILL.md` → **zero hits**, so the fast
path has none; `grep -rln security plugins/dev/skills/` → `validate/SKILL.md` only, so no whole-project
scan exists anywhere in the plugin. `sed -n '92p' validate/SKILL.md` → "Security review does not run
for architecture cycles," and `dev:pr` does not branch on `cycle_type`, so those cycles open
unreviewed PRs. **The product plan's own command list was wrong in both directions** and was corrected
by `ls ~/.claude/commands/`: it named `merge.md`, which does not exist, and omitted `branches.md`,
which does — a set named from memory rather than swept, which is exactly what pass 2 exists to catch.
`grep -o '/security-review[a-z-]*' pr.md` → `/security-review-pr`, and `test -f` on all three
candidates confirms **no such command file exists**, so `pr.md`'s security gate is already a dangling
reference. The claim that the lane stops on a failing suite was checked and **found false** — the
Verify section says only "Record each result verbatim," which is why Scope §3 settles the ambiguity
instead of asserting a convention that was not there. `CLAUDE.md:11` and `plugin.json`'s key list
confirm a new skill touches no marketplace or plugin manifest. Open-debt cross-check run against the
P5 corpus: 9 active items intersect this cycle's surface files by front-matter `files:`; three were
surfaced and all three folded in (§5), the rest left untouched.*
