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
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
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
    item_id = os.path.splitext(os.path.basename(path))[0]
    item = {
        "id": item_id,
        # Unique even when the same stem exists in both the active corpus and
        # closed/ — an interrupted close leaves exactly that. `id` is what the
        # page displays; `key` is what selects and highlights, so neither copy
        # can shadow the other into being unreachable.
        "key": ("closed/" + item_id) if archived else item_id,
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
    # First hit wins, and the active corpus is loaded before closed/, so a stem
    # present in both resolves to the active copy.
    index = {}
    for item in items:
        index.setdefault(item["id"], item)
    for item in items:
        value = item["fields"].get("possibly_related_to")
        if not isinstance(value, str) or not value.strip():
            continue
        value = value.strip()
        for candidate in (value, "debt-" + value, "backlog-" + value):
            target = index.get(candidate)
            if target is not None:
                item["related"] = {
                    "id": candidate,
                    "key": target["key"],
                    "resolved": True,
                    "archived": target["archived"],
                }
                break
        else:
            item["related"] = {
                "id": value, "key": None, "resolved": False, "archived": False,
            }


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
    # validate/SKILL.md severity ladder; deliberately wider than the contract's
    # sole accepted value (P3). P2 appears because debt-p9-issue-body-fence-width
    # carries it today, and Nit because closed/ keeps archived items at values the
    # contract no longer accepts — both must stay orderable, per the membership
    # rule above.
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
# repo — entry adapters seed items from Linear, P9 delivers them as GitHub issues — so
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

# The page carries its own style and script inline and fetches nothing, so every
# source but inline can be denied outright. frame-ancestors keeps another origin
# from framing the store; 'unsafe-inline' is what the inline <style>/<script> need.
CONTENT_SECURITY_POLICY = (
    "default-src 'none'; "
    "style-src 'unsafe-inline'; "
    "script-src 'unsafe-inline'; "
    "frame-ancestors 'none'; "
    "base-uri 'none'; "
    "form-action 'none'"
)


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

    def _respond(self, status, content_type, payload, with_body, with_identity=True):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        if payload is not None:
            self.send_header("Content-Length", str(len(payload)))
        if with_identity:
            # Only ever on a response to an allowed host. The identity string is
            # an absolute path on this machine, and the 403 below is precisely
            # the response a rebinding attacker can read.
            self.send_header(IDENTITY_HEADER, self.primary)
            self.send_header(PID_HEADER, str(os.getpid()))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy", CONTENT_SECURITY_POLICY)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if with_body and payload:
            self.wfile.write(payload)

    def _handle(self, with_body):
        # Loopback binding alone does not stop a page elsewhere from pointing a
        # hostname at 127.0.0.1 and reading this document same-origin.
        if _host_name(self.headers.get("Host", "")) not in LOOPBACK_HOSTS:
            self._respond(
                403, "text/plain; charset=utf-8", b"Forbidden.\n", with_body,
                with_identity=False,
            )
            return

        path = urllib.parse.urlsplit(self.path).path
        if path != "/":
            self._respond(404, "text/plain; charset=utf-8", b"Not found.\n", with_body)
            return

        if not with_body:
            # HEAD is the probe path. Answer the identity question without
            # reading the store or rendering the page: the probe runs up to ten
            # times per command and would otherwise re-parse the whole store
            # each time, only to discard the bytes. Content-Length is omitted
            # rather than guessed, since nothing was rendered to measure.
            self._respond(200, "text/html; charset=utf-8", None, False)
            return

        try:
            # Read the store fresh on every request — this is the whole of
            # "refresh the tab and see the current files".
            payload = render_page(load_store(self.primary)).encode("utf-8")
        except Exception as exc:  # a template or render fault, never a bad item
            message = ("Could not render the backlog store: %s\n" % exc).encode("utf-8")
            self._respond(500, "text/plain; charset=utf-8", message, with_body)
            return

        self._respond(200, "text/html; charset=utf-8", payload, with_body)

    def do_GET(self):
        self._handle(with_body=True)

    def do_HEAD(self):
        self._handle(with_body=False)

    # No do_POST/do_PUT/do_DELETE: the base class answers those 501 on its own,
    # which is exactly right for a server with no write path.

    def version_string(self):
        # Default would name the exact Python patch version on every response.
        return "dev-backlog-viewer"

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


# --- The command line -------------------------------------------------------
#
# Server identity is probed over the wire, never recorded: no pidfile, no port
# file, no state file, nothing in .gitignore. A stale artifact is then impossible
# to leave behind.

PORT_RANGE = list(range(8730, 8740))
SCRIPT_NAME = os.path.basename(os.path.abspath(__file__))
PROBE_TIMEOUT = 0.4
START_TIMEOUT = 3.0
STOP_TIMEOUT = 2.0
POLL_INTERVAL = 0.1

# Terminal copy. This module is its single source — the skill prints it verbatim.
STARTED = (
    "Backlog viewer running at {url}\n"
    "Serving docs/backlog/ from {primary} — read-only, loopback only.\n"
    "Refresh the page any time; it re-reads the files on every load.\n"
    "Stop it with: /dev:debt view stop"
)
ALREADY_RUNNING = (
    "Backlog viewer is already running at {url}\n"
    "Stop it with: /dev:debt view stop"
)
STOPPED = "Backlog viewer stopped."
NOT_RUNNING = "No backlog viewer is running for this repo."
PRIMARY_FAILURE = (
    "Can't resolve the repository root, so there's no store to serve.\n"
    "{error}\n"
    "Run this from inside the repository."
)
NO_FREE_PORT = (
    "Ports 8730-8739 are all in use by something else, so the viewer didn't start.\n"
    "Free one of them, or stop whatever is holding them, and try again."
)
USAGE = "Usage: viewer.py [start|stop|serve --port <n> [--primary <path>]]"

_SPAWNED = []  # detached children, kept referenced for this process's lifetime


def viewer_url(port):
    return "http://%s:%d" % (BIND_ADDRESS, port)


class _NoRedirects(urllib.request.HTTPRedirectHandler):
    """Refuse 3xx. A process squatting a port could otherwise redirect the probe
    to an arbitrary external URL and turn /dev:debt view into an outbound beacon."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_PROBE_OPENER = urllib.request.build_opener(_NoRedirects)


def probe(port, timeout=PROBE_TIMEOUT):
    """Ask a port who it is. Returns ("viewer", info) / ("free", None) / ("other", None)."""
    request = urllib.request.Request(viewer_url(port) + "/", method="HEAD")
    try:
        response = _PROBE_OPENER.open(request, timeout=timeout)
        headers = response.headers
        response.close()
    except urllib.error.HTTPError as exc:
        headers = exc.headers  # still ours if it carries the identity header
        exc.close()
    except urllib.error.URLError as exc:
        if isinstance(exc.reason, ConnectionRefusedError):
            return ("free", None)
        return ("other", None)
    except ConnectionRefusedError:
        return ("free", None)
    except Exception:
        # Something is there that will not answer. Treat it as occupied rather
        # than binding into it.
        return ("other", None)

    identity = headers.get(IDENTITY_HEADER)
    if not identity:
        return ("other", None)

    try:
        pid = int(headers.get(PID_HEADER))
    except (TypeError, ValueError):
        pid = None
    if pid is not None and pid <= 0:
        # os.kill(0, …) signals our whole process group and os.kill(-1, …) every
        # process we may signal. A pid off the wire never gets to mean either.
        pid = None
    return ("viewer", {"port": port, "primary": identity, "pid": pid})


def find_running(primary):
    """The viewer serving this primary, or None. A viewer for another checkout does not match."""
    for port in PORT_RANGE:
        kind, info = probe(port)
        if kind == "viewer" and info["primary"] == primary:
            return info
    return None


def free_ports():
    """Ports in the range that nothing is listening on, in range order."""
    return [port for port in PORT_RANGE if probe(port)[0] == "free"]


def _spawn(primary, port):
    """Start a detached child that outlives this process and its terminal.

    start_new_session=True calls setsid(2) — the portable equivalent of
    `nohup … & disown`, and necessary because macOS ships no setsid binary.
    cwd=primary so the child's own resolve_primary reports the same identity.
    All three streams go to DEVNULL: an inherited stdout would hold the caller's
    pipe open and hang it.
    """
    child = subprocess.Popen(
        [sys.executable, os.path.abspath(__file__), "serve", "--port", str(port)],
        cwd=primary,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
        close_fds=True,
    )
    # Never reaped — the child is meant to outlive us. Holding the handle keeps
    # Popen from warning about the running process it finds when collected.
    _SPAWNED.append(child)
    return child


def _await_viewer(port, primary):
    """Poll until the port answers as our viewer, or the deadline passes."""
    deadline = time.time() + START_TIMEOUT
    while time.time() < deadline:
        kind, info = probe(port)
        if kind == "viewer" and info["primary"] == primary:
            return info
        time.sleep(POLL_INTERVAL)
    return None


def cmd_start(primary):
    # The full identity pass finishes before any bind decision: if our viewer is
    # already up on a later port, binding an earlier free one would start a second.
    running = find_running(primary)
    if running:
        print(ALREADY_RUNNING.format(url=viewer_url(running["port"])))
        return 0

    candidates = free_ports()
    if not candidates:
        print(NO_FREE_PORT)
        return 1

    for port in candidates:
        _spawn(primary, port)
        # Poll for our own identity rather than assuming success, so the URL
        # printed is always the one actually serving.
        if _await_viewer(port, primary):
            print(STARTED.format(url=viewer_url(port), primary=primary))
            return 0

        kind, info = probe(port)
        if kind == "viewer" and info["primary"] == primary:
            # Slow to come up, not lost. Treating this as a lost race would
            # spawn a second server for the same primary — and a later stop
            # would only ever find the first, orphaning this one for good.
            print(STARTED.format(url=viewer_url(port), primary=primary))
            return 0
        if kind != "free":
            continue  # another process won the race for this port
        print("The viewer didn't start on port %d. Run it in the foreground to see why:" % port)
        print("  %s %s serve --port %d" % (sys.executable, os.path.abspath(__file__), port))
        return 1

    print(NO_FREE_PORT)
    return 1


def _pid_is_viewer(pid):
    """True when pid's command line is one of our serve processes.

    The pid cmd_stop acts on comes off the wire, so anything that can bind a
    port in the range can name a pid it does not own. Without this check a
    squatter answering with the right identity header could make us SIGTERM an
    arbitrary process of the invoking user's.
    """
    try:
        result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "args="],
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.SubprocessError):
        return False  # can't confirm, so don't signal
    if result.returncode != 0:
        return False
    args = result.stdout.strip()
    return SCRIPT_NAME in args and "serve" in args.split()


def cmd_stop(primary):
    running = find_running(primary)
    if not running:
        print(NOT_RUNNING)
        return 0

    pid = running["pid"]
    url = viewer_url(running["port"])
    if pid is None:
        print("Found a backlog viewer at %s, but it reported no process id." % url)
        return 1

    if not _pid_is_viewer(pid):
        print("Found a backlog viewer at %s reporting pid %d," % (url, pid))
        print("but that process isn't a %s serve process. Nothing was stopped." % SCRIPT_NAME)
        return 1

    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        pass  # already gone

    deadline = time.time() + STOP_TIMEOUT
    while time.time() < deadline:
        kind, info = probe(running["port"])
        if kind != "viewer" or info["primary"] != primary:
            print(STOPPED)
            return 0
        time.sleep(POLL_INTERVAL)

    print("Backlog viewer at %s is still running (pid %d)." % (url, pid))
    return 1


def main(argv):
    args = list(argv)
    command = "start"
    if args and not args[0].startswith("-"):
        command = args.pop(0)
    if command not in ("serve", "start", "stop"):
        print("Unknown command '%s'.\n%s" % (command, USAGE))
        return 1

    port = None
    primary_override = None
    while args:
        flag = args.pop(0)
        if flag in ("--port", "--primary") and not args:
            print("%s needs a value.\n%s" % (flag, USAGE))
            return 1
        if flag == "--port":
            try:
                port = int(args.pop(0))
            except ValueError:
                print("--port takes a number.\n%s" % USAGE)
                return 1
        elif flag == "--primary":
            primary_override = args.pop(0)
        else:
            print("Unrecognized argument '%s'.\n%s" % (flag, USAGE))
            return 1

    if command == "serve" and port is None:
        print("serve needs --port <n>.\n%s" % USAGE)
        return 1
    if command != "serve" and (port is not None or primary_override is not None):
        print("%s takes no arguments.\n%s" % (command, USAGE))
        return 1

    # --primary exists for tests and fixture runs only; the skill never passes it,
    # so there is exactly one PRIMARY derivation in normal use.
    if primary_override is not None:
        primary = os.path.abspath(primary_override)
    else:
        try:
            primary = resolve_primary()
        except PrimaryError as exc:
            print(PRIMARY_FAILURE.format(error=exc))  # printed before anything binds
            return 1

    if command == "start":
        return cmd_start(primary)
    if command == "stop":
        return cmd_stop(primary)

    try:
        serve(primary, port)
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
