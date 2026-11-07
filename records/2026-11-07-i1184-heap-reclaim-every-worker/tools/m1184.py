#!/usr/bin/env python3
"""Headless #1184 run: resident with the seeded 10k-row tree, no UI; per block, one bare read-only call,
anonymous RSS before / 5 s / 35 s after. Run inside `dbus-run-session --`.
usage: m1184.py NAME APPDIR SEEDTREE OUT [--blocks N]
The seeded tree's rows carry absolute paths under /tmp/i1149b/w2, so the run root is that path (one run at a time)."""
import json, os, shutil, signal, subprocess, sys, time
from pathlib import Path
os.umask(0o077)
name, appdir, seed, out = sys.argv[1], Path(sys.argv[2]).resolve(), Path(sys.argv[3]), Path(sys.argv[4])
a = sys.argv[5:]; blocks = int(a[a.index('--blocks')+1]) if '--blocks' in a else 3
root = Path('/tmp/i1149b/w2')
assert not Path(f'{root}/rt/putgd/session.sock').exists(), 'socket present: another run?'
for sub in ('config', 'data', 'files'):
    if (root/sub).exists(): shutil.rmtree(root/sub)   # this script's own previous copy of the seed, same fixed path
    shutil.copytree(seed/sub, root/sub, symlinks=True)
for d in ('state', 'cache', 'rt'): (root/d).mkdir(parents=True, exist_ok=True)
os.chmod(root/'rt', 0o700)
lock = root/'data'/'putgd'/'resident.lock'
if lock.is_file(): lock.unlink()
out.mkdir(parents=True, exist_ok=True)
DROP = ('DISPLAY', 'WAYLAND_DISPLAY', 'XDG_SESSION_TYPE', 'XDG_CURRENT_DESKTOP', 'XDG_SESSION_DESKTOP', 'DESKTOP_SESSION', 'XAUTHORITY',
        'QT_QPA_PLATFORMTHEME', 'GNOME_DESKTOP_SESSION_ID', 'KDE_FULL_SESSION', 'XDG_DATA_DIRS', 'XDG_CONFIG_DIRS', 'XDG_SESSION_ID')
env = {k: v for k, v in os.environ.items() if k not in DROP}
env.update({'XDG_CONFIG_HOME': str(root/'config'), 'XDG_DATA_HOME': str(root/'data'), 'XDG_STATE_HOME': str(root/'state'), 'XDG_CACHE_HOME': str(root/'cache'),
            'XDG_RUNTIME_DIR': str(root/'rt'), 'QT_QPA_PLATFORM': 'offscreen', 'PUTGD_STARTED_FOR_UPLOAD': '1'})
assert '/run/user/' not in env['DBUS_SESSION_BUS_ADDRESS']
sock = root/'rt'/'putgd'/'session.sock'; assert len(str(sock).encode()) <= 107
cli = appdir/'usr'/'bin'/'putgd-cli'; cli_env = dict(env); cli_env['LD_LIBRARY_PATH'] = str(appdir/'usr'/'lib')
def call(method, params=None, timeout=60):
    r = subprocess.run([str(cli), '--socket', str(sock), method, json.dumps(params or {})], env=cli_env, capture_output=True, text=True, timeout=timeout)
    try: return json.loads(r.stdout)
    except Exception: return {'ok': False, 'raw': r.stdout[-300:], 'stderr': r.stderr[-300:]}
def rollup(pid):
    v = {}
    for line in Path(f'/proc/{pid}/smaps_rollup').read_text().splitlines():
        f = line.split()
        if len(f) == 3 and f[2] == 'kB': v[f[0].rstrip(':')] = int(f[1])
    return {'Rss': v['Rss'], 'Anonymous': v['Anonymous']}
identity = json.loads(subprocess.check_output([str(appdir/'AppRun'), '--version-json'], env=env))
log = open(out/'resident.log', 'ab')
proc = subprocess.Popen([str(appdir/'AppRun'), '--background'], env=env, stdout=log, stderr=log, cwd=str(root), start_new_session=True)
def resident():
    stack = [proc.pid]
    while stack:
        cur = stack.pop()
        try:
            if Path(f'/proc/{cur}/comm').read_text().strip() == 'putgd': return cur
            for task in Path(f'/proc/{cur}/task').iterdir(): stack += [int(c) for c in (task/'children').read_text().split()]
        except FileNotFoundError: pass
    raise SystemExit('no resident')
for _ in range(150):
    time.sleep(0.2)
    if sock.exists() and call('ui.snapshot', timeout=10).get('result', {}).get('operationsReady'): break
pid = resident()
result = {'name': name, 'identity': identity, 'host': os.uname().nodename, 'blocks': []}
time.sleep(100)  # startup trim, startup cleanup pass (60 s) and their releases
ops = call('operation.recent').get('result', {}).get('operations', [])
opid = ops[0]['id'] if ops else 'missing'
hist = call('history.list', {'limit': 1}).get('result', {})
hid = (hist.get('records') or hist.get('rows') or [{}])[0].get('id', 'missing')
time.sleep(40)
calls = [('operation.recent', {}), ('operation.inspect', {'id': opid}), ('history.detail', {'id': hid})]
def counters(): return call('diagnostics').get('result', {}).get('memory', {})
for b in range(blocks):
    for method, params in calls:
        # Start each read from a trimmed heap: history.list arms the reclamation on every build.
        call('history.list', {'limit': 50}); time.sleep(8)
        c0 = counters()['allocatorReclamationCount']; time.sleep(3); before = rollup(pid)
        r = call(method, params); ok = r.get('ok', 'error' not in r)
        time.sleep(5); s5 = rollup(pid)
        time.sleep(30); s35 = rollup(pid)
        c1 = counters()['allocatorReclamationCount']
        row = {'block': b+1, 'method': method, 'ok': ok, 'err': (r.get('error') or {}).get('code'), 'before': before, 'after5': s5, 'after35': s35, 'reclaims': c1 - c0}
        result['blocks'].append(row); print(json.dumps(row), flush=True)
        time.sleep(5)
result['diagnostics_memory'] = counters()
call('ui.quit')
for _ in range(100):
    time.sleep(0.2)
    if proc.poll() is not None and not Path(f'/proc/{pid}').exists(): break
else:
    os.kill(pid, signal.SIGTERM); proc.wait(20)
(out/'result.json').write_text(json.dumps(result, indent=1) + '\n'); print('done', name, flush=True)
