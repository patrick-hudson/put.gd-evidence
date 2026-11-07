#!/usr/bin/env python3
"""sum1187.py RESULT.json... — per run: build, mode, median RSS and file-backed MiB over idle windows, releases, helper state."""
import json, sys, statistics
WINDOWS = [(100, 185), (190, 240), (245, 300)]
print('| Run | Build | Extension | ' + ' | '.join(f'{a}-{b} s RSS / file' for a, b in WINDOWS) + ' | Page releases | Helper at end |')
print('|---|---|---|' + '---|' * len(WINDOWS) + '---|---|')
for p in sys.argv[1:]:
    r = json.load(open(p)); s = {d['t']: d for d in r['series']}
    cells = []
    for a, b in WINDOWS:
        ts = [t for t in range(a, b + 1, 5) if t in s]
        cells.append(f"{statistics.median(s[t]['Rss'] for t in ts)/1024:.2f} / {statistics.median(s[t]['file'] for t in ts)/1024:.2f}" if ts else '')
    mem = r.get('diagnostics_memory') or {}
    print(f"| {r['name']} | `{r['identity']['gitCommit'][:12]}` | {r['mode']} | " + ' | '.join(cells) + f" | {mem.get('imagePageReleaseCount')} | {(r.get('source') or {}).get('helper', {}).get('available')} |")
