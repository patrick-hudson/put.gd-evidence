#!/usr/bin/env python3
"""checks.py RUN KEY DESKTOP [--skip-lock]

The #1363 functional sequence on one two-monitor lab guest, run on its QEMU host:
Capture monitor per head, Repeat last region and its refusals, delayed captures with
the countdown seen on screen and absent from the image, both cancel paths and a lock
during the countdown. Prints one line per check and exits 1 when any check fails.
DESKTOP is cinnamon, gnome, kde, budgie or hyprland. Needs Pillow on the host and,
for budgie and hyprland, /tmp/wayland_pointer.py and /tmp/env.sh in the guest.
"""
import json, os, subprocess, sys, tempfile, time
from PIL import Image, ImageChops, ImageStat

ROOT = os.environ['SWEEP_ROOT']; LAB = [sys.executable, os.path.join(ROOT, 'tools/lab/lab.py')]
run, key, desktop = sys.argv[1:4]; skip_lock = '--skip-lock' in sys.argv
RUN = os.path.join(ROOT, 'work/lab-runs', run); state = json.load(open(os.path.join(RUN, 'state.json')))
SSH = ['-i', key, '-o', 'IdentitiesOnly=yes', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes', '-o', 'ConnectTimeout=10',
       '-o', 'UserKnownHostsFile=' + state['known_hosts']]
WORK = os.path.join(RUN, 'acceptance'); os.makedirs(WORK, mode=0o700, exist_ok=True)
ENV = '. /tmp/env.sh; '
# Where each QEMU head sits in the compositor's layout (labwc orders the outputs its own way).
ORIGIN = {0: (1024, 0), 1: (0, 0)} if desktop == 'budgie' else {0: (0, 0), 1: (1280, 0)}
SIZE = {0: (1280, 800), 1: (1024, 768)}; EXTENT = (2304, 800)
MOVE = {
    'cinnamon': ('DISPLAY=:0 xrandr --output Virtual-2 --pos 1280x32', 'DISPLAY=:0 xrandr --output Virtual-2 --pos 1280x0'),
    'gnome': ('gdctl set --logical-monitor --primary --monitor Virtual-1 --logical-monitor --monitor Virtual-2 --below Virtual-1',
              'gdctl set --logical-monitor --primary --monitor Virtual-1 --logical-monitor --monitor Virtual-2 --right-of Virtual-1'),
    'kde': ('export XDG_RUNTIME_DIR=/run/user/$(id -u) WAYLAND_DISPLAY=wayland-0; kscreen-doctor output.Virtual-2.position.1280,32',
            'export XDG_RUNTIME_DIR=/run/user/$(id -u) WAYLAND_DISPLAY=wayland-0; kscreen-doctor output.Virtual-2.position.1280,0'),
    'budgie': (ENV + 'wlr-randr --output Virtual-1 --pos 1024,64', ENV + 'wlr-randr --output Virtual-1 --pos 1024,0'),
    'hyprland': (ENV + '''hyprctl eval 'hl.monitor({ output = "Virtual-2", mode = "1024x768@60", position = "1280x100", scale = 1 })' ''',
                 ENV + '''hyprctl eval 'hl.monitor({ output = "Virtual-1", mode = "1280x800@60", position = "0x0", scale = 1 })'; '''
                       '''hyprctl eval 'hl.monitor({ output = "Virtual-2", mode = "1024x768@60", position = "1280x0", scale = 1 })' '''),
}[desktop]

def guest(cmd, timeout=60):
    out = subprocess.run(['ssh', '-n', '-p', str(state['ssh_port'])] + SSH + ['lab@127.0.0.1', cmd], capture_output=True, text=True, timeout=timeout)
    return out.stdout.strip()
def lab(*args, timeout=90):
    out = subprocess.run(LAB + list(args), capture_output=True, text=True, timeout=timeout)
    text = out.stdout.strip().splitlines()[-1] if out.stdout.strip() else out.stderr.strip()[-300:]
    try: return json.loads(text)
    except Exception: return {'raw': text}
def cli(method, params=None):
    r = lab('cli', '--run', RUN, '--method', method, '--params', json.dumps(params or {}))
    with open(os.path.join(WORK, 'session.jsonl'), 'a') as f: f.write(json.dumps({'method': method, 'params': params, 'reply': r}) + '\n')
    return r.get('result', r) if isinstance(r, dict) else r
def qmp(evs, head=None):
    return lab('input', '--run', RUN, *(['--head', str(head)] if head is not None else []), json.dumps(evs))
def tablet(x, y, w, h):
    return [{'type': 'abs', 'data': {'axis': 'x', 'value': int(x * 32767 / (w - 1))}}, {'type': 'abs', 'data': {'axis': 'y', 'value': int(y * 32767 / (h - 1))}}]
def button(down): return [{'type': 'btn', 'data': {'down': down, 'button': 'left'}}]
def locate(x, y):
    # Global layout point -> (head, x, y) for the X11 per-head tablets.
    for head, (ox, oy) in ORIGIN.items():
        w, h = SIZE[head]
        if ox <= x < ox + w and oy <= y < oy + h: return head, x - ox, y - oy
    raise SystemExit('point outside the layout')
def move(x, y):
    # A QEMU tablet that is asked for the position it last reported sends nothing, and with
    # one tablet per head the pointer then stays on the other head: always nudge first.
    if desktop == 'cinnamon':
        head, hx, hy = locate(x, y); qmp(tablet(max(hx - 3, 0), max(hy - 3, 0), *SIZE[head]), head); qmp(tablet(hx, hy, *SIZE[head]), head)
    elif desktop in ('gnome', 'kde'): qmp(tablet(max(x - 3, 0), max(y - 3, 0), *EXTENT)); qmp(tablet(x, y, *EXTENT))
    else: guest(ENV + 'python3 /tmp/wayland_pointer.py move %d %d --extent %d %d' % (x, y, *EXTENT))
def click(x, y):
    if desktop in ('budgie', 'hyprland'):
        guest(ENV + 'python3 /tmp/wayland_pointer.py click %d %d --extent %d %d' % (x, y, *EXTENT)); return
    head = locate(x, y)[0] if desktop == 'cinnamon' else None
    move(x, y); time.sleep(0.25); qmp(button(True), head); time.sleep(0.15); qmp(button(False), head)
def drag(x1, y1, x2, y2):
    if desktop in ('budgie', 'hyprland'):
        guest(ENV + 'python3 /tmp/wayland_pointer.py drag %d %d %d %d --extent %d %d --steps 8' % (x1, y1, x2, y2, *EXTENT)); return
    head = locate(x1, y1)[0] if desktop == 'cinnamon' else None
    move(x1, y1); time.sleep(0.3); qmp(button(True), head); time.sleep(0.2)
    for step in range(1, 9): move(x1 + (x2 - x1) * step // 8, y1 + (y2 - y1) * step // 8); time.sleep(0.05)
    time.sleep(0.2); qmp(button(False), head)
def start(action, delay=0):
    params = {'action': action}
    if delay: params['delaySeconds'] = delay
    r = cli('action.invoke', params)
    if 'operationId' not in r: raise SystemExit('invoke failed: ' + json.dumps(r)[:300])
    return r['operationId'], time.time()
def wait(op, limit=60):
    end = time.time() + limit
    while time.time() < end:
        o = cli('operation.inspect', {'id': op})
        if o.get('state') not in ('accepted', 'acquiring', 'stored', 'running', 'editing', 'recording', None):
            paths = [i.get('local', {}).get('path') for i in o.get('items', [])]
            return {'state': o['state'], 'code': o.get('error', {}).get('code', ''), 'message': o.get('error', {}).get('message', ''),
                    'action': o.get('action'), 'path': paths[0] if paths else None, 'done': time.time()}
        time.sleep(0.25)
    return {'state': 'timeout', 'code': '', 'message': '', 'action': '', 'path': None, 'done': time.time()}
def invoke(action, delay=0):
    op, began = start(action, delay); r = wait(op); r['seconds'] = r['done'] - began; return r
count = [0]
def fetch(path):
    count[0] += 1; local = os.path.join(WORK, 'capture-%d.png' % count[0])
    subprocess.run(['scp', '-q', '-P', str(state['ssh_port'])] + SSH + ['lab@127.0.0.1:' + path, local], check=True, stdin=subprocess.DEVNULL, timeout=120)
    return Image.open(local).convert('RGB')
def dump(head):
    lab('screenshot', '--run', RUN, '--head', str(head)); return Image.open(os.path.join(RUN, 'witness-head%d.ppm' % head)).convert('RGB')
def differs(a, b): return sum(ImageStat.Stat(ImageChops.difference(a, b)).mean) / 3
failed = [0]
def row(name, ok, detail):
    if not ok: failed[0] += 1
    with open(os.path.join(WORK,'rows.jsonl'),'a') as f: f.write(json.dumps({'row':name,'passed':bool(ok),'detail':detail})+'\n')
    print('%-4s %-46s %s' % ('ok' if ok else 'FAIL', name, detail), flush=True)
def region(delay=0):
    op, began = start('region', delay); time.sleep(2.5); drag(300, 300, 600, 500); released = time.time()
    r = wait(op); r['after'] = r['done'] - released; return r



sys.path.insert(0,os.path.join(ROOT,'tools/lab'))
import lab as native, shlex
assert cli('diagnostics')['build']['gitTree']=='4346aa6ecf750b5cceb4dcedf6c10e5c11279ad3'
# Native environment exported by the lab's real-session discovery, no guessed display.
native.guest_session(RUN,"python3 - <<'PYENV'\nimport os,shlex\nopen('/tmp/env.sh','w').write('\\n'.join('export '+k+'='+shlex.quote(v) for k,v in os.environ.items())+'\\n')\nPYENV\n")
for f in ('wayland_pointer.py','wayland_toplevels.py','gtk_clipboard_fixture.py'):
 native.put(RUN,os.path.join(ROOT,'tools/lab',f),'/tmp/'+f)
fixture_pid=None
try:
 doc=cli('settings.get'); cli('settings.patch',{'patch':{'archive':{'keepUploads':True},'preferences':{'notifications':False,'regionSelectionMode':'live'},'actions':{name:{'destination':'local','profileId':None} for name in ('region','desktop','window')}},'expectedRevision':doc['metadata']['observedRevision']})
 time.sleep(5)
 def frame(name):
  for head in (0,1): dump(head).save(os.path.join(WORK,name+'-head%d.png'%head))
 def check(name,call):
  for attempt in (1,2):
   try:
    ok,detail=call(); row(name,ok,json.dumps({'attempt':attempt,**detail})); frame(name+'-'+str(attempt))
    if ok: return
   except Exception as e: row(name,False,json.dumps({'attempt':attempt,'driverError':str(e)})); frame(name+'-'+str(attempt))
 def capture(action,selection=None,delay=0):
  op,_=start(action,delay)
  if selection: time.sleep(1.5); drag(*selection)
  v=wait(op); im=fetch(v['path']) if v['path'] else None
  return v,im
 def dimensions(action,size,selection=None,delay=0):
  v,im=capture(action,selection,delay)
  return v['state']=='completed' and im is not None and im.size==size,{'operation':v,'size':im.size if im else None}
 if desktop=='hyprland':
  doc=cli('settings.get'); cli('settings.patch',{'patch':{'actions':{'region':{'shortcut':'Ctrl+Shift+F9'}}},'expectedRevision':doc['metadata']['observedRevision']}); time.sleep(2)
  def early(kind):
   old={v['id'] for v in cli('operation.recent')['operations']}; move(300,300); native.key(RUN,['ctrl','shift','f9'])
   if kind=='escape': lab('key','--run',RUN,'esc')
   else: guest(ENV+'python3 /tmp/wayland_pointer.py drag 300 300 600 500 --extent 2304 800 --settle-ms 0 --step-ms 10')
   for _ in range(100):
    new=[v for v in cli('operation.recent')['operations'] if v['id'] not in old]
    if new and new[0]['state'] in ('completed','cancelled','failed'): break
    time.sleep(.1)
   return bool(new) and new[0]['state']==('cancelled' if kind=='escape' else 'completed'),{'operation':new[0] if new else None}
  check('early-hotkey-drag',lambda:early('drag')); check('early-hotkey-escape',lambda:early('escape'))
finally:
 if fixture_pid: native.guest_session(RUN,'kill -TERM '+str(fixture_pid)+'\n')
 cli('ui.quit')
print('# %d failed'%failed[0],flush=True)
sys.exit(1 if failed[0] else 0)
