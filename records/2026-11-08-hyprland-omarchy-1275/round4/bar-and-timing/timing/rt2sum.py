#!/usr/bin/env python3
"""rt2sum.py TRIALS.jsonl SYNC.log [WL.log]: per trial, independent-client wl_display.sync stalls next to the catcher's timeline (ms after the hotkey)."""
import json, re, statistics, sys
rows = [json.loads(l) for l in open(sys.argv[1])]
stalls = []
for l in open(sys.argv[2], errors='replace'):
    if l.startswith('#'): continue
    p = l.split()
    if len(p) == 2: stalls.append((float(p[0]), float(p[1])))
stamp = re.compile(r'^\[(\d\d):(\d\d):(\d\d\.\d+)\]\s+(?:\{[^}]*\}\s+)?(.*)')
lines = []
if len(sys.argv) > 3:
    for raw in open(sys.argv[3], errors='replace'):
        m = stamp.match(raw)
        if m: lines.append((int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)), m.group(4)))
out = []
for r in rows:
    t0 = r['hotkeyGuest']; base = t0 % 86400
    ev = [((t - base) * 1000, x) for t, x in lines if -0.2 <= t - base <= 4]
    def first(p):
        for d, x in ev:
            if re.search(p, x): return d, x
        return None, None
    ms = lambda s: (s - t0) * 1000
    # round trips that overlap a window: [start, start+dur]
    def worst(a, b): return max([d for s, d in stalls if ms(s) <= b and ms(s) + d >= a] or [0.0])
    def blocked(a, b):  # total ms the compositor answered nothing in [a,b]
        return sum(min(ms(s) + d, b) - max(ms(s), a) for s, d in stalls if ms(s) <= b and ms(s) + d >= a)
    row = {'trial': r['trial'], 'outcome': r.get('outcome', 'control'), 'load1': r.get('load1')}
    pe, _ = first(r'hyprland_global_shortcut_v1#\d+\.pressed'); req, line = first(r'get_layer_surface.*putgd-region-catcher')
    if req is not None:
        lay = re.search(r'new id zwlr_layer_surface_v1#(\d+)', line).group(1)
        conf, _ = first(r'zwlr_layer_surface_v1#%s\.configure' % lay)
        row.update({'pressedEvent': pe and round(pe, 1), 'requestAfterEvent': round(req - pe, 1), 'configure': conf and round(conf, 1), 'requestToConfigure': conf and round(conf - req, 1), 'pressAt': r.get('pressAfter') and round(r['pressAfter'] * 1000, 1), 'syncWorstRequestToConfigure': conf and round(worst(req, conf), 1), 'syncBlockedRequestToConfigure': conf and round(blocked(req, conf), 1)})
    row['syncWorst0to1000'] = round(worst(0, 1000), 1); row['syncBlocked0to1000'] = round(blocked(0, 1000), 1)
    out.append(row); print(json.dumps(row))
# summary
def med(k, rs):
    v = [r[k] for r in rs if r.get(k) is not None]; return round(statistics.median(v), 1) if v else None
keys = ['pressedEvent', 'requestAfterEvent', 'requestToConfigure', 'syncWorst0to1000', 'syncBlocked0to1000']
print(json.dumps({'median': {k: med(k, out) for k in keys}, 'n': len(out), 'tally': {o: sum(1 for r in out if r['outcome'] == o) for o in {r['outcome'] for r in out}}}))
