import json, os, subprocess, time, pathlib
S = pathlib.Path(os.environ['S']); B = pathlib.Path(os.environ['BUILD'])
log = open(S / 'result.log', 'w')
def say(*a): print(*a, file=log, flush=True)
def cli(m, p=None, timeout=30):
    r = subprocess.run([str(B / 'putgd-cli'), m, json.dumps(p or {})], capture_output=True, text=True, timeout=timeout)
    try: return json.loads(r.stdout)
    except Exception: return {'raw': r.stdout, 'err': r.stderr}
def wait(c, s, step=0.2):
    end = time.time() + s
    while time.time() < end:
        v = c()
        if v: return v
        time.sleep(step)
w = subprocess.run(['wayland-info'], capture_output=True, text=True).stdout
say('globals', sorted({l.split("'")[1] for l in w.splitlines() if "interface: '" in l and ('capture' in l or 'toplevel' in l or 'data_control' in l or 'layer_shell' in l or 'xdg_output' in l)}))
res = subprocess.Popen([str(B / 'putgd'), '--background'], stdout=open(S / 'resident.log', 'w'), stderr=subprocess.STDOUT)
sock = pathlib.Path(os.environ['XDG_RUNTIME_DIR']) / 'putgd/session.sock'
say('socket', bool(wait(lambda: sock.exists(), 20))); time.sleep(2)
caps = cli('capabilities').get('result', {}); src = caps.get('source', {})
say('adapter', src.get('adapter'))
say('capture', json.dumps({k: {'available': v.get('available'), 'error': v.get('error')} for k, v in src.get('capture', {}).items()}))
say('clipboard', json.dumps(src.get('clipboard'))[:300])
sh = src.get('shortcuts', {})
say('shortcuts', sh.get('available'), sh.get('backend'), sh.get('error'), {k: (v.get('state'), v.get('error')) for k, v in sh.get('bindings', {}).items() if v.get('requested')})
rev = cli('settings.get').get('result', {}).get('metadata', {}).get('acceptedRevision')
say('patch', cli('settings.patch', {'patch': {'archive': {'keepUploads': True, 'root': str(S / 'archive')}, 'actions': {a: {'destination': 'local'} for a in ('region', 'window', 'desktop', 'clipboard')}}, 'expectedRevision': rev}).get('ok'))
time.sleep(1)
def run_action(a):
    before = {o['id'] for o in cli('operation.recent').get('result', {}).get('operations', [])}
    r = cli('action.invoke', {'action': a}, timeout=60)
    op = wait(lambda: next((o for o in cli('operation.recent').get('result', {}).get('operations', []) if o['id'] not in before and o.get('state') in ('completed', 'failed', 'cancelled')), None), 30)
    return r, op
r, op = run_action('desktop')
say('desktop', json.dumps(r)[:150], op and op.get('state'), op and json.dumps(op.get('error'))[:200], op and [ (i.get('artifact') or {}).get('bytes') for i in op.get('items', [])])
foot = subprocess.Popen(['foot', '-a', 'redwin', '-T', 'redwin', '-o', 'colors.background=c00000', '-W', '60x20', 'sh', '-c', 'sleep 120'])
time.sleep(3)
say('windows', json.dumps(cli('capture.windows').get('result', {}))[:400])
r, op = run_action('window')
say('window', json.dumps(r)[:150], op and op.get('state'), op and json.dumps(op.get('error'))[:200], op and [(i.get('artifact') or {}).get('bytes') for i in op.get('items', [])])
arts = sorted((S / 'archive').rglob('*.png'), key=lambda p: p.stat().st_mtime)
say('archive pngs', [str(p.relative_to(S)) for p in arts])
time.sleep(3)
say('clipboard before wl-copy', subprocess.run(['wl-paste', '-l'], capture_output=True, text=True, timeout=5).stdout.split()[:4])
subprocess.run(['wl-copy', 'magpie import text'])
time.sleep(2)
say('clipboard after wl-copy', subprocess.run(['wl-paste', '-l'], capture_output=True, text=True, timeout=5).stdout.split()[:4])
r, op = run_action('clipboard')
say('clipboard import', op and op.get('state'), op and json.dumps(op.get('error'))[:200], op and [(i.get('artifact') or {}).get('mime') for i in op.get('items', [])])
types = subprocess.run(['wl-paste', '-l'], capture_output=True, text=True, timeout=5).stdout.split()
say('clipboard now offers', types[:6])
for kind in ('monitor', 'window'):
    prep = cli('recording.prepare', {'target': {'kind': kind}, 'format': 'mp4', 'fps': 30}, timeout=60)
    rid = prep.get('result', {}).get('recordingId') or prep.get('result', {}).get('id')
    say('prepare', kind, prep.get('ok'), json.dumps(prep.get('error'))[:200])
    if not rid: continue
    wait(lambda: cli('recording.inspect', {'id': rid}).get('result', {}).get('state') == 'ready', 30)
    cli('recording.start', {'id': rid}); time.sleep(4); cli('recording.stop', {'id': rid}, timeout=60)
    wait(lambda: cli('recording.inspect', {'id': rid}).get('result', {}).get('state') == 'reviewing', 60)
    ins = cli('recording.inspect', {'id': rid}).get('result', {})
    say('recorded', kind, ins.get('state'), ins.get('canvas'), ins.get('durationUs'), json.dumps(ins.get('error'))[:200])
    if ins.get('state') == 'reviewing':
        out = S / f'{kind}.mp4'; cli('recording.saveCopy', {'id': rid, 'path': str(out)})
        wait(lambda: (cli('recording.inspect', {'id': rid}).get('result', {}).get('lastExit') or cli('recording.inspect', {'id': rid}).get('result', {}).get('lastExport') or {}).get('status') in ('saved', 'failed'), 120)
        m = subprocess.run([str(B / 'putgd-record'), '--motion', str(out), '8'], capture_output=True, text=True)
        say('motion', kind, m.stdout.strip(), m.stderr.strip()[:200])
    cli('recording.cancel', {'id': rid})
    wait(lambda: cli('recording.capabilities').get('result', {}).get('active') is None, 30)
foot.terminate()
cli('ui.quit'); res.wait(30); say('DONE')
