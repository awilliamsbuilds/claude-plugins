# Backlog Viewer — Implementation Plan
*Branch: feature/backlog-viewer · 2026-08-13*
*Milestone 1 of `docs/dev/product-plans/dev-observability.md`*

## Files

| File | Action | Purpose |
|------|--------|---------|
| `plugins/dev/skills/debt/viewer.py` | Create | The whole runtime: front-matter parser, store loader, facet derivation, page render, HTTP server, CLI (`serve` / `start` / `stop`) |
| `plugins/dev/skills/debt/viewer_page.html` | Create | Page template — shell markup, inline `<style>`, inline `<script>`, one `__STORE_JSON__` placeholder |
| `plugins/dev/skills/debt/test_viewer.py` | Create | `unittest` suite (stdlib). Real-corpus regression net + synthetic rule coverage |
| `plugins/dev/skills/debt/SKILL.md` | Modify | `view` / `view stop` verbs: description triggers, Step 1 exemption, Step 2 dispatch, new Step 9, Invocation list |

Run tests with `python3 -m unittest discover -s plugins/dev/skills/debt -p 'test_*.py'` from `$WORKDIR`.

**No task introduces a `state.json` key.** This cycle adds a `dev:debt` verb, not a workflow stage, so no task carries an `Interfaces:` `State keys:` line. That omission is deliberate, not missing.

**Python floor is 3.9.6** (macOS system Python, verified). Stdlib only — no PyYAML, no pip, no build step. Do not use `match`, `X | Y` type unions in annotations, or `dict |` merge; write annotations as comments or `typing` forms if at all.

---

## Tasks

### Task 1: Front-matter parser

What: Parse one item file's text into an ordered field dict plus its body, raising a descriptive error on structural failure rather than dropping data silently.
Used by: Task 2's store loader, once per file.
Depends on: nothing — first task.
Files: create `plugins/dev/skills/debt/viewer.py`, create `plugins/dev/skills/debt/test_viewer.py`
Interfaces:
- Consumes: nothing
- Produces:
  - `class ParseError(Exception)` — message is a human sentence naming the line number
  - `parse_front_matter(text)` → `(fields, body)` where `fields` is a `dict` in file order with values of type `str` / `int` / `list[str]` / `None`, and `body` is the text after the closing delimiter, `\n`-stripped at both ends

This is the risk centre named by spec Technical Constraints. Its failure mode — a silently dropped or mangled field — is exactly what Success Criterion 1 guards against, so every rule below is a loud failure rather than a lenient guess.

Implementation steps:
1. Normalize line endings: `text.replace("\r\n", "\n").replace("\r", "\n")`, then `split("\n")`.
2. If line 0 is not exactly `---` → `ParseError("file does not open with a '---' front-matter delimiter")`.
3. Find the first index `i >= 1` where the line is exactly `---`. If none → `ParseError("front-matter is never closed by a '---' delimiter")`. Front lines are `lines[1:i]`; body is `"\n".join(lines[i+1:]).strip("\n")`.
4. Walk the front lines with an explicit index so list continuations can be consumed. For each line (1-based line numbers in messages count from the start of the file):
   - Blank/whitespace-only → skip.
   - Matches `^([A-Za-z_][A-Za-z0-9_]*):(?:[ \t](.*))?$` → key + remainder (remainder is `""` when the line is bare `key:`). If the key is already in `fields` → `ParseError("duplicate key '<key>' at line N")`. A duplicate is a hand-edit error and last-wins would silently discard data.
   - Matches `^ {2}-(?:[ \t](.*))?$` with no open block-list key → `ParseError("list item at line N has no parent key")`.
   - Anything else → `ParseError("line N is neither a 'key:' entry nor a '  - ' list item: <line verbatim>")`.
5. Value forms, applied to the remainder:
   - `""` (bare `key:`) → look ahead past blank lines: if the next line matches `^ {2}-`, consume every consecutive `^ {2}-(?:[ \t](.*))?$` line as a block list (each entry stripped, surrounding matched `'`/`"` removed, empty entries kept out). Otherwise the value is `None`.
   - `[]` → `[]`.
   - Starts with `[` and ends with `]` → split the inner text on `,`, strip each part, drop empty parts → `list[str]`.
   - Starts with `[` without ending in `]` → `ParseError("unclosed inline list at line N")`. Multi-line flow lists are not in the schema.
   - Otherwise a scalar: strip, remove one layer of matched surrounding `'` or `"`.
6. **Do not strip `#` comments.** Values are preserved verbatim — the contract says the store is the authority and `severity` in particular is "preserved verbatim." A stray comment renders visibly in the field table, which is the correct outcome; stripping it risks eating a legitimate `#`.
7. Coerce `recurrence` to `int` when the scalar is all digits; leave it a string otherwise (a malformed value must stay visible, not become `0`).
8. Tests — real corpus: locate `docs/backlog/` from the test file's own repo (walk up from `__file__` to the directory containing `docs/backlog`, so the test has no hardcoded path), and assert every file matching `debt-*.md` / `backlog-*.md` in the active corpus and in `closed/` parses without `ParseError` and yields a non-empty body. Assert nothing about which keys exist — the viewer reads the store, it does not enforce the contract.
9. Tests — synthetic rules, one case each: inline list `cycles: [a, b]`; empty inline list `files: []`; block list `files:` + two `  - path` lines; bare `key:` with a following `key:` line → `None`; `recurrence: 2` → `int`; quoted scalar; missing opening delimiter → `ParseError`; missing closing delimiter → `ParseError`; duplicate key → `ParseError`; junk line → `ParseError`; `  - ` with no parent → `ParseError`; unclosed `[` → `ParseError`; CRLF input parses identically to LF.

---

### Task 2: PRIMARY resolution and store loader

What: Resolve the primary checkout with a guard, then read the whole store — active corpus and `closed/` archive — into one serializable dict, badging unparseable items instead of dropping them.
Used by: Task 4's renderer (called once per HTTP request by Task 6) and Task 7's CLI.
Depends on: Task 1.
Files: modify `plugins/dev/skills/debt/viewer.py`, modify `plugins/dev/skills/debt/test_viewer.py`
Interfaces:
- Consumes: `parse_front_matter(text)` → `(fields, body)` and `ParseError` from Task 1
- Produces:
  - `class PrimaryError(Exception)`
  - `resolve_primary(cwd=None)` → `str` absolute path of the primary checkout
  - `load_store(primary)` → `dict` with keys `state` (`"ok"` / `"empty"` / `"absent"`), `repo_name` (`str`), `total` (`int`), `items` (`list[dict]`), `facets` (`dict` — populated in Task 3; this task sets it to `{}`)
  - item dict keys, exactly: `id` (`str`, the filename stem, e.g. `debt-p9-issue-body-fence-width`), `archived` (`bool`), `fields` (`dict`), `body` (`str`), `parse_error` (`str` or `None`), `raw` (`str` or `None` — set only when `parse_error` is set), `related` (`None`, or `{"id": str, "resolved": bool, "archived": bool}`), `search` (`str`, lowercased)
- Shared procedure: **PRIMARY resolution — this task is the canonical and only implementation.** Task 8 must not add a second derivation to `SKILL.md`, and Task 7's CLI must not re-derive it. Spec Technical Constraints forbid growing the count of unguarded `PRIMARY=` sites (`debt-primary-cd-failure-unchecked`), so there is exactly one new site and it carries the guard.

Implementation steps:
1. `resolve_primary(cwd=None)`: run `["git", "rev-parse", "--git-common-dir"]` via `subprocess.run(..., cwd=cwd or os.getcwd(), capture_output=True, text=True)`.
   - Non-zero return code → `PrimaryError` whose message includes the command and the captured stderr.
   - Empty or whitespace-only stdout → `PrimaryError("git rev-parse --git-common-dir returned no output")`. **This is the non-empty guard the spec requires.**
   - Otherwise `parent = os.path.dirname(out.strip()) or "."`, then `primary = os.path.abspath(os.path.join(cwd or os.getcwd(), parent))`.
   - `os.path.isdir(primary)` false → `PrimaryError` naming the path.
   - Use `os.path.abspath`, not `realpath`. What matters is that two launches from different cwds produce the **same string** (verified: from the worktree `git rev-parse --git-common-dir` returns the absolute `<primary>/.git`, from the primary it returns `.git` — both reduce to the identical primary path), because that string is the identity key Task 7 matches on.
2. `load_store(primary)`:
   - `store_dir = os.path.join(primary, "docs", "backlog")`. Not a directory → return `{"state": "absent", "repo_name": os.path.basename(primary), "total": 0, "items": [], "facets": {}}`.
   - Active corpus is the P5 glob: `sorted(glob(store_dir/"debt-*.md")) + sorted(glob(store_dir/"backlog-*.md"))`. This excludes `docs/backlog/README.md` by construction — no special case needed.
   - Archive: the same two globs under `store_dir/"closed"` when that directory exists.
   - Both empty → `state` `"empty"`, `items` `[]`, `total` `0`.
   - Otherwise `state` `"ok"`.
3. Per file: read with `open(path, encoding="utf-8", errors="replace")` so an encoding problem cannot raise. `id` is the filename stem. `archived` is True for files under `closed/`.
   - `parse_front_matter` succeeds → `fields`, `body`, `parse_error=None`, `raw=None`.
   - `ParseError` → `fields={}`, `body=""`, `parse_error=str(e)`, `raw=<full file text>`.
   - `OSError` on read → same badged shape, `parse_error` is the OSError message, `raw=None`. One unreadable file must never take the server down.
4. Relationship resolution, after every item is loaded: build `index = {item["id"]: item["archived"]}`. For each item whose `fields.get("possibly_related_to")` is a non-empty string `v`, set `related` by trying, in this order, `v`, then `"debt-" + v`, then `"backlog-" + v` — first hit wins, giving `{"id": <matched id>, "resolved": True, "archived": index[<matched id>]}`. No hit → `{"id": v, "resolved": False, "archived": False}`. Both forms are supported because the contract says the field points at the slug while all four live values carry the full `<type>-<slug>` stem.
5. `search` blob per item: lowercase of `id` + every field **value** joined by spaces (lists joined by space, ints stringified, `None` → nothing) + `body` + `parse_error` + `raw` when present. **Field names are excluded** — including them would make every item match the word "severity". Including `files` values is what makes typing `plan/SKILL.md` find every item touching it (spec Scope), and including `raw` is what keeps a malformed item findable (spec Edge Cases).
6. **Do not put `primary` in the returned dict.** It reaches the served page otherwise, needlessly writing an absolute home-directory path into the HTML. The page identifies the repo by `repo_name` only.
7. Tests: real corpus — `len(store["items"])` equals the number of files the two globs match across active and `closed/` (a property, not the literal 30, so the suite survives the store growing); every item has a non-empty `id`; the four items carrying `possibly_related_to` resolve, and the three pointing into `closed/` come back `archived: True`; searching `plugins/dev/skills/plan/SKILL.md` matches at least one item via its `files` values.
8. Tests: synthetic — a `tempfile.TemporaryDirectory()` store built from string literals covering absent store, empty store (directory present, no item files), a lone `README.md` (still `"empty"`), a malformed item (badged, `raw` populated, still counted), an item whose `possibly_related_to` names nothing (`resolved: False`), an item read from `closed/` (`archived: True`), and an item with `files: []` (present in `items`, findable by `search` on its slug).
9. Tests: `resolve_primary` — from the repo returns an existing directory; called with `cwd` set to a non-repo temp directory raises `PrimaryError`.

---

### Task 3: Facet derivation and ordering

What: Derive the filter rail's options and counts from the values actually present on disk, ordered by a per-field display rank that never decides membership.
Used by: Task 4 embeds the result in the page; Task 5's JS renders it as checkboxes.
Depends on: Task 2.
Files: modify `plugins/dev/skills/debt/viewer.py`, modify `plugins/dev/skills/debt/test_viewer.py`
Interfaces:
- Consumes: the `items` list produced by `load_store(primary)` in Task 2 — each item a dict with an `id`, a `fields` dict, and `archived` / `parse_error` keys
- Produces:
  - `FACET_FIELDS = ("type", "status", "scope", "severity")`
  - `FACET_RANK = {"status": ["open", "in-progress", "promoted", "closed"], "severity": ["P1", "P2", "P3", "Nit"]}`
  - `derive_facets(items)` → `{field: [{"value": str_or_None, "label": str, "count": int}, ...]}` for each of the four fields, and `load_store` now sets `store["facets"] = derive_facets(items)`

The rank lists are the one hardcoded list this design admits, and their scope is load-bearing: **rank orders values, it never gates membership.** Sources — `status` order is the lifecycle table at `plugins/dev/references/tech-debt.md:159–162` (`open` / `in-progress` / `promoted` / `closed`, verified); `severity` order is the ladder at `plugins/dev/skills/validate/SKILL.md:108–111` (`P1` / `P2` / `P3` / `Nit`, verified). `type` and `scope` have no inherent sequence and sort alphabetically. `severity`'s list deliberately extends past the contract's stated `P3 | Nit`, because `debt-p9-issue-body-fence-width` carries `P2` today.

Implementation steps:
1. For each field in `FACET_FIELDS`, tally across **all** items — active and archived together. An item's value is `item["fields"].get(field)`; `None`, a non-string, or an empty/whitespace string all fall into the missing bucket.
2. Badged items (`parse_error` set) have `fields == {}` and therefore land in every field's missing bucket. That is correct: they stay visible and stay filterable.
3. Order each field's list: values present in that field's rank list, in rank order → every other present value, alphabetically → the missing bucket last.
4. The missing bucket is `{"value": None, "label": "none", "count": n}`, emitted only when `n > 0`. `None` is the sentinel rather than the string `"none"` so an item literally carrying `severity: none` stays distinguishable.
5. A ranked value with zero live items emits **no entry at all** — `P1` and `in-progress` appear the moment one item carries them, and not before.
6. Never use `FACET_RANK` as a validity check or a filter. A value absent from the rank list is ordered after the ranked ones, never dropped.
7. Tests: on the real corpus, `severity` yields `P2` before `P3` before `Nit` then `none`, and `status` yields `open`, `promoted`, `closed` in that order with no `in-progress` entry; counts sum to `len(items)` for every field.
8. Tests: on a synthetic corpus (temp dir, string literals) containing `scope: plugin`, `status: in-progress`, and an out-of-contract `severity: P7` — the `plugin` and `in-progress` facets appear, `in-progress` sorts between `open` and `promoted`, and `P7` sorts after `Nit` but before `none`. This is the Success Criterion 2 fixture at the unit level.

---

### Task 4: Page template, render, and safe data embedding

What: Turn a store dict into one self-contained HTML document by substituting a JSON literal into a sibling template that carries the shell markup, the layout CSS, and the empty states.
Used by: Task 6's `do_GET`, once per request.
Depends on: Task 3.
Files: create `plugins/dev/skills/debt/viewer_page.html`, modify `plugins/dev/skills/debt/viewer.py`, modify `plugins/dev/skills/debt/test_viewer.py`
Interfaces:
- Consumes: the store dict from `load_store(primary)` — keys `state`, `repo_name`, `total`, `items`, `facets` — with `facets` shaped as `{field: [{"value", "label", "count"}, ...]}` from Task 3
- Produces:
  - `TEMPLATE_PATH = pathlib.Path(__file__).with_name("viewer_page.html")`
  - `embed_json(obj)` → `str`, a `<script>`-safe JSON literal
  - `render_page(store)` → `str`, the complete document
  - the DOM contract Task 5 binds to: element ids `#count`, `#sort`, `#search`, `#rail`, `#clear`, `#list`, `#detail`, `#empty`, and the CSS classes `.chip`, `.row`, `.row.selected`, `.row.linked`, `.badge-parse-error`

The template is a source file read at render time; the **served** document still fetches nothing, so design's "no external assets" holds.

Implementation steps:
1. `embed_json(obj)`: `json.dumps(obj, ensure_ascii=False, separators=(",", ":"))`, then replace `<` → `<`, `>` → `>`, `&` → `&`, U+2028 → ` `, U+2029 → ` `. The first three make `</script>` and `<!--` inert inside the script block; the last two are JS line terminators that would otherwise break the literal. **Store text can originate outside this repo** — `dev:fix` seeds items from Linear and §P9 delivers items as GitHub issues — so this is a real injection boundary, not a formality.
2. `render_page(store)`: read `TEMPLATE_PATH` as UTF-8 and `template.replace("__STORE_JSON__", embed_json(store))`. Missing template → `RuntimeError` naming the expected path.
3. Template `<head>`: `<meta charset="utf-8">`, static `<title>dev backlog</title>` (Task 5 refines it to `dev backlog — <repo-name>` from the embedded data), and the inline `<style>`.
4. Template layout, per the wireframe at 1440 × 900: a 52px header bar holding `dev backlog` + muted repo name, `#count`, `#sort`, `#search`; then a three-column row — `#rail` 226px, `#list` 396px, `#detail` flexible. The list scrolls independently of the detail pane; that independence is the whole reason Option B was chosen, so neither column may scroll the page body. Below ~1000px the detail pane wraps under the list; that narrow case is explicitly not a requirement.
5. Chip CSS: one vocabulary shared by rows and the detail pane — `.chip` plus modifiers for each `type`, `status`, and `severity` value, colour carrying meaning. Unknown values get the neutral `.chip` styling rather than disappearing.
6. `.badge-parse-error` replaces the chip row on a badged item, styled so it cannot be mistaken for a parsed chip.
7. Empty-state markup in `#empty`, copy verbatim from design:
   - filters match nothing → `No items match these filters.` / `Clear a filter, or widen the search.`
   - `state == "empty"` → `No items in docs/backlog/ yet.` / `Capture one with /dev:debt add.`
   - `state == "absent"` → `docs/backlog/ doesn't exist in this repo.` / `Run /dev:init to set up the backlog store.`
8. Static copy in the shell, verbatim from design: search placeholder `Search body, fields, file paths…`, the `Clear all` control, the rail's lowercase field headings `type` · `status` · `scope` · `severity` in that order, and the detail pane's resting state `Select an item to read it.`
9. The `<script>` block ends with `const STORE = __STORE_JSON__;` and nothing else — Task 5 fills in the behavior below it.
10. Tests: `render_page` on a store whose body text contains the literal `</script>`, `<!--`, and `&` produces a document containing none of those sequences inside the script literal; the string `__STORE_JSON__` does not survive into the output; `json.loads` of the extracted literal round-trips the store; the key `primary` appears nowhere in the output; a store with `state == "absent"` still renders a complete document.

---

### Task 5: Client behavior — filter, sort, search, detail, relationship traversal

What: Make the rendered page interactive against its embedded data — facet checkboxes, two sorts, free-text search, detail rendering, and relationship links that jump across the active/closed boundary.
Used by: the operator in the browser; nothing in Python calls it.
Depends on: Task 4.
Files: modify `plugins/dev/skills/debt/viewer_page.html`
Interfaces:
- Consumes: `const STORE` in the page — `{state, repo_name, total, items, facets}`, where each item has `id`, `archived`, `fields`, `body`, `parse_error`, `raw`, `related` (`null` or `{id, resolved, archived}`), `search`; and each facet entry has `value` (`string` or `null`), `label`, `count`. Also the ids and classes from Task 4: `#count`, `#sort`, `#search`, `#rail`, `#clear`, `#list`, `#detail`, `#empty`, `.chip`, `.row`, `.row.selected`, `.row.linked`, `.badge-parse-error`
- Produces: nothing — terminal task for the page layer

**TDD deviation, stated deliberately:** this is browser JS with no test runner in a repo that has no build tooling, so `unittest` cannot exercise it. Verification is Task 9's manual pass against the real store, which is the same standard the Shape prototype was held to. Task 4's tests already cover everything that crosses the Python/JS boundary.

Implementation steps:
1. On load: set `document.title` and the header's repo label from `STORE.repo_name`; render the rail from `STORE.facets`; render the list; select nothing.
2. Rail: one checkbox group per field in `STORE.facets`, in the order the object gives them (`type`, `status`, `scope`, `severity`), each option labelled `<label>` with its count right-aligned. Counts are the unfiltered totals Task 3 computed and do not change as filters are applied — the header's `<n> of <total>` is what reflects the active filter.
3. Filter semantics: within a field, checked values OR together; across fields, they AND. A checked option whose `value` is `null` matches items missing that field. Nothing is checked on load — all items render, per design's explicit rejection of a default `status: open` filter.
4. Sort: a `<select>` with `sort: first_recorded` and `sort: recurrence`. **Default is `first_recorded`, oldest first** — design's UX Decisions says recurrence "barely discriminates today" (27 of 30 items are `1`) and "should not present it as the obvious default answer", and names `first_recorded` the axis that works across the whole corpus. The wireframe's `[sort: recurrence ▾]` is a static sketch; the prose governs. Tie-break both sorts by `id` ascending so ordering is stable. `recurrence` sorts descending, coercing a missing or non-numeric value to `0`; items missing `first_recorded` sort last.
5. Search: case-insensitive substring of the trimmed query against `item.search`, applied on top of the facet filter. Empty query matches everything.
6. Header count renders `<n> of <total>` always — both numbers, so an active filter is never invisible.
7. Row: the slug, then a chip line (`type` · `status` · `severity`, each chip omitted when the value is missing) with `first_recorded` right-aligned. A badged item shows `PARSE ERROR` in place of the chip line. No file count on the row — the detail pane lists actual paths, which is the only form of that fact worth having.
8. Detail pane on selection: header with the item id and its chips; meta line `recorded <date> · seen <n>× · <cycles>` (cycles joined by `, `); a field table listing every front-matter key in file order with its value (lists rendered one entry per line); the rendered body; then the relationship link.
9. Body renderer: escape `&`, `<`, `>` **first**, then split on blank lines into paragraphs, then apply `**bold**` → `<strong>` and `` `code` `` → `<code>` within each paragraph, then join as `<p>` elements. Because escaping precedes markup generation, no store text can inject markup. **Every other insertion of store-derived text uses `textContent` or `createElement` — never `innerHTML`.** This is the client half of the boundary Task 4 guards on the server side.
10. Badged item detail: the parse-error copy `This file's front-matter couldn't be parsed, so its fields are unavailable. The raw file is below.` followed by `item.raw` in a `<pre>` set via `textContent`.
11. Relationship link, from `item.related`: resolved → `possibly related to <id>` as a clickable link, with a ` (closed)` suffix when `related.archived`; unresolved → the plain text `possibly related to <id> — not found in store`, not a link. Clicking swaps the detail pane to the target and adds `.row.linked` to its row **without changing the filter, the sort, or the search**. If the target is filtered out of the current list there is no row to highlight — show it in the detail pane anyway and skip the highlight silently.
12. `Clear all` unchecks every facet and clears the search; it does not change the sort or the selection.
13. Empty states: when the filtered set is empty show the "No items match these filters." block; when `STORE.state` is `"empty"` or `"absent"` show that state's block instead and render no rail options.

---

### Task 6: HTTP server, route allowlist, and identity headers

What: Serve the rendered page on loopback for exactly one path, re-reading the store on every request, and advertise the server's identity so launches can find each other.
Used by: Task 7's `serve` subcommand, and Task 7's probe reads the headers it emits.
Depends on: Task 4 (needs `render_page`) and Task 2 (needs `load_store`).
Files: modify `plugins/dev/skills/debt/viewer.py`, modify `plugins/dev/skills/debt/test_viewer.py`
Interfaces:
- Consumes: `load_store(primary)` → store dict and `render_page(store)` → `str` (Tasks 2 and 4)
- Produces:
  - `IDENTITY_HEADER = "X-Dev-Backlog-Viewer"` and `PID_HEADER = "X-Dev-Backlog-Viewer-Pid"`
  - `make_server(primary, port)` → a bound `ThreadingHTTPServer` whose `server_address[1]` is the actual port (so `port=0` yields an ephemeral port for tests)
  - `serve(primary, port)` → runs `serve_forever()`, never returns normally

Implementation steps:
1. `class ViewerHandler(BaseHTTPRequestHandler)` with the primary path carried as a class attribute set by `make_server` via a per-server subclass. Leave `protocol_version` at its `HTTP/1.0` default and always send an accurate `Content-Length` — no keep-alive state to get wrong for a single-document page.
2. Define **only** `do_GET` and `do_HEAD`. Do not define `do_POST`/`do_PUT`/`do_DELETE`; `BaseHTTPRequestHandler` answers those `501 Unsupported method` on its own, which is the behavior we want. There is no write path and no second route.
3. Every response — 200, 403, 404, 500 alike — carries `IDENTITY_HEADER: <primary>`, `PID_HEADER: <os.getpid()>`, `X-Content-Type-Options: nosniff`, and `Cache-Control: no-store`.
4. **Host check before routing.** Take `self.headers.get("Host", "")`, strip a trailing `:<port>`, and accept only `127.0.0.1`, `localhost`, and `[::1]` / `::1`. Anything else → `403` with a short plain-text body. Loopback binding alone does not stop a malicious page from rebinding a hostname to 127.0.0.1 and reading this document same-origin; this closes that. Spec Technical Constraints call serving repo contents over HTTP a security surface, not a default to relax.
5. Routing: `urllib.parse.urlsplit(self.path).path`. Exactly `/` → the page. Everything else → `404` with a short plain-text body. A query string on `/` is ignored, not rejected.
6. `do_GET` on `/`: call `load_store(self.primary)` **fresh on every request**, then `render_page(...)`, and send it as `text/html; charset=utf-8`. This per-request read is the entirety of Success Criterion 3 — a refresh reflects the current files with no skill re-invocation.
7. Wrap the load/render in `try/except Exception` → `500` with the exception message as plain text. The server must stay up; Task 2 already badges per-file failures, so a 500 here means a template or render fault, not a bad item.
8. `do_HEAD` runs the same Host check and routing and sends the same status and headers with no body, so Task 7's probe is cheap and never renders the page.
9. Override `log_message` to a no-op — the detached process writes to `/dev/null` anyway, and stderr noise would be invisible rather than useful.
10. `make_server(primary, port)`: `ThreadingHTTPServer(("127.0.0.1", port), handler_subclass)` with `daemon_threads = True`. Bind `127.0.0.1` explicitly, never `""` or `0.0.0.0` (Success Criterion 5). Leave `allow_reuse_address` at its default so a restart after `stop` is not blocked by `TIME_WAIT`.
11. Tests: run `make_server(primary, 0)` in a daemon thread and, over `urllib.request`, assert — `GET /` → 200, `text/html`, both identity headers present with the correct primary and a live pid; `GET /nope` → 404; `GET /?x=1` → 200; a request with `Host: evil.example.com` → 403; `POST /` → 501; `server_address[0] == "127.0.0.1"`; and that editing a file in a temp store between two `GET /` calls changes the second response (the Success Criterion 3 property, asserted mechanically).

---

### Task 7: CLI — serve, start, stop, probe, detach

What: Give the skill three commands — a foreground `serve`, an idempotent detached `start`, and a `stop` — with a single probe procedure that decides whether a viewer is already up.
Used by: Task 8's `SKILL.md` step invokes `start` and `stop`; Task 9 invokes `serve --primary` against a synthetic store.
Depends on: Task 6.
Files: modify `plugins/dev/skills/debt/viewer.py`, modify `plugins/dev/skills/debt/test_viewer.py`
Interfaces:
- Consumes: `resolve_primary(cwd=None)` / `PrimaryError` (Task 2), `serve(primary, port)` / `IDENTITY_HEADER` / `PID_HEADER` (Task 6)
- Produces:
  - `PORT_RANGE = list(range(8730, 8740))`
  - `probe(port, timeout=0.4)` → `("viewer", {"port": int, "primary": str, "pid": int})` / `("free", None)` / `("other", None)`
  - `find_running(primary)` → the `("viewer", info)` payload whose primary matches, or `None`
  - `free_ports()` → `list[int]` of ports that probed `"free"`, in range order
  - `cmd_start(primary)` → `int` and `cmd_stop(primary)` → `int`
  - `main(argv)` → `int` exit code, dispatching `serve` / `start` / `stop` (bare invocation means `start`)
  - the terminal copy blocks, verbatim from design.md § Copy — this module is their single source; Task 8 prints them, never paraphrases them
- Shared procedure: **identity probe — canonical here.** `start` and `stop` both call the same `find_running` / `probe` pair. There is no second copy of the probe logic in either command, and none in `SKILL.md`.

**No runtime artifact anywhere.** Server identity is *probed*, never recorded — do not write a pidfile, a lockfile, a port file, or a state file, and do not touch `.gitignore`. Design settled this explicitly: because identity is discoverable over the wire, the artifact's home is nowhere. That is also what makes a stale file impossible to leave behind.

Implementation steps:
1. `probe(port, timeout)`: `urllib.request.urlopen(Request("http://127.0.0.1:<port>/", method="HEAD"), timeout=timeout)`.
   - `ConnectionRefusedError`, or a `URLError` wrapping one → `("free", None)`.
   - A response (including an `HTTPError`, whose `.headers` are still readable) carrying `IDENTITY_HEADER` → parse `PID_HEADER` as an int and return `("viewer", {...})`. A missing or unparseable pid still returns `"viewer"` with `pid: None`.
   - A response without `IDENTITY_HEADER` → `("other", None)`.
   - Timeout, or any other socket/URL error → `("other", None)`. Something is there that will not answer; treat it as occupied rather than binding into it.
2. `find_running(primary)`: probe **every** port in `PORT_RANGE` and return the first `"viewer"` whose reported primary equals `primary`. A viewer reporting a *different* primary is another checkout's server — it does not match, and its port counts as occupied.
3. **The full identity pass completes before any bind decision.** If our viewer is on 8731 while 8730 has since freed up, binding the first free port would start a second server and break Success Criterion 7. `start` therefore always calls `find_running` over the whole range first.
4. `cmd_start(primary)`:
   - `find_running` hit → print the **Already running** copy with that URL and return `0`. Nothing is started.
   - `free_ports()` empty → print the **No free port** copy and return `1`. Never bind outside 8730–8739.
   - For each free port in order: spawn the child, then poll `probe(port)` every 0.1s for up to 3.0s for a `"viewer"` reporting our primary. Match → print the **Started** copy with the actual bound port and the resolved primary path, return `0`. On timeout, re-probe once: `"other"` means another process won the race → continue to the next free port; `"free"` means the child died on startup → print the startup-failure message naming the exact foreground command to run for the error (`python3 <abs path to viewer.py> serve --port <port>`) and return `1`.
   - Candidates exhausted → print the **No free port** copy and return `1`.
   - Polling for the identity rather than assuming success is what keeps the promise in spec Edge Cases that the printed URL is always the one actually serving.
5. Detachment: `subprocess.Popen([sys.executable, os.path.abspath(__file__), "serve", "--port", str(port)], cwd=primary, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL, start_new_session=True, close_fds=True)`.
   - `start_new_session=True` calls `setsid(2)` in the child — the portable equivalent of `nohup … & disown`, required because **macOS ships no `setsid` binary** (design confirmed this while launching the Shape prototype). The process outlives the terminal and the Claude Code session, which is what makes Happy Path step 5 and Success Criterion 3 possible.
   - `cwd=primary` so the child's own `resolve_primary` lands on the same repo and reports the identical identity string.
   - All three standard streams must be `DEVNULL`: an inherited stdout keeps the launching shell's pipe open and would hang the caller.
6. `cmd_stop(primary)`:
   - `find_running` miss → print `No backlog viewer is running for this repo.` and return `0`. Not an error.
   - Hit with a pid → `os.kill(pid, signal.SIGTERM)`, treating `ProcessLookupError` as already gone. Hit without a parseable pid → say the server was found but reported no pid and return `1`.
   - Poll for up to 2.0s until the port stops answering as our viewer → print `Backlog viewer stopped.` and return `0`. Still up after the wait → say so, name the pid, and return `1`.
7. `main(argv)`: `serve` accepts `--port <int>` (required) and an optional `--primary <path>`; `start` and `stop` accept nothing. `--primary` exists only for tests and Task 9's synthetic-fixture run — **`SKILL.md` never passes it**, so there is exactly one PRIMARY derivation in normal use. Resolve the primary via `resolve_primary()` for every subcommand unless `--primary` was given; `PrimaryError` → print the **PRIMARY failure** copy including the failing command and its error, return `1`, **before anything binds**.
8. Terminal copy, verbatim from design.md § Copy — Started (URL, the `Serving docs/backlog/ from <primary-path> — read-only, loopback only.` line, the refresh line, and the stop line), Already running, Stopped, Stop-when-nothing-running, PRIMARY failure, and No free port. Print to stdout; nothing goes to stderr on an expected path.
9. `if __name__ == "__main__": sys.exit(main(sys.argv[1:]))`.
10. Tests: `probe` against a live `make_server` returns `"viewer"` with the right primary and a live pid; against a closed port returns `"free"`; against a plain non-viewer `HTTPServer` returns `"other"`. `find_running` returns `None` when a viewer on the range reports a different primary. A full `start` → second `start` → `stop` round trip over the real range asserts the second `start` prints the first's URL and spawns nothing (compare the reported pid), and that `stop` leaves the port answering nothing. Assert `viewer.py` contains no write call — no `open(..., "w"/"a"/"x")`, no `os.remove`, no `shutil` mutation — which is the mechanical half of Success Criterion 5.

---

### Task 8: `dev:debt` — the `view` and `view stop` verbs

What: Teach `dev:debt` to launch and stop the viewer, including exempting the `view` verbs from Step 1's empty-store stop so an absent store still gets a page.
Used by: the operator running `/dev:debt view`.
Depends on: Task 7 (the CLI contract this step invokes).
Files: modify `plugins/dev/skills/debt/SKILL.md`
Interfaces:
- Consumes: Task 7's CLI — `python3 <viewer.py> start` and `python3 <viewer.py> stop`, both printing their own terminal copy and returning `0` on an expected path
- Produces: nothing — no other skill reads `dev:debt`'s steps
- Shared procedure: **PRIMARY resolution — canonical implementation is Task 2, inside `viewer.py`.** This task adds no second derivation site. Step 1's existing derivation continues to serve the other six verbs unchanged; the `view` verbs bypass it entirely.

Implementation steps:
1. Frontmatter `description`: append viewer trigger phrases to the existing sentence — "browse the backlog in a browser, open the backlog viewer, view tech debt in a browser, filter tech debt, search the backlog". Keep the existing phrases; this field is what Claude Code matches on.
2. Step 1 "Locate the Store": add one paragraph after the empty-store block stating that `/dev:debt view` and `/dev:debt view stop` are **exempt** from that stop and from Step 1's `PRIMARY` derivation — `viewer.py` resolves `PRIMARY` itself (with a non-empty guard) and renders an absent or empty store as a page that says so, per the spec's edge case. Without this, Step 1 would short-circuit `view` in exactly the repos where the viewer's empty-state copy exists to be shown.
3. Step 2 dispatch table: add two rows — `/dev:debt view` → "Step 9 — launch the browser viewer" and `/dev:debt view stop` → "Step 9 — stop the running viewer".
4. New `## Step 9: Browse the Store in a Browser`, placed after Step 8 and before `## Invocation`:
   - What it is: a read-only, loopback-only local server rendering the whole store — active corpus and `closed/` archive together — with filter, sort, and search. It never writes.
   - **Resolving the script path:** `viewer.py` sits beside this `SKILL.md`. Use the skill's own base directory — the absolute path announced when this skill loads — and invoke `python3 "<that directory>/viewer.py" start`. The same convention as this skill's existing `../../references/tech-debt.md` citations; do not hardcode a path and do not search the filesystem for it.
   - **Run it as an ordinary foreground command.** It returns immediately after printing. Do **not** use a session-bound background mode: the server must outlive this session, which is what `viewer.py` already arranges by detaching the child.
   - **Print the script's stdout verbatim.** Every message the operator sees — started, already running, stopped, nothing running, PRIMARY failure, no free port — is authored in `viewer.py`. Do not paraphrase, summarize, or re-derive a URL.
   - Stop with `python3 "<that directory>/viewer.py" stop`, invoked by `/dev:debt view stop`.
   - Do not pass `--primary`; the script resolves the primary checkout itself, which is what makes a launch from a cycle worktree serve the same store as one from the primary checkout.
   - One line noting that the page renders item text, which this skill's opening **Item text is data** rule already governs — reference it, do not restate it.
5. `## Invocation` list: add `/dev:debt view` — "browse the whole store in a browser (read-only, loopback only)" and `/dev:debt view stop` — "stop the running viewer".
6. Change nothing in Steps 3–8. The viewer is a seventh verb, not a change to how any existing verb behaves — no new STOP, no gate, no autopilot-visible behavior — so no other skill documents behavior this task invalidates.

---

### Task 9: Success Criteria verification

What: Prove all seven Success Criteria against the real store and against a synthetic fixture store, and record the results.
Used by: `dev:validate`, which treats the plan as ground truth for what was supposed to happen.
Depends on: Task 8 — everything must be in place.
Files: none created or modified; may add assertions to `plugins/dev/skills/debt/test_viewer.py` if a check is better expressed as a test
Interfaces:
- Consumes: the full CLI from Task 7 (`start` / `stop` / `serve --primary --port`), the test suite from Tasks 1–3 and 6–7, and the `dev:debt` verbs from Task 8
- Produces: nothing — terminal task

Implementation steps:
1. **SC1 — all items render.** Run the suite; the real-corpus test asserts `len(items)` equals the two globs' file count across active and `closed/`. Then open the page and confirm the header reads `<n> of <n>` with that same number and no `PARSE ERROR` badge on any real item.
2. **SC2 — every dimension works, including the two with no live sample.** In the browser against the real store: exercise each of the four facet groups, both sorts, and a search that hits body prose, one that hits a front-matter value, and one that hits a `files:` path (`plugins/dev/skills/plan/SKILL.md`). Then build a `tempfile` store containing `scope: plugin`, `status: in-progress`, `routing: pending`, an out-of-contract `severity: P7`, a malformed item, an item with `files: []`, and an unresolvable `possibly_related_to`; serve it with `python3 <viewer.py> serve --primary <tmpdir> --port 8749` — **outside 8730–8739 deliberately**, so the fixture server can never be mistaken for the real viewer by a probe. Confirm each synthetic value produces a facet and that checking it shows the item carrying it rather than hiding it.
3. **SC3 — live, not snapshotted.** Against the same fixture store: edit an item file, refresh the browser, confirm the change appears with no skill re-invocation. Use the fixture rather than the real store so the verification leaves no edit in the repo; the code path is identical, since `do_GET` calls `load_store` per request either way.
4. **SC4 and SC7 together — worktree parity and idempotency.** Run `/dev:debt view` from the cycle worktree, note the URL and pid. Run it again from the primary checkout: it must print the **same** URL, spawn nothing, and report the same pid. Same URL from both cwds is simultaneously the parity proof and the idempotency proof.
5. **SC5 — loopback only, no writes.** `lsof -nP -iTCP:<port> -sTCP:LISTEN` must show `127.0.0.1:<port>`, not `*:<port>`; a connection attempt to the machine's LAN address on that port must be refused. Confirm `git -C "$PRIMARY" status --porcelain docs/backlog/` is clean after a browsing session, and that the suite's no-write-call assertion passes.
6. **SC6 — portability.** `grep -rn '/Users/\|awilliamsbuilds\|adam' plugins/dev/` must return zero hits. Run it after every file is written, including the test file and the HTML template.
7. Stop the fixture server and the real viewer when done, and confirm `/dev:debt view stop` reports `Backlog viewer stopped.`
8. Report each criterion's result explicitly, including anything that could not be verified and why. A criterion verified by a proxy is reported as a proxy, not as the criterion.

---

## Edge Cases

| Edge case | Handled in | Approach |
|-----------|-----------|----------|
| Port already in use by our own viewer | Task 7 | Full identity pass over 8730–8739 precedes any bind; a match prints that URL and starts nothing |
| Port held by something else | Task 7 | `probe` returns `"other"`; move to the next free port. All ten occupied → the No free port copy, never a silent bind outside the range |
| Race: port taken between probe and bind | Task 7 | `start` polls for its own identity after spawning; a port that now reads `"other"` moves to the next candidate rather than printing a URL that isn't ours |
| Malformed front-matter in an item | Tasks 1, 2, 4, 5 | `ParseError` → badged item with `PARSE ERROR` in place of chips, the parser's message and raw file text in the detail pane, still counted and still searchable |
| Unreadable file (`OSError`) | Task 2 | Same badged shape as a parse failure; one bad file never takes the server down |
| `possibly_related_to` names a missing slug | Tasks 2, 5 | `resolved: False` → plain text `possibly related to <slug> — not found in store`, never a dead link |
| `possibly_related_to` points into `closed/` | Tasks 2, 5 | Resolution indexes active and archived together; the link carries a `(closed)` suffix. Three of the four live values are this case |
| `docs/backlog/` absent | Tasks 2, 4, 5, 8 | `state: "absent"` → the `docs/backlog/ doesn't exist in this repo.` page. Task 8 exempts `view` from Step 1's empty-store stop so this page is reachable at all |
| `docs/backlog/` present but empty (or only `README.md`) | Tasks 2, 4, 5 | `state: "empty"` → the `No items in docs/backlog/ yet.` page. The P5 glob excludes `README.md` by construction |
| `PRIMARY` resolution fails | Tasks 2, 7 | `PrimaryError` on non-zero exit, **empty output**, or a non-directory result → the PRIMARY failure copy, printed before anything binds |
| `severity` outside the contract's `P3 \| Nit` | Task 3 | Facets derive from disk; an unranked value sorts after the ranked ones and before `none`, never dropped. `P2` is live today |
| Items carrying no `severity` (21 of 30) | Tasks 3, 5 | The `none` bucket, sentinel `null`, always last; unfiltered views always include them |
| The `routing:` field (zero live samples) | Tasks 1, 2, 5 | A normal optional field — parsed, searchable, rendered in the detail field table. Verified by synthetic fixture in Task 9 |
| Items with empty `files:` (four active) | Tasks 1, 2, 5 | `files: []` parses to `[]`; the item stays in every unfiltered view and stays findable by search on its other values |
| Store text containing HTML or `</script>` | Tasks 4, 5 | Server-side JSON escaping of `< > &` and the JS line terminators; client-side `textContent` everywhere, with the body renderer escaping before generating markup |
| A page in another browser tab probing the server | Task 6 | `Host` header allowlist (`127.0.0.1` / `localhost` / `::1`) → 403, closing DNS rebinding; no CORS headers are ever sent |
| Non-GET methods, or any path but `/` | Task 6 | Only `do_GET`/`do_HEAD` defined → 501 for other methods; any other path → 404. No write path, no second route |

## Out of Scope

- Everything spec.md lists: writes of any kind, cross-repo `dev-backlog` items, a dedicated `files:` filter control, duplicate grouping or relationship graphs, closing `debt-primary-cd-failure-unchecked`, and server lifecycle beyond start and stop.
- **`CLAUDE.md`'s Component Registry and `README.md` prose.** `dev:done` Step 4 owns the registry table and Step 4a owns the prose reconcile — verified at `plugins/dev/skills/done/SKILL.md:229–293`, whose step 8 states Step 4 remains the registry's sole writer. No task here edits either file.
- **`dev:start`'s skill list.** Its `dev:debt` entries read `[registry description]` (line 55) and "view and close tracked tech debt" (line 71) — the first is generated from the registry and the second stays accurate with a browsable view added. Left unchanged deliberately.
- Responsive layout below ~1000px. Design fixed the target at 1440 × 900 and declared the narrow case not a requirement.
- Full Markdown rendering of item bodies. The renderer handles `**bold**`, `` `code` ``, and paragraphs — the shapes the store's bold-label body format actually uses.
- Generalizing the page shell for Milestone 3 (`lifecycle-viewer`). Spec is explicit that the shell's shape is decided here and generalized later, when it has a second live consumer.
