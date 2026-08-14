"""Tests for the dev:debt backlog viewer.

Run from the repository root with:

    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s plugins/dev/skills/debt -p 'test_*.py'

The env var matters: this module imports `viewer`, and on a Python that writes bytecode
next to the source it would drop `plugins/dev/skills/debt/__pycache__/` into the repo —
untracked files whose payloads embed absolute source paths, which the portability grep
would then find.
"""

import os
import sys
import unittest

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


if __name__ == "__main__":
    unittest.main()
