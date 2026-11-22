"""Annotate pictures with put.gd's own editor in a headless private resident: annotate.py DIR TREE (DIR/plan.json)."""
import json, os, subprocess, sys, tempfile, time
from pathlib import Path
d = Path(sys.argv[1]).resolve(); plan = json.loads((d / 'plan.json').read_text())
with tempfile.TemporaryDirectory(prefix='an20-', dir='/tmp') as directory:
    root = Path(directory); runtime = root / 'r'; runtime.mkdir(mode=0o700)
    sock = runtime / 'putgd/session.sock'
    env = dict(os.environ, QT_QPA_PLATFORM='offscreen', XDG_RUNTIME_DIR=str(runtime))
    env.pop('DISPLAY', None); env.pop('WAYLAND_DISPLAY', None)
    for n in ('CONFIG', 'DATA', 'STATE', 'CACHE'):
        env['XDG_' + n + '_HOME'] = str(root / n.lower())
    log = (root / 'resident.log').open('w')
    res = subprocess.Popen(['dbus-run-session', '--', '/usr/bin/putgd', '--background'], env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)
    def cli(m, p=None):
        r = subprocess.run(['/usr/bin/putgd-cli', '--socket', str(sock), '--params-stdin', m], input=json.dumps(p or {}), text=True, env=env, capture_output=True, timeout=60)
        try: return json.loads(r.stdout)
        except ValueError: return {'ok': False, 'error': r.stderr[-200:]}
    def retry(m, p=None):
        end = time.monotonic() + 40
        while True:
            r = cli(m, p)
            if r.get('ok'): return r['result']
            if time.monotonic() > end: raise RuntimeError((m, r))
            time.sleep(.4)
    try:
        b = retry('diagnostics')['build']; assert b['gitTree'] == sys.argv[2], b
        for pic in plan:
            oid = retry('editor.open', {'source': 'file', 'path': str(d / pic['from'])})['operationId']
            retry('editor.apply', {'id': oid, 'commands': [{'op': 'add', 'shape': s} for s in pic['shapes']]})
            retry('editor.saveCopy', {'id': oid, 'path': str(d / pic['to'])})
            retry('editor.cancel', {'id': oid}); print('saved', pic['to'], flush=True)
        print('build', b['gitCommit'], b['gitTree'])
    finally:
        cli('ui.quit'); 
        try: res.wait(10)
        except subprocess.TimeoutExpired: res.terminate(); res.wait(10)
