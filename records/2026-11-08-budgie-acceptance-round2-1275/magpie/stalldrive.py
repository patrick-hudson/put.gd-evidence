import json, os, subprocess, time, pathlib
from PIL import Image, ImageChops
S = pathlib.Path(os.environ['S']); B = pathlib.Path(os.environ.get('BUILD', '/usr/bin'))
log = open(S / 'result.log', 'w')
def say(*a): print(time.strftime('%H:%M:%S'), *a, file=log, flush=True)
def cli(m, p=None, timeout=60):
    r = subprocess.run([str(B / 'putgd-cli'), m, json.dumps(p or {})], capture_output=True, text=True, timeout=timeout)
    try: return json.loads(r.stdout)
    except Exception: return {'raw': r.stdout}
def wait(c, s, step=0.2):
    end = time.time() + s
    while time.time() < end:
        v = c()
        if v: return v
        time.sleep(step)
def st(rid): return cli('recording.inspect', {'id': rid}).get('result', {}).get('state')
res = subprocess.Popen([str(B / 'putgd'), '--background'], stdout=open(S / 'resident.log', 'w'), stderr=subprocess.STDOUT)
wait(lambda: (pathlib.Path(os.environ['XDG_RUNTIME_DIR']) / 'putgd/session.sock').exists(), 20); time.sleep(2)
rev = cli('settings.get').get('result', {}).get('metadata', {}).get('acceptedRevision')
cli('settings.patch', {'patch': {'archive': {'keepUploads': True, 'root': str(S / 'archive')}, 'actions': {'desktop': {'destination': 'local'}}}, 'expectedRevision': rev}); time.sleep(1)
cmd = 'while :; do date +%s.%N; sleep 0.05; done'
foot = subprocess.Popen(['foot', '-a', 'win1', '-T', 'win1', '-W', '60x20', 'sh', '-c', cmd]); time.sleep(3)
def record(label):
    rid = cli('recording.prepare', {'target': {'kind': 'window'}, 'format': 'mp4', 'fps': 30}).get('result', {}).get('recordingId')
    wait(lambda: st(rid) == 'ready', 30); cli('recording.start', {'id': rid}); time.sleep(3); cli('recording.stop', {'id': rid}, timeout=60)
    wait(lambda: st(rid) == 'reviewing', 30); r = cli('recording.inspect', {'id': rid}).get('result', {})
    say(label, r.get('state'), r.get('canvas'), r.get('window'))
    cli('recording.cancel', {'id': rid}); wait(lambda: cli('recording.capabilities').get('result', {}).get('active') is None, 30); time.sleep(1)
def desk():
    n = len(list((S / 'archive').rglob('*.png'))); cli('action.invoke', {'action': 'desktop'}, timeout=20)
    wait(lambda: len(list((S / 'archive').rglob('*.png'))) > n, 20)
    return Image.open(sorted((S / 'archive').rglob('*.png'), key=lambda p: p.stat().st_mtime)[-1]).convert('RGB')
for i in range(7): record(f'win1 rec {i}')
a = desk(); time.sleep(1.5); b = desk()
diff = ImageChops.difference(a, b).getbbox()
say('desktop screenshots 1.5 s apart after the stall: changed bbox', diff, '(foot still drawing)' if diff else '(nothing changed)')
foot2 = subprocess.Popen(['foot', '-a', 'win2', '-T', 'win2', '-W', '40x10', 'sh', '-c', cmd]); time.sleep(3)
record('win2 (new window, active) rec 0')
say('DONE'); foot.terminate(); foot2.terminate(); cli('ui.quit'); res.wait(30)
