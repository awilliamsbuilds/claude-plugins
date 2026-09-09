---
type: backlog
scope: repo
status: open
first_recorded: 2026-09-09
cycles: [dev-process-hardening-closeout]
recurrence: 1
files:
  - plugins/dev/skills/spec/SKILL.md
---

**What:** After `dev:spec` Step 6 creates a cycle worktree, seed the repo's ignored dependency
directories from the primary checkout with a copy-on-write clone (`cp -c -R` on APFS,
`cp --reflink=auto` on a Linux filesystem that supports it), instead of leaving the new worktree to a
full dependency reinstall.

**Why:** A fresh worktree does not inherit ignored files. Three of the five repos running `/dev`
carry a `node_modules` (186M / 571M / 584M), so each cycle in them pays a reinstall today.

Measured on this machine 2026-09-05: cloning 584 MB / 31,976 files took **5.1 seconds and 9 MB** of
real disk, copy-on-write. That measurement is what declined Milestone 4b of
`dev-process-hardening` — seeding captures 4b's entire surviving benefit for **every** cycle,
plan-governed or not, from one place in `dev:spec` Step 6 rather than a coordinated edit across ten
resolution blocks.

**Done looks like:** Step 6 seeds the worktree's ignored dependency directories when the filesystem
supports reflink cloning, and **skips seeding entirely otherwise** — never falling back to a real
copy, which would be the 584 MB this avoids. Two correctness points to settle when building it: the
seed must be gated on the branch's lockfile matching the primary checkout's, or followed by the
normal install to reconcile; and a package with absolute paths baked into a native build may need a
documented "delete it and reinstall" escape hatch.
