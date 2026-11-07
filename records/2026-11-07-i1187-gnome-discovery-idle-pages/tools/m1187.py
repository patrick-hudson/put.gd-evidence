#!/usr/bin/env python3
"""Headless GNOME-resident idle memory run for #1187. Run inside `dbus-run-session --`.
usage: m1187.py NAME APPDIR OUT MODE [--secs N] [--enable-at T]
APPDIR is an extracted AppImage (squashfs-root). MODE: absent | enabled. The fake Shell (fake_shell.py next to
this script) owns org.gnome.Shell on the private bus; the resident runs as a GNOME Wayland core resident
(QCoreApplication, no display connection). Samples smaps_rollup every 5 s; full smaps at 60/120/180 s and the end."""
import json, os, signal, subprocess, sys, time
from pathlib import Path
os.umask(0o077)
name, appdir, out, mode = sys.argv[1], Path(sys.argv[2]).resolve(), Path(sys.argv[3]), sys.argv[4]
a = sys.argv[5:]
secs = int(a[a.index('--secs')+1]) if '--secs' in a else 240
enable_at = int(a[a.index('--enable-at')+1]) if '--enable-at' in a else None
reclaim_at = [int(x) for x in a[a.index('--reclaim-at')+1].split(',')] if '--reclaim-at' in a else []  # force cgroup reclaim of the resident's scope
scoped = bool(reclaim_at) or '--scope' in a
real = '--real' in a
here = Path(__file__).resolve().parent
root = Path('/tmp/i1187') / name
if root.exists(): raise SystemExit(f'{root} exists')
for d in ('config', 'data', 'state', 'cache', 'rt'): (root/d).mkdir(parents=True)
os.chmod(root/'rt', 0o700); out.mkdir(parents=True, exist_ok=True)
DROP = ('DISPLAY', 'WAYLAND_DISPLAY', 'XDG_SESSION_TYPE', 'XDG_CURRENT_DESKTOP', 'XDG_SESSION_DESKTOP', 'DESKTOP_SESSION', 'XAUTHORITY',
        'QT_QPA_PLATFORM', 'QT_QPA_PLATFORMTHEME', 'GNOME_DESKTOP_SESSION_ID', 'KDE_FULL_SESSION', 'XDG_DATA_DIRS', 'XDG_CONFIG_DIRS', 'XDG_SESSION_ID')
env = {k: v for k, v in os.environ.items() if k not in DROP}
env.update({'XDG_CONFIG_HOME': str(root/'config'), 'XDG_DATA_HOME': str(root/'data'), 'XDG_STATE_HOME': str(root/'state'), 'XDG_CACHE_HOME': str(root/'cache'),
            'XDG_RUNTIME_DIR': str(root/'rt'), 'XDG_SESSION_TYPE': 'wayland', 'WAYLAND_DISPLAY': 'wayland-i1187-none', 'XDG_CURRENT_DESKTOP': 'GNOME',
            'PUTGD_STARTED_FOR_UPLOAD': '1'})
if real:
    shell_env = None
    for p in Path('/proc').iterdir():
        try:
            if p.name.isdigit() and p.stat().st_uid == os.getuid() and (p/'comm').read_text().strip() == 'gnome-shell':
                shell_env = dict(kv.split('=', 1) for kv in (p/'environ').read_bytes().decode(errors='replace').split('\0') if '=' in kv); break
        except (FileNotFoundError, PermissionError, ProcessLookupError): pass
    assert shell_env, 'no gnome-shell'
    env['DBUS_SESSION_BUS_ADDRESS'] = shell_env.get('DBUS_SESSION_BUS_ADDRESS', f'unix:path=/run/user/{os.getuid()}/bus')
    env['WAYLAND_DISPLAY'] = f'/run/user/{os.getuid()}/' + shell_env.get('WAYLAND_DISPLAY', 'wayland-0')
    assert Path(env['WAYLAND_DISPLAY']).exists(), env['WAYLAND_DISPLAY']
    gx_env = dict(os.environ); gx_env['DBUS_SESSION_BUS_ADDRESS'] = env['DBUS_SESSION_BUS_ADDRESS']
    def ext(verb): return subprocess.run(['gnome-extensions', verb, 'putgd@put.gd'], env=gx_env, capture_output=True, text=True).returncode
    def ext_state(): return subprocess.run(['gnome-extensions', 'info', 'putgd@put.gd'], env=gx_env, capture_output=True, text=True).stdout
    ext('enable' if mode == 'enabled' else 'disable'); time.sleep(2)
else:
    assert 'DBUS_SESSION_BUS_ADDRESS' in env and 'i1187' not in env['DBUS_SESSION_BUS_ADDRESS'], 'run inside dbus-run-session'
    assert '/run/user/' not in env['DBUS_SESSION_BUS_ADDRESS'], 'refusing the real session bus'
sock = root/'rt'/'putgd'/'session.sock'; assert len(str(sock).encode()) <= 107
cli = appdir/'usr'/'bin'/'putgd-cli'; cli_env = dict(env); cli_env['LD_LIBRARY_PATH'] = str(appdir/'usr'/'lib')
def call(method, params=None, timeout=30):
    r = subprocess.run([str(cli), '--socket', str(sock), method, json.dumps(params or {})], env=cli_env, capture_output=True, text=True, timeout=timeout)
    try: return json.loads(r.stdout)
    except Exception: return {'ok': False, 'raw': r.stdout[-300:], 'stderr': r.stderr[-300:]}
def rollup(pid):
    v = {}
    for line in Path(f'/proc/{pid}/smaps_rollup').read_text().splitlines():
        f = line.split()
        if len(f) == 3 and f[2] == 'kB': v[f[0].rstrip(':')] = int(f[1])
    v['file'] = v['Rss'] - v['Anonymous'] - v.get('Shmem', 0)  # file-backed resident pages (rollup: Rss = Anonymous + file + shmem)
    return v
def evict(tree):
    n = 0
    for p in tree.rglob('*'):
        if p.is_file() and not p.is_symlink():
            try:
                fd = os.open(p, os.O_RDONLY); os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_DONTNEED); os.close(fd); n += 1
            except OSError: pass
    return n
evicted = evict(appdir) if scoped else 0
shell_log = out/'shell.jsonl'
if real:
    shell = None; shell_log.write_text('')
else:
    shell = subprocess.Popen(['python3', '-I', str(here/'fake_shell.py'), str(shell_log)] + (['--enabled'] if mode == 'enabled' else []), env=env, start_new_session=True)
    time.sleep(1.5)
identity = json.loads(subprocess.check_output([str(appdir/'AppRun'), '--version-json'], env=env))
log = open(out/'resident.log', 'ab')
unit = 'i1187-' + name
if scoped:
    # systemd-run talks to the real user manager; the resident itself gets the private roots and bus through env(1).
    run_env = {k: v for k, v in env.items() if k not in ('DBUS_SESSION_BUS_ADDRESS',)}
    run_env['XDG_RUNTIME_DIR'] = f'/run/user/{os.getuid()}'
    cmd = ['systemd-run', '--user', '--scope', '--quiet', '-p', 'MemoryAccounting=yes', '--unit', unit, 'env',
           f'XDG_RUNTIME_DIR={env["XDG_RUNTIME_DIR"]}', f'DBUS_SESSION_BUS_ADDRESS={env["DBUS_SESSION_BUS_ADDRESS"]}', str(appdir/'AppRun'), '--background']
else:
    run_env, cmd = env, [str(appdir/'AppRun'), '--background']
proc = subprocess.Popen(cmd, env=run_env, stdout=log, stderr=log, cwd=str(root), start_new_session=True)
def resident():
    # AppRun may exec or wrap: find the exact putgd process.
    stack = [proc.pid]
    while stack:
        cur = stack.pop()
        try:
            if Path(f'/proc/{cur}/comm').read_text().strip() == 'putgd': return cur
            for task in Path(f'/proc/{cur}/task').iterdir(): stack += [int(c) for c in (task/'children').read_text().split()]
        except FileNotFoundError: pass
    raise SystemExit('no resident')
for _ in range(100):
    time.sleep(0.2)
    if sock.exists(): break
pid = resident(); t0 = time.monotonic()
cgroup = Path('/sys/fs/cgroup') / Path(f'/proc/{pid}/cgroup').read_text().strip().split('::', 1)[1].lstrip('/')
def majflt(): return int(Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()[9])
result = {'extension_before': ext_state() if real else None, 'cgroup': str(cgroup), 'evicted_files': evicted, 'reclaims': [], 'name': name, 'mode': mode, 'identity': identity, 'host': os.uname().nodename, 'pid': pid, 't0': t0, 'series': [], 'enable_at': enable_at}
full_at = {60, 120, 180, secs}
enabled_sent = None
t = 0
while t <= secs:
    while time.monotonic() - t0 < t: time.sleep(0.05)
    if enable_at is not None and enabled_sent is None and t >= enable_at:
        if real: ext('enable')
        else: os.kill(shell.pid, signal.SIGUSR1)
        enabled_sent = time.monotonic()
        if real:
            # Function check (this run's later memory samples are disturbed by it): how soon the idle resident finds the helper.
            for _ in range(60):
                src = call('capabilities').get('result', {}).get('source', {})
                if src.get('helper', {}).get('available'): result['discovered_after_enable_s'] = round(time.monotonic() - enabled_sent, 2); break
                time.sleep(0.5)
    if t in reclaim_at:
        before = rollup(pid)['Rss']
        rc = []
        for _ in range(8):  # mapped file pages need several aging passes
            try: (cgroup/'memory.reclaim').write_text('200M'); rc.append('ok')
            except OSError as e: rc.append(str(e.errno))
            time.sleep(0.4)
        result['reclaims'].append({'t': t, 'rc': rc, 'rss_before': before, 'rss_after': rollup(pid)['Rss']})
    r = rollup(pid); r['t'] = t; r['majflt'] = majflt(); result['series'].append(r)
    if t in full_at: (out/f'{t:04d}s.smaps').write_text(Path(f'/proc/{pid}/smaps').read_text())
    print(json.dumps({k: r[k] for k in ('t', 'Rss', 'Anonymous', 'file', 'majflt')}), flush=True)
    t += 5
# Only now touch the resident through its socket: capability and memory counters.
caps = call('capabilities')
result['source'] = caps.get('result', {}).get('source')
result['diagnostics_memory'] = call('diagnostics').get('result', {}).get('memory')
if '--capture-after' in a:
    # End-to-end check after the idle discovery: one desktop capture through the extension to a private local destination.
    import shutil
    got = call('settings.get').get('result', {}); doc = got.get('document', {}); rev = got.get('metadata', {}).get('acceptedRevision')
    for k, act in doc.get('actions', {}).items():
        if isinstance(act, dict) and 'destination' in act: act['destination'] = 'local'; act['profileId'] = None
    if isinstance(doc.get('captureDefaults'), dict): doc['captureDefaults']['destination'] = 'local'; doc['captureDefaults']['profileId'] = None
    (root/'files').mkdir(exist_ok=True)
    if isinstance(doc.get('archive'), dict): doc['archive']['root'] = str(root/'files'); doc['archive']['keepUploads'] = True
    if isinstance(doc.get('preferences'), dict) and 'notifications' in doc['preferences']: doc['preferences']['notifications'] = False
    result['capture_settings'] = call('settings.save', {'document': doc, 'expectedRevision': rev}).get('ok')
    result['capture_invoke'] = call('action.invoke', {'action': 'desktop'}, timeout=90)
    for _ in range(60):
        time.sleep(1)
        ops = call('operation.recent').get('result', {}).get('operations', [])
        if ops and all(o.get('state') in ('completed', 'failed', 'partial', 'cancelled') for o in ops): break
    result['capture_state'] = [{k: o.get(k) for k in ('id', 'state', 'action', 'error')} for o in call('operation.recent').get('result', {}).get('operations', [])][:2]
    pngs = sorted((root/'files').rglob('*.png'))
    if pngs: shutil.copy(pngs[-1], out/'capture-after-enable.png'); result['capture_file'] = pngs[-1].name
if real: result['extension_after'] = ext_state()
calls = [json.loads(l) for l in shell_log.read_text().splitlines()]
result['shell_events'] = [dict(e, rel=round(e['t'] - t0, 2)) for e in calls]
result['hello_count'] = sum(1 for e in calls if e['event'] == 'call' and e.get('method') == 'Hello') + sum(1 for e in calls if e['event'] == 'absent_call' and e.get('method') == 'Hello')
if enabled_sent:
    hellos = [e['t'] for e in calls if e['event'] == 'call' and e.get('method') == 'Hello' and e['t'] >= enabled_sent]
    result['first_hello_after_enable_s'] = round(hellos[0] - enabled_sent, 3) if hellos else None
call('ui.quit')
for _ in range(100):
    time.sleep(0.2)
    if proc.poll() is not None and not Path(f'/proc/{pid}').exists(): break
else:
    for x in {pid, proc.pid}:
        try: os.kill(x, signal.SIGTERM)
        except ProcessLookupError: pass
    proc.wait(20)
if shell: shell.terminate(); shell.wait(10)
result['exit'] = proc.returncode
(out/'result.json').write_text(json.dumps(result, indent=1) + '\n')
print('done', name, 'hello', result['hello_count'], 'source.ready?', json.dumps(result['source'])[:300], flush=True)
