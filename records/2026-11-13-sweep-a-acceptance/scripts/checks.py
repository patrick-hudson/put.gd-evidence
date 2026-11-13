#!/usr/bin/env python3
"""checks.py RUN KEY DESKTOP [--skip-lock]

The #1363 functional sequence on one two-monitor lab guest, run on its QEMU host:
Capture monitor per head, Repeat last region and its refusals, delayed captures with
the countdown seen on screen and absent from the image, both cancel paths and a lock
during the countdown. Prints one line per check and exits 1 when any check fails.
DESKTOP is cinnamon, gnome, kde, budgie or hyprland. Needs Pillow on the host and,
for budgie and hyprland, /tmp/wayland_pointer.py and /tmp/env.sh in the guest.
"""
import json, os, subprocess, sys, tempfile, time
from PIL import Image, ImageChops, ImageStat

ROOT = os.path.expanduser('~/work/i1363'); LAB = [sys.executable, os.path.join(ROOT, 'tools/lab/lab.py')]
run, key, desktop = sys.argv[1:4]; skip_lock = '--skip-lock' in sys.argv
RUN = os.path.join(ROOT, 'work/lab-runs', run); state = json.load(open(os.path.join(RUN, 'state.json')))
SSH = ['-i', key, '-o', 'IdentitiesOnly=yes', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes', '-o', 'ConnectTimeout=10',
       '-o', 'UserKnownHostsFile=' + os.path.join(ROOT, 'work/hostkeys', run, 'known_hosts')]
WORK = tempfile.mkdtemp(prefix='p1363-checks-')
ENV = '. /tmp/env.sh; '
# Where each QEMU head sits in the compositor's layout (labwc orders the outputs its own way).
ORIGIN = {0: (1024, 0), 1: (0, 0)} if desktop == 'budgie' else {0: (0, 0), 1: (1280, 0)}
SIZE = {0: (1280, 800), 1: (1024, 768)}; EXTENT = (2304, 800)
MOVE = {
    'cinnamon': ('DISPLAY=:0 xrandr --output Virtual-2 --pos 1280x32', 'DISPLAY=:0 xrandr --output Virtual-2 --pos 1280x0'),
    'gnome': ('gdctl set --logical-monitor --primary --monitor Virtual-1 --logical-monitor --monitor Virtual-2 --below Virtual-1',
              'gdctl set --logical-monitor --primary --monitor Virtual-1 --logical-monitor --monitor Virtual-2 --right-of Virtual-1'),
    'kde': ('export XDG_RUNTIME_DIR=/run/user/$(id -u) WAYLAND_DISPLAY=wayland-0; kscreen-doctor output.Virtual-2.position.1280,32',
            'export XDG_RUNTIME_DIR=/run/user/$(id -u) WAYLAND_DISPLAY=wayland-0; kscreen-doctor output.Virtual-2.position.1280,0'),
    'budgie': (ENV + 'wlr-randr --output Virtual-1 --pos 1024,64', ENV + 'wlr-randr --output Virtual-1 --pos 1024,0'),
    'hyprland': (ENV + '''hyprctl eval 'hl.monitor({ output = "Virtual-2", mode = "1024x768@60", position = "1280x100", scale = 1 })' ''',
                 ENV + '''hyprctl eval 'hl.monitor({ output = "Virtual-1", mode = "1280x800@60", position = "0x0", scale = 1 })'; '''
                       '''hyprctl eval 'hl.monitor({ output = "Virtual-2", mode = "1024x768@60", position = "1280x0", scale = 1 })' '''),
}[desktop]

def guest(cmd, timeout=60):
    out = subprocess.run(['ssh', '-n', '-p', str(state['ssh_port'])] + SSH + ['lab@127.0.0.1', cmd], capture_output=True, text=True, timeout=timeout)
    return out.stdout.strip()
def lab(*args, timeout=90):
    out = subprocess.run(LAB + list(args), capture_output=True, text=True, timeout=timeout)
    text = out.stdout.strip().splitlines()[-1] if out.stdout.strip() else out.stderr.strip()[-300:]
    try: return json.loads(text)
    except Exception: return {'raw': text}
def cli(method, params=None):
    r = lab('cli', '--run', RUN, '--method', method, '--params', json.dumps(params or {}))
    return r.get('result', r) if isinstance(r, dict) else r
def qmp(evs, head=None):
    return lab('input', '--run', RUN, *(['--head', str(head)] if head is not None else []), json.dumps(evs))
def tablet(x, y, w, h):
    return [{'type': 'abs', 'data': {'axis': 'x', 'value': int(x * 32767 / (w - 1))}}, {'type': 'abs', 'data': {'axis': 'y', 'value': int(y * 32767 / (h - 1))}}]
def button(down): return [{'type': 'btn', 'data': {'down': down, 'button': 'left'}}]
def locate(x, y):
    # Global layout point -> (head, x, y) for the X11 per-head tablets.
    for head, (ox, oy) in ORIGIN.items():
        w, h = SIZE[head]
        if ox <= x < ox + w and oy <= y < oy + h: return head, x - ox, y - oy
    raise SystemExit('point outside the layout')
def move(x, y):
    # A QEMU tablet that is asked for the position it last reported sends nothing, and with
    # one tablet per head the pointer then stays on the other head: always nudge first.
    if desktop == 'cinnamon':
        head, hx, hy = locate(x, y); qmp(tablet(max(hx - 3, 0), max(hy - 3, 0), *SIZE[head]), head); qmp(tablet(hx, hy, *SIZE[head]), head)
    elif desktop in ('gnome', 'kde'): qmp(tablet(max(x - 3, 0), max(y - 3, 0), *EXTENT)); qmp(tablet(x, y, *EXTENT))
    else: guest(ENV + 'python3 /tmp/wayland_pointer.py move %d %d --extent %d %d' % (x, y, *EXTENT))
def click(x, y):
    if desktop in ('budgie', 'hyprland'):
        guest(ENV + 'python3 /tmp/wayland_pointer.py click %d %d --extent %d %d' % (x, y, *EXTENT)); return
    head = locate(x, y)[0] if desktop == 'cinnamon' else None
    move(x, y); time.sleep(0.25); qmp(button(True), head); time.sleep(0.15); qmp(button(False), head)
def drag(x1, y1, x2, y2):
    if desktop in ('budgie', 'hyprland'):
        guest(ENV + 'python3 /tmp/wayland_pointer.py drag %d %d %d %d --extent %d %d --steps 8' % (x1, y1, x2, y2, *EXTENT)); return
    head = locate(x1, y1)[0] if desktop == 'cinnamon' else None
    move(x1, y1); time.sleep(0.3); qmp(button(True), head); time.sleep(0.2)
    for step in range(1, 9): move(x1 + (x2 - x1) * step // 8, y1 + (y2 - y1) * step // 8); time.sleep(0.05)
    time.sleep(0.2); qmp(button(False), head)
def start(action, delay=0):
    params = {'action': action}
    if delay: params['delaySeconds'] = delay
    r = cli('action.invoke', params)
    if 'operationId' not in r: raise SystemExit('invoke failed: ' + json.dumps(r)[:300])
    return r['operationId'], time.time()
def wait(op, limit=60):
    end = time.time() + limit
    while time.time() < end:
        o = cli('operation.inspect', {'id': op})
        if o.get('state') not in ('accepted', 'acquiring', 'stored', 'running', 'editing', 'recording', None):
            paths = [i.get('local', {}).get('path') for i in o.get('items', [])]
            return {'state': o['state'], 'code': o.get('error', {}).get('code', ''), 'message': o.get('error', {}).get('message', ''),
                    'action': o.get('action'), 'path': paths[0] if paths else None, 'done': time.time()}
        time.sleep(0.25)
    return {'state': 'timeout', 'code': '', 'message': '', 'action': '', 'path': None, 'done': time.time()}
def invoke(action, delay=0):
    op, began = start(action, delay); r = wait(op); r['seconds'] = r['done'] - began; return r
count = [0]
def fetch(path):
    count[0] += 1; local = os.path.join(WORK, 'capture-%d.png' % count[0])
    subprocess.run(['scp', '-q', '-P', str(state['ssh_port'])] + SSH + ['lab@127.0.0.1:' + path, local], check=True, stdin=subprocess.DEVNULL, timeout=120)
    return Image.open(local).convert('RGB')
def dump(head):
    lab('screenshot', '--run', RUN, '--head', str(head)); return Image.open(os.path.join(RUN, 'witness-head%d.ppm' % head)).convert('RGB')
def differs(a, b): return sum(ImageStat.Stat(ImageChops.difference(a, b)).mean) / 3
failed = [0]
def row(name, ok, detail):
    if not ok: failed[0] += 1
    print('%-4s %-46s %s' % ('ok' if ok else 'FAIL', name, detail), flush=True)
def region(delay=0):
    op, began = start('region', delay); time.sleep(2.5); drag(300, 300, 600, 500); released = time.time()
    r = wait(op); r['after'] = r['done'] - released; return r

build = cli('diagnostics').get('build', {})
print('# %s guest %s, put.gd %s (git tree %s)' % (desktop, run, build.get('version', 'unknown'), build.get('gitTree', '?')[:12]), flush=True)
# Captures are kept locally so their pixels can be read back. put.gd's own desktop notifications are
# turned off for the run: Omarchy stacks them over the top of the monitor, beside the pill.
doc = cli('settings.get'); prefs = doc['document'].get('preferences', {})
if not doc['document']['archive'].get('keepUploads') or prefs.get('regionSelectionMode') == 'screenshot_first' or prefs.get('notifications', True):
    patch = {'archive': {'keepUploads': True}, 'preferences': {'regionSelectionMode': 'live', 'notifications': False}}
    cli('settings.patch', {'patch': patch, 'expectedRevision': doc['metadata']['observedRevision']}); time.sleep(8)

# 1. The monitor under the pointer, each head, and the whole desk.
sizes = []
for head in (0, 1):
    ox, oy = ORIGIN[head]; move(ox + 400, oy + 400); time.sleep(0.6)
    r = invoke('monitor'); got = fetch(r['path']).size if r['path'] else None; sizes.append(got)
    row('Capture monitor, pointer on head %d' % head, r['state'] == 'completed' and got == SIZE[head], '%s %s' % (r['state'], '%dx%d' % got if got else r['code']))
r = invoke('desktop'); got = fetch(r['path']).size if r['path'] else None
row('Capture desktop', got == EXTENT, '%s %s' % (r['state'], '%dx%d' % got if got else r['code']))

# 2. Repeat last region. A resident that already remembers a region skips the first refusal.
remembered = cli('capabilities').get('source', {}).get('capture', {}).get('repeat', {}).get('remembered')
if not remembered:
    r = invoke('repeat'); row('Repeat before any region', r['code'] == 'repeat_unavailable' and r['action'] == 'region', '%s %s' % (r['state'], r['code']))
else: print('     %-46s %s' % ('Repeat before any region', 'not run: this resident already remembers a region'))
a = region(); first = fetch(a['path']) if a['path'] else None
row('Capture region, 300x200 drag', a['state'] == 'completed' and first is not None and first.size == (300, 200), '%s %s' % (a['state'], '%dx%d' % first.size if first else a['code']))
b = invoke('repeat'); second = fetch(b['path']) if b['path'] else None
same = first is not None and second is not None and first.size == second.size and differs(first, second) == 0
note = 'same pixels'
if not same and first is not None and second is not None and first.size == second.size:
    # Hyprland with software cursors (a VM) sometimes paints the selector's cross cursor into the
    # frame of the selected region, at the corner where the drag ended. put.gd asks for no cursor
    # (ext-image-copy options 0), so only that corner may differ.
    box = ImageChops.difference(first, second).getbbox()
    if box and box[0] >= first.size[0] - 16 and box[1] >= first.size[1] - 16:
        same = True; note = 'same pixels but the compositor\'s cross cursor in the last %dx%d px of the selected capture' % (first.size[0] - box[0], first.size[1] - box[1])
row('Repeat last region', b['state'] == 'completed' and same, '%s %s' % (b['state'], note if same else 'pixels differ' if second else b['code']))
guest(MOVE[0]); time.sleep(2.5); r = invoke('repeat')
row('Repeat after one monitor moved', r['code'] == 'repeat_layout_changed', '%s %s' % (r['state'], r['code']))
guest(MOVE[1]); time.sleep(2.5); r = invoke('repeat')
row('Repeat after the layout is restored', r['state'] == 'completed', '%s %s' % (r['state'], r['code']))

# 3. Delayed desktop capture: the pill is on the pointer's monitor and not in the image.
# The clean reference is taken after the capture: right after a layout change a desktop is still
# redrawing its wallpaper and panels (Omarchy takes a few seconds), which is not the pill.
head = 1; ox, oy = ORIGIN[head]; time.sleep(4); move(ox + 500, oy + 400); time.sleep(0.6)
op, began = start('desktop', 5); time.sleep(2.0); during = dump(head); r = wait(op); r['seconds'] = r['done'] - began; time.sleep(1.0); before = dump(head)
# The pill is centred at the top of the monitor; desktop notifications (Omarchy stacks put.gd's own
# at the top right) must not be taken for it, so only the middle of the top strip is compared.
left = SIZE[head][0] // 2 - 125; strip = (left, 0, left + 250, 140)
box = ImageChops.difference(before.crop(strip), during.crop(strip)).point(lambda v: 255 if v > 24 else 0).getbbox()
if box: box = (box[0] + left, box[1], box[2] + left, box[3])
row('Countdown on the pointer\'s monitor', box is not None and (box[2] - box[0]) > 120, 'pill at %s of head %d' % (box, head) if box else 'no pill seen')
pill = None
if box and r['path']:
    pill = (ox + (box[0] + box[2]) // 2, oy + (box[1] + box[3]) // 2); image = fetch(r['path'])
    crop = image.crop((ox + box[0], oy + box[1], ox + box[2], oy + box[3]))
    clean, shown = differs(crop, before.crop(box)), differs(crop, during.crop(box))
    row('Delayed desktop capture (5 s)', r['state'] == 'completed' and clean < 2 and shown > 8 and 4.5 < r['seconds'] < 12,
        '%s in %.1f s, pill not in the image (differs %.1f from the clean screen, %.1f from the pill)' % (r['state'], r['seconds'], clean, shown))
else: row('Delayed desktop capture (5 s)', False, '%s %s' % (r['state'], r['code']))

# 4. Delayed live region: the area first, then the countdown.
move(700, 600); r = region(3)
row('Delayed region (3 s), area chosen first', r['state'] == 'completed' and 2.8 < r['after'] < 7, '%s %.1f s after the drag' % (r['state'], r['after']))

# 5. Both ways to cancel.
if pill:
    move(ox + 500, oy + 400); time.sleep(0.4); op, _ = start('desktop', 10); time.sleep(2.5); click(*pill); r = wait(op, 20)
    row('Click on the pill', r['state'] == 'cancelled' and not r['path'], '%s %s' % (r['state'], r['code']))
    move(ox + 500, oy + 400)
op, _ = start('monitor', 10); time.sleep(2.5); cli('operation.cancel', {'id': op}); r = wait(op, 20); time.sleep(1.2)
gone = differs(dump(head).crop(box), before.crop(box)) < 2 if box else False
row('operation.cancel during the countdown', r['state'] == 'cancelled' and gone, '%s, pill gone' % r['state'] if gone else '%s, pill still on screen' % r['state'])

# 6. A lock during the countdown.
if not skip_lock:
    session = guest("loginctl list-sessions --no-legend | awk '/seat0/{print $1; exit}'")
    lock = {'cinnamon': 'export DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus; cinnamon-screensaver-command --lock',
            'gnome': 'loginctl lock-session ' + session, 'kde': 'loginctl lock-session ' + session,
            'budgie': ENV + 'busctl --user call org.buddiesofbudgie.BudgieScreenlock /org/buddiesofbudgie/Screenlock org.buddiesofbudgie.BudgieScreenlock Lock',
            'hyprland': ENV + 'omarchy-shell lock lock'}[desktop]
    op, _ = start('desktop', 10); time.sleep(3); guest(lock); r = wait(op, 30)
    row('Screen locked during the countdown', r['code'] == 'session_locked' and not r['path'], '%s %s' % (r['state'], r['code']))
    print('     %s' % r['message'])
    if desktop == 'cinnamon': guest('export DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus; cinnamon-screensaver-command -d')
    elif desktop in ('gnome', 'kde'): guest('loginctl unlock-session ' + session)
    else:
        if desktop == 'hyprland': lab('key', '--run', RUN, 'esc'); time.sleep(1.2)
        for name in ('p', 'u', 't', 'g', 'd', 'minus', 'l', 'a', 'b'): lab('key', '--run', RUN, name); time.sleep(0.12)
        lab('key', '--run', RUN, 'ret')
    time.sleep(3); r = invoke('desktop')
    row('Capture again after unlocking', r['state'] == 'completed', '%s %s' % (r['state'], r['code']))
print('# %d failed' % failed[0]); sys.exit(1 if failed[0] else 0)
