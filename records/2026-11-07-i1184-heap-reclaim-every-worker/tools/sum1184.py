#!/usr/bin/env python3
"""sum1184.py RESULT.json... — per (build, method) medians over blocks of anonymous MiB before/5 s/35 s after, and reclamations."""
import json, sys, statistics, collections
rows = collections.defaultdict(list)
for p in sys.argv[1:]:
    r = json.load(open(p)); build = r['identity']['gitCommit'][:12]
    for b in r['blocks']: rows[(build, b['method'])].append(b)
print('| Build | Call | Blocks | Before | 5 s after | 35 s after | Retained | Reclamations |')
print('|---|---|---|---|---|---|---|---|')
for (build, method), bs in sorted(rows.items(), key=lambda kv: (kv[0][1], kv[0][0])):
    m = lambda k: statistics.median(x[k]['Anonymous'] for x in bs) / 1024
    rec = statistics.median(x['reclaims'] for x in bs)
    print(f'| `{build}` | `{method}` | {len(bs)} | {m("before"):.2f} | {m("after5"):.2f} | {m("after35"):.2f} | {m("after35")-m("before"):+.2f} | {rec:g} |')
