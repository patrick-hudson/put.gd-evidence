#!/usr/bin/env python3
"""Keep records/README.md complete.

  index.py          add a row for every top-level records/ entry the index does not link
  index.py --check  report those entries and change nothing

Exit status: 0 complete or written, 1 --check found missing entries, 2 the index
could not be read or the repository could not be queried.

Entries come from the HEAD commit's tree and titles from its blobs, so this works
in a sparse blobless clone and downloads only the READMEs it needs. Existing rows
are never changed; run it from the repository root after committing the record.
"""
from __future__ import annotations

import argparse
import calendar
import os
import re
import sys
from collections import defaultdict
from urllib.parse import quote, unquote

from check import GitError, decode_text, git, readme_title

INDEX = "records/README.md"
TABLE_HEAD = "| Record | Issue / PR | Summary |"
TABLE_RULE = "| --- | --- | --- |"
UNDATED = "Undated"
NONE = "—"

MONTHS = {name: number for number, name in enumerate(calendar.month_name) if name}
MONTH_HEADING = re.compile(r"^## ([A-Z][a-z]+) (\d{4})$")
DATED_NAME = re.compile(r"^(\d{4})-(\d{2})-\d{2}-")
TRAILING_NUMBER = re.compile(r"^\d{4}-\d{2}-\d{2}-(?:.*-)?(\d+)$")
ISSUE_REFERENCE = re.compile(r"(?<![\w&])#(\d+)\b")
FIRST_CELL = re.compile(r"^\|((?:[^|\\]|\\.)*)\|")
LINK_TARGET = re.compile(r"\]\(([^)\s]+)\)")


def linked_entries(lines):
    """Return the top-level records named in the first cell of any table row."""
    linked = set()
    for line in lines:
        cell = FIRST_CELL.match(line)
        if not cell:
            continue
        for target in LINK_TARGET.findall(cell[1]):
            path = unquote(target.split("#", 1)[0]).removeprefix("./")
            if path and not path.startswith("..") and ":" not in path:
                linked.add(path.split("/", 1)[0])
    return linked


def tree_entries():
    """Map each top-level entry under records/ at HEAD to its git object type."""
    entries = {}
    output = git("ls-tree", "-z", "--full-tree", "HEAD", "--", "records/")
    for item in output.split(b"\0"):
        if item:
            meta, path = item.split(b"\t", 1)
            name = os.fsdecode(path)[len("records/"):]
            if name != "README.md":
                entries[name] = meta.decode().split()[1]
    return entries


def blob_title(path):
    return readme_title(decode_text(git("cat-file", "blob", f"HEAD:{path}")))


def row_for(name, kind):
    """Build the table row for one entry."""
    quoted = quote(name, safe="")
    title = None
    if kind == "blob":
        link = quoted
        stem = os.path.splitext(name)[0]
        if name.endswith(".md"):
            title = blob_title(f"records/{name}")
    else:
        stem = name
        listing = git("ls-tree", "--full-tree", "--name-only", "HEAD", "--",
                      f"records/{name}/README.md").strip()
        if listing:
            link = f"{quoted}/README.md"
            title = blob_title(f"records/{name}/README.md")
        else:
            link = f"{quoted}/"
    numbers = {int(number) for number in ISSUE_REFERENCE.findall(title or "")}
    trailing = TRAILING_NUMBER.match(stem)
    if trailing:
        numbers.add(int(trailing[1]))
    issues = ", ".join(f"#{number}" for number in sorted(numbers)) or NONE
    summary = (title or NONE).replace("|", "\\|")
    return f"| [{name}]({link}) | {issues} | {summary} |"


def section_for(name):
    dated = DATED_NAME.match(name)
    if dated and 1 <= int(dated[2]) <= 12:
        return f"{calendar.month_name[int(dated[2])]} {dated[1]}"
    return UNDATED


def month_key(heading):
    parsed = MONTH_HEADING.match(heading)
    if parsed and parsed[1] in MONTHS:
        return (int(parsed[2]), MONTHS[parsed[1]])
    return None


def new_section_position(lines, heading):
    """Find where a missing section goes: months newest first, then Undated."""
    key = month_key(heading)
    months = [(i, month_key(line)) for i, line in enumerate(lines) if month_key(line)]
    if key:
        for position, existing in months:
            if existing < key:
                return position
    start = months[-1][0] + 1 if months else 0
    for position in range(start, len(lines)):
        if lines[position].startswith("## "):
            return position
    return len(lines)


def add_rows(lines, section, rows):
    heading = f"## {section}"
    if heading not in lines:
        position = new_section_position(lines, heading)
        block = [heading, "", TABLE_HEAD, TABLE_RULE, *rows, ""]
        if position == len(lines):
            while lines and not lines[-1]:
                lines.pop()
            position = len(lines)
            if lines:
                block.insert(0, "")
        lines[position:position] = block
        return
    start = lines.index(heading) + 1
    for position in range(start, len(lines)):
        if lines[position].startswith("## "):
            break
        if lines[position].startswith("| ---"):
            lines[position + 1:position + 1] = rows
            return
    lines[start:start] = ["", TABLE_HEAD, TABLE_RULE, *rows]


def main():
    sys.stderr.reconfigure(errors="backslashreplace")
    parser = argparse.ArgumentParser(description="Keep records/README.md complete.")
    parser.add_argument("--check", action="store_true",
                        help="report missing entries and change nothing")
    args = parser.parse_args()
    try:
        root = git("rev-parse", "--show-toplevel").decode().rstrip("\n")
        os.chdir(root)
        with open(INDEX, encoding="utf-8", newline="") as index:
            lines = index.read().split("\n")
        entries = tree_entries()
        missing = sorted(set(entries) - linked_entries(lines))
        if args.check:
            for name in missing:
                print(f"{INDEX}: no row for {name}", file=sys.stderr)
            return 1 if missing else 0
        sections = defaultdict(list)
        for name in sorted(missing, reverse=True):
            sections[section_for(name)].append(row_for(name, entries[name]))
    except (GitError, OSError) as error:
        print(f"index.py: {error}", file=sys.stderr)
        return 2
    for section, rows in sections.items():
        add_rows(lines, section, rows)
    if missing:
        with open(INDEX, "w", encoding="utf-8", newline="") as index:
            index.write("\n".join(lines))
    print(f"{len(missing)} row(s) added")
    return 0


if __name__ == "__main__":
    sys.exit(main())
