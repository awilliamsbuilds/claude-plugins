#!/usr/bin/env python3
"""Read-only browser view of the /dev backlog store (docs/backlog/).

Launched by `/dev:debt view`. Serves one loopback route that re-reads the store on
every request, so a refreshed tab always shows the current files. Never writes.

Stdlib only — the repo has no build tooling and no package manager, and PyYAML is
not available, so the front-matter parser below is hand-rolled against the schema
in plugins/dev/references/tech-debt.md.
"""

import re

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
