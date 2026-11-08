#!/usr/bin/env python3
"""toast.py RUN LABEL: after two region captures on the scale-2 output, grab that output and report what is on it (notification namespaces, frames)."""
import json, subprocess, sys, time
sys.path.insert(0, '/home/patrick/work/d1275/lab/tools/lab')
import lab
name, label = sys.argv[1], sys.argv[2]; run = '/home/patrick/work/d1275/lab/work/lab-runs/' + name
W, H = 1792, 800
def G(c): return subprocess.run(['/home/patrick/work/d1275/gs.sh', name, c], capture_output=True, text=True, timeout=30).stdout
def ipc(t): return G(f"~/d/probe/hc ~/d/probe/hipc.py '{t}'")
def move(x, y): return [{'type': 'abs', 'data': {'axis': 'x', 'value': int(x * 32767 / (W - 1))}}, {'type': 'abs', 'data': {'axis': 'y', 'value': int(y * 32767 / (H - 1))}}]
def btn(d): return [{'type': 'btn', 'data': {'down': d, 'button': 'left'}}]
def shot(tag):
    G(f"~/d/probe/hc grim -o PUTGD-2 /tmp/toast-{label}-{tag}.png")
    d = json.loads(ipc('j/layers')); return sorted({(m, l['namespace'], l['x'], l['y'], l['w'], l['h']) for m, v in d.items() for lv in v['levels'].values() for l in lv if m == 'PUTGD-2'})
ipc('output create headless PUTGD-2'); time.sleep(1)
ipc('eval hl.monitor({ output = "PUTGD-2", mode = "1024x768@60", position = "1280x0", scale = 2 })'); time.sleep(6)
print('before', shot('before'))
for i in range(2):
    lab.input_events(run, move(1380, 100)); time.sleep(0.3); lab.key(run, ['ctrl', 'shift', '1']); time.sleep(1.5)
    lab.input_events(run, btn(True)); time.sleep(0.1)
    for s in range(1, 13): lab.input_events(run, move(1380 + 300 * s / 12, 100 + 200 * s / 12)); time.sleep(0.02)
    time.sleep(0.1); lab.input_events(run, btn(False)); time.sleep(1.2)
    print('after', i, shot(f'after{i}'))
time.sleep(9); print('later', shot('later'))
ipc('output remove PUTGD-2'); time.sleep(1); ipc('eval hl.monitor({ output = "Virtual-1", mode = "1280x800@60", position = "0x0", scale = 1 })')
