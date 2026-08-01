# dev:reflect — Explicit PR Target — Implementation Plan
*Branch: feature/reflect-pr-base-explicit-target · 2026-07-31*

## Files

| File | Action | Purpose |
|------|--------|---------|
| `plugins/dev/skills/reflect/SKILL.md` | Modify | Replace step 2 of § *Skill edits go through the plugins repo — always* (currently the single line 186) with an explicit target-resolution procedure plus a `gh pr create` invocation carrying `--repo` and `--head` |

Nothing else is created or modified. `plugins/dev/skills/pr/SKILL.md` and
`plugins/dev/references/tech-debt.md` are **read** during Build for wording alignment and the §P9
citation anchor, and must end the cycle byte-identical.

## Tasks

### Task 1: Step 2 — resolve the PR target

**What:** Rewrite the front of step 2 so that both routes into it arrive at a validated `owner/name`
slug naming the repo the PR must open in, with no path left for `gh` to infer one.

**Used by:** Task 2's `gh pr create` invocation consumes the slug this task produces. Read by a
maintainer following the fork scenario through the skill text (Success Criterion 6).

**Depends on:** nothing — first task.

**Files:** `plugins/dev/skills/reflect/SKILL.md` (modify, § *Skill edits go through the plugins repo
— always*, step 2)

**Interfaces:**
- Consumes: from step 1 (unmodified, read-only) — on the dogfood route, the marketplace `owner/repo`
  slug step 1 already derived by tracing the skill's cache path → the marketplace name in it → that
  marketplace's registry entry; on the ask route, the filesystem path the user named. Also consumes
  `plugins/dev/references/tech-debt.md` §P9.target-resolution as a citation target, not as text to copy.
- Produces: two named values that Task 2 substitutes into its command block —
  `<resolved-target-slug>` (a string matching `^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$`, the `owner/name` of
  the repo the PR opens in) and `<source-repo-path>` (the filesystem path of the source checkout the
  branch was made in). Use these exact placeholder names in the prose so Task 2's block reads as their
  consumer.
- Shared procedure: the normalize-to-`owner/name` + allowlist-validate procedure is applied on both the
  dogfood and the ask route. This task is its **sole** implementation in `reflect/SKILL.md` — it is
  written once, in one sentence, and both routes point at that one sentence. `references/tech-debt.md`
  §P9.target-resolution remains the **canonical** definition of the rule itself; this task **cites** it
  and holds no second copy (Success Criterion 4). Do not give the two routes their own normalize/validate
  wording — two copies of one rule is exactly the drift the contract names.

**Implementation steps:**

1. Read `plugins/dev/skills/reflect/SKILL.md` lines 177–190 to see the whole section, and
   `plugins/dev/references/tech-debt.md` lines 348–358 for the exact §P9.target-resolution text being
   cited. Do not edit either of the latter.
2. Replace the numbered item `2.` (currently: *"Create a feature branch (never commit to `main`), apply
   the same edit there (copy the finished cache file over, or re-apply the diff), commit, push, and open
   a PR with `gh`."*). Keep its first half — branch creation, applying the edit, commit, push — intact in
   meaning and ordering; that ordering is load-bearing for Task 2. Everything added below hangs off the
   second half.
3. State the rule that governs the whole step, before either route: **the PR target is always named
   explicitly; `gh` never resolves the repo from the git remotes.** Give the reason in one clause — `gh`'s
   rule for a fork is to send the PR to the fork's parent, so a user working in their own fork of the
   plugin repo would otherwise have their skill edit proposed against the upstream.
4. Write the **dogfood route**: step 1's shortcut has already established that the current checkout *is*
   the source repo, and in doing so already derived the marketplace slug. Step 2 uses **that value**.
   State plainly that §P9's *config read* — the `enabledPlugins["dev@<mp>"]` →
   `extraKnownMarketplaces[<mp>].source.repo` lookup — is **not** performed here: it is a different
   lookup from step 1's registry trace, and re-running it would shadow step 1's derivation, which this
   cycle does not touch. Add no `enabledPlugins` or `extraKnownMarketplaces` reference anywhere in
   `reflect/SKILL.md` (Success Criterion 2 is verified by their absence).
5. Write the **ask route**: when step 1 fell through to asking the user where the plugin source repo
   lives, no slug exists yet. Derive one by running `git remote get-url origin` **in the checkout the
   user named** (not the cwd), then normalize and validate it per the shared sentence from the
   `Shared procedure:` note above. Then **echo the normalized `owner/name` back to the user and ask them
   to confirm it before the PR is created.** Say why the echo exists: a fork's own `origin` is its own
   slug and therefore the correct home, and the confirmation is what makes a wrong answer visible instead
   of silent.
6. Write the §P9 reconciliation note, immediately after the ask route so a reader following the citation
   meets it in place. §P9 says the target is **"never guessed from `origin`"**; that rule governs §P9's
   own subject — resolving a *cross-repo routing delivery target*, where the current repo is by
   definition not the destination, so `origin` is the wrong source. This path is the opposite situation:
   the user has just *named* the destination checkout, and its `origin` is that checkout's own identity,
   not a guess about a foreign repo. State that the ask route borrows only §P9's normalization and
   allowlist, never its no-`origin` resolution rule.
7. Write the shared normalize-and-validate sentence once: the derived value is normalized to `owner/name`
   and must satisfy §P9.target-resolution's allowlist before it reaches `gh`. Link to
   `../../references/tech-debt.md` §P9.target-resolution. Do **not** restate the regex, and do not restate
   the leading-`-` rejection as a rule of this file — name the consequence only (below), and let the
   citation carry the rule.
8. Write the two stop conditions as prose, both ending the step without creating a PR:
   - **The named checkout has no `origin`, or has several remotes and no unambiguous `origin`.** There is
     no slug to derive. Say so, tell the user they can open the PR by hand, and stop — do not guess, and
     do not fall back to a bare `gh pr create`. Note that step 1 already refuses to guess a path for the
     same reason.
   - **The resolved slug fails the §P9 allowlist** — notably any value beginning with `-`, an
     argument-injection vector into `gh --repo`. Per §P9 this is a user error: say so and stop, never pass
     it to `gh`.
9. Confirm by reading the result that step 1, the *"Ask fallback (the common case)"* paragraph at the end
   of the section, steps 3 and 4, and the two-confirmation gate above the section are all unchanged. The
   ask route's derive-echo-confirm belongs to step 2 because it resolves a *PR target*, not because it
   changes how the user is asked — placing it in step 2 is what keeps step 1 and the fallback paragraph
   byte-identical.

---

### Task 2: Step 2 — the `gh pr create` invocation

**What:** Add the actual command block that opens the PR, wrapped so it runs inside the resolved source
checkout and carrying `--repo` and `--head` explicitly.

**Used by:** the maintainer or agent executing step 2 — this block is the executable end of the
procedure. It is the surface Success Criteria 1 and 5 are checked against.

**Depends on:** Task 1 — the block substitutes `<resolved-target-slug>` and `<source-repo-path>`, both of
which Task 1 defines. Writing the block first would leave both undefined.

**Files:** `plugins/dev/skills/reflect/SKILL.md` (modify, same step 2, immediately after Task 1's prose)

**Interfaces:**
- Consumes: `<resolved-target-slug>` (validated `owner/name` string) and `<source-repo-path>`
  (filesystem path of the source checkout), both produced by Task 1, plus the feature branch name created
  by step 2's existing first half.
- Produces: nothing — terminal task. Step 3 (cache/repo parity) and step 4 (tell the user the PR URL)
  already exist and are unmodified; step 4 consumes the PR URL from this command's output exactly as it
  does today.
- Shared procedure: this block is a **mirror** of `plugins/dev/skills/pr/SKILL.md` Step 4's invocation
  pattern in *form only* — the `( cd … && gh pr create … )` wrapper and the explicit `--head`. It is not
  a mirror in content: `pr/SKILL.md` opens the cycle's own PR in the user's project repo and passes
  `--base`/`--head` with no `--repo`; this block opens a plugin skill-edit PR and passes `--repo`/`--head`
  with no `--base`. Restating the shared structure in full: **wrap the invocation in a `( cd "<path>" &&
  … )` subshell because `gh` has no `-C` flag; pass `--head` explicitly so `gh` cannot infer the head from
  whatever branch the shared tree happens to be on.** `pr/SKILL.md` is read for this pattern and must not
  be edited (Success Criterion 7).

**Implementation steps:**

1. Read `plugins/dev/skills/pr/SKILL.md` lines 129–137 for the existing wrapper pattern and the sentence
   explaining it. Match its shape; do not modify that file.
2. State the ordering prerequisite in prose before the block: the branch must already be **pushed** to
   the target repo before `gh pr create` can reference it as `--head`. Step 2's existing first half
   already commits and pushes in that order — say explicitly that the push is a prerequisite of this
   command, not an independent step, so a future edit cannot reorder them silently.
3. Write the command block:
   ```bash
   ( cd "<source-repo-path>" && gh pr create \
       --repo "<resolved-target-slug>" \
       --head "<branch-name>" \
       --title "<one-line summary of the skill change>" \
       --body "<what changed and which /dev cycle surfaced it>" )
   ```
4. Add the one-sentence rationale for the wrapper, mirroring `pr/SKILL.md`'s: `gh` has no `-C` flag, and
   the resolved source checkout is not necessarily the cwd — on the ask route it is wherever the user
   pointed — so the invocation runs inside `<source-repo-path>` with an explicit `--head`.
5. State that `--head` takes the **bare branch name**, not the cross-fork `owner:branch` form. On both
   routes the resolved target is the checkout's own repo, so head repo and base repo coincide; the
   cross-fork syntax would be wrong here.
6. State why `--base` is deliberately **absent**: with `--repo` explicit, `gh` bases the PR on *that
   repo's* default branch, which is already the correct outcome — including for a fork whose default
   branch is not `main`. Pinning `--base` would require querying the target's default branch
   (`gh repo view --json defaultBranchRef`) rather than assuming `main`, buying determinism at the cost of
   an extra API round-trip and a new failure mode. Write this as a short note so a later reader does not
   read the omission as an oversight and "fix" it.
7. Read the finished section start-to-finish once as the fork scenario, checking Success Criterion 6
   traces: a user in `them/plugins`, marketplace registered to `them/plugins` → step 1's dogfood
   comparison matches → step 2's dogfood route carries `them/plugins` → the block runs
   `gh pr create --repo them/plugins` → the PR opens in `them/plugins` and nowhere else. If any hop
   requires knowledge not present in the text, fix the text.

## Edge Cases

| Edge case | Handled in | Approach |
|-----------|-----------|----------|
| Ask fallback with no config slug | Task 1 (step 5) | Derive from the named checkout's `origin`, normalize, validate, echo, confirm. Never fall back to an unqualified `gh pr create`. |
| Named checkout has no `origin`, or several remotes | Task 1 (step 8) | No slug is derivable — say so and stop; the user can open the PR by hand. Never guess. |
| Resolved slug fails the §P9 allowlist (notably leading `-`) | Task 1 (step 8) | A user error per §P9: say so and stop, never pass it to `gh`. |
| Fork whose default branch is not `main` | Task 2 (step 6) | `--base` deliberately omitted; with `--repo` explicit, `gh` bases on that repo's default branch, which is already correct. |
| Checkout under `~/.claude/plugins/cache/` | Task 1 (step 9) | Step 1 already routes this to the ask fallback and is unchanged; the ask route's new derive-echo-confirm applies to it. |
| Head branch not yet on the remote when `gh pr create` runs | Task 2 (step 2) | The push in step 2's existing first half is named as a prerequisite of the command, not an independent step. |

## Out of Scope

- **`plugins/dev/skills/pr/SKILL.md` Step 4** — read for its wrapper pattern, never edited (Success
  Criterion 7).
- **Step 1's discovery logic** and the *"Ask fallback (the common case)"* paragraph — read, never edited.
  Both are correct as written; the defect is entirely downstream.
- **Steps 3 and 4** of the same section, and the two-confirmation gate preceding it — untouched.
- **`plugins/dev/references/tech-debt.md`** — §P9.target-resolution is cited, never modified and never
  copied.
- **The `CLAUDE.md` Component Registry row for `dev:reflect`** — it will need a line about the explicit
  PR target, but `dev:done` Step 4a owns README/`CLAUDE.md` prose reconciliation post-merge. Build must
  not edit it here.
- **`dev:autopilot`'s "When autopilot stops" list** — checked, no ripple. Task 1 adds a confirmation and
  two stop conditions, but the whole skill-edit path sits behind Step 6's gate, which is standard-mode-only
  and requires an explicit "yes"; in autopilot the suggestion is recorded to the backlog instead and this
  path is never reached. No new autopilot stop exists to document.
- **Adding `--repo` anywhere else in the repo** — `grep -rn "gh pr create"` also hits `plan/SKILL.md`;
  out of scope, different surface.
