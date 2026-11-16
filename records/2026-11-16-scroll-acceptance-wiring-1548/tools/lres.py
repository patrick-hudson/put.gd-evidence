#!/usr/bin/env python3
"""A lab put.gd resident for PR #1548's desktop checks: its own config, data, cache and
runtime directory, every destination local, the helper's debug log on, in its own
systemd user scope. Session environment from the desktop's own process.

lres.py ROOT start APP [--expect-tree TREE]
lres.py ROOT stop
lres.py ROOT rpc METHOD [JSON]
lres.py ROOT env            (prints the environment as JSON)
ROOT holds env.json (written by start), c/ d/ s/ cache/ archive/ helper.log.
"""
import json, os, subprocess, sys, time
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
UNIT = 'w1548-res'
RUNTIME = Path('/tmp/w48')


def session_env():
    uid = os.getuid()
    run = f'/run/user/{uid}'
    # A child of the session first: a compositor's own environment may lack WAYLAND_DISPLAY.
    names = ['quickshell', 'plasmashell', 'gnome-shell', 'cinnamon', 'labwc', 'kwin_wayland', 'Hyprland']
    pid = None
    for n in names:
        out = subprocess.run(['pgrep', '-u', str(uid), '-x', n], capture_output=True, text=True).stdout.split()
        if out:
            pid = out[0]
            break
    if not pid:
        raise SystemExit('no desktop process found')
    raw = (Path('/proc') / pid / 'environ').read_bytes().split(b'\0')
    env = dict(x.decode(errors='replace').split('=', 1) for x in raw if b'=' in x)
    keep = ['DISPLAY', 'WAYLAND_DISPLAY', 'XAUTHORITY', 'XDG_SESSION_TYPE', 'XDG_CURRENT_DESKTOP', 'XDG_SESSION_DESKTOP', 'DESKTOP_SESSION',
            'DBUS_SESSION_BUS_ADDRESS', 'HYPRLAND_INSTANCE_SIGNATURE', 'LANG', 'OMARCHY_PATH']
    e = {k: env[k] for k in keep if k in env}
    e.setdefault('DBUS_SESSION_BUS_ADDRESS', f'unix:path={run}/bus')
    if e.get('XDG_SESSION_TYPE') == 'wayland' and not e.get('WAYLAND_DISPLAY'):
        sockets = sorted(n for n in os.listdir(run) if n.startswith('wayland-') and not n.endswith('.lock'))
        if sockets:
            e['WAYLAND_DISPLAY'] = sockets[0]
    if e.get('WAYLAND_DISPLAY') and not e['WAYLAND_DISPLAY'].startswith('/'):
        e['WAYLAND_DISPLAY'] = f'{run}/' + e['WAYLAND_DISPLAY']
    if e.get('XDG_SESSION_TYPE') == 'x11' and 'DISPLAY' not in e:
        e['DISPLAY'] = ':0'
    e.update(PIPEWIRE_RUNTIME_DIR=run, PULSE_SERVER=f'unix:{run}/pulse/native')
    return e, run


def resident_env():
    e, run = session_env()
    e.update(XDG_RUNTIME_DIR=str(RUNTIME), XDG_CONFIG_HOME=str(ROOT / 'c'), XDG_DATA_HOME=str(ROOT / 'd'), XDG_STATE_HOME=str(ROOT / 's'),
             XDG_CACHE_HOME=str(ROOT / 'cache'), PUTGD_RECORD_DEBUG_LOG=str(ROOT / 'helper.log'))
    if e.get('XDG_SESSION_TYPE') == 'wayland':
        e['QT_QPA_PLATFORM'] = 'wayland'
    return e, run


def cli_cmd():
    return json.loads((ROOT / 'cli.json').read_text())


def rpc(method, params=None):
    e = json.loads((ROOT / 'env.json').read_text())
    r = subprocess.run([*cli_cmd(), method, json.dumps(params or {})], env=dict(os.environ, **e), capture_output=True, text=True, timeout=100)
    try:
        o = json.loads(r.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(r.stdout + r.stderr)
    if not o.get('ok'):
        raise RuntimeError(json.dumps(o))
    return o['result']


def start(app, expect_tree=None):
    for n in ['c', 'd', 's', 'cache', 'archive']:
        (ROOT / n).mkdir(mode=0o700, parents=True, exist_ok=True)
    if not RUNTIME.exists():
        RUNTIME.mkdir(mode=0o700)
    e, run = resident_env()
    # The helper and the resident reach the desktop through the real runtime dir's sockets.
    for name in os.listdir(run):
        link = RUNTIME / name
        if name != 'putgd' and not link.exists() and not link.is_symlink():
            link.symlink_to(Path(run) / name)
    (ROOT / 'env.json').write_text(json.dumps(e))
    app = json.loads(app) if app.startswith('[') else [app]
    cli = [str(Path(app[0]).with_name('putgd-cli'))] if Path(app[0]).name == 'putgd' else None
    if Path(app[0]).name == 'AppRun':
        base = Path(app[0]).parent
        cli = ['env', f'LD_LIBRARY_PATH={base}/usr/lib:{base}/usr/lib/putgd', str(base / 'usr/bin/putgd-cli')]
    (ROOT / 'cli.json').write_text(json.dumps(cli or ['putgd-cli']))
    pass_env = [f'{k}={v}' for k, v in e.items()]
    subprocess.Popen(['systemd-run', '--user', '--scope', f'--unit={UNIT}', 'env', *pass_env, *app, '--background'],
                     env=dict(os.environ, XDG_RUNTIME_DIR=run), stdout=open(ROOT / 'resident.log', 'w'), stderr=subprocess.STDOUT, start_new_session=True)
    for _ in range(300):
        try:
            s = rpc('settings.get')
            break
        except Exception as err:
            last = err
            time.sleep(0.1)
    else:
        raise SystemExit(f'resident did not answer: {last}')
    t = rpc('settings.developmentTemplate')
    d = t.get('document', t)
    for v in d['actions'].values():
        if isinstance(v, dict) and 'destination' in v:
            v.update(destination='local', profileId=None)
    d['archive'].update(keepUploads=True, root=str(ROOT / 'archive'))
    d['preferences']['updates'] = {'check': False}
    # The `scroll` hotkey, for the bar's caption (env LRES_SCROLL_KEY, e.g. Ctrl+Shift+F7).
    if os.environ.get('LRES_SCROLL_KEY') and isinstance(d['actions'].get('scroll'), dict):
        d['actions']['scroll']['shortcut'] = os.environ['LRES_SCROLL_KEY']
    rpc('settings.save', {'document': d, 'expectedRevision': s['metadata']['observedRevision']})
    rpc('settings.reload')
    diag = rpc('diagnostics')
    (ROOT / 'diagnostics.json').write_text(json.dumps(diag, indent=1))
    if expect_tree and diag['build'].get('gitTree') != expect_tree:
        raise SystemExit(f"wrong build: {diag['build']}")
    doc = rpc('settings.get')['document']
    assert all(v['destination'] == 'local' for v in doc['actions'].values() if isinstance(v, dict) and 'destination' in v)
    print(json.dumps({'build': diag['build'], 'allLocal': True, 'fromTop': doc['preferences'].get('scrollCaptureFromTop')}), flush=True)


def stop():
    subprocess.run(['systemctl', '--user', 'stop', f'{UNIT}.scope'], env=dict(os.environ, XDG_RUNTIME_DIR=f'/run/user/{os.getuid()}'))


if __name__ == '__main__':
    cmd = sys.argv[2]
    if cmd == 'start':
        args = sys.argv[3:]
        tree = args[args.index('--expect-tree') + 1] if '--expect-tree' in args else None
        start(args[0], tree)
    elif cmd == 'stop':
        stop()
    elif cmd == 'rpc':
        print(json.dumps(rpc(sys.argv[3], json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}), indent=1))
    elif cmd == 'env':
        print(json.dumps(resident_env()[0]))
