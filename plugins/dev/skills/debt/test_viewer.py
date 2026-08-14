"""Tests for the dev:debt backlog viewer.

Run from the repository root with:

    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s plugins/dev/skills/debt -p 'test_*.py'

The env var matters: this module imports `viewer`, and on a Python that writes bytecode
next to the source it would drop `plugins/dev/skills/debt/__pycache__/` into the repo —
untracked files whose payloads embed absolute source paths, which the portability grep
would then find.
"""

import io
import json
import os
import re
import shutil
import signal
import socket
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import viewer  # noqa: E402


def repo_root():
    """Walk up from this file to the checkout holding docs/backlog — never a fixed path."""
    d = os.path.dirname(os.path.abspath(__file__))
    while True:
        if os.path.isdir(os.path.join(d, "docs", "backlog")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            raise RuntimeError("no ancestor directory contains docs/backlog")
        d = parent


def corpus_files():
    """Every item file in the real store: active corpus first, then closed/."""
    import glob as _glob

    store = os.path.join(repo_root(), "docs", "backlog")
    paths = []
    for base in (store, os.path.join(store, "closed")):
        if not os.path.isdir(base):
            continue
        paths += sorted(_glob.glob(os.path.join(base, "debt-*.md")))
        paths += sorted(_glob.glob(os.path.join(base, "backlog-*.md")))
    return paths


class TestParseRealCorpus(unittest.TestCase):
    """The 30-odd real files are the parser's test corpus, per spec Technical Constraints."""

    def test_every_item_file_parses(self):
        paths = corpus_files()
        self.assertGreater(len(paths), 0, "expected the real store to hold item files")
        for path in paths:
            with self.subTest(path=os.path.basename(path)):
                with open(path, encoding="utf-8") as fh:
                    text = fh.read()
                fields, body = viewer.parse_front_matter(text)
                self.assertTrue(fields, "front-matter parsed to nothing")
                self.assertTrue(body.strip(), "body parsed to nothing")


class TestParseRules(unittest.TestCase):
    def parse(self, text):
        return viewer.parse_front_matter(text)

    def test_inline_list(self):
        fields, _ = self.parse("---\ncycles: [a, b]\n---\nbody\n")
        self.assertEqual(fields["cycles"], ["a", "b"])

    def test_empty_inline_list(self):
        fields, _ = self.parse("---\nfiles: []\n---\nbody\n")
        self.assertEqual(fields["files"], [])

    def test_block_list(self):
        text = "---\nfiles:\n  - one/path.md\n  - two/path.md\nstatus: open\n---\nbody\n"
        fields, _ = self.parse(text)
        self.assertEqual(fields["files"], ["one/path.md", "two/path.md"])
        self.assertEqual(fields["status"], "open")

    def test_bare_key_without_list_is_none(self):
        fields, _ = self.parse("---\nrouting:\nstatus: open\n---\nbody\n")
        self.assertIsNone(fields["routing"])
        self.assertEqual(fields["status"], "open")

    def test_recurrence_coerced_to_int(self):
        fields, _ = self.parse("---\nrecurrence: 2\n---\nbody\n")
        self.assertEqual(fields["recurrence"], 2)
        self.assertIsInstance(fields["recurrence"], int)

    def test_malformed_recurrence_stays_visible(self):
        fields, _ = self.parse("---\nrecurrence: many\n---\nbody\n")
        self.assertEqual(fields["recurrence"], "many")

    def test_quoted_scalar_unquoted_once(self):
        fields, _ = self.parse("---\ntitle: 'a value'\n---\nbody\n")
        self.assertEqual(fields["title"], "a value")

    def test_hash_is_not_treated_as_a_comment(self):
        fields, _ = self.parse("---\nstatus: open # really\n---\nbody\n")
        self.assertEqual(fields["status"], "open # really")

    def test_field_order_is_file_order(self):
        fields, _ = self.parse("---\ntype: debt\nscope: repo\nstatus: open\n---\nbody\n")
        self.assertEqual(list(fields.keys()), ["type", "scope", "status"])

    def test_body_is_text_after_the_closing_delimiter(self):
        fields, body = self.parse("---\ntype: debt\n---\n\nfirst\n\nsecond\n\n")
        self.assertEqual(body, "first\n\nsecond")

    def test_body_may_contain_a_delimiter_line(self):
        _, body = self.parse("---\ntype: debt\n---\nabove\n---\nbelow\n")
        self.assertEqual(body, "above\n---\nbelow")

    def test_crlf_parses_identically_to_lf(self):
        lf = "---\nfiles:\n  - a.md\nstatus: open\n---\nbody line\n"
        crlf = lf.replace("\n", "\r\n")
        self.assertEqual(self.parse(lf), self.parse(crlf))

    def test_missing_opening_delimiter(self):
        with self.assertRaises(viewer.ParseError):
            self.parse("type: debt\n---\nbody\n")

    def test_missing_closing_delimiter(self):
        with self.assertRaises(viewer.ParseError):
            self.parse("---\ntype: debt\nbody\n")

    def test_duplicate_key(self):
        with self.assertRaises(viewer.ParseError) as ctx:
            self.parse("---\ntype: debt\ntype: backlog\n---\nbody\n")
        self.assertIn("duplicate key", str(ctx.exception))

    def test_junk_line(self):
        with self.assertRaises(viewer.ParseError) as ctx:
            self.parse("---\ntype: debt\nnot a field\n---\nbody\n")
        self.assertIn("3", str(ctx.exception))

    def test_orphan_list_item(self):
        with self.assertRaises(viewer.ParseError) as ctx:
            self.parse("---\n  - orphan\n---\nbody\n")
        self.assertIn("no parent key", str(ctx.exception))

    def test_unclosed_inline_list(self):
        with self.assertRaises(viewer.ParseError) as ctx:
            self.parse("---\ncycles: [a, b\n---\nbody\n")
        self.assertIn("unclosed inline list", str(ctx.exception))


class StoreFixture(object):
    """A synthetic store built from string literals in a temp directory."""

    def __init__(self, make_dir=True):
        self.root = tempfile.mkdtemp()
        self.store = os.path.join(self.root, "docs", "backlog")
        if make_dir:
            os.makedirs(self.store)

    def write(self, name, text, archived=False):
        target = os.path.join(self.store, "closed") if archived else self.store
        if not os.path.isdir(target):
            os.makedirs(target)
        path = os.path.join(target, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        return path

    def cleanup(self):
        shutil.rmtree(self.root, ignore_errors=True)


def item_text(**overrides):
    fields = {
        "type": "debt",
        "scope": "repo",
        "status": "open",
        "first_recorded": "2026-08-01",
        "cycles": "[some-cycle]",
        "recurrence": "1",
        "files": "[]",
    }
    fields.update(overrides)
    lines = ["---"]
    for key, value in fields.items():
        if value is None:
            lines.append("%s:" % key)
        else:
            lines.append("%s: %s" % (key, value))
    lines += ["---", "", "**What's wrong:** a synthetic item.", ""]
    return "\n".join(lines)


class TestLoadRealStore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = viewer.load_store(repo_root())

    def test_state_and_totals_match_the_globs(self):
        expected = len(corpus_files())
        self.assertEqual(self.store["state"], "ok")
        self.assertEqual(len(self.store["items"]), expected)
        self.assertEqual(self.store["total"], expected)

    def test_repo_name_is_the_directory_name(self):
        self.assertEqual(self.store["repo_name"], os.path.basename(repo_root()))

    def test_every_item_has_an_id_and_none_are_badged(self):
        for item in self.store["items"]:
            self.assertTrue(item["id"])
            self.assertIsNone(item["parse_error"], item["id"])

    def test_readme_is_not_an_item(self):
        self.assertNotIn("README", [item["id"] for item in self.store["items"]])

    def test_archive_is_loaded_alongside_the_active_corpus(self):
        archived = [item for item in self.store["items"] if item["archived"]]
        self.assertGreater(len(archived), 0)

    def test_relationships_resolve_across_the_archive_boundary(self):
        related = [item for item in self.store["items"] if item["related"]]
        self.assertEqual(len(related), 4)
        for item in related:
            self.assertTrue(item["related"]["resolved"], item["id"])
        into_closed = [item for item in related if item["related"]["archived"]]
        self.assertEqual(len(into_closed), 3)

    def test_search_blob_covers_files_paths(self):
        needle = "plugins/dev/skills/plan/skill.md"
        hits = [item for item in self.store["items"] if needle in item["search"]]
        self.assertGreater(len(hits), 0)

    def test_search_blob_excludes_field_names(self):
        # Every item has a `status:` key; only the ones whose values say so should match.
        hits = [item for item in self.store["items"] if "status" in item["search"]]
        self.assertLess(len(hits), len(self.store["items"]))

    def test_primary_path_is_not_in_the_store_dict(self):
        self.assertNotIn("primary", self.store)


class TestLoadSyntheticStore(unittest.TestCase):
    def setUp(self):
        self.fixture = None

    def tearDown(self):
        if self.fixture:
            self.fixture.cleanup()

    def test_absent_store(self):
        self.fixture = StoreFixture(make_dir=False)
        store = viewer.load_store(self.fixture.root)
        self.assertEqual(store["state"], "absent")
        self.assertEqual(store["items"], [])
        self.assertEqual(store["total"], 0)

    def test_empty_store(self):
        self.fixture = StoreFixture()
        store = viewer.load_store(self.fixture.root)
        self.assertEqual(store["state"], "empty")
        self.assertEqual(store["items"], [])

    def test_readme_only_store_is_still_empty(self):
        self.fixture = StoreFixture()
        self.fixture.write("README.md", "# the store\n")
        store = viewer.load_store(self.fixture.root)
        self.assertEqual(store["state"], "empty")

    def test_malformed_item_is_badged_not_dropped(self):
        self.fixture = StoreFixture()
        self.fixture.write("debt-good.md", item_text())
        self.fixture.write("debt-broken.md", "type: debt\nno delimiters here\n")
        store = viewer.load_store(self.fixture.root)
        self.assertEqual(store["total"], 2)
        broken = [i for i in store["items"] if i["id"] == "debt-broken"][0]
        self.assertIsNotNone(broken["parse_error"])
        self.assertIn("no delimiters here", broken["raw"])
        self.assertEqual(broken["fields"], {})
        self.assertIn("no delimiters here", broken["search"])

    def test_unresolvable_relationship(self):
        self.fixture = StoreFixture()
        self.fixture.write("debt-a.md", item_text(possibly_related_to="debt-nowhere"))
        store = viewer.load_store(self.fixture.root)
        self.assertEqual(store["items"][0]["related"],
                         {"id": "debt-nowhere", "resolved": False, "archived": False})

    def test_relationship_named_by_bare_slug(self):
        self.fixture = StoreFixture()
        self.fixture.write("debt-a.md", item_text(possibly_related_to="target"))
        self.fixture.write("debt-target.md", item_text(), archived=True)
        store = viewer.load_store(self.fixture.root)
        source = [i for i in store["items"] if i["id"] == "debt-a"][0]
        self.assertEqual(source["related"],
                         {"id": "debt-target", "resolved": True, "archived": True})

    def test_archived_items_are_flagged(self):
        self.fixture = StoreFixture()
        self.fixture.write("debt-closed-one.md", item_text(status="closed"), archived=True)
        store = viewer.load_store(self.fixture.root)
        self.assertTrue(store["items"][0]["archived"])

    def test_item_with_empty_files_is_present_and_findable(self):
        self.fixture = StoreFixture()
        self.fixture.write("backlog-no-files.md", item_text(type="backlog", files="[]"))
        store = viewer.load_store(self.fixture.root)
        self.assertEqual(store["total"], 1)
        self.assertEqual(store["items"][0]["fields"]["files"], [])
        self.assertIn("backlog-no-files", store["items"][0]["search"])


class TestFacets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = viewer.load_store(repo_root())

    def values(self, field, store=None):
        facets = (store or self.store)["facets"]
        return [entry["value"] for entry in facets[field]]

    def test_all_four_fields_are_faceted(self):
        self.assertEqual(list(self.store["facets"].keys()), list(viewer.FACET_FIELDS))

    def test_counts_sum_to_the_item_total(self):
        for field in viewer.FACET_FIELDS:
            total = sum(entry["count"] for entry in self.store["facets"][field])
            self.assertEqual(total, len(self.store["items"]), field)

    def test_severity_is_ranked_worst_first_with_none_last(self):
        self.assertEqual(self.values("severity"), ["P2", "P3", "Nit", None])

    def test_status_follows_the_lifecycle_order(self):
        self.assertEqual(self.values("status"), ["open", "promoted", "closed"])

    def test_ranked_values_with_no_live_item_emit_no_entry(self):
        self.assertNotIn("in-progress", self.values("status"))
        self.assertNotIn("P1", self.values("severity"))

    def test_missing_bucket_uses_a_null_sentinel_not_the_string_none(self):
        entry = [e for e in self.store["facets"]["severity"] if e["value"] is None][0]
        self.assertEqual(entry["label"], "none")

    def test_type_and_scope_sort_alphabetically(self):
        self.assertEqual(self.values("type"), ["backlog", "debt"])
        self.assertEqual(self.values("scope"), ["repo"])


class TestFacetsWithNoLiveSample(unittest.TestCase):
    """Success Criterion 2's fixture at the unit level — values the store has none of."""

    def setUp(self):
        self.fixture = StoreFixture()
        self.fixture.write("debt-plugin-scoped.md", item_text(scope="plugin"))
        self.fixture.write("debt-in-flight.md", item_text(status="in-progress"))
        self.fixture.write("debt-off-contract.md", item_text(severity="P7"))
        self.fixture.write("debt-worst.md", item_text(severity="Nit"))
        self.fixture.write("debt-plain.md", item_text())
        self.fixture.write("debt-promoted.md", item_text(status="promoted"))
        self.store = viewer.load_store(self.fixture.root)

    def tearDown(self):
        self.fixture.cleanup()

    def values(self, field):
        return [entry["value"] for entry in self.store["facets"][field]]

    def test_scope_plugin_produces_a_facet(self):
        self.assertIn("plugin", self.values("scope"))

    def test_in_progress_sorts_between_open_and_promoted(self):
        self.assertEqual(self.values("status"), ["open", "in-progress", "promoted"])

    def test_out_of_contract_severity_sorts_after_ranked_values_and_before_none(self):
        self.assertEqual(self.values("severity"), ["Nit", "P7", None])

    def test_selecting_a_derived_value_never_hides_the_item_carrying_it(self):
        for field, value in (("scope", "plugin"), ("status", "in-progress"), ("severity", "P7")):
            entry = [e for e in self.store["facets"][field] if e["value"] == value][0]
            self.assertEqual(entry["count"], 1, "%s: %s" % (field, value))


def store_literal(html):
    """The JSON literal the page embeds. json.dumps emits no raw newline, so it is one line."""
    marker = "const STORE = "
    start = html.index(marker) + len(marker)
    line = html[start:].split("\n", 1)[0]
    return line.rstrip().rstrip(";")


class TestRenderPage(unittest.TestCase):
    def setUp(self):
        self.fixture = StoreFixture()

    def tearDown(self):
        self.fixture.cleanup()

    def hostile_store(self):
        body = "</script><!-- & <img src=x onerror=alert(1)>     done"
        self.fixture.write("debt-hostile.md", item_text() + "\n" + body + "\n")
        return viewer.load_store(self.fixture.root)

    def test_placeholder_does_not_survive(self):
        html = viewer.render_page(self.hostile_store())
        self.assertNotIn("__STORE_JSON__", html)

    def test_hostile_text_is_inert_inside_the_script_literal(self):
        literal = store_literal(viewer.render_page(self.hostile_store()))
        for sequence in ("</script>", "<!--", "<", ">", "&", "\u2028", "\u2029"):
            self.assertNotIn(sequence, literal, sequence)

    def test_literal_round_trips_through_json_loads(self):
        store = self.hostile_store()
        literal = store_literal(viewer.render_page(store))
        self.assertEqual(json.loads(literal), store)

    def test_primary_path_never_reaches_the_page(self):
        html = viewer.render_page(viewer.load_store(self.fixture.root))
        self.assertNotIn(self.fixture.root, html)
        self.assertNotIn('"primary"', html)

    def test_absent_store_still_renders_a_complete_document(self):
        empty = StoreFixture(make_dir=False)
        try:
            html = viewer.render_page(viewer.load_store(empty.root))
        finally:
            empty.cleanup()
        self.assertTrue(html.startswith("<!doctype html>"))
        self.assertIn("</html>", html)
        self.assertIn("docs/backlog/ doesn't exist in this repo.", html)

    def test_document_carries_the_dom_contract(self):
        html = viewer.render_page(viewer.load_store(repo_root()))
        for element_id in ("repo", "count", "sort", "search", "rail", "clear", "list",
                           "detail", "detail-resting", "detail-resting-count",
                           "empty-filters", "empty-store", "empty-absent"):
            self.assertIn('id="%s"' % element_id, html, element_id)
        for option in ('value="first_recorded"', 'value="recurrence"'):
            self.assertIn(option, html, option)

    def test_page_fetches_nothing_external(self):
        html = viewer.render_page(viewer.load_store(repo_root()))
        for pattern in ("<link", "src=\"http", "@import", "<script src"):
            self.assertNotIn(pattern, html, pattern)

    def test_missing_template_is_a_named_error(self):
        original = viewer.TEMPLATE_PATH
        viewer.TEMPLATE_PATH = original.with_name("no_such_template.html")
        try:
            with self.assertRaises(RuntimeError) as ctx:
                viewer.render_page(viewer.load_store(self.fixture.root))
            self.assertIn("no_such_template.html", str(ctx.exception))
        finally:
            viewer.TEMPLATE_PATH = original


class ServerFixture(object):
    """A live viewer on an ephemeral loopback port, torn down with the test."""

    def __init__(self, primary):
        self.server = viewer.make_server(primary, 0)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()

    @property
    def base(self):
        return "http://127.0.0.1:%d" % self.port

    def request(self, path="/", method="GET", host=None):
        request = urllib.request.Request(self.base + path, method=method)
        if host:
            request.add_header("Host", host)
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                return response.getcode(), response.headers, response.read()
        except urllib.error.HTTPError as exc:
            return exc.code, exc.headers, exc.read()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)


class TestHttpServer(unittest.TestCase):
    def setUp(self):
        self.fixture = StoreFixture()
        self.fixture.write("debt-served.md", item_text())
        self.server = ServerFixture(self.fixture.root)

    def tearDown(self):
        self.server.stop()
        self.fixture.cleanup()

    def test_binds_loopback_only(self):
        self.assertEqual(self.server.server.server_address[0], "127.0.0.1")

    def test_root_serves_the_page(self):
        status, headers, body = self.server.request("/")
        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "text/html; charset=utf-8")
        self.assertIn(b"debt-served", body)

    def test_every_response_advertises_its_identity(self):
        for path, expected in (("/", 200), ("/nope", 404)):
            status, headers, _ = self.server.request(path)
            self.assertEqual(status, expected)
            self.assertEqual(headers[viewer.IDENTITY_HEADER], self.fixture.root)
            self.assertEqual(int(headers[viewer.PID_HEADER]), os.getpid())
            self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
            self.assertEqual(headers["Cache-Control"], "no-store")

    def test_unknown_path_is_404(self):
        status, _, _ = self.server.request("/nope")
        self.assertEqual(status, 404)

    def test_query_string_on_root_is_ignored(self):
        status, _, _ = self.server.request("/?status=open")
        self.assertEqual(status, 200)

    def test_foreign_host_header_is_refused(self):
        status, _, _ = self.server.request("/", host="evil.example.com")
        self.assertEqual(status, 403)

    def test_loopback_host_names_are_accepted(self):
        for host in ("127.0.0.1:%d" % self.server.port, "localhost:%d" % self.server.port):
            status, _, _ = self.server.request("/", host=host)
            self.assertEqual(status, 200, host)

    def test_head_returns_headers_without_a_body(self):
        status, headers, body = self.server.request("/", method="HEAD")
        self.assertEqual(status, 200)
        self.assertEqual(body, b"")
        self.assertIn(viewer.IDENTITY_HEADER, headers)

    def test_write_methods_are_unsupported(self):
        for method in ("POST", "PUT", "DELETE"):
            status, _, _ = self.server.request("/", method=method)
            self.assertEqual(status, 501, method)

    def test_store_is_re_read_on_every_request(self):
        _, _, first = self.server.request("/")
        self.assertNotIn(b"debt-added-later", first)
        self.fixture.write("debt-added-later.md", item_text())
        _, _, second = self.server.request("/")
        self.assertIn(b"debt-added-later", second)
        self.assertNotEqual(first, second)

    def test_a_render_failure_does_not_take_the_server_down(self):
        original = viewer.TEMPLATE_PATH
        viewer.TEMPLATE_PATH = original.with_name("no_such_template.html")
        try:
            status, headers, _ = self.server.request("/")
            self.assertEqual(status, 500)
            self.assertIn(viewer.IDENTITY_HEADER, headers)
        finally:
            viewer.TEMPLATE_PATH = original
        status, _, _ = self.server.request("/")
        self.assertEqual(status, 200)


def a_closed_port():
    """An ephemeral port that nothing is listening on."""
    sock = socket.socket()
    try:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]
    finally:
        sock.close()


class PlainHandler(BaseHTTPRequestHandler):
    """A server that answers but is not ours — no identity header."""

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Length", "0")
        self.end_headers()

    do_GET = do_HEAD

    def log_message(self, fmt, *args):
        pass


class TestProbe(unittest.TestCase):
    def setUp(self):
        self.fixture = StoreFixture()
        self.fixture.write("debt-probed.md", item_text())
        self.server = ServerFixture(self.fixture.root)

    def tearDown(self):
        self.server.stop()
        self.fixture.cleanup()

    def test_a_live_viewer_identifies_itself(self):
        kind, info = viewer.probe(self.server.port)
        self.assertEqual(kind, "viewer")
        self.assertEqual(info["primary"], self.fixture.root)
        self.assertEqual(info["pid"], os.getpid())
        self.assertEqual(info["port"], self.server.port)

    def test_a_closed_port_is_free(self):
        self.assertEqual(viewer.probe(a_closed_port()), ("free", None))

    def test_a_server_that_is_not_ours_is_other(self):
        other = HTTPServer(("127.0.0.1", 0), PlainHandler)
        thread = threading.Thread(target=other.serve_forever)
        thread.daemon = True
        thread.start()
        try:
            self.assertEqual(viewer.probe(other.server_address[1]), ("other", None))
        finally:
            other.shutdown()
            other.server_close()
            thread.join(timeout=5)

    def test_find_running_matches_on_the_primary(self):
        original = viewer.PORT_RANGE
        viewer.PORT_RANGE = [self.server.port]
        try:
            self.assertIsNone(viewer.find_running(os.path.join(self.fixture.root, "elsewhere")))
            found = viewer.find_running(self.fixture.root)
            self.assertIsNotNone(found)
            self.assertEqual(found["port"], self.server.port)
            # A viewer for another checkout still occupies its port.
            self.assertEqual(viewer.free_ports(), [])
        finally:
            viewer.PORT_RANGE = original


class TestCliRoundTrip(unittest.TestCase):
    """start -> start again -> stop, against the real repo and the real port range."""

    def setUp(self):
        self.primary = viewer.resolve_primary(repo_root())
        if viewer.find_running(self.primary):
            self.skipTest("a backlog viewer is already running for this repo")

    def tearDown(self):
        running = viewer.find_running(self.primary)
        if running and running.get("pid"):
            try:
                os.kill(running["pid"], signal.SIGTERM)
            except (OSError, ProcessLookupError):
                pass

    def capture(self, call):
        buffer = io.StringIO()
        stdout = sys.stdout
        sys.stdout = buffer
        try:
            code = call()
        finally:
            sys.stdout = stdout
        return code, buffer.getvalue()

    def test_start_is_idempotent_and_stop_shuts_it_down(self):
        code, first_output = self.capture(lambda: viewer.cmd_start(self.primary))
        self.assertEqual(code, 0, first_output)
        self.assertIn("Backlog viewer running at", first_output)

        running = viewer.find_running(self.primary)
        self.assertIsNotNone(running)
        url = "http://127.0.0.1:%d" % running["port"]
        self.assertIn(url, first_output)
        self.assertIn(self.primary, first_output)

        code, second_output = self.capture(lambda: viewer.cmd_start(self.primary))
        self.assertEqual(code, 0, second_output)
        self.assertIn("Backlog viewer is already running at", second_output)
        self.assertIn(url, second_output)
        # Nothing new was spawned: the same process is still answering.
        self.assertEqual(viewer.find_running(self.primary)["pid"], running["pid"])

        code, stop_output = self.capture(lambda: viewer.cmd_stop(self.primary))
        self.assertEqual(code, 0, stop_output)
        self.assertEqual(stop_output.strip(), "Backlog viewer stopped.")
        self.assertIsNone(viewer.find_running(self.primary))

        code, again = self.capture(lambda: viewer.cmd_stop(self.primary))
        self.assertEqual(code, 0)
        self.assertEqual(again.strip(), "No backlog viewer is running for this repo.")

    def test_the_detached_server_serves_the_repo_store(self):
        self.capture(lambda: viewer.cmd_start(self.primary))
        running = viewer.find_running(self.primary)
        self.assertIsNotNone(running)
        with urllib.request.urlopen("http://127.0.0.1:%d/" % running["port"], timeout=5) as response:
            page = response.read().decode("utf-8")
        self.assertIn("dev backlog", page)
        self.capture(lambda: viewer.cmd_stop(self.primary))


class TestCliArguments(unittest.TestCase):
    def capture(self, argv):
        buffer = io.StringIO()
        stdout = sys.stdout
        sys.stdout = buffer
        try:
            code = viewer.main(argv)
        finally:
            sys.stdout = stdout
        return code, buffer.getvalue()

    def test_serve_requires_a_port(self):
        code, output = self.capture(["serve"])
        self.assertEqual(code, 1)
        self.assertIn("--port", output)

    def test_unknown_command_is_reported(self):
        code, output = self.capture(["frobnicate"])
        self.assertEqual(code, 1)
        self.assertIn("frobnicate", output)

    def test_primary_failure_prints_the_designed_copy(self):
        tmp = tempfile.mkdtemp()
        cwd = os.getcwd()
        os.chdir(tmp)
        try:
            code, output = self.capture(["stop"])
        finally:
            os.chdir(cwd)
            shutil.rmtree(tmp, ignore_errors=True)
        self.assertEqual(code, 1)
        self.assertIn("Can't resolve the repository root, so there's no store to serve.", output)
        self.assertIn("Run this from inside the repository.", output)


class TestNoWritePath(unittest.TestCase):
    """The mechanical half of "the server never writes to disk"."""

    WRITE_CALLS = (
        re.compile(r"""open\([^)]*['"][waxr]\+?[bt]?['"]"""),
        re.compile(r"os\.(remove|unlink|rmdir|rename|replace|makedirs|mkdir)\b"),
        re.compile(r"shutil\.\w+"),
        re.compile(r"\.write_text\("),
    )

    def test_viewer_module_contains_no_file_write(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "viewer.py"),
                  encoding="utf-8") as handle:
            source = handle.read()
        for pattern in self.WRITE_CALLS:
            self.assertIsNone(pattern.search(source), pattern.pattern)


class TestResolvePrimary(unittest.TestCase):
    def test_resolves_from_inside_the_repo(self):
        primary = viewer.resolve_primary(os.path.dirname(os.path.abspath(__file__)))
        self.assertTrue(os.path.isdir(primary))
        self.assertTrue(os.path.isdir(os.path.join(primary, ".git")) or
                        os.path.isfile(os.path.join(primary, ".git")))

    def test_same_answer_from_the_repo_root_and_from_a_subdirectory(self):
        root = repo_root()
        self.assertEqual(viewer.resolve_primary(root),
                         viewer.resolve_primary(os.path.join(root, "plugins", "dev")))

    def test_outside_a_repository_raises(self):
        tmp = tempfile.mkdtemp()
        try:
            with self.assertRaises(viewer.PrimaryError):
                viewer.resolve_primary(tmp)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
