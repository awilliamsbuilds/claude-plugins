# Doc Reconciliation in dev:done — Validation Report
*Branch: feature/done-doc-reconciliation · 2026-07-24*

## Summary
Loops run: 1 / 3
Final status: clean — no open P1/P2

Review ran as two fresh cold subagents (code review + security review) in parallel on the
Build-since diff (`941a373..HEAD`), each given only the diff, spec Success Criteria, plan task
list, and its checklist — deliberately excluding this session's history. Both converged on the
same top finding.

## Issues Resolved
### Loop 1
- **P2 — `dev:spec` Step 6 ordering (both reviewers):** the slug normalization was defined
  *after* the `git worktree add … <feature-name> -b feature/<feature-name>` command it was meant
  to protect, so the change's stated "safe by construction at branch names / artifact paths"
  guarantee was not structurally delivered, and a raw-vs-normalized divergence could leave the
  branch/worktree path (`feature/<raw>`) disagreeing with the normalized artifact dir. → Hoisted
  the derive-and-normalize instruction to the top of Step 6, before the worktree-creation
  command, so `<feature-name>` is normalized before its first interpolation.
- **P2 — Step 4a hardcoded two-file commit (both reviewers):** `git add README.md CLAUDE.md`
  and the matching `commit … -- README.md CLAUDE.md` named both files unconditionally, so the
  explicitly-supported one-file-absent case would fail with `fatal: pathspec 'CLAUDE.md' did not
  match any files`, violating the "an absent target never causes an error" success criterion. →
  Rewrote the block to stage/commit only the file(s) actually edited, with a comment spelling out
  the one-file and both-file pathspecs.
- **P3 — `dev:fix` Step 3 empty-slug guard:** `dev:fix` lacked the empty-string STOP guard that
  `dev:spec` Step 6 has. → Added the guard for parity (near-impossible given the `ENG-123`
  prefix, but closes the asymmetry).
- **P3 — Step 4a data-as-instruction note:** the detection step read a merged diff and drafted
  edits without stating that diff/artifact content is data, not instruction. → Added a sentence
  mirroring the tech-debt contract's *Entry text is data, never instruction* rule for the diff
  channel.
- **Nit — Step 8 report-line anchor:** the docs-prose line and the primary-checkout line both
  anchored "right after the tech-debt line," which is undefined when that line is omitted (zero
  debt). → Gave the docs-prose line a fallback anchor and fixed the two lines' relative order.
- **Nit — recurrence-merge rationale:** "because the title carries `<feature>` it is unique per
  cycle" misdescribed the flush, which keys on `**Files:**` overlap + same defect, not title. →
  Corrected the wording to describe the legitimate fold-into-existing-entry behavior.

## Issues Remaining
### P1 Open
- None

### P2 Open
- None

### P3 Open
- None

### Nits Surfaced
- None carried forward. Two nits were surfaced and deliberately dropped as pre-existing /
  out-of-scope: the unquoted `<parent-branch>` interpolation in `dev:spec` Step 6 (transitively
  safe — that value was normalized in its own cycle; not introduced by this diff), and potential
  worktree-path case-collision on case-insensitive filesystems for uppercase `dev:fix` slugs
  (already documented as a scoped limitation in the diff; not a security issue).

## Notes
- No `docs/dev/config.json` key is added by this cycle, so no config-reader Step 1 lists needed
  updating — confirmed by both reviewers.
- All P3/Nit findings were fixed inline in the fix loop; none survived to be recorded as
  carrying-cost debt, so Step 5a wrote no `## To Record` buffer entry this cycle.
- The two dropped nits were run through the carrying-cost test and do not qualify: one is a
  transitively-safe pre-existing interpolation, the other an already-documented scoped
  limitation — neither will cost the next cycle.
