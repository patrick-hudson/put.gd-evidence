import json, os, subprocess, time, pathlib
S = pathlib.Path(os.environ['S']); B = pathlib.Path(os.environ.get('BUILD', '/usr/bin'))
RUNS = int(os.environ.get('RUNS', '4')); CONTENT = os.environ.get('CONTENT', 'static')
log = open(S / 'result.log', 'w')
def say(*a): print(time.strftime('%H:%M:%S'), *a, file=log, flush=True)
def cli(m, p=None, timeout=60):
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
say('compositor', os.environ.get('COMP', 'magpie'), 'content', CONTENT, 'runs', RUNS)
say('globals', sorted({l.split("'")[1] for l in w.splitlines() if "interface: '" in l and ('capture' in l or 'toplevel' in l or 'virtual' in l or 'layer_shell' in l or 'input' in l)}))
res = subprocess.Popen([str(B / 'putgd'), '--background'], stdout=open(S / 'resident.log', 'w'), stderr=subprocess.STDOUT)
sock = pathlib.Path(os.environ['XDG_RUNTIME_DIR']) / 'putgd/session.sock'
say('socket', bool(wait(lambda: sock.exists(), 20))); time.sleep(2)
rev = cli('settings.get').get('result', {}).get('metadata', {}).get('acceptedRevision')
say('patch', cli('settings.patch', {'patch': {'archive': {'keepUploads': True, 'root': str(S / 'archive')}}, 'expectedRevision': rev}).get('ok'))
cmd = 'sleep 600' if CONTENT == 'static' else 'while :; do date +%s.%N; sleep 0.05; done'
foot = subprocess.Popen(['foot', '-a', 'redwin', '-T', 'redwin', '-o', 'colors.background=c00000', '-W', '60x20', 'sh', '-c', cmd])
time.sleep(3)
say('windows', json.dumps(cli('recording.windows').get('result', {}))[:400])
ok = 0
PRE = os.environ.get('PRE', '')
def st(rid): return cli('recording.inspect', {'id': rid}).get('result', {}).get('state')
for i in range(RUNS):
    t0 = time.time()
    if PRE == 'monitor':
        # B's failing sequence: a monitor recording reviewed and cancelled, then the window at once.
        a = cli('recording.prepare', {'target': {'kind': 'monitor'}, 'format': 'mp4', 'fps': 30}).get('result', {}).get('recordingId')
        wait(lambda: st(a) == 'ready', 30); cli('recording.start', {'id': a}); time.sleep(3); cli('recording.stop', {'id': a}, timeout=60)
        wait(lambda: st(a) == 'reviewing', 30)
        mi = cli('recording.inspect', {'id': a}).get('result', {})
        say(i, 'monitor', mi.get('state'), mi.get('canvas'), mi.get('durationUs'))
        cli('recording.cancel', {'id': a})
        say(i, 'capabilities.active after cancel', cli('recording.capabilities').get('result', {}).get('active'))
    prep = cli('recording.prepare', {'target': {'kind': 'window'}, 'format': 'mp4', 'fps': 30}, timeout=60)
    rid = prep.get('result', {}).get('recordingId') or prep.get('result', {}).get('id')
    say(i, 'prepare', prep.get('ok'), json.dumps(prep.get('error'))[:200])
    if not rid: continue
    _ = wait(lambda: cli('recording.inspect', {'id': rid}).get('result', {}).get('state') in ('ready', 'failed', None), 30)
    ins = cli('recording.inspect', {'id': rid})
    say(i, 'ready-state', ins.get('result', {}).get('state'), json.dumps(ins.get('error'))[:200], 'canvas', ins.get('result', {}).get('canvas'))
    s1 = cli('recording.start', {'id': rid}); say(i, 'start', s1.get('ok'), json.dumps(s1.get('error'))[:200])
    time.sleep(4)
    s2 = cli('recording.stop', {'id': rid}, timeout=60); say(i, 'stop', s2.get('ok'), json.dumps(s2.get('error'))[:300], json.dumps(s2.get('result'))[:300])
    wait(lambda: cli('recording.inspect', {'id': rid}).get('result', {}).get('state') in ('reviewing', 'failed', None), 60)
    ins = cli('recording.inspect', {'id': rid})
    r = ins.get('result', {})
    say(i, 'recorded', r.get('state'), r.get('canvas'), r.get('durationUs'), json.dumps(r.get('error'))[:300], 'outer', json.dumps(ins.get('error'))[:300], r.get('stopReason'))
    if r.get('state') == 'reviewing':
        out = S / f'clip{i}.mp4'
        cli('recording.saveCopy', {'id': rid, 'path': str(out)})
        wait(lambda: (cli('recording.inspect', {'id': rid}).get('result', {}).get('lastExport') or {}).get('status') in ('saved', 'failed'), 120)
        m = subprocess.run([str(B / 'putgd-record'), '--motion', str(out), '8'], capture_output=True, text=True)
        say(i, 'motion', m.stdout.strip(), m.stderr.strip()[:200])
        ok += 1
    cli('recording.cancel', {'id': rid})
    wait(lambda: cli('recording.capabilities').get('result', {}).get('active') is None, 30)
    time.sleep(1)
say('RESULT', f'{ok}/{RUNS}')
foot.terminate()
cli('ui.quit'); res.wait(30); say('DONE')
