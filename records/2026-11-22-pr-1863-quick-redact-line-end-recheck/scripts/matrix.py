#!/usr/bin/env python3
"""Summarize the revised-build recheck and link its machine-readable reports."""
import json
from pathlib import Path
import sys

root = Path(sys.argv[1])
rows = [
    ("1", "Token, cards and signing hex"),
    ("3", "Token and AWS key"),
    ("4", "Token and plain words"),
    ("6", "Token, right card and distant card"),
    ("5-jwt", "Unlabelled three-row JWT"),
    ("5-jwt-labeled", "Labelled three-row JWT"),
    ("5-hex", "Four-letter hex tail"),
    ("5-hex-three", "Three-letter hex tail"),
    ("a-dot-jwt", "JWT wrapped at its first dot"),
    ("b-long-jwt", "731-character JWT in xed"),
    ("c-loose-hex", "Three-letter hex tail at 2.2 line-height"),
]
print("| Case | Result | Nonzero counts | Visible redaction rectangles |")
print("| --- | --- | --- | ---: |")
for key, name in rows:
    rel = Path("m74/recheck") / key / "pixels.json"
    report = json.loads((root / rel).read_text())
    status = "Pass" if report["pass"] else "Fail"
    counts = ", ".join(f"{report['counts'][kind]} {kind}" for kind in ("key", "card", "email", "ip", "phone")
                       if report["counts"].get(kind)) or "None"
    print(f"| {name} | [{status}]({rel}) | {counts} | {len(report['marks'])} |")
