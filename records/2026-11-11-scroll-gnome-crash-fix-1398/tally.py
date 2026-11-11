#!/usr/bin/env python3
"""tally.py RUN...: iterations and Shell crashes per variant and per delay, from loop.jsonl."""
import json, sys, collections
from pathlib import Path
for name in sys.argv[1:]:
    rows = [json.loads(l) for l in (Path.home() / 'work/fx5' / name / 'loop.jsonl').read_text().splitlines()]
    its = [r for r in rows if 'i' in r and not r.get('fatal')]
    per = collections.OrderedDict()
    prev = None
    crashes = 0
    for r in rows:
        if 'i' in r and not r.get('fatal'):
            per.setdefault(r['delay'], [0, 0])[0] += 1
            if r.get('crash'):
                per[r['delay']][1] += 1; crashes += 1
            prev = r
        elif (r.get('fatal') and r.get('crash')) or r.get('lateCrash'):
            # the Shell died after the previous iteration's own check
            if prev is not None:
                per[prev['delay']][1] += 1
            crashes += 1
    states = collections.Counter(json.dumps({k: r.get(k) for k in ('prepare', 'ready', 'start', 'after', 'cancel', 'quit') if k in r}) for r in its)
    print('%s: %d iterations, %d Shell crashes; by delay %s' % (name, len(its), crashes, ', '.join('%gs %d/%d' % (d, c, n) for d, (n, c) in per.items())))
    for s, n in states.most_common(4):
        print('   %3d x %s' % (n, s))
