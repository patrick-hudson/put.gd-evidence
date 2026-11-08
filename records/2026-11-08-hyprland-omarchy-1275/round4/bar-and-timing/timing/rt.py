#!/usr/bin/env python3
"""rt.py RUN TRIALS WAIT DELAY OUT.jsonl: d69 host side. Attempt-2 condition with absolute guest times for each trial, to line up against WAYLAND_DEBUG."""
import datetime, json, subprocess, sys, time
sys.path.insert(0, '/home/patrick/work/d1275/lab/tools/lab')
import lab
name, trials, wait, delay, out = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
run = '/home/patrick/work/d1275/lab/work/lab-runs/' + name
agent = subprocess.Popen(['/home/patrick/work/d1275/gs.sh', name, '~/d/probe/hc python3 -u /home/lab/d/probe/selagent.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
def ask(l): agent.stdin.write(l + '\n'); agent.stdin.flush(); return json.loads(agent.stdout.readline())
def ipc(t): subprocess.run(['/home/patrick/work/d1275/gs.sh', name, f"~/d/probe/hc ~/d/probe/hipc.py '{t}'"], capture_output=True)
import os
NOOUT = os.environ.get('NOOUT') == '1'; CONTROL = os.environ.get('CONTROL') == '1'
W, H = (1280, 800) if NOOUT else (2304, 800)
def move(x, y): return [{'type': 'abs', 'data': {'axis': 'x', 'value': int(x * 32767 / (W - 1))}}, {'type': 'abs', 'data': {'axis': 'y', 'value': int(y * 32767 / (H - 1))}}]
def btn(d): return [{'type': 'btn', 'data': {'down': d, 'button': 'left'}}]
pressed = [0.0]
def drag():
    lab.input_events(run, move(300, 200)); time.sleep(0.05); lab.input_events(run, btn(True)); pressed[0] = pressed[0] or time.time(); time.sleep(0.1)
    for i in range(1, 13): lab.input_events(run, move(300 + 400 * i / 12, 200 + 300 * i / 12)); time.sleep(0.02)
    time.sleep(0.1); lab.input_events(run, btn(False))
def finished(before):
    o = {}
    for _ in range(20):
        o = ask('op')
        if o.get('id') != before and o.get('state') not in ('selecting', 'acquiring', 'pending'): return o
        time.sleep(0.5)
    return o
def offsets():
    best = None
    for _ in range(15):
        a = time.time(); g = ask('t')['t']; b = time.time()
        if best is None or b - a < best[1]: best = (g - (a + b) / 2, b - a)
    return best[0]
tally = {}; f = open(out, 'w')
for i in range(trials):
    before = None if CONTROL else ask('op')['id']
    if not NOOUT:
        ipc('output create headless PUTGD-2'); time.sleep(0.5)
        ipc('eval hl.monitor({ output = "Virtual-1", mode = "1280x800@60", position = "0x0", scale = 1 })')
        ipc('eval hl.monitor({ output = "PUTGD-2", mode = "1024x768@60", position = "1280x0", scale = 1 })')
    time.sleep(wait); offset = offsets()
    if CONTROL:
        t0 = time.time(); time.sleep(2.0)
        row = {'trial': i, 'hotkeyGuest': round(t0 + offset, 4), 'control': True}
        f.write(json.dumps(row) + '\n'); f.flush(); print(json.dumps(row), flush=True)
        ipc('output remove PUTGD-2'); time.sleep(0.5); ipc('eval hl.monitor({ output = "Virtual-1", mode = "1280x800@60", position = "0x0", scale = 1 })'); time.sleep(2.0); continue
    pressed[0] = 0.0; ask(f'w {1 if NOOUT else 2} 6'); t0 = time.time(); lab.key(run, ['ctrl', 'shift', '1']); time.sleep(max(0.0, delay - (time.time() - t0))); drag()
    w = json.loads(agent.stdout.readline())
    o = finished(before)
    if o.get('id') != before and o.get('state') in ('completed', 'stored'): outcome = 'ok' if o.get('size') == [400, 300] else 'wrong-size'
    elif o.get('id') == before or o.get('state') in ('selecting', 'acquiring', 'pending'):
        drag(); o2 = finished(before); outcome = 'lost+' + ('recovered' if o2.get('state') in ('completed', 'stored') and o2.get('id') != before else 'stuck')
        if 'stuck' in outcome: lab.key(run, ['esc']); time.sleep(1.0)
    else: outcome = 'other:%s:%s' % (o.get('state'), o.get('code'))
    rel = lambda k: None if w.get(k) is None else round(w[k] - offset - t0, 3)
    row = {'trial': i, 'hotkeyGuest': round(t0 + offset, 4), 'pressGuest': round(pressed[0] + offset, 4), 'pressAfter': round(pressed[0] - t0, 3), 'catcherSeen': rel('catcher'), 'helperSeen': rel('helper'), 'selectorFirst': rel('first'), 'load1': w.get('load'), 'outcome': outcome}
    f.write(json.dumps(row) + '\n'); f.flush(); print(json.dumps(row), flush=True); tally[outcome] = tally.get(outcome, 0) + 1
    if not NOOUT: ipc('output remove PUTGD-2'); time.sleep(0.5); ipc('eval hl.monitor({ output = "Virtual-1", mode = "1280x800@60", position = "0x0", scale = 1 })'); time.sleep(2.0)
    else: time.sleep(2.0)
print(json.dumps({'summary': tally, 'waitAfterOutput': wait, 'delay': delay}), flush=True); agent.stdin.close(); agent.wait(timeout=10)
