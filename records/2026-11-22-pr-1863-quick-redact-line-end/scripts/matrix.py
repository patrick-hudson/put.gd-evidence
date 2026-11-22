#!/usr/bin/env python3
"""Render pass/fail and nonzero counts from the pixel reports."""
import json
from pathlib import Path
import sys

root = Path(sys.argv[1])
runs = ("m74/nightly", "m74/candidate", "k72/nightly-clean", "k72/candidate")
rows = [
    ("1", "Token, two cards and hex"),
    ("2", "Token and email"),
    ("3", "Token and AWS key"),
    ("4", "Token and plain words"),
    ("5-jwt", "JWT wrapped across three rows"),
    ("5-jwt-labeled", "Labeled JWT variant"),
    ("5-hex", "Wrapped hex with four-letter tail"),
    ("5-hex-three", "Wrapped hex with three-letter tail"),
    ("6", "Token, right card and distant card"),
]
print("| Case | Mint nightly | Mint candidate | Kubuntu nightly | Kubuntu candidate |")
print("| --- | --- | --- | --- | --- |")
for key, label in rows:
    cells = [key + " " + label]
    for run in runs:
        prefix = "m74/nightly-wrap" if run == "m74/nightly" and key in ("5-jwt-labeled", "5-hex-three") else run
        rel = Path(prefix) / key / "pixels.json"
        if not (root / rel).exists():
            cells.append("Not run")
            continue
        result = json.loads((root / rel).read_text())
        outcome = "Pass" if result["pass"] else "Fail"
        counts = ", ".join(f"{result['counts'][k]} {k}" for k in ("key", "card", "email", "phone", "ip")
                           if result["counts"].get(k))
        cells.append(f"[{outcome}]({rel}) · {counts or '0 matches'}")
    print("| " + " | ".join(cells) + " |")
