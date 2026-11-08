# Cancel a monitor recording, then prepare a window recording at once (no
# wait for the old helper). Before the fix this hits recording_active.
import json, os, subprocess, time, pathlib
S = pathlib.Path(os.environ['S']); B = pathlib.Path(os.environ.get('BUILD', '/usr/bin'))
RUNS = int(os.environ.get('RUNS', '5'))
log = open(S / 'result.log', 'w')
def say(*a): print(time.strftime('%H:%M:%S'), *a, file=log, flush=True)
def cli(m, p=None, timeout=60):
    r = subprocess.run([str(B / 'putgd-cli'), m, json.dumps(p or {})], capture_output=True, text=True, timeout=timeout)
    try: return json.loads(r.stdout)
    except Exception: return {'raw': r.stdout, 'err': r.stderr}
def wait(c, s, step=0.1):
    end = time.time() + s
    while time.time() < end:
        v = c()
        if v: return v
        time.sleep(step)
def st(rid): return cli('recording.inspect', {'id': rid}).get('result', {}).get('state')
res = subprocess.Popen([str(B / 'putgd'), '--background'], stdout=open(S / 'resident.log', 'w'), stderr=subprocess.STDOUT)
sock = pathlib.Path(os.environ['XDG_RUNTIME_DIR']) / 'putgd/session.sock'
say('compositor', os.environ.get('COMP', 'magpie'), 'build', str(B), 'socket', bool(wait(lambda: sock.exists(), 20))); time.sleep(2)
foot = subprocess.Popen(['foot', '-a', 'redwin', '-T', 'redwin', '-W', '60x20', 'sh', '-c', 'while :; do date +%s.%N; sleep 0.05; done'])
time.sleep(3)
say('ready', bool(wait(lambda: cli('recording.capabilities').get('ok'), 20, 0.5)))
rev = cli('settings.get').get('result', {}).get('metadata', {}).get('acceptedRevision')
say('patch', cli('settings.patch', {'patch': {'archive': {'keepUploads': True, 'root': str(S / 'archive')}}, 'expectedRevision': rev}).get('ok')); time.sleep(1)
ok = 0
for i in range(RUNS):
    p = cli('recording.prepare', {'target': {'kind': 'monitor'}, 'format': 'mp4', 'fps': 30})
    a = p.get('result', {}).get('recordingId')
    if not a: say(i, 'monitor prepare failed', json.dumps(p)[:300]); time.sleep(2); continue
    wait(lambda: st(a) == 'ready', 30)
    if os.environ.get('FROM', 'reviewing') == 'reviewing':
        cli('recording.start', {'id': a}); time.sleep(2); cli('recording.stop', {'id': a}); wait(lambda: st(a) == 'reviewing', 30)
    cli('recording.cancel', {'id': a})
    active = cli('recording.capabilities').get('result', {}).get('active')
    b = cli('recording.prepare', {'target': {'kind': 'window'}, 'format': 'mp4', 'fps': 30})
    rid = b.get('result', {}).get('recordingId')
    s = wait(lambda: st(rid) in ('ready', None), 30)
    final = st(rid)
    say(i, os.environ.get('FROM', 'reviewing'), 'capabilities.active after cancel', active, 'window prepare ok', b.get('ok'), '-> state', final)
    if final == 'ready': ok += 1; cli('recording.cancel', {'id': rid})
    wait(lambda: cli('recording.capabilities').get('result', {}).get('active') is None, 30); time.sleep(1.5)
say('RESULT', f'{ok}/{RUNS}')
foot.terminate(); cli('ui.quit'); res.wait(30); say('DONE')
