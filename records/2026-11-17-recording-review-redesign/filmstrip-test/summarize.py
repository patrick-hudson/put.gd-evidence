#!/usr/bin/env python3
"""Print markdown summaries from run_bench.py JSON Lines."""
import json
import math
from pathlib import Path
from statistics import median
import sys

def pct95(values):
    return sorted(values)[math.ceil(0.95 * len(values)) - 1]

def pair(values, decimals=1):
    return f"{median(values):.{decimals}f} / {pct95(values):.{decimals}f}"

for arg in sys.argv[1:]:
    log = Path(arg)
    cases = {}
    for line in log.read_text().splitlines():
        run = json.loads(line)
        cases.setdefault((run["mode"], run["n"]), []).append(run)
    print(f"### {log.stem}\n")
    print("| Mode | N | Warm runs | Cold wall ms | Warm wall ms | First 2 ms cold | First 2 ms warm | Per request ms warm | CPU cores warm | Peak RSS MiB warm | Other cores warm |")
    print("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for (mode, count), runs in cases.items():
        cold = next(r for r in runs if r["cache"] == "cold")
        warm = [r for r in runs if r["cache"] == "warm"]
        if not warm:
            continue
        calls = [ms for r in warm for ms in r.get("calls_ms", [])]
        ends = warm[0].get("first_two_ms", 0) if mode in {"A", "An", "B"} else 0
        print("| " + " | ".join([
            mode, str(count or "—"), str(len(warm)), f"{cold['wall_ms']:.1f}",
            pair([r["wall_ms"] for r in warm]),
            f"{cold['first_two_ms']:.1f}" if ends else "—",
            pair([r["first_two_ms"] for r in warm]) if ends else "—",
            pair(calls) if calls else "—",
            pair([r["cpu_cores"] for r in warm], 2),
            pair([r["rss_kib"] / 1024 for r in warm]),
            pair([r["other_cores"] for r in warm], 2),
        ]) + " |")
    print()
