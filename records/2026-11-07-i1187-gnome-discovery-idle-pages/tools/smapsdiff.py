#!/usr/bin/env python3
"""smapsdiff.py A.smaps B.smaps [N] — per-file resident (Rss minus Anonymous) kB in A and B, biggest |B-A| first."""
import sys, collections
def load(p):
    agg = collections.Counter(); name = None
    for line in open(p):
        f = line.split()
        if not f: continue
        if '-' in f[0] and len(f) >= 5 and ':' not in f[0]:
            name = f[5] if len(f) >= 6 else '[anon]'
            name = name.split('/')[-1] if name.startswith('/') else name
        elif f[0] == 'Rss:': agg[name] += int(f[1])
        elif f[0] == 'Anonymous:': agg[name] -= int(f[1])
    return agg
a, b = load(sys.argv[1]), load(sys.argv[2]); n = int(sys.argv[3]) if len(sys.argv) > 3 else 25
print(f'total file kB  A={sum(a.values())}  B={sum(b.values())}')
for k in sorted(set(a) | set(b), key=lambda k: -abs(b[k] - a[k]))[:n]:
    print(f'{b[k]-a[k]:+7d}  A={a[k]:6d}  B={b[k]:6d}  {k}')
