# Build Notes — legacy-tracker-migration

## Task 13: untouched-files invariant (Success Criterion 11)

Run at the end of Build, from the cycle worktree:

```bash
git diff --stat main...HEAD -- \
  plugins/dev/references/tech-debt.md \
  plugins/dev/skills/init/SKILL.md \
  plugins/dev/skills/debt/SKILL.md \
  plugins/dev/skills/done/SKILL.md
```

**Result: empty output.** All four protected files end the cycle byte-identical to `main`. (Per the
plan, the *output* is the signal — `git diff --stat` exits 0 either way.)

Full branch surface for cross-checking:

| File | Change |
|---|---|
| `plugins/dev/skills/migrate-tracker/SKILL.md` | new, 562 lines — the deliverable |
| `plugins/dev/skills/start/SKILL.md` | +2 lines (Task 12) |
| `docs/dev/legacy-tracker-migration/*` | cycle artifacts |

## L1–L8 parse-rule verification (Task 4 / Task 5)

The deliverable is prose, so the parse rules were validated by implementing them exactly as written
in § The Legacy Format and running them against the real fixture (`git show
7ebe89a^:docs/dev/tech-debt.md`). Harness was throwaway; results:

```
ENTRY_COUNT=11 (open=4, closed=7)        # matches spec grounding exactly
parsed=11  BUCKET_E=0
disposition holds: True                   # every ### heading → exactly one record
trap mid-line-bold-colon: '**Behavior is safe:**' retained inside What's wrong = True
trap table-in-value: table rows retained = True, blank lines retained = True
L3 closed-with-N>1: [('Sweep for gate-path state writes that', 2, ['state-write-mode-audit'])]
L6 entries missing Files: none
L8 titles unique: True; paren-disambiguated titles: none
```

Both **L5-field-end** truncation traps behave as specified, and the `Recurrence: 2` closed entry with
a one-name cycle list confirms Step 4 **rule A**'s padding rule is load-bearing rather than
defensive.

## Grounded citations

Every line-number citation in the skill was re-read against the real file during Build:

- `debt/SKILL.md:53-55` — the P7 silent-degrade exception (direct question deserves an answer) ✓
- `debt/SKILL.md:217-221` — the synthetic `manual` marker device rule A mirrors ✓
- `debt/SKILL.md:234-241` — local-merge exclusion for off-repo `plugin` items ✓
- `debt/SKILL.md:266-268` — never-commit, and its reason ✓
- `init/SKILL.md:41`, `:42`, `:49-52`, `:77` — Scenario D prompt, both backfill branches, the
  "only automatic path" self-description ✓
- `references/tech-debt.md:142-150` — basename is what `possibly_related_to:` targets ✓
- `references/tech-debt.md:417` — the retirement note for the old parsing machinery ✓
- `ab054df:plugins/dev/references/tech-debt.md:112-113` — "if they disagree, `Cycles:` is
  authoritative" ✓
- `7ebe89a^:docs/dev/tech-debt.md:109`+ — the table-in-value fixture entry; `:110` its
  `Recurrence: 2` meta line ✓

Two claims verified empirically rather than by reading:

- **`PRIMARY` absolute fix.** From the primary checkout the inherited form yields `.`; the new
  `cd … && pwd` form yields `/Users/adam/Development/claude-plugins`. Confirmed from both a primary
  checkout and a linked worktree.
- **P9.target-resolution.** Resolves `dev@local-plugins` →
  `extraKnownMarketplaces['local-plugins'].source.repo` = `awilliamsbuilds/claude-plugins`, which
  equals this repo's `origin` slug — so this repo is correctly the P9.dogfood case.
- **The hand-migration defect rule A prevents is real.** `docs/backlog/closed/debt-gate-path-state-writes.md`
  currently carries `cycles: [state-write-mode-audit]` (one name) against `recurrence: 2`, violating
  P1's `recurrence == len(cycles)` invariant. Not fixed here — out of scope for this cycle, and the
  file is a protected-adjacent artifact of the earlier migration, not this skill's output.
