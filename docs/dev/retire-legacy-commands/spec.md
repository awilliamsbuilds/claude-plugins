# Retire Legacy Commands

*Branch: feature/retire-legacy-commands · Confidence: 88% — Ready · 2026-08-15*
*Cycle type: feature · Tier: deep*
*Milestone 3 of `docs/dev/product-plans/dev-fast-path.md`*

## Intent

Five files sit in `~/.claude/commands/`; four of them predate the `dev` plugin and overlap it. They cannot simply be
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

**1. A new `dev:secure` skill — on-demand, outside the pipeline.**

Two verbs, sibling to `dev:debt` in shape (no stage gate, no `state.json`, no cycle artifacts):

| Verb | Behavior |
|---|---|
| `/dev:secure` | Whole-project audit — the replacement for `security-review.md` |
| `/dev:secure diff` | Current-diff audit — the replacement for `security-review-diff.md` |

**The name is a verb, and the skill must correct its own implication immediately.** `/dev:secure`
reads as an imperative — *secure this project* — and the honest answer it returns is *here's what is
stopping it.* That reading works, and it stays accurate if the skill later grows to fix rather than
only report. But because "secure" names an action this version does not take, **the frontmatter
description and the skill's own opening line must both state that it reports and modifies nothing.**
The name may not be the only thing telling the user what happens.

*Recorded because the alternative was argued and lost:* the spec author twice raised that `secure`
names an outcome the skill does not deliver, and proposed `risk` (widest headroom, pairs with
`dev:debt`) or `audit`. The user chose `secure` on the grounds that the namespace's convention is
single-word and verb-shaped — `fix`, `validate`, `build`, `plan`, `shape`, `reflect` — and that a
noun would sit apart from it. The requirement above is what carries the cost of that choice.

**Report only. It writes nothing.** Findings are printed, severity-classified, and the skill stops.
It does not write to `docs/backlog/`, does not prompt, and does not modify a single file. This keeps
the new skill's blast radius at zero and makes retiring `security-review.md` an exact trade rather
than an expansion. (Chosen over offer-to-capture and auto-capture; the store's writer set stays as the
tech-debt contract defines it.)

**Where this meets `dev:fix`'s rigor floor, the floor wins.** The floor requires the lane to capture
anything deferred to `docs/backlog/`. The new skill writing nothing is a property of *the skill*, not
a licence for its **caller** to drop findings: when the lane declines to fix a P3 or Nit the audit
surfaced, the lane captures it per the floor, exactly as it already captures any other deferred work.
The skill reports; the lane decides and records.

**2. `/dev:fix` gains a security review — by calling `/dev:secure diff`, not by growing its own.**

The lane runs the diff audit before it opens a PR. It **calls the new skill's `diff` verb** rather
than restating the checklist, so there is one canonical implementation and no mirror to drift. This is
the seam the two-verb design exists to create.

**On a P1/P2 finding the lane fixes it inline, once, then re-reviews before proceeding.** Bounded
exactly:

1. Attempt the fix in the same unattended run.
2. **Cold re-review the fix diff** — a fresh subagent seeing only that diff, the pattern `dev:validate`
   Step 4 step 8 already uses.
3. Clean → open the PR. **A P1 or P2 on the re-review → stop, commit the work, open no PR.**

   The gate is **P1/P2, matching the initial review's own threshold** and `dev:validate` Step 4 step
   8's rule that the re-reviewer gates loop exit on P1/P2 only. A P3 or Nit surfaced by the re-review
   does not block — blocking on one would mean a Nit stops the PR on the second pass while the same
   Nit ships on the first.

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

**The suite half of this rule is `/dev:fix`-only, and that asymmetry is deliberate.** `dev:validate`
runs no test suite at all — verified, its Steps 1–6 contain no suite invocation; `dev:build` runs
tests per task during TDD, and `dev:validate` reviews. So on the pipeline route there is only a build
to apply the rule to. Say that in both skills rather than implying a symmetry that does not exist.

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
| `security-review.md` | `/dev:secure` |
| `security-review-diff.md` | `/dev:secure diff` |

**No PR in this repo can delete them** — they live in the user's home directory. This cycle documents
the exact removal step in a named home: a `## Retired commands` section in **`README.md`**, which
`CLAUDE.md` already establishes as the human-facing front door for what the plugins are and how to
set them up. It lists each retired command, its `/dev` replacement, and the `rm` the user runs — and
states plainly that the keystroke is theirs. `pr.md`'s entry additionally notes that its security step
already referenced a command (`/security-review-pr`) that never existed, so the flow it advertised had
not been running.

**5. Three debt items, folded in at the Step 7 cross-check.**

- `debt-validate-fix-claims-unmeasured` — **closed.** `dev:validate` Step 4 gains the rule that a fix
  asserting what a command or tool does must verify it by running it. Directly earned: this cycle
  writes build-detection shell into two skills, which is exactly that class of claim.
- `debt-bare-reference-paths-do-not-resolve` — **closed.** The two remaining bare `references/` paths
  in `init/SKILL.md` and `done/SKILL.md` gain the `../../` prefix that resolves.
- `debt-primary-cd-failure-unchecked` — **not closed, and deliberately so.** The new skill needs its
  own `PRIMARY` derivation for a stated reason: both verbs must resolve the repository root to scope
  what they audit, and the skill can be invoked from inside a `.dev-worktrees/<feature>` tree, so it
  cannot rely on the shell's directory — the same situation `dev:debt` Step 1 solves the same way. This cycle guards *that one site* so the item's count
  does not grow 12 → 13 and its body does not go stale on merge. The other 12 sites stay unguarded and
  the item stays `status: open`. This is the same forced-bookkeeping shape `entry-adapters` hit.

**Note for Plan — six workstreams, at the top of one deep cycle's range.** In scope: the new skill
with two checklists, the lane's bounded fix loop plus cold re-review, build/suite rules across two
skills, the retirement documentation, and three debt items. **If the task list comes back oversized,
the split seam is capability-then-retirement, not layer-shaped:** (1) §1 + §2 + §5's `PRIMARY` guard —
the security half, which is precisely what makes retiring the two `security-review*` commands a trade
rather than a loss; then (2) §3 + §4 + the two debt closes. §3 depends on nothing in §1, and §4's
retirement table cannot honestly be written until §1 exists. This is a fallback ordering, not an
instruction to split.

## Out of Scope

- **Security review on architecture cycles.** `dev:validate` excludes them by an explicit rule, and
  they still reach `dev:pr` and open PRs. **The user was shown this hole and chose to keep the
  carve-out**, on the grounds that architecture cycles produce committed decision documents rather
  than code. This cycle documents the reasoning in `dev:validate` so it reads as a decision rather
  than an oversight — but "every PR gets a security review" therefore carries one named exception, and
  the spec says so rather than overclaiming.
- **`branches.md`.** It restarts a launchd service for a personal app and has nothing to do with
  `/dev`. The product plan's command list never named it; it is excluded rather than swept up.
- **Whole-project audit on every PR.** `/dev:secure` is ad hoc. Running a full-project scan per PR
  would re-report the same findings every cycle; the per-PR check is the diff audit.
- **Writing audit findings to `docs/backlog/`.** Considered and declined — see Scope §1.
- **Security vectors deliberately deferred — named rather than assumed, because the skill is expected
  to grow into them.** This cycle ships the checklist `security-review.md` and `dev:validate` Step 2
  already carry: injection, authn/authz gaps, data exposure, dependency and config issues, and a few
  business-logic classes, plus the ecosystem scanners (`npm audit`, `pip-audit`, `govulncheck`) and
  committed-secret greps. Out for now, each for a stated reason:
  - **Threat modeling** — trust boundaries, attack trees, STRIDE. A different discipline requiring
    system context this skill does not read, not a longer checklist.
  - **Active testing / DAST** — the skill never executes an attack, only reads. Running one would need
    a live target and a safety story neither this spec nor the lane has.
  - **IaC and container configuration** — Terraform, Dockerfiles, k8s manifests. A distinct rule set
    and distinct tooling; the natural second vector to add.
  - **Supply-chain provenance** — lockfile integrity, dependency confusion, typosquatting. The
    scanners cover *known-vulnerable versions*; they say nothing about whether the package is the one
    you meant.
  - **Secret liveness** — the greps find committed secrets but cannot tell a revoked key from an
    active one, which is what determines urgency.
  - **Compliance mapping** — SOC 2, OWASP ASVS coverage. Reporting against a framework is a different
    output shape from reporting findings.

  Adding any of these is a later cycle. They are listed so the growth path is a decision rather than
  a rediscovery, and so the name's headroom is backed by a written scope.
- **Retiring `~/.claude/commands/` as a mechanism.** Only these four files are addressed.
- **Closing the remaining 12 unguarded `PRIMARY` derivations.** See Scope §5.
- **A fix loop on the fast path beyond one round.** The single round is the bound; a second finding
  stops rather than iterating.

## Success Criteria

1. `/dev:secure` exists at `plugins/dev/skills/secure/SKILL.md` and its whole-project verb prints
   a severity-classified report while creating, modifying, and deleting **zero** files —
   `git status --porcelain` is byte-identical before and after a run.
2. `/dev:secure diff` audits only the current diff against the default branch, and its findings use
   the same P1/P2/P3/Nit vocabulary `dev:validate` Step 3 already defines — not a second severity
   scheme.
3. `/dev:fix` invokes `/dev:secure diff` before opening a PR. **The lane does not restate the
   security checklist** — `grep -c 'injection\|XSS\|CSRF' plugins/dev/skills/fix/SKILL.md` returns
   zero, proving the call is a call and not a copy.
4. On a P1/P2 the lane fixes once, cold re-reviews **that fix's diff**, and opens the PR only on a
   clean re-review. A finding on the re-review leaves the work committed on the branch with no PR
   opened, and the report says which finding stopped it.
5. A failing build **or** a failing test suite stops `/dev:fix` before the PR, with the work committed
   and reported. Both are covered by a single stated rule, not two.
6. A repo with no detectable build system runs the lane unchanged and says in the PR body that no
   build was found — distinguishable from "the build passed."
7. `README.md` carries a `## Retired commands` section naming all four of
   `{fix,pr,security-review,security-review-diff}.md`, each with its `/dev` replacement and the `rm`
   command, and stating the deletion is the user's to run. `branches.md` does not appear in it.
   Checkable: `grep -c '^| \`' README.md` against that section returns 4.
8. `plugins/dev/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` are **unchanged** —
   verified against `origin/main`. Adding a skill to an existing plugin touches only a new `SKILL.md`
   (`CLAUDE.md:11`), and a diff to either file means that rule was misread.
9. `docs/backlog/debt-validate-fix-claims-unmeasured.md` and
   `docs/backlog/debt-bare-reference-paths-do-not-resolve.md` are in `docs/backlog/closed/` with
   `status: closed`, and ``grep -rn '`references/' plugins/dev/skills/ --include=SKILL.md`` returns
   zero. **The backtick form is the load-bearing part:** the two stale paths are inline code spans,
   not Markdown links, so the link-form grep `'](references/'` returns zero *today* and would pass
   whether or not the fix landed. The debt item's own `**Done looks like:**` carries that same broken
   grep and **must be corrected before the item is closed** — otherwise this cycle archives it against
   a test that cannot fail.
10. `docs/backlog/debt-primary-cd-failure-unchecked.md` still reads `status: open` with **12** entries
    in `files:` and body counts agreeing. `dev:secure` carries a guarded derivation, so it is not a
    13th site.
12. `dev:validate` detects and runs a build where one exists, stops the stage before `dev:pr` if it
    fails, and records the result in `validation.md`. Where no build system is detected it says so
    rather than implying success. **This criterion exists because Scope §3 gives the build check to
    two skills and the earlier criteria only test one** — and because the suite half of §3's rule does
    not apply here, `dev:validate` running no suite.
11. `/dev`, `/dev:autopilot`, and stages `shape`/`plan`/`build`/`spec`/`pr` are byte-identical
    except where a retired command is referenced. `dev:fix` and `dev:validate` change as Scope §2–3
    require. `dev:init` and `dev:done` change **only** by the `../../` reference-path fix in §5 —
    nothing in Scope assigns either of them any other change, and `dev:pr` none at all.

## Happy Path

1. `/dev:fix "drop the redundant prefix from the dev skill names"` in a repo with a build script.
2. Preflight passes; the lane grounds, triages at 0 unresolved decisions, branches, and makes the edit.
3. **Verify:** the build runs and passes; the test suite runs and passes. Both results recorded verbatim.
4. **Security:** the lane calls `/dev:secure diff`. One P2 is found — an unquoted variable reaching a
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
- **`/dev:secure` run in a repo with no git remote or on a detached HEAD.** The whole-project verb
  needs neither; the `diff` verb does need a base to diff against, and stops naming the reason when it
  cannot resolve one.
- **`/dev:secure diff` with an empty diff.** Say so and stop; do not report "no findings," which
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
- **Frontmatter `name:` must stay bare** (`secure`, not `dev:secure`) or autocomplete renders
  `/dev:dev:secure`.
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
