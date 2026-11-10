#!/usr/bin/env python3
"""annotate.py RUN KEY IN.png OUT.png COMMANDS.json

Draws call-outs on a picture with put.gd's own image editor, in a lab guest, through
the session methods the MCP helper's open_editor / edit_image / save_editor_copy use:
editor.open (file), editor.apply, editor.saveCopy, editor.cancel.
COMMANDS.json is a list of shapes, e.g.
  [{"kind":"rectangle","rect":[x,y,w,h]}, {"kind":"arrow","from":[x,y],"to":[x,y]}, {"kind":"text","at":[x,y],"text":"..."}]
"""
import json, os, subprocess, sys, time
ROOT = os.path.expanduser('~/work/i1363'); LAB = [sys.executable, os.path.join(ROOT, 'tools/lab/lab.py')]
run, key, src, dst, spec = sys.argv[1:6]; RUN = os.path.join(ROOT, 'work/lab-runs', run)
state = json.load(open(os.path.join(RUN, 'state.json')))
SSH = ['-i', key, '-o', 'IdentitiesOnly=yes', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
       '-o', 'UserKnownHostsFile=' + os.path.join(ROOT, 'work/hostkeys', run, 'known_hosts')]
def guest(cmd): return subprocess.run(['ssh', '-n', '-p', str(state['ssh_port'])] + SSH + ['lab@127.0.0.1', cmd], capture_output=True, text=True, timeout=60)
def cli(method, params):
    out = subprocess.run(LAB + ['cli', '--run', RUN, '--method', method, '--params', json.dumps(params)], capture_output=True, text=True, timeout=90)
    text = out.stdout.strip().splitlines()[-1] if out.stdout.strip() else out.stderr.strip()[-300:]
    try: r = json.loads(text)
    except Exception: return {'error': text}
    return r.get('result', r)
COLOR = '#ff2d55'
shapes = json.load(open(spec)); commands = []
for shape in shapes:
    shape = dict(shape)
    if shape['kind'] != 'redact': shape.setdefault('color', COLOR)
    if shape['kind'] in ('rectangle', 'arrow'): shape.setdefault('width', 4)
    if shape['kind'] == 'text': shape.setdefault('fontPixels', 22)
    commands.append({'op': 'add', 'shape': shape})
name = 'p1363-%d' % os.getpid()
guest('mkdir -p /home/lab/p1363-pics')
subprocess.run(['scp', '-q', '-P', str(state['ssh_port'])] + SSH + [src, 'lab@127.0.0.1:/home/lab/p1363-pics/%s-in.png' % name], check=True, stdin=subprocess.DEVNULL, timeout=120)
opened = cli('editor.open', {'source': 'file', 'path': '/home/lab/p1363-pics/%s-in.png' % name}); op = opened.get('operationId')
if not op: print('open failed', json.dumps(opened)[:400]); sys.exit(1)
ok = False
for _ in range(40):
    time.sleep(0.5); view = cli('editor.inspect', {'id': op})
    if isinstance(view, dict) and view.get('phase') == 'editing': ok = True; break
if not ok: print('editor not ready', json.dumps(view)[:400]); sys.exit(1)
applied = cli('editor.apply', {'id': op, 'commands': commands})
if 'error' in applied or applied.get('ok') is False: print('apply failed', json.dumps(applied)[:600]); cli('editor.cancel', {'id': op}); sys.exit(1)
saved = cli('editor.saveCopy', {'id': op, 'path': '/home/lab/p1363-pics/%s-out.png' % name, 'overwrite': True})
cli('editor.cancel', {'id': op})
if 'error' in saved or saved.get('ok') is False: print('save failed', json.dumps(saved)[:600]); sys.exit(1)
subprocess.run(['scp', '-q', '-P', str(state['ssh_port'])] + SSH + ['lab@127.0.0.1:/home/lab/p1363-pics/%s-out.png' % name, dst], check=True, stdin=subprocess.DEVNULL, timeout=120)
guest('rm -f /home/lab/p1363-pics/%s-in.png /home/lab/p1363-pics/%s-out.png' % (name, name))
print('annotated', dst, len(commands), 'shapes')
