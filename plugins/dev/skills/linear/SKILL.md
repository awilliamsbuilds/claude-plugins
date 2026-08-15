---
name: linear
description: "Linear-aware entry point into the full seven-stage /dev workflow. Takes a Linear issue ID (e.g., /dev:linear ENG-123) or lists open issues to pick from. Pre-fills spec dimensions from the issue, starts confidence meter higher, names branch from issue ID. Continues into normal /dev spec flow. For a fast, artifact-free change use /dev:fix instead."
---

# dev:linear — Linear Issue Entry Point

**Announce:** "I'm using dev:linear to start a /dev cycle from a Linear issue."

## Purpose

Enter the /dev workflow from a Linear issue. Pre-fill as much of the spec as the issue provides, start the confidence meter higher, and name the branch from the issue ID.

## Step 1: Get the Issue

**If an issue ID was provided as argument (e.g., `ENG-123`):**

Fetch via Linear MCP:
```
mcp__linear-server__get_issue({ id: "ENG-123" })
```

Extract:
- `title` → feature name and spec Intent
- `description` → Intent, Scope, Happy Path (parse what's there)
- `priority` → tier hint (Urgent/High → at least Standard; Low → Micro candidate)
- `labels` → cycle type hint (bug → feature cycle; "architecture", "decision" → architecture cycle)
- Acceptance criteria (if present in description) → Success Criteria

**If no argument provided:**

Fetch open issues assigned to the current user:
```
mcp__linear-server__list_issues({ assignee: "me", state: "Todo" })
```

Display the list and ask: "Which issue are you working on?"

Wait for selection, then fetch that issue.

## Step 2: Map Issue to Spec Dimensions

Attempt to map issue content onto confidence dimensions. Mark each as true or false:

| Dimension | From Issue |
|-----------|-----------|
| Intent | title + description opening → usually 20% filled |
| Scope | description scope section if present |
| Success criteria | acceptance criteria in description |
| Happy path | description steps if present |
| Edge cases | rarely in issues; default false |
| Out of scope | rarely explicit; default false |
| UI needed | infer from labels/title ("UI", "frontend", "button", "screen") |
| Technical constraints | sometimes in description |
| Audience | rarely in issues; inherit from CLAUDE.md if available |
| Dependencies | "blocks" / "blocked by" links in issue |

Pre-fill the confidence score from mapped dimensions. Show the pre-populated state:

```
Starting /dev from Linear issue ENG-123: "[Issue Title]"

Pre-filled from issue:
  ✓ Intent: [extracted sentence]
  ✓ Success criteria: [extracted criteria]
  ? Scope: [extracted or "needs clarification"]
  ✗ Edge cases, Out of scope, Technical constraints: not in issue

Starting confidence: 45% — Sufficient

I'll ask only about the missing dimensions before writing the spec.
```

## Step 3: Set Branch Name

Branch naming for fix cycles: `fix/ENG-123-short-title`

Where `short-title` is kebab-case derived from the issue title (2-4 words, strip articles/prepositions).

Example: issue "ENG-123: Fix broken logout button on mobile" → `fix/ENG-123-fix-logout-button`

**Normalize the cycle slug to a character allowlist by construction.** The `short-title` portion is kebab-cased and lowercased as today; the full cycle slug `ENG-123-<short-title>` is then normalized to match `^[A-Za-z0-9][A-Za-z0-9-]*$` — collapse every run of characters outside `[A-Za-z0-9-]` to a single `-` and strip any leading/trailing `-`. If normalization yields an empty string, STOP and ask for a valid slug rather than proceeding — in practice the alphanumeric `ENG-123` prefix makes this near-impossible, but the guard keeps parity with `dev:spec` Step 6. Uppercase is permitted **only** so the Linear issue-ID prefix (e.g. `ENG-123`) survives; the `short-title` itself stays strict-lowercase. This is injection-safe — no shell metacharacter can reach any downstream `<feature>` interpolation. The uppercase tolerance is scoped to `dev:linear`; `dev:spec` (Step 6) stays strict-lowercase `^[a-z0-9][a-z0-9-]*$`.

**Note — bare-slug argument matchers stay lowercase-only.** `dev:done` and `dev:plan` accept a bare positional feature slug only when it matches `^[a-z0-9][a-z0-9-]*$`, and those matchers are intentionally left unchanged this cycle. Resolving an uppercase `dev:linear` slug (e.g. `ENG-123-fix-logout-button`) as a *bare* argument to those skills is a pre-existing lowercase-only limitation, out of scope here — the slug still resolves fine via its PR-URL and artifact-path forms.

```bash
GIT_COMMON=$(git rev-parse --git-common-dir) || { echo "Not a git repository."; exit 1; }
PRIMARY=$(cd "$(dirname "$GIT_COMMON")" && pwd)
git -C "$PRIMARY" fetch origin
git -C "$PRIMARY" worktree add "$PRIMARY/.dev-worktrees/ENG-123-<short-title>" -b fix/ENG-123-<short-title> origin/main
# WORKDIR="$PRIMARY/.dev-worktrees/ENG-123-<short-title>" for the rest of the cycle
```

This mirrors `dev:spec` Step 6 — the cycle is isolated in its own worktree from the start; `worktreePath` is recorded when spec initializes state.json. No shared-tree fallback.

## Step 4: Store Linear Issue Reference

In state.json, set:
```json
"linear_issue": {
  "id": "ENG-123",
  "title": "[Issue Title]",
  "url": "[Issue URL]"
}
```

## Step 5: Continue Into /dev:spec

Initialize state.json with the pre-filled confidence dimensions from Step 2. Set `stage` to `"spec"`.

Continue with dev:spec from **Step 7: Ground the Spec in the Codebase**, then **Step 8: Guided Questioning** — but start from the pre-filled state. Grounding still runs: a fix operates on existing code, so verifying the issue's as-is claims against the codebase is load-bearing, not optional. Show only unscored dimensions as questions. Show the confidence meter from the start (pre-filled score).

When spec is complete, the rest of the /dev flow continues normally (shape if UI, plan, build, validate, PR, done).
