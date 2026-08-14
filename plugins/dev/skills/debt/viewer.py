#!/usr/bin/env python3
"""Read-only browser view of the /dev backlog store (docs/backlog/).

Launched by `/dev:debt view`. Serves one loopback route that re-reads the store on
every request, so a refreshed tab always shows the current files. Never writes.

Stdlib only — the repo has no build tooling and no package manager, and PyYAML is
not available, so the front-matter parser below is hand-rolled against the schema
in plugins/dev/references/tech-debt.md.
"""

import glob
import json
import os
import pathlib
import re
import subprocess
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# --- Front-matter parsing ---------------------------------------------------
#
# The store's front-matter is a small hand-edited subset of YAML: `key: scalar`,
# inline lists (`cycles: [a, b]`, `files: []`), block lists (`files:` then two-space
# `  - entry` lines), and bare `key:` with no value. Every rule here fails loudly.
# A silently dropped or mangled field is the failure mode Success Criterion 1 exists
# to prevent, so guessing is never the right answer.

KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):(?:[ \t](.*))?$")
LIST_ITEM_RE = re.compile(r"^ {2}-(?:[ \t](.*))?$")
INT_RE = re.compile(r"^[0-9]+$")

DELIMITER = "---"


class ParseError(Exception):
    """One item file's front-matter could not be read. The message names the line."""


def _unquote(value):
    """Remove one layer of matched surrounding quotes, if present."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def _scalar_or_inline_list(remainder, lineno):
    value = remainder.strip()
    if value.startswith("["):
        if not value.endswith("]"):
            raise ParseError("unclosed inline list at line %d" % lineno)
        parts = (_unquote(part.strip()) for part in value[1:-1].split(","))
        return [part for part in parts if part]
    return _unquote(value)


def parse_front_matter(text):
    """Parse one item file into (fields, body).

    `fields` is a dict in file order; values are str, int, list of str, or None.
    `body` is everything after the closing delimiter, stripped of leading and
    trailing newlines. Raises ParseError on any structural failure.
    """
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    if not lines or lines[0] != DELIMITER:
        raise ParseError("file does not open with a '---' front-matter delimiter")

    close = None
    for index in range(1, len(lines)):
        if lines[index] == DELIMITER:
            close = index
            break
    if close is None:
        raise ParseError("front-matter is never closed by a '---' delimiter")

    body = "\n".join(lines[close + 1:]).strip("\n")

    fields = {}
    i = 1
    while i < close:
        line = lines[i]
        lineno = i + 1  # messages count lines from the start of the file

        if not line.strip():
            i += 1
            continue

        match = KEY_RE.match(line)
        if match:
            key = match.group(1)
            remainder = match.group(2) or ""
            if key in fields:
                # Last-wins would silently discard a hand-edit mistake.
                raise ParseError("duplicate key '%s' at line %d" % (key, lineno))

            if remainder.strip() == "":
                nxt = i + 1
                while nxt < close and not lines[nxt].strip():
                    nxt += 1
                if nxt < close and LIST_ITEM_RE.match(lines[nxt]):
                    entries = []
                    while nxt < close:
                        item = LIST_ITEM_RE.match(lines[nxt])
                        if not item:
                            break
                        entry = _unquote((item.group(1) or "").strip())
                        if entry:
                            entries.append(entry)
                        nxt += 1
                    fields[key] = entries
                    i = nxt
                    continue
                fields[key] = None
            else:
                fields[key] = _scalar_or_inline_list(remainder, lineno)
            i += 1
            continue

        if LIST_ITEM_RE.match(line):
            raise ParseError("list item at line %d has no parent key" % lineno)

        raise ParseError(
            "line %d is neither a 'key:' entry nor a '  - ' list item: %s" % (lineno, line)
        )

    recurrence = fields.get("recurrence")
    if isinstance(recurrence, str) and INT_RE.match(recurrence):
        fields["recurrence"] = int(recurrence)

    return fields, body


# --- The store --------------------------------------------------------------

STORE_PARTS = ("docs", "backlog")
ARCHIVE_DIRNAME = "closed"
ITEM_GLOBS = ("debt-*.md", "backlog-*.md")


class PrimaryError(Exception):
    """The primary checkout could not be resolved, so there is no store to serve."""


def resolve_primary(cwd=None):
    """Absolute path of the primary checkout — the only PRIMARY derivation in this cycle.

    Two launches from different working directories (a cycle worktree and the primary
    checkout) must produce the identical string, because that string is the identity
    a running server reports and a second launch matches on.
    """
    cwd = cwd or os.getcwd()
    command = ["git", "rev-parse", "--git-common-dir"]
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    except OSError as exc:
        raise PrimaryError("could not run `%s`: %s" % (" ".join(command), exc))

    if result.returncode != 0:
        raise PrimaryError(
            "`%s` failed: %s" % (" ".join(command), result.stderr.strip() or "no error output")
        )

    out = result.stdout.strip()
    if not out:
        # The guard debt-primary-cd-failure-unchecked records missing at the other sites.
        raise PrimaryError("`%s` returned no output" % " ".join(command))

    primary = os.path.abspath(os.path.join(cwd, os.path.dirname(out) or "."))
    if not os.path.isdir(primary):
        raise PrimaryError("resolved repository root is not a directory: %s" % primary)
    return primary


def _item_paths(directory):
    """Item files in one directory. The two globs exclude README.md by construction."""
    paths = []
    for pattern in ITEM_GLOBS:
        paths += sorted(glob.glob(os.path.join(directory, pattern)))
    return paths


def _search_blob(item):
    """Lowercased haystack: id, field *values*, body, and the raw text of a bad file.

    Field names are deliberately excluded — including them would make every item
    match the word "severity". Field values are what make a `files:` path findable.
    """
    parts = [item["id"]]
    for value in item["fields"].values():
        if value is None:
            continue
        if isinstance(value, list):
            parts.append(" ".join(value))
        else:
            parts.append(str(value))
    parts.append(item["body"])
    if item["parse_error"]:
        parts.append(item["parse_error"])
    if item["raw"]:
        parts.append(item["raw"])
    return " ".join(parts).lower()


def _load_item(path, archived):
    item = {
        "id": os.path.splitext(os.path.basename(path))[0],
        "archived": archived,
        "fields": {},
        "body": "",
        "parse_error": None,
        "raw": None,
        "related": None,
        "search": "",
    }
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            text = handle.read()
    except OSError as exc:
        # One unreadable file must never take the server down.
        item["parse_error"] = str(exc)
        item["search"] = _search_blob(item)
        return item

    try:
        fields, body = parse_front_matter(text)
    except ParseError as exc:
        item["parse_error"] = str(exc)
        item["raw"] = text
        item["search"] = _search_blob(item)
        return item

    item["fields"] = fields
    item["body"] = body
    item["search"] = _search_blob(item)
    return item


def _resolve_relationships(items):
    """Link `possibly_related_to` across the active corpus and the archive together.

    The contract names the field's value a slug; every live value carries the full
    `<type>-<slug>` stem. Both forms resolve, first hit winning.
    """
    index = dict((item["id"], item["archived"]) for item in items)
    for item in items:
        value = item["fields"].get("possibly_related_to")
        if not isinstance(value, str) or not value.strip():
            continue
        value = value.strip()
        for candidate in (value, "debt-" + value, "backlog-" + value):
            if candidate in index:
                item["related"] = {
                    "id": candidate,
                    "resolved": True,
                    "archived": index[candidate],
                }
                break
        else:
            item["related"] = {"id": value, "resolved": False, "archived": False}


# --- Facets -----------------------------------------------------------------
#
# Options come from the values found on disk, never from the contract's enums —
# that is what keeps an out-of-contract value (severity: P2 today) filterable
# rather than invisible. The rank lists below order values; they never decide
# membership, and must never be reused as a validity check.

FACET_FIELDS = ("type", "status", "scope", "severity")
FACET_RANK = {
    # references/tech-debt.md lifecycle table
    "status": ["open", "in-progress", "promoted", "closed"],
    # validate/SKILL.md severity ladder; extends past the contract's P3 | Nit
    # because debt-p9-issue-body-fence-width carries P2 today
    "severity": ["P1", "P2", "P3", "Nit"],
    # type and scope have no inherent sequence — they sort alphabetically
}


def derive_facets(items):
    """Tally each faceted field across all items, active and archived together."""
    facets = {}
    for field in FACET_FIELDS:
        counts = {}
        missing = 0
        for item in items:
            value = item["fields"].get(field)
            # Badged items carry no fields at all, so they land in every missing
            # bucket — visible and filterable rather than dropped.
            if not isinstance(value, str) or not value.strip():
                missing += 1
                continue
            value = value.strip()
            counts[value] = counts.get(value, 0) + 1

        rank = FACET_RANK.get(field, [])
        ordered = [value for value in rank if value in counts]
        ordered += sorted(value for value in counts if value not in rank)

        entries = [
            {"value": value, "label": value, "count": counts[value]} for value in ordered
        ]
        if missing:
            # None, not the string "none", so an item literally carrying
            # `severity: none` stays distinguishable from one carrying nothing.
            entries.append({"value": None, "label": "none", "count": missing})
        facets[field] = entries
    return facets


def load_store(primary):
    """Read the whole store — active corpus and closed/ archive — into one dict.

    Called fresh on every HTTP request, which is what keeps a refreshed tab current.
    `primary` is deliberately not part of the result: it would put an absolute home
    directory path into the served HTML for no reason.
    """
    items = []
    state = "absent"

    store_dir = os.path.join(primary, *STORE_PARTS)
    if os.path.isdir(store_dir):
        archive_dir = os.path.join(store_dir, ARCHIVE_DIRNAME)
        items = [_load_item(path, False) for path in _item_paths(store_dir)]
        if os.path.isdir(archive_dir):
            items += [_load_item(path, True) for path in _item_paths(archive_dir)]
        _resolve_relationships(items)
        state = "ok" if items else "empty"

    return {
        "state": state,
        "repo_name": os.path.basename(primary),
        "total": len(items),
        "items": items,
        "facets": derive_facets(items),
    }


# --- Rendering --------------------------------------------------------------

TEMPLATE_PATH = pathlib.Path(__file__).with_name("viewer_page.html")
STORE_PLACEHOLDER = "__STORE_JSON__"

# Escapes applied to the embedded JSON literal. The first three keep `</script>`
# and `<!--` inert inside the script block; the last two are JS line terminators
# that would otherwise break the literal. Store text can originate outside this
# repo — dev:fix seeds items from Linear, P9 delivers them as GitHub issues — so
# this is a real injection boundary. All five are \u escapes, which json.loads
# reverses, so the data still round-trips.
JSON_ESCAPES = (
    ("<", "\\u003c"),
    (">", "\\u003e"),
    ("&", "\\u0026"),
    ("\u2028", "\\u2028"),
    ("\u2029", "\\u2029"),
)


def embed_json(obj):
    """Serialize obj as a JSON literal that is safe inside a <script> block."""
    text = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    for needle, replacement in JSON_ESCAPES:
        text = text.replace(needle, replacement)
    return text


def render_page(store):
    """Substitute the store into the page template, producing one complete document."""
    try:
        template = TEMPLATE_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError("page template missing at %s: %s" % (TEMPLATE_PATH, exc))
    return template.replace(STORE_PLACEHOLDER, embed_json(store))


# --- The server -------------------------------------------------------------
#
# One route, one document, no write path. BaseHTTPRequestHandler with an explicit
# allowlist rather than SimpleHTTPRequestHandler, which would serve its working
# directory and expose the whole repo.

IDENTITY_HEADER = "X-Dev-Backlog-Viewer"
PID_HEADER = "X-Dev-Backlog-Viewer-Pid"
LOOPBACK_HOSTS = frozenset(("127.0.0.1", "localhost", "::1", "[::1]"))
BIND_ADDRESS = "127.0.0.1"


def _host_name(raw):
    """The host from a Host header, with any :port stripped."""
    host = (raw or "").strip()
    if host.startswith("["):
        end = host.find("]")
        return host[:end + 1] if end != -1 else host
    if host.count(":") > 1:
        return host  # bare IPv6 literal carries no port
    return host.split(":")[0]


class ViewerHandler(BaseHTTPRequestHandler):
    """Serves GET / and HEAD / for one primary checkout. Everything else is refused."""

    primary = None  # set by make_server on a per-server subclass

    def _respond(self, status, content_type, payload, with_body):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header(IDENTITY_HEADER, self.primary)
        self.send_header(PID_HEADER, str(os.getpid()))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if with_body:
            self.wfile.write(payload)

    def _handle(self, with_body):
        # Loopback binding alone does not stop a page elsewhere from pointing a
        # hostname at 127.0.0.1 and reading this document same-origin.
        if _host_name(self.headers.get("Host", "")) not in LOOPBACK_HOSTS:
            self._respond(403, "text/plain; charset=utf-8", b"Forbidden.\n", with_body)
            return

        path = urllib.parse.urlsplit(self.path).path
        if path != "/":
            self._respond(404, "text/plain; charset=utf-8", b"Not found.\n", with_body)
            return

        try:
            # Read the store fresh on every request — this is the whole of
            # "refresh the tab and see the current files".
            page = render_page(load_store(self.primary))
        except Exception as exc:  # a template or render fault, never a bad item
            message = ("Could not render the backlog store: %s\n" % exc).encode("utf-8")
            self._respond(500, "text/plain; charset=utf-8", message, with_body)
            return

        self._respond(200, "text/html; charset=utf-8", page.encode("utf-8"), with_body)

    def do_GET(self):
        self._handle(with_body=True)

    def do_HEAD(self):
        self._handle(with_body=False)

    # No do_POST/do_PUT/do_DELETE: the base class answers those 501 on its own,
    # which is exactly right for a server with no write path.

    def log_message(self, fmt, *args):
        pass  # the detached process writes to /dev/null anyway


def make_server(primary, port):
    """Bind a viewer on loopback. port=0 yields an ephemeral port for tests."""
    handler = type("BoundViewerHandler", (ViewerHandler,), {"primary": primary})
    server = ThreadingHTTPServer((BIND_ADDRESS, port), handler)
    server.daemon_threads = True
    return server


def serve(primary, port):
    """Run the viewer in the foreground. Does not return."""
    make_server(primary, port).serve_forever()
