# Debt Pending — plan-challenger

Buffered tech debt for this cycle. `dev:done` Step 6a flushes this into `docs/dev/tech-debt.md`
and Step 7 deletes it. Nothing else reads it.

## To Record

### Plan challenger adds new mode-sensitive state counters to the sweep surface
**What's wrong:** This cycle adds a cold-review challenger to `dev:plan` with its own
`state.json` counters, following the same shape as `dev:spec`'s `challenge.*`. That makes
plan-challenger the next cycle to hand-add mode-sensitive counters that must be written
identically in standard and autopilot to avoid the recurring "gate-path write dead in autopilot,
read unqualified by `dev:reflect`" defect. This cycle guards its own new counters by design, but
does **not** run the exhaustive nine-skill audit — it expands the surface that audit must cover
and is a further data point that hand-vigilance per counter is not holding, which is the argument
for the deferred preventive mechanism (`dev:plan`'s Interfaces block naming, per state key, which
mode writes it).
**Why deferred:** The full audit is its own scoped cycle by explicit scope decision; this cycle
stays bounded to adding the plan challenger.
**Done looks like:** Every `state.json` key written by a `dev:*` skill — now including the
plan-challenger counters this cycle adds — is traced to the mode(s) that write it, and gate-only
writes are moved pre-gate or duplicated into the autopilot path.
**Files:** plugins/dev/skills/plan/SKILL.md, plugins/dev/skills/spec/SKILL.md, plugins/dev/skills/reflect/SKILL.md, plugins/dev/skills/autopilot/SKILL.md
*Source: dev:spec · plan-challenger*

## To Close
