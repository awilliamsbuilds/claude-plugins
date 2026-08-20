---
type: debt
scope: plugin
status: open
first_recorded: 2026-08-20
cycles: [autopilot-resume-stage]
recurrence: 1
files: [plugins/dev/skills/validate/SKILL.md]
---

**What's wrong:** `dev:validate` Step 4 classifies each open P3 as **defect-class** (fix inline) or
**polish** (defer to Step 5a). Both branches assume the P3 concerns prose or code already in the
diff. Neither covers a P3 that proposes **new behavior outside the cycle's spec scope** — a reviewer
observation about something the diff merely touches. Such a finding reads as defect-class (it names
a concrete gap), so the loop implements it, and the new behavior gets neither spec review nor plan
review nor a challenger pass.

  Observed here: loop 1's reviewer flagged PR re-entry as a latent gap, explicitly qualifying it
  "latent, not live: no documented producer creates that shape today." The fix loop implemented it
  anyway, got it wrong twice, and consumed two of three loops before reverting to the reviewer's
  original position.

**Why deferred:** Recording it is the honest move — the cycle that discovered the gap is the worst
place to fix it, since the fix is itself a scope decision about a stage skill.

**Done looks like:** Step 4's classification names a third disposition — a finding that proposes
behavior the cycle's spec does not cover is **deferred to Step 5a regardless of how concrete it
is**, with the reviewer's own scope qualification ("latent", "not reachable today") read as the
signal rather than as detail.

**Cost if not paid:** the fix loop stays the one place in the pipeline where new behavior can enter
with no spec, no plan, and no challenger — the three nets the workflow otherwise insists on — and it
enters there under review pressure, which is when judgment is worst.
