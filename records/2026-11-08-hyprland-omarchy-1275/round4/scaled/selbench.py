#!/usr/bin/env python3
"""selbench.py RUN OUTPUTS W H X1 Y1 X2 Y2 TRIALS DELAYS... : d69 host side, region selector readiness on a lab guest.
The region hotkey (Ctrl+Shift+1) goes in through QMP; a persistent guest agent (selagent.py) reports when the selector
layer is mapped. For each delay D (seconds after the hotkey), TRIALS drags from (X1,Y1) to (X2,Y2) in tablet space WxH
(the layout's bounding box). Outcome per trial: ok (a new region operation completed at the dragged size), wrong-size,
lost (no new completed operation; the selector is still up and is then cancelled with Escape) or other.
Also, 'map' trials (hotkey, wait, Escape) measure hotkey -> layer mapped. JSON lines to stdout."""
import json, statistics, subprocess, sys, time
sys.path.insert(0, '/home/patrick/work/d1275/lab/tools/lab')
import lab
run_name, outputs, W, H, x1, y1, x2, y2, trials = sys.argv[1], int(sys.argv[2]), *map(int, sys.argv[3:9]), int(sys.argv[9])
delays = [float(d) for d in sys.argv[10:]]
run = '/home/patrick/work/d1275/lab/work/lab-runs/' + run_name
agent = subprocess.Popen(['/home/patrick/work/d1275/gs.sh', run_name, '~/d/probe/hc python3 -u /home/lab/d/probe/selagent.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
def ask(line):
    agent.stdin.write(line + '\n'); agent.stdin.flush(); return json.loads(agent.stdout.readline())
def read(): return json.loads(agent.stdout.readline())
def emit(v): print(json.dumps(v), flush=True)
# Clock offset guest - host over the open channel: keep the sample with the smallest round trip.
best = None
for _ in range(25):
    a = time.time(); g = ask('t')['t']; b = time.time()
    if best is None or b - a < best[1]: best = (g - (a + b) / 2, b - a)
offset, rtt = best; emit({'offset': round(offset, 4), 'rtt': round(rtt, 4)})
def move(x, y): return [{'type': 'abs', 'data': {'axis': 'x', 'value': int(x * 32767 / (W - 1))}}, {'type': 'abs', 'data': {'axis': 'y', 'value': int(y * 32767 / (H - 1))}}]
def btn(down): return [{'type': 'btn', 'data': {'down': down, 'button': 'left'}}]
def hotkey():
    t = time.time(); lab.key(run, ['ctrl', 'shift', '1']); return t
def escape(): lab.key(run, ['esc'])
press_at = [0.0]
import os
expected = [int(v) for v in os.environ['EXPECT'].split('x')] if os.environ.get('EXPECT') else [abs(x2 - x1), abs(y2 - y1)]
cmprect = os.environ.get('CMPRECT') or f'{min(x1, x2)} {min(y1, y2)} {abs(x2 - x1)} {abs(y2 - y1)}'
prepositioned = os.environ.get('PREPOS') == '1'   # the pointer waits at the start point before the hotkey; the press has no move before it
def drag():
    if not prepositioned: lab.input_events(run, move(x1, y1)); time.sleep(0.05)
    lab.input_events(run, btn(True)); press_at[0] = time.time(); time.sleep(0.1)
    for i in range(1, 13): lab.input_events(run, move(x1 + (x2 - x1) * i / 12, y1 + (y2 - y1) * i / 12)); time.sleep(0.02)
    time.sleep(0.1); lab.input_events(run, btn(False))
def settle():
    # Leave no selector up between trials.
    for _ in range(3):
        o = ask('op')
        if o.get('state') in ('selecting', 'acquiring', 'pending'): escape(); time.sleep(1.0)
        else: return o
    return ask('op')
maps = []
for i in range(trials):
    settle(); time.sleep(0.8)
    lab.input_events(run, move(x1 - 40 if x1 > 60 else x1 + 40, y1)); time.sleep(0.2)
    ask(f'w {outputs} 6'); t = hotkey(); r = read()
    first = None if r['first'] is None else r['first'] - offset - t; full = None if r['all'] is None else r['all'] - offset - t
    maps.append(full); emit({'kind': 'map', 'trial': i, 'first': first and round(first, 3), 'all': full and round(full, 3), 'polls': r['polls']})
    time.sleep(0.4); escape(); time.sleep(1.2)
ok_maps = [m for m in maps if m is not None]
if ok_maps: emit({'kind': 'map-summary', 'n': len(ok_maps), 'median': round(statistics.median(ok_maps), 3), 'min': round(min(ok_maps), 3), 'max': round(max(ok_maps), 3)})
results = {}
for d in delays:
    for i in range(trials):
        before = settle()['id']; time.sleep(0.8)
        if prepositioned: lab.input_events(run, move(x1, y1)); time.sleep(0.3)
        ask('ref ' + os.environ.get('REFARG', ''))
        ask(f'w {outputs} 6'); t = hotkey()
        time.sleep(max(0.0, d - (time.time() - t))); drag(); pressed = press_at[0] - t
        r = read(); full = None if r['all'] is None else r['all'] - offset - t; catcher = None if r.get('catcher') is None else round(r['catcher'] - offset - t, 3)
        outcome = None; o = None
        for _ in range(20):
            o = ask('op')
            if o.get('id') != before and o.get('state') not in ('selecting', 'acquiring', 'pending'): break
            time.sleep(0.5)
        if o.get('id') != before and o.get('state') in ('completed', 'stored'): outcome = 'ok' if o.get('size') == expected else 'wrong-size'
        elif o.get('id') == before or o.get('state') in ('selecting', 'acquiring', 'pending'): outcome = 'lost'
        else: outcome = 'other'
        pixels = None
        if outcome == 'ok' and o.get('name'): pixels = ask(f"cmp {o['name']} {cmprect}")
        recovered = None
        if outcome == 'lost':
            # The selector is up: does the next drag still make the selection?
            lab.input_events(run, move(x1, y1)); time.sleep(0.2); drag()
            for _ in range(20):
                o = ask('op')
                if o.get('id') != before and o.get('state') not in ('selecting', 'acquiring', 'pending'): break
                time.sleep(0.5)
            recovered = o.get('id') != before and o.get('state') in ('completed', 'stored') and o.get('size') == expected
            if not recovered: escape(); time.sleep(1.0)
        emit({'kind': 'drag', 'delay': d, 'trial': i, 'pressedAfter': round(pressed, 3), 'mappedAfter': full and round(full, 3), 'catcherAfter': catcher, 'pixels': pixels, 'outcome': outcome, 'secondDragCompleted': recovered, 'op': {k: o.get(k) for k in ('state', 'code', 'size')}})
        results.setdefault(d, []).append(outcome + ('' if recovered is None else ('+recovered' if recovered else '+stuck')))
emit({'kind': 'drag-summary', 'results': {str(d): {k: v.count(k) for k in set(v)} for d, v in results.items()}})
agent.stdin.close(); agent.wait(timeout=10)
