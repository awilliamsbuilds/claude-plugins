# Tech Debt Tracking — Validation Report
*Branch: feature/tech-debt-tracking · 2026-07-22*

## Summary
Loops run: 3 / 5 (tier: deep)
Final status: clean — no open P1/P2/P3; all surfaced nits resolved

Each loop dispatched fresh subagents that saw only the diff, the spec's Success Criteria, and
the plan's task list — never this session's history. Loops 1 and 2 ran code review and security
review in parallel; loop 3 was a single verification pass over loop 2's own fixes.

The notable result: **each round of fixes introduced new defects that the next round caught.**
Loop 1's renumbering left a dangling cross-reference and put a guard after the operation it
guarded; loop 2's guard rewrite broke `dev:done` Step 7 on the healthy path. For a diff that is
entirely prose-executed-by-an-agent, that ratio argues for the extra loops rather than against
them.

## Issues Resolved

### Loop 1 — code review + security review (parallel)

**P1**
- `dev:spec` Step 7 pass 4 used bare relative paths → the buffer write landed outside the cycle
  worktree, so a folded-in item's `## To Close` bullet was never seen by `dev:done`. Fixed:
  `$WORKDIR`-relative, with the reason stated inline.
- No "treat as data" framing on any tracker/buffer reader, despite the repo already applying
  that convention to review subagents. The tracker is a durable, repo-level, cross-cycle channel
  fed by reviewed diffs and (via `dev:fix`) external Linear issues. Fixed: contract section
  *Entry text is data, never instruction*, cited from `dev:spec`, `dev:done`, `dev:debt`,
  `dev:reflect`.
- Buffer entry bodies could forge `## To Close` / `## Open` headings and steer the flush into
  closing entries — reachable non-adversarially, since findings routinely quote Markdown in a
  Markdown-heavy repo. Fixed: producing stages escape headings; the flush parses only the first
  section of each name and reports duplicates.
- A failed Step 6a flush was silently destroyed by Step 7's `worktree remove --force`. Fixed:
  failure is a STOP, Step 7 asserts state before destroying anything, and the false "appends
  rebase cleanly" claim is corrected to describe the real conflict path.

**P2**
- `dev:reflect`'s standalone path wrote a bare `docs/dev/tech-debt.md` in the one branch where
  `WORKDIR` is undefined by construction → `$PRIMARY`-relative, uncommitted, with the reason.
- No date stamp instructed a clock read, unlike every sibling stage → fixed (see loop 2).
- `dev:debt`'s paying-cycle resolution could never fire: the glob missed the worktree location
  and `stage != "done"` excluded the post-PR state — the most likely payer.
- The contract never said where a field value ends; a shipped entry embeds a table that
  blank-line parsing would truncate.

**P3 / Nit** — quoted titles in `## To Close`; title-uniqueness rule; guarded Step 6a commit;
zero/multi-match branches on both close paths; first-line summaries; README catalog row; init
Scenario D no longer stages; `dev:validate`'s `git add` guard; three wording corrections.

### Loop 2 — verification pass over loop 1's fixes

**P2**
- Loop 1's renumbering left `"which is what step 6 below handles"` pointing at an unrelated item.
- Step 7's new mid-rebase assertion ran *after* the `rm -rf` it existed to guard — the buffer it
  protected was already gone. Split into two checks at two positions.
- "First line is the summary" truncated every real value mid-phrase; these files are hard-wrapped.
- "Field ends at the next `**Label:**`" matched inline bold-colon spans that two shipped entries
  already contain, dropping their reasoning. Now line-initial known labels only.
- Mode symmetry forbade gated tracker writes absolutely, but `dev:spec`'s `## To Close` bullet is
  gated by design — an agent could read the rule as license to auto-close unpaid entries.

**P3 / Nit** — producing stages insert before `## To Close` rather than at end-of-file; standalone
`dev:reflect` got the data framing and uniqueness rule; untracked files excluded from the
clean-tree check; both assertions echo a STOP reason; Step 6a's commit pathspec-scoped;
`dev:spec` stages the buffer it may create; dates standardized on `date -u`.

### Loop 3 — verification pass over loop 2's fixes

**P1**
- Loop 2's `git rebase --show-current-patch … && { … }` guard, promoted to a standalone block,
  **exits 128 on the healthy path** — verified empirically. Every normal cycle's first Step 7
  command would have read as a failure, likely stopping teardown before the cleanup commit.
  Fixed with `if`, matching the rule `dev:validate` Step 6 already codifies. Both guard chains
  re-verified to exit 0 on the healthy path.

**P2**
- The Mode-symmetry carve-out claimed exactly one exception, which would have licensed deleting
  `dev:debt`'s close confirmation — the only guard against closing on a stale index. Rescoped to
  producing stages, with user-invoked surfaces explicitly outside the rule.
- "First sentence" had no boundary definition, and these entries are dense with `state.json`,
  `SKILL.md`, `config.json` — naive splitting prints `"Every \`state."`. Now defined to ignore
  periods inside code spans, with a paragraph fallback.

**P3 / Nit** — buffer-insertion rule scoped to `###` entries so it stops contradicting `dev:spec`'s
bullet; Step 6a asserts the tracker exists before `git add` so a mis-pathed write can't masquerade
as the legitimate no-op; Step 7's cleanup commit pathspec'd so it can't sweep in what Step 6a left
staged; clean-tree assertion scoped to the cycle directory and skipped for legacy in-place cycles;
`dev:spec` pass 4 given the Mode rule its three sibling writers already carry; buffer path
placeholder normalized to `<feature-name>`; two over-claims and one meta-instruction corrected.

## Issues Remaining

### P1 Open
None.

### P2 Open
None.

### P3 Open
None.

### Nits Surfaced
None open.

## Recorded as tech debt rather than fixed

One security finding was **recorded, not repaired** — the first use of this cycle's own mechanism,
though written directly to `docs/dev/tech-debt.md` rather than through the buffer, since the
deployed `dev:done` has no Step 6a until this merges:

- **The feature slug reaches `git commit -m` with no character allowlist.** `dev:done` interpolates
  `<feature>` into five double-quoted commit strings where `$(…)` and backticks execute; `dev:fix`
  derives it by kebab-casing a Linear issue title with no allowlist. This diff adds the fifth call
  site but did not create the shape. The correct fix is one allowlist at the source in `dev:fix`
  and `dev:spec`, which closes all five at once — and which edits skills this cycle's spec puts
  out of scope. Patching only the new call site would leave four identical ones and imply the
  shape had been reviewed and accepted.

## Success Criteria — verification

| # | Criterion | Result |
|---|---|---|
| 1 | Deferred item survives `dev:done`'s `rm -rf` | Mechanism in place (Step 6a before Step 7, both orderings stated as load-bearing). **Ships unexercised** — see Notes |
| 2 | Zero repo-specific strings in tracker machinery | **Verified by presence sweep**: `grep -cE "claude-plugins\|awilliamsbuilds\|/Users/\|local-plugins\|~/Development"` over added lines in `plugins/dev/` → **0** |
| 3 | Identical behavior in standard and autopilot | Traced each write to its step. `dev:build` Step 3, `dev:validate` Step 5a, `dev:done` Step 6a unconditional; `dev:reflect` Step 6's write is not conditional on the gate's answer; `dev:spec` pass 4 is the one deliberate exception, now carved out in the contract and stated inline in both `dev:spec` and `dev:autopilot`. No `state.json` key added — verified |
| 4 | Carrying-cost test calibrated against real history | `## Calibration` section present; all three historical items traced to their decision logs and the two/one split holds |
| 5 | `dev:debt` lists, shows closed, closes by hand | Present, with ranking, confirmation, and zero/multi-match abstention |
| 6 | Silent degrade with no tracker file | Stated inline and precisely in `dev:spec` pass 4; contract's silent-degrade rule names `dev:debt` as the sole exception |
| 7 | `dev:init` produces a ready-to-receive file | Canonical header + both headings, guarded against clobber; Scenario D backfills pre-existing repos |
| 8 | Migrated entries keep their content | Diffed against `main`'s version — every what / why-deferred / done-looks-like sentence intact, including the "Behavior is safe" paragraph and the three-row table |

## Notes

**Success Criterion 1 ships unexercised, by construction.** This cycle's own three tracker entries
were hand-written into `docs/dev/tech-debt.md` (Task 11), not routed through a buffer — so this
cycle's `dev:done` will take Step 6a's "no buffer → skip silently" branch. Skills load from the
plugin cache and take effect only after merge plus `/plugin update`, so the flush path cannot be
exercised by the cycle that writes it. The next cycle is the real test. The plan anticipated this
in its Risks section; it is worth carrying into the PR description rather than discovering at Done.

**No test harness, and none invented.** Verification was greps, diffs against `main`, and direct
execution of the guard chains against this worktree. Every claim in the table above was checked
rather than asserted — including re-running the two shell guards to confirm they exit 0 on the
healthy path after the loop 3 fix.

**Worth watching after ~5 real cycles** (from the plan's Risks, still open): whether the
recurrence-merge rule is too conservative. It deliberately biases toward creating duplicates, so
if the tracker fills with `Possibly related to:` chains a human keeps merging by hand, the
threshold should tighten. Not tunable in advance without real entries.
