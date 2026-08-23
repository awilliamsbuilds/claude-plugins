---
type: debt
scope: repo
status: open
severity: P2
first_recorded: 2026-08-15
cycles: [fast-path]
recurrence: 1
files:
  - plugins/dev/references/tech-debt.md
  - plugins/dev/skills/reflect/SKILL.md
---

**What's wrong:** §P9.target-resolution's slug allowlist was
`^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$`, while both §P9 and `dev:reflect` Step 6's stop conditions
described it as rejecting any value beginning with `-` — "an argument-injection vector into the
`gh --repo` invocation." It did not: `-` sat inside the character class, so `-foo/bar` and
`--repo/x` both passed. Verified empirically. The stated security property was not the delivered
one. **Fixed by `retro-inside-pr`**, which made the anchored form canonical in §P9; this item is
buffered for closure in that cycle.

**Why deferred:** §P9 is the shared cross-repo routing contract, read by `dev:debt` (`add`/`list`/
`inbox`), `dev:done`'s flush, and `dev:reflect`. Tightening the regex there changes validation
behavior for all of them, which is a scope decision rather than an edit — and `fast-path`'s Success
Criterion 6 forbade that cycle touching those skills beyond the rename and the duplication pointers.
`dev:fix` protected itself by anchoring the first character
(`^[A-Za-z0-9._][A-Za-z0-9._-]*/[A-Za-z0-9._][A-Za-z0-9._-]*$`) and saying why, so the new site was
never exposed while the shared claim stood wrong.

**Done looks like:** §P9's regex anchors its first character in both segments, or its prose stops
claiming a property it does not deliver. `dev:reflect` Step 6's stop conditions carry the matching
claim, corrected in the same pass, and `dev:fix` drops its local divergence note in favour of citing
§P9 plainly. **All three landed in `retro-inside-pr`.**
