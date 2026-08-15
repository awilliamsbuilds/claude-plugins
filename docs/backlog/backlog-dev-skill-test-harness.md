---
type: backlog
scope: repo
status: open
first_recorded: 2026-08-12
cycles: [manual, entry-adapters]
recurrence: 2
files: []
---

**What:** A test harness that exercises the `/dev` skills against fixture repos and asserts
behavior, so editing a `SKILL.md` can't silently break a stage.
**Why:** `/dev` is now a dozen interlocking skills plus a shared contract, and the only
verification an edit gets is the cycle that made it. The cross-skill contracts — the
`debt-pending.md` buffer format, `state.json` fields, the P-numbered procedures in
`references/tech-debt.md` — are enforced by prose agreement alone. A stage can drift from the
contract and nothing catches it until a live cycle hits that seam, which is the worst possible
place to find out.
**Done looks like:** Editing a `/dev` skill can be checked by running a harness that exercises
the affected stages against fixture repos and fails on contract drift.

**Recurrence — `entry-adapters` (2026-08-15).** The cost stopped being hypothetical and became a
measurable hole in a cycle's own verification. `entry-adapters` shipped eleven success criteria;
**seven of them — SC1, SC2, SC3, SC4, SC5, SC7, SC9 — could not be executed at all**, because every
one asserts *behavior* (a dispatch routes correctly, a stop fires before a branch is created, a status
is asked once per team then cached, an item ends up in `closed/` after the merge tail) and this repo
has no harness that can run a skill. The four mechanical criteria — SC6, SC8, SC10, SC11 — were real
greps with real output; the other seven were verified by **walking the edited procedure by hand
against the real files** and recording which criterion was checked how.

That is the best available substitute and it is not equivalent: hand-walking is performed by the same
agent that wrote the change, in the same session, which is precisely the reviewer-equals-author
failure the cold-review stages exist to prevent — except here there is no cold-review option, because
there is nothing to run. A cycle can therefore report "build complete, criteria verified" while the
majority of its criteria rest on the author's own reading.

**What this recurrence adds to the case:** the gap is worst exactly where `/dev` is most valuable —
multi-skill seams. `entry-adapters` touched nine skills plus a new shared reference, and its riskiest
behaviors are cross-skill by construction (the lane's branch name carrying an item's identity into a
*separate* `/dev:fix merge` invocation; `dev:spec` writing a `state.json` key that only `dev:pr`
reads). Those are the seams no single file's prose can verify, and they are the ones a fixture-repo
harness would catch first. Four of this cycle's plan-stage blockers were exactly this class of defect,
each found by a human-dispatched cold reviewer rather than by anything automatic.
