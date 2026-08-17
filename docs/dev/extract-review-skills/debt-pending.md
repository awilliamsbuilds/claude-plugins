# Debt Pending — extract-review-skills

Buffer for this cycle's tech-debt writes. Flushed by `dev:done` Step 6a.

## To Record

- **debt-spec-grounding-sweep-file-set-lags-scope**
  `type: debt` · `scope: repo` · `possibly_related_to: debt-spec-grounding-citation-unverified`
  `files:` `plugins/dev/skills/spec/SKILL.md`

  **What's wrong:** `dev:spec` Step 7's grounding inventory records a sweep's *result* but nothing
  re-derives its *input set* when scope later grows. Step 7 runs once, early; Step 12a's revisions then
  add files to the cycle. The recorded count keeps looking authoritative — it was produced by a real
  command — while having been computed over a file set that no longer matches the spec.

  Measured in this cycle, the open-debt `files:` sweep was restated three times and was wrong at every
  step before the last: **6** items, then **8** once Scope 9 added `dev/SKILL.md`, then **12** once
  `spec/SKILL.md` and `plan/SKILL.md` were recognized as edited by item 7, then **17** once
  `references/tech-debt.md` was included. Each correction came from a *cold reviewer re-running the
  sweep*, never from the spec noticing its own input had changed.

  Note the shape, which is the same one `debt-spec-grounding-citation-unverified` records for a
  different reason: neither `spec_revisions` (0) nor `confidence.final_score` (100 / Ready) can see
  this class. Both measure internal coherence, and a spec that consistently reasons over a stale set is
  perfectly coherent with itself. The adjacent instances in this cycle came from the same family of
  incomplete-enumeration errors but different roots — a `grep` pattern narrower than the class it was
  sampling (`validate.*Step 2` missing three behavior citations and two intra-file ones), and a framing
  that hid a member ("code + security" concealing Step 2's third checklist) — so a fix scoped only to
  file sets will not catch those.

  **Why deferred:** This is what the next cycle pays. Three of this cycle's sixteen challenger blockers
  were stale enumerations, and each cost a full cold-review round — roughly one round in three spent
  re-deriving a set the spec had already claimed to have swept. The `files:` sweep specifically gates
  which open debt gets named in Out of Scope, so a stale set silently drops items from a cycle's
  declared surface; here it omitted eleven of seventeen at the first pass. Left alone, every
  multi-revision cycle re-pays this, and the cost scales with how much Step 12a improves the spec —
  the better the challenger works, the staler Step 7's sweeps get.

  Deferred rather than patched because the right form is not obvious and touches two places: Step 7
  needs re-derivation to be *triggered* by scope change rather than performed once, and Step 12a's
  grounding lens currently re-runs the recorded command rather than asking whether its inputs are still
  the right ones. A blanket "re-run every sweep each revision" would be expensive and would still miss
  the pattern-too-narrow variant.

  **Done looks like:** a grounding-inventory entry whose claim depends on a file set records that set,
  and any Scope edit that adds a file to the cycle invalidates the entries computed without it — so a
  count cannot survive the change that falsified it. Step 12a's grounding lens checks the sweep's inputs
  against the spec's final scope, not only that the recorded command reproduces its recorded output.

## To Close

- debt-secure-tree-scoping-unsettled — this cycle makes `dev:validate` call `/dev:secure` from a
  cycle worktree, which is exactly the ambiguity the item records: `dev:secure` audits `$PRIMARY`
  while a cycle runs in `.dev-worktrees/<feature>`. All three clauses of its *Done looks like* are
  met, and the split between them is the point:
  **(a)** the tree rule is now per-verb rather than blanket — the `diff` verb takes an optional
  `<tree>` from the caller (validated, and a failure **stops** rather than falling back), while the
  **whole-project verb keeps `$PRIMARY` as a documented refusal**, which the item's *Why deferred*
  explicitly allows ("a caller-supplied tree, **or a documented refusal**"). A reader who takes (a)
  to mean "every verb takes a tree" would reopen this wrongly.
  **(b)** the whole-project report header names the tree **as an absolute path**
  (`**Tree audited:** <path>`), *replacing* the old ambiguous `**Scope:** <repo slug or path>` field
  rather than sitting beside it; the `diff` header gained the same field, which the clause did not
  demand but item 2 made necessary.
  **(c)** the unactionable "run `/dev:secure diff` from the primary checkout of it" line is gone,
  replaced by one naming the tree argument. Paid, not deferred.
