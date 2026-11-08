#!/usr/bin/env python3
"""catcher_edge.py RUN CASE TRIALS: d69 host side, the press catcher's end paths on Hyprland, real QEMU input.
right-early: right button 0.1 s after the hotkey (catcher up, selector not). Expect: both layers gone, no new image, next region works.
output-gone: two outputs; left press on the catcher 0.1 s after the hotkey, PUTGD-2 removed while held, release. Expect: no layer left, no image of the wrong size, next region works.
pointer-gone: left press on the catcher, the USB tablet is unplugged while held (QMP device_del), plugged back. Expect: drag cancelled, no layer left, no new image, next region works."""
import json, subprocess, sys, time
sys.path.insert(0, '/home/patrick/work/d1275/lab/tools/lab')
import lab
name, case, trials = sys.argv[1], sys.argv[2], int(sys.argv[3]); run = '/home/patrick/work/d1275/lab/work/lab-runs/' + name
agent = subprocess.Popen(['/home/patrick/work/d1275/gs.sh', name, '~/d/probe/hc python3 -u /home/lab/d/probe/selagent.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
def ask(l): agent.stdin.write(l + '\n'); agent.stdin.flush(); return json.loads(agent.stdout.readline())
def G(c): return subprocess.run(['/home/patrick/work/d1275/gs.sh', name, c], capture_output=True, text=True, timeout=30).stdout
def ipc(t): return G(f"~/d/probe/hc ~/d/probe/hipc.py '{t}'")
def layers():
    d = json.loads(ipc('j/layers'))
    return sorted({l['namespace'] for m in d.values() for v in m['levels'].values() for l in v if l['namespace'].startswith('putgd')})
def images(): return int(G('ls ~/Documents/put.gd/images | wc -l').strip() or -1)
W, H = 1280, 800
def set_space(w, h):
    global W, H; W, H = w, h
def move(x, y): return [{'type': 'abs', 'data': {'axis': 'x', 'value': int(x * 32767 / (W - 1))}}, {'type': 'abs', 'data': {'axis': 'y', 'value': int(y * 32767 / (H - 1))}}]
def btn(b, down): return [{'type': 'btn', 'data': {'down': down, 'button': b}}]
hot = lambda: lab.key(run, ['ctrl', 'shift', '1'])
def clear(left):
    if left: lab.key(run, ['esc']); time.sleep(2)
def drag():
    lab.input_events(run, move(300, 200)); time.sleep(0.1); lab.input_events(run, btn('left', True)); time.sleep(0.1)
    for i in range(1, 13): lab.input_events(run, move(300 + 400 * i / 12, 200 + 300 * i / 12)); time.sleep(0.02)
    time.sleep(0.1); lab.input_events(run, btn('left', False))
def wait_op(before):
    o = {}
    for _ in range(20):
        o = ask('op')
        if o.get('id') != before and o.get('state') not in ('selecting', 'acquiring', 'pending'): return o
        time.sleep(0.5)
    return o
def next_works():
    before = ask('op').get('id'); hot(); time.sleep(1.5); drag(); o = wait_op(before); return o.get('id') != before and o.get('state') in ('completed', 'stored') and o.get('size') == [400, 300], {k: o.get(k) for k in ('state', 'code', 'size')}
def tablet():
    with lab.QMP(lab.Path(run) / 'qmp.sock') as q:
        for c in q.execute('qom-list', {'path': '/machine/peripheral-anon'}):
            if c['type'] == 'child<usb-tablet>': return '/machine/peripheral-anon/' + c['name']
        for c in q.execute('qom-list', {'path': '/machine/peripheral'}):
            if c['type'] == 'child<usb-tablet>': return c['name']
def outputs(two):
    if two:
        ipc('output create headless PUTGD-2'); time.sleep(0.5)
        ipc('eval hl.monitor({ output = "Virtual-1", mode = "1280x800@60", position = "0x0", scale = 1 })')
        ipc('eval hl.monitor({ output = "PUTGD-2", mode = "1024x768@60", position = "1280x0", scale = 1 })'); time.sleep(4); set_space(2304, 800)
    else:
        ipc('output remove PUTGD-2'); time.sleep(1); ipc('eval hl.monitor({ output = "Virtual-1", mode = "1280x800@60", position = "0x0", scale = 1 })'); time.sleep(3); set_space(1280, 800)
results = []
serial = 0
for i in range(trials):
    if case == 'output-gone': outputs(True)
    lab.input_events(run, move(300, 200)); time.sleep(0.5)
    before = ask('op').get('id'); n = images(); extra = {}
    hot(); time.sleep(0.1)
    if case == 'right-early':
        lab.input_events(run, btn('right', True)); time.sleep(0.05); lab.input_events(run, btn('right', False)); time.sleep(2.5)
    elif case == 'output-gone':
        lab.input_events(run, btn('left', True)); time.sleep(0.15); lab.input_events(run, move(500, 350)); time.sleep(0.4); up = layers(); extra['layersDuring'] = up
        ipc('output remove PUTGD-2'); time.sleep(3); set_space(1280, 800); lab.input_events(run, btn('left', False)); time.sleep(2.5); ipc('eval hl.monitor({ output = "Virtual-1", mode = "1280x800@60", position = "0x0", scale = 1 })'); time.sleep(3)
    elif case == 'pointer-gone':
        lab.input_events(run, btn('left', True)); time.sleep(0.15); lab.input_events(run, move(500, 350)); time.sleep(0.4); up = layers(); extra['layersDuring'] = up
        dev = tablet(); extra['device'] = dev
        with lab.QMP(lab.Path(run) / 'qmp.sock') as q: q.execute('device_del', {'id': dev})
        time.sleep(3); extra['devicesGone'] = G('~/d/probe/hc hyprctl devices | grep -ci tablet').strip(); extra['layersAfterUnplug'] = layers()
        serial += 1
        with lab.QMP(lab.Path(run) / 'qmp.sock') as q: q.execute('device_add', {'driver': 'usb-tablet', 'id': 'tab%d-%d' % (int(time.time()), serial)})
        time.sleep(3)
    left = layers(); m = images(); o = ask('op'); ok = not left
    if case in ('right-early', 'pointer-gone'): ok = ok and m == n
    if left: clear(left); left2 = layers()
    nxt, detail = next_works()
    ok = ok and nxt
    results.append(ok); print(json.dumps({'case': case, 'trial': i, 'ok': ok, 'layersLeft': left, 'imagesAdded': m - n, 'op': {k: o.get(k) for k in ('state', 'code', 'size')}, 'nextRegion': detail, **extra}), flush=True)
    time.sleep(1.5)
print(json.dumps({'summary': {case: f'{sum(results)}/{len(results)}'}}), flush=True); agent.stdin.close(); agent.wait(timeout=10)
