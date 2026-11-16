#!/usr/bin/env python3
"""Real relative clicks on the inside bar's buttons (PR #1548, item 2).

insideclick.py ROOT DRIVER
A capture of the whole screen (driver user or putgd) over a fresh Firefox on Wikipedia;
the bar sits inside the region. A uinput mouse (flat) moves to each button's centre
from where the pointer is and clicks: Auto-scroll, Auto-scroll again, Done; then a
second capture and Cancel. After each click, scroll.inspect says whether it acted.
Native pictures (X11: import -window root) before each click go to ROOT.
"""
import json, os, re, subprocess, sys, time
from pathlib import Path

root = Path(sys.argv[1]).resolve()
driver = sys.argv[2]
here = Path(__file__).resolve().parent
sys.path.insert(0, str(here))
import ptrial

env = json.loads((root / 'env.json').read_text())
os.environ.update(env)
cli = json.loads((root / 'cli.json').read_text())
rows = []


def rec(k, v):
    rows.append({'label': k, 'value': v})
    (root / f'inside-{driver}-results.json').write_text(json.dumps(rows, indent=1))
    print(k, json.dumps(v)[:400], flush=True)


def rpc(m, p=None):
    r = subprocess.run([*cli, m, json.dumps(p or {})], capture_output=True, text=True, timeout=100)
    o = json.loads(r.stdout)
    if not o.get('ok'):
        raise RuntimeError(json.dumps(o))
    return o['result']


def shot(name):
    if os.environ.get('XDG_SESSION_TYPE') == 'x11':
        subprocess.run(['import', '-window', 'root', str(root / f'{name}.png')], capture_output=True)
    elif os.environ.get('HYPRLAND_INSTANCE_SIGNATURE') or 'wlroots' in os.environ.get('XDG_CURRENT_DESKTOP', '').lower():
        subprocess.run(['grim', '-c', str(root / f'{name}.png')], capture_output=True)


mouse = subprocess.Popen(['sudo', '-n', 'python3', str(here / 'umouse.py')], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
assert mouse.stdout.readline().startswith('ready')
time.sleep(0.5)
ptrial.flat()
pos = None


def to(x, y):
    """Move the real pointer to x,y: by the compositor's answer where there is one, else from the top-left corner."""
    global pos
    now = ptrial.cursor()
    if now is None:
        if pos is None:
            # The bottom-left corner: the top-left one opens Plasma's overview and GNOME's Activities.
            for _ in range(5):
                mouse.stdin.write('m -1000 1000\n')
                mouse.stdin.flush()
                time.sleep(0.03)
            pos = [0, 1079]
        now = pos
    # In steps of at most 40 px every 10 ms (about 4,000 px/s at most): a hand, not a jump.
    dx, dy = x - now[0], y - now[1]
    n = max(1, int(max(abs(dx), abs(dy)) / 40))
    sent = [0, 0]
    for i in range(1, n + 1):
        sx, sy = round(dx * i / n) - sent[0], round(dy * i / n) - sent[1]
        sent[0] += sx
        sent[1] += sy
        mouse.stdin.write(f'm {sx} {sy}\n')
        mouse.stdin.flush()
        time.sleep(0.01)
    pos = [x, y]
    time.sleep(0.3)
    return ptrial.cursor()


def click(name, x, y):
    landed = to(x, y)
    shot(f'inside-{driver}-{name}-before')
    mouse.stdin.write('d\n')
    mouse.stdin.flush()
    time.sleep(0.08)
    mouse.stdin.write('u\n')
    mouse.stdin.flush()
    time.sleep(1.5)
    return landed


prof = root / f'ff-profile-inside-{driver}'
prof.mkdir(parents=True, exist_ok=True)
(prof / 'user.js').write_text('user_pref("browser.shell.checkDefaultBrowser", false);\nuser_pref("browser.aboutwelcome.enabled", false);\nuser_pref("datareporting.policy.dataSubmissionEnabled", false);\n')
ff = subprocess.Popen([os.environ.get('FF', 'firefox'), '--new-instance', '--no-remote', '--profile', str(prof), 'https://en.wikipedia.org/wiki/Linux'],
                      env=dict(os.environ, MOZ_DBUS_REMOTE='0'), stdout=open(root / 'firefox.log', 'w'), stderr=subprocess.STDOUT)
sid = None
try:
    time.sleep(10)
    for capture in ('first', 'second'):
        offset = (root / 'helper.log').stat().st_size if (root / 'helper.log').exists() else 0
        sid = rpc('scroll.prepare', {'rect': [0, 0, 1920, 1080], 'driver': driver})['id']
        rpc('scroll.start', {'id': sid})
        time.sleep(2)
        text = (root / 'helper.log').read_bytes()[offset:].decode('utf-8', 'replace')
        m = re.search(r'scroll: bar at (-?\d+),(-?\d+) (\d+)x(\d+) (inside|outside); (.*)', text)
        bar = {'rect': list(map(int, m.groups()[:4])), 'where': m.group(5)}
        for b in re.finditer(r'(\w+) (-?\d+),(-?\d+) (\d+)x(\d+)', m.group(6)):
            bar[b.group(1)] = [int(b.group(2)) + int(b.group(4)) // 2, int(b.group(3)) + int(b.group(5)) // 2]
        rec(f'{capture}-bar', bar)
        rec(f'{capture}-start', rpc('scroll.inspect', {'id': sid}))
        presses = [('auto-1', 'autoScroll'), ('auto-2', 'autoScroll'), ('done', 'done')] if capture == 'first' else [('cancel', 'cancel')]
        for name, button in presses:
            landed = click(name, *bar[button])
            v = rpc('scroll.inspect', {'id': sid}) if name not in ('done', 'cancel') else None
            if v is None:
                for _ in range(40):
                    v = rpc('scroll.inspect', {'id': sid})
                    if v.get('state') in ('done', 'failed', 'cancelled'):
                        break
                    time.sleep(0.3)
            rec(f'{capture}-{name}', {'target': bar[button], 'cursorBeforeClick': landed,
                                      'state': v.get('state'), 'driver': v.get('driver'), 'activity': v.get('activity'), 'paused': v.get('paused'), 'pausedBy': v.get('pausedBy'),
                                      'endReason': v.get('endReason'), 'height': v.get('height'), 'hiddenCells': v.get('hiddenCells'), 'hiddenRows': v.get('hiddenRows')})
        sid = None
        (root / f'inside-{driver}-{capture}-helper.log').write_text((root / 'helper.log').read_bytes()[offset:].decode('utf-8', 'replace'))
        time.sleep(1)
finally:
    if sid:
        try:
            if rpc('scroll.inspect', {'id': sid}).get('state') in ('capturing', 'ready', 'preparing'):
                rpc('scroll.cancel', {'id': sid})
        except Exception:
            pass
    mouse.stdin.write('q\n')
    mouse.stdin.flush()
    mouse.wait(5)
    ff.terminate()
    ff.wait(10)
