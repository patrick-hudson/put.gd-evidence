#!/usr/bin/env python3
"""cmp.py HOSTDIR BEFORE AFTER... : text identity and helper totalMs / peak for #1808."""
import json, statistics, sys
from pathlib import Path
d = Path(sys.argv[1]); before = sys.argv[2]; afters = sys.argv[3:]
def load(L): return {r['id']: r for r in json.loads((d / L / 'rows.json').read_text())}
B = load(before)
def big(r): return r.get('dims') and r['dims'][0] * r['dims'][1] >= 4_000_000
def groups(R):
    g = {'all': list(R.values())}
    g['screens_1080p'] = [r for r in R.values() if r['cls'] == 'monitor' and not big(r)]
    g['screens_4mp+'] = [r for r in R.values() if big(r)]
    g['gnome4k'] = [r for r in R.values() if r['id'].startswith('gnome4k')]
    return g
def stat(rs):
    ok = [r for r in rs if r['status'] == 'ok']
    t = [r['totalMs'] / 1000 for r in ok if r.get('totalMs') is not None]
    pk = [r.get('peakKiB') or r.get('peakRssKiB') or 0 for r in ok]
    return dict(n=len(ok), failed=len(rs) - len(ok), sum_s=round(sum(t), 2), mean_s=round(statistics.mean(t), 3) if t else None,
                median_s=round(statistics.median(t), 3) if t else None, peak_max_MiB=round(max(pk) / 1024, 1) if pk else None)
out = {before: {k: stat(v) for k, v in groups(B).items()}}
for L in afters:
    A = load(L)
    same = sum(1 for i in B if i in A and A[i]['status'] == 'ok' and B[i]['status'] == 'ok' and A[i].get('text') == B[i].get('text'))
    diff = [i for i in B if i in A and A[i]['status'] == 'ok' and B[i]['status'] == 'ok' and A[i].get('text') != B[i].get('text')]
    out[L] = {k: stat(v) for k, v in groups(A).items()}
    out[L]['identical_to_before'] = f'{same}/{len(B)}'
    out[L]['differs'] = diff
    out[L]['top_peaks'] = sorted(((round((r.get('peakKiB') or r.get('peakRssKiB') or 0) / 1024, 1), i) for i, r in A.items() if r['status'] == 'ok'), reverse=True)[:5]
    out[L]['gnome4k_rows'] = {i: (r.get('totalMs'), round((r.get('peakKiB') or r.get('peakRssKiB') or 0) / 1024, 1)) for i, r in A.items() if i.startswith('gnome4k')}
out[before]['gnome4k_rows'] = {i: (r.get('totalMs'), round((r.get('peakKiB') or r.get('peakRssKiB') or 0) / 1024, 1)) for i, r in B.items() if i.startswith('gnome4k')}
print(json.dumps(out, indent=1))
