#!/usr/bin/env python3
"""The acceptance's controlled arrow case (PR #1548, item 1), run on the desktop itself.

arrow.py ROOT LABEL [--driver putgd|user] [--at 1840,960] [--mouse CMD]
Firefox on Wikipedia "Linux" (fresh profile); the real relative uinput pointer put at
--at; native pictures with and without the cursor (grim -c / grim, Hyprland and other
wlroots desktops; spectacle-less KWin and GNOME are not covered here); a capture of the
whole screen (driver as given), no motion, Done after 3 s; the saved image copied to
ROOT/LABEL-capture.png. Analyse with arrowcheck.py.
"""
import json, os, shlex, shutil, subprocess, sys, time
from pathlib import Path

root = Path(sys.argv[1]).resolve()
label = sys.argv[2]
args = sys.argv[3:]
opt = lambda k, d: args[args.index(k) + 1] if k in args else d
driver = opt('--driver', 'putgd')
at = [int(v) for v in opt('--at', '1840,960').split(',')]
here = Path(__file__).resolve().parent
mouse_cmd = opt('--mouse', f'python3 {here}/umouse.py')
env = json.loads((root / 'env.json').read_text())
os.environ.update(env)
cli = json.loads((root / 'cli.json').read_text())
rows = {}


def rec(k, v):
    rows[k] = v
    (root / f'{label}-results.json').write_text(json.dumps(rows, indent=1))
    print(k, json.dumps(v)[:300], flush=True)


def rpc(m, p=None):
    r = subprocess.run([*cli, m, json.dumps(p or {})], capture_output=True, text=True, timeout=100)
    o = json.loads(r.stdout)
    if not o.get('ok'):
        raise RuntimeError(json.dumps(o))
    return o['result']


HYPR = bool(os.environ.get('HYPRLAND_INSTANCE_SIGNATURE'))


def cursor():
    if not HYPR:
        return None
    d = json.loads(subprocess.check_output(['hyprctl', 'cursorpos', '-j'], text=True))
    return [int(d['x']), int(d['y'])]


prof = root / f'ff-profile-{label}'
prof.mkdir(parents=True, exist_ok=True)
(prof / 'user.js').write_text('user_pref("browser.shell.checkDefaultBrowser", false);\nuser_pref("browser.aboutwelcome.enabled", false);\nuser_pref("datareporting.policy.dataSubmissionEnabled", false);\n')
ff = subprocess.Popen([os.environ.get('FF', 'firefox'), '--new-instance', '--no-remote', '--profile', str(prof), 'https://en.wikipedia.org/wiki/Linux'],
                      env=dict(os.environ, MOZ_DBUS_REMOTE='0'), stdout=open(root / 'firefox.log', 'w'), stderr=subprocess.STDOUT)
sid = None
try:
    time.sleep(12)
    rec('build', rpc('diagnostics')['build'])
    mouse = subprocess.Popen(shlex.split(mouse_cmd), stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    assert mouse.stdout.readline().startswith('ready')
    time.sleep(0.5)
    before = cursor()
    if HYPR:
        for _ in range(3):
            now = cursor()
            if now == at:
                break
            mouse.stdin.write(f'm {at[0] - now[0]} {at[1] - now[1]}\n')
            mouse.stdin.flush()
            time.sleep(0.3)
    else:
        # No cursor query (KWin, Mutter): pinned to the bottom-left corner (the top-left one
        # opens Plasma's overview and GNOME's Activities), then moved by the anchor's distance
        # with flat acceleration. The screen is 1920x1080 on every builder here.
        sys.path.insert(0, str(here))
        import ptrial
        ptrial.flat()
        for _ in range(5):
            mouse.stdin.write('m -1000 1000\n')
            mouse.stdin.flush()
            time.sleep(0.03)
        dy = at[1] - 1079
        for _ in range(4):
            mouse.stdin.write(f'm {at[0] // 4} {dy // 4}\n')
            mouse.stdin.flush()
            time.sleep(0.03)
        time.sleep(0.3)
    mouse.stdin.write('q\n')
    mouse.stdin.flush()
    mouse.wait(5)
    rec('anchor', {'before': before, 'target': at, 'after': cursor(), 'method': 'real relative uinput, before prepare'})
    time.sleep(1)
    if HYPR:
        subprocess.run(['grim', '-c', str(root / f'{label}-native-with-cursor.png')], check=True)
        subprocess.run(['grim', str(root / f'{label}-native-without-cursor.png')], check=True)
    rec('pointer-before-prepare', cursor())
    offset = (root / 'helper.log').stat().st_size if (root / 'helper.log').exists() else 0
    sid = rpc('scroll.prepare', {'rect': [0, 0, 1920, 1080], 'maxHeight': 60000, 'driver': driver})['id']
    rpc('scroll.start', {'id': sid})
    time.sleep(3)
    rec('pointer-before-done', cursor())
    rec('before-done', rpc('scroll.inspect', {'id': sid}))
    rec('end', rpc('scroll.stop', {'id': sid}))
    for _ in range(100):
        v = rpc('scroll.inspect', {'id': sid})
        if v.get('state') in ('done', 'failed', 'cancelled'):
            break
        time.sleep(0.3)
    rec('final', v)
    found = None
    for _ in range(50):
        recs = rpc('history.list', {'limit': 5})['records']
        found = next((r for r in recs if r.get('operationId') == sid and r.get('local', {}).get('status') == 'saved'), None)
        if found:
            break
        time.sleep(0.3)
    rec('history', found)
    shutil.copyfile(found['local']['path'], root / f'{label}-capture.png')
    text = (root / 'helper.log').read_bytes()[offset:].decode('utf-8', 'replace')
    (root / f'{label}-helper.log').write_text(text)
    rec('injects', [l for l in text.splitlines() if 'scroll inject:' in l][:12])
finally:
    if sid:
        try:
            if rpc('scroll.inspect', {'id': sid}).get('state') in ('capturing', 'ready', 'preparing'):
                rpc('scroll.cancel', {'id': sid})
        except Exception:
            pass
    ff.terminate()
    ff.wait(10)
