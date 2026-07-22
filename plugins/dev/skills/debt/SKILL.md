---
name: dev:debt
description: "View and manage the /dev tech debt tracker. Use when the user wants to see tech debt, view tech debt, list tech debt, check what debt we have, show deferred items, review known issues, see what was deferred, close a debt item, mark debt paid, mark debt as done, or asks 'what tech debt do we have', 'what did we defer', 'what's in the tech debt tracker'. Reads docs/dev/tech-debt.md."
---

# dev:debt — Tech Debt Tracker

**Announce:** "I'm using dev:debt to read the tech debt tracker."

## Purpose

The on-demand surface for `docs/dev/tech-debt.md`. This skill owns **all reads** and **all
manual lifecycle changes** — listing open entries, showing closed ones, and closing an entry by
hand.

It does not own the rest of the lifecycle. `dev:done` Step 6a owns **automatic** closing, and
the producing stages (`dev:build`, `dev:validate`, `dev:reflect`) only ever append to their
cycle's buffer. Nothing here writes a buffer.

Manual closing exists for one specific case: a later cycle fixes a debt item incidentally,
without folding it into scope, so nothing closes it automatically. That entry stays open until
someone closes it here.

The tracker format and the recurrence ranking are defined in `../../references/tech-debt.md`.

## Step 1: Locate the Tracker

Never rely on the shell's current directory. Compute the primary checkout, then read the
tracker from it:

    PRIMARY=$(dirname "$(git rev-parse --git-common-dir)")

The tracker is `$PRIMARY/docs/dev/tech-debt.md`. Do not `cd`.

**If the file is absent, or exists with an empty `## Open` and `## Closed`:** say so plainly —

```
No tech debt tracked in this repo yet.
```

— and stop. This is the one place the silent-degrade rule in the contract does **not** apply:
the user asked the question directly and deserves an answer, not silence.

## Step 2: Dispatch on the Argument

| Invocation | Behavior |
|---|---|
| `/dev:debt` or `/dev:debt list` | Step 3 — list open entries |
| `/dev:debt show <n>` | Step 4 — full detail for one entry |
| `/dev:debt closed` | Step 5 — list closed entries |
| `/dev:debt close <n\|title>` | Step 6 — close an entry |

## Step 3: List Open Entries

Parse `## Open` and rank by **the recurrence ranking** from the contract: `Recurrence:`
descending, ties broken by the most recent name in `Cycles:`.

Print one block per entry — index, title, recurrence, cycles, files, and the one-line
`**Done looks like:**`:

```
Open tech debt — N items (ranked by recurrence):

1. <Title>
   Recurrence: 3 · Cycles: alpha, beta, gamma
   Files: path/one.md, path/two.md
   Done looks like: <the one-line done-looks-like>

2. <Title>
   ...

Full detail: /dev:debt show <n>   ·   Close one: /dev:debt close <n>
```

**Do not dump `**What's wrong:**` in full here** — that's what `show` is for. The list is meant
to be scannable when deciding what to fold into an upcoming cycle.

If `## Open` is empty but `## Closed` has entries, say "No open tech debt. N closed items —
`/dev:debt closed`."

## Step 4: Show One Entry

Print the entry verbatim — title, meta line, and every field including the full
`**What's wrong:**` and any `**Possibly related to:**` cross-reference. Indices are the
positions from Step 3's ranked list.

## Step 5: List Closed Entries

Parse `## Closed` and print newest-first by close date, each showing the paying cycle:

```
Closed tech debt — N items:

1. <Title>
   Closed 2026-07-22 by cycle <name> · First recorded: 2026-07-14 · Recurrence: 2
   Done looks like: <the one-line done-looks-like>
```

## Step 6: Close an Entry

Accept either a Step 3 index or an entry title.

1. **Resolve the paying cycle.** If a `docs/dev/*/state.json` exists with `stage != "done"`,
   use that cycle's feature name. If several match, or none do, ask which cycle paid it.

2. **Confirm before writing.** Echo the resolved entry title and the paying cycle back to the
   user and wait for confirmation:

   ```
   Close "<exact entry title>" — paid by cycle <name>? (yes/no)
   ```

   A wrong close is the destructive direction: a stale-open entry is recoverable, a wrongly
   closed one silently disappears from every list. Indices are positional and drift as entries
   are added — never close on an index without echoing the title it resolved to.

3. **Write.** Move the entry verbatim from `## Open` to `## Closed` and rewrite its meta line
   to the Closed form from the contract:

   `*Closed YYYY-MM-DD by cycle <name> · First recorded: YYYY-MM-DD · Recurrence: N*`

4. **Do not commit.** Tell the user the file is modified but uncommitted so they can fold it
   into their next commit:

   ```
   Closed "<title>" in docs/dev/tech-debt.md (modified, not committed).
   ```

   This is deliberate. `dev:debt` is invoked outside a cycle, usually with the primary checkout
   sitting on `main`, and the standing convention is never to commit directly to `main`. Do not
   "fix" this by adding a commit.

## Invocation

- `/dev:debt` — list open entries, ranked by recurrence (same as `list`)
- `/dev:debt list` — same as above
- `/dev:debt show <n>` — full detail for one open entry
- `/dev:debt closed` — list closed entries, newest first
- `/dev:debt close <n|title>` — close an entry, naming the cycle that paid it
