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
    body='putgd-cli '+shlex.quote(method)+' '+shlex.quote(json.dumps(params or {}))+' || true\n'
    r=json.loads(native.guest_session(RUN,body))
    with open(os.path.join(WORK,'session.jsonl'),'a') as f:f.write(json.dumps({'method':method,'params':params,'reply':r})+'\n')
    return r.get('result',r)

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



# Round B additions to the round A two-head driver. No product code is changed.
sys.path.insert(0,os.path.join(ROOT,'tools/lab'))
import lab as native,shlex,hashlib,re,pathlib,math
EXPECTED=os.environ.get('SWEEP_EXPECTED_TREE','e12d7610bec4319749a5b55b5411ce3f2b7318c2')
identity=cli('diagnostics')['build'];assert identity['gitTree']==EXPECTED;pathlib.Path(WORK,'build-identity.json').write_text(json.dumps(identity,indent=2))
native.guest_session(RUN,"python3 - <<'PYENV'\nimport os,shlex\nopen('/tmp/env.sh','w').write('\\n'.join('export '+k+'='+shlex.quote(v) for k,v in os.environ.items())+'\\n')\nPYENV\n")
for f in ('wayland_pointer.py','wayland_toplevels.py','gtk_clipboard_fixture.py'):
 native.put(RUN,os.path.join(ROOT,'tools/lab',f),'/tmp/'+f)
native.put(RUN,os.path.join(ROOT,'guest_fixture.py'),'/tmp/guest_fixture.py')
native.put(RUN,os.path.join(ROOT,'activate_wlr.py'),'/tmp/activate_wlr.py')
fixture_pid=None;active_record=None;active_editor=None;fixture='/tmp/sweep-b-fixture';control_id=0

def shell(body):return native.guest_session(RUN,body)
def call(method,params=None):
 value=cli(method,params)
 if value.get('ok') is False:raise RuntimeError(method+': '+json.dumps(value.get('error')))
 return value

def frames(name):
 for h in (0,1):dump(h).save(os.path.join(WORK,name+'-head%d.png'%h))
def check(name,fn,attempts=2):
 for attempt in range(1,attempts+1):
  try:
   okay,detail=fn();row(name,okay,json.dumps({'attempt':attempt,**detail}));frames(name+'-'+str(attempt))
   if okay:return True
  except Exception as e:row(name,False,json.dumps({'attempt':attempt,'driverError':str(e)}));frames(name+'-'+str(attempt))
 return False

def patch(value):
 d=call('settings.get');return call('settings.patch',{'patch':value,'expectedRevision':d['metadata']['observedRevision']})
def control(**value):
 global control_id
 control_id+=1;value['id']=control_id
 body="from pathlib import Path\np=Path(%r);p.write_text(%r)\np.replace(%r)"%(fixture+'/control.tmp',json.dumps(value),fixture+'/control.json')
 shell('python3 -c '+shlex.quote(body)+'\n')
 for _ in range(40):
  raw=guest('cat '+fixture+'/control-ack.json 2>/dev/null')
  if raw and json.loads(raw).get('id')==control_id:return
  time.sleep(.05)
 raise RuntimeError('GTK control acknowledgement missing')
def primary():
 guest('test ! -f '+fixture+'/primary.json || mv '+fixture+'/primary.json '+fixture+'/primary-previous.json')
 control(primaryRead=True)
 for _ in range(40):
  raw=guest('cat '+fixture+'/primary.json 2>/dev/null')
  if raw:
   v=json.loads(raw);assert v.get('text')=='putgd B PRIMARY sentinel',v;return v
  time.sleep(.05)
 raise RuntimeError('PRIMARY read missing')
def find_fixture():
 for h in (0,1):
  lab('screenshot','--run',RUN,'--head',str(h));p=os.path.join(RUN,'witness-head%d.ppm'%h);v=native.locate_fixture_paint(p)
  if v:return h,v
 raise RuntimeError('Independent GTK paint not found')
def focus_fixture():
 if desktop=='budgie':guest(ENV+'python3 /tmp/activate_wlr.py')
 elif desktop=='hyprland':
  control(fullscreen=True)
  reply=guest(ENV+'python3 /tmp/activate_wlr.py')
  pathlib.Path(WORK,'fixture-focus-commands.jsonl').open('a').write(json.dumps({'nativeActivation':reply})+'\n')
  time.sleep(.5)
 elif desktop=='kde':
  code='const w=workspace.windowList().find(w=>w.caption==="put.gd independent GTK clipboard fixture");if(w){w.minimized=false;workspace.activeWindow=w;}'
  shell("python3 -c "+shlex.quote("open('/tmp/raise-fixture.js','w').write("+repr(code)+")")+"\n")
  ident=shell('qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.loadScript /tmp/raise-fixture.js sweep-b-raise\n').strip().splitlines()[-1]
  try:shell('qdbus6 org.kde.KWin /Scripting/Script'+ident+' org.kde.kwin.Script.run\n')
  finally:shell('qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript sweep-b-raise\n')
 move(2300,740);time.sleep(.2);h,v=find_fixture();ox,oy=ORIGIN[h];click(ox+v['x']+100,oy+v['y']+100);return h,v

def process_tree(stage):
 resident=native.verify_running_app(RUN)['pid']
 code='''import json,pathlib,os
root=RESIDENT;allp={}
for p in pathlib.Path('/proc').iterdir():
 if not p.name.isdecimal():continue
 try:
  s=(p/'stat').read_text().rsplit(')',1)[1].split();allp[int(p.name)]={'pid':int(p.name),'parent':int(s[1]),'startTicks':int(s[19]),'comm':(p/'comm').read_text().strip(),'exe':os.readlink(p/'exe')}
 except OSError:pass
ids={root}
while True:
 new={pid for pid,v in allp.items() if v['parent'] in ids}
 if new<=ids:break
 ids|=new
print(json.dumps({'residentPid':root,'processes':[allp[p] for p in sorted(ids) if p in allp]}))'''.replace('RESIDENT',str(resident))
 tree=json.loads(shell('python3 -c '+shlex.quote(code)+'\n').strip().splitlines()[-1]);listed=call('recording.windows')
 native_windows=guest(ENV+'python3 /tmp/wayland_toplevels.py') if desktop in ('budgie','hyprland') else None
 detail={'processTree':tree,'offered':listed,'nativeWindows':json.loads(native_windows) if native_windows else None}
 pathlib.Path(WORK,stage+'-windows.json').write_text(json.dumps(detail,indent=2))
 expected_helper='putgd-record' if stage in ('2-recording-bar','2-review') else 'putgd-ui'
 assert any(p['comm']==expected_helper for p in tree['processes']),{'missingWindowHelper':expected_helper,'tree':tree}
 offered=listed.get('windows',[]);external=[w for w in offered if 'independent GTK clipboard' in w.get('title','')]
 own=[w for w in offered if w.get('appId') in ('putgd','putgd-ui','putgd-record','putgd-region','org.putgd.App') or w.get('title') in ('put.gd','Edit image','Review recording')]
 assert external and not own,{'external':external,'ownOffered':own}
 return detail

def composite():
 im=Image.new('RGB',EXTENT)
 for h in (0,1):im.paste(dump(h),ORIGIN[h])
 return im

def capture(action,rect=None):
 op,_=start(action)
 if rect:time.sleep(1.5);drag(*rect)
 v=wait(op);im=fetch(v['path']) if v.get('path') else None
 return op,v,im

def compare_capture(action,rect=None):
 control(motion=False);move(20,740);time.sleep(.2);reference=composite();box=(0,0,*EXTENT)
 if action=='monitor':
  move(1700,500);h=locate(1700,500)[0];ox,oy=ORIGIN[h];w,hg=SIZE[h];box=(ox,oy,ox+w,oy+hg)
 elif rect:box=rect
 op,v,im=capture(action,rect);expected=reference.crop(box);difference=differs(im,expected) if im and im.size==expected.size else None
 reference.save(os.path.join(WORK,'1-'+action+'-reference.png'))
 if im:im.save(os.path.join(WORK,'1-'+action+'-result.png'))
 return v['state']=='completed' and difference is not None and difference<1,{'operationId':op,'operation':v,'dimensions':im.size if im else None,'referenceBox':box,'meanAbsoluteDifference':difference}

def cancel_then_new(button_name):
 op,_=start('region');time.sleep(.8)
 if button_name=='esc':native.key(RUN,['esc'])
 elif desktop in ('budgie','hyprland'):guest(ENV+'python3 /tmp/wayland_pointer.py click 400 400 --extent 2304 800 --button right')
 else:native.pointer(RUN,400,400,*EXTENT,True,button='right');native.pointer(RUN,400,400,*EXTENT,False,button='right')
 v=wait(op);frames('1-cancel-'+button_name)
 okay,new=compare_capture('region',(300,300,600,500))
 return v['state']=='cancelled' and okay,{'cancelOperation':v,'newRegion':new}

def wait_record(rid,desired,limit=100):
 end=time.monotonic()+limit
 while time.monotonic()<end:
  v=call('recording.inspect',{'id':rid})
  if v['state'] in desired:return v
  if v['state'] in ('failed','cancelled'):raise RuntimeError('recording state '+json.dumps(v))
  time.sleep(.15)
 raise RuntimeError('recording deadline '+','.join(desired))
def finish_record():
 global active_record
 if active_record:
  try:call('recording.cancel',{'id':active_record})
  except Exception:pass
  active_record=None

def record(kind,moving=True,highlight=False,own_checks=False):
 global active_record
 control(motion=False);h,paint=focus_fixture();ox,oy=ORIGIN[h]
 target={'kind':kind}
 if kind=='monitor':target['identity']='Virtual-'+str(h+1);move(ox+paint['x']+100,oy+paint['y']+100)
 elif kind=='region':target['rect']=[ox+paint['x']+10,oy+paint['y']+10,300,200]
 elif kind=='window':
  wins=call('recording.windows')['windows'];target['identity']=next(w['identity'] for w in wins if 'independent GTK clipboard' in w.get('title',''))
 active_record=call('recording.prepare',{'target':target,'format':'mp4','audio':{'system':False},'clickHighlights':highlight})['recordingId']
 rc_path='$HOME/.config/budgie-desktop/labwc/rc.xml';before_rc_sha=guest('sha256sum '+rc_path).split()[0] if highlight and desktop=='budgie' else None;before_rc=native.ssh(RUN,'cat '+rc_path) if highlight and desktop=='budgie' else None
 rid=active_record;ready=wait_record(rid,('ready',));frames('4-'+kind+'-ready')
 if own_checks:process_tree('2-recording-bar')
 call('recording.overlay',{'id':rid,'visible':False});control(motion=moving);call('recording.start',{'id':rid})
 for n in range(5):
  if moving:move(ox+paint['x']+30+n*40,oy+paint['y']+60)
  time.sleep(.3)
 paused=call('recording.pause',{'id':rid});assert paused['state']=='paused',paused;time.sleep(.3);resumed=call('recording.resume',{'id':rid});assert resumed['state']=='recording',resumed
 for n in range(5):
  if moving:move(ox+paint['x']+220-n*35,oy+paint['y']+100)
  time.sleep(.3)
 if highlight:click(ox+paint['x']+100,oy+paint['y']+365);time.sleep(.5)
 stopped=call('recording.stop',{'id':rid});wait_record(rid,('reviewing',));frames('4-'+kind+'-review')
 if own_checks:process_tree('2-review')
 path=fixture+'/'+kind+('-moving' if moving else '-frozen')+'-'+rid+'.mp4';call('recording.saveCopy',{'id':rid,'path':path});done=wait_record(rid,('reviewing',),180)
 local=pathlib.Path(WORK)/(kind+('-moving' if moving else '-frozen')+'-'+rid+'.mp4');native.get(RUN,path,str(local));env=dict(os.environ,APPDIR=os.path.join(ROOT,'analyzer/squashfs-root'))
 helper=os.path.join(ROOT,'analyzer/squashfs-root/usr/bin/putgd-record');analysis=subprocess.run([helper,'--motion',str(local),'8'],env=env,capture_output=True,text=True,timeout=90);score=re.search(r'^motion=([0-9.]+)',analysis.stdout,re.M);assert score,analysis.stderr[-300:]
 after_rc=None
 if before_rc is not None:
  for _ in range(40):
   after_rc=native.ssh(RUN,'cat '+rc_path)
   if after_rc==before_rc:break
   time.sleep(.1)
  after_rc_sha=guest('sha256sum '+rc_path).split()[0];assert before_rc_sha==after_rc_sha,'labwc bytes differ';pathlib.Path(WORK,'6-rc-before.xml').write_text(before_rc);pathlib.Path(WORK,'6-rc-after.xml').write_text(after_rc);assert before_rc==after_rc,'labwc rc.xml was not restored'
 result={'rcXmlBeforeSha256':before_rc_sha,'rcXmlAfterSha256':None if before_rc is None else after_rc_sha,'rcXmlRestored':None if before_rc is None else before_rc==after_rc,'target':target,'ready':ready,'paused':paused,'resumed':resumed,'review':stopped,'export':done.get('lastExport'),'motion':float(score[1]),'clip':str(local),'bytes':local.stat().st_size}
 finish_record();control(motion=False);return result

def paste(label):
 guest('test ! -f '+fixture+'/paste.json || mv '+fixture+'/paste.json '+fixture+'/paste-previous.json');focus_fixture();native.key(RUN,['ctrl','v'])
 for _ in range(40):
  raw=guest('cat '+fixture+'/paste.json 2>/dev/null')
  if raw:
   value=json.loads(raw);pathlib.Path(WORK,label+'-paste.json').write_text(json.dumps(value,indent=2))
   if value.get('image'):native.get(RUN,fixture+'/paste.png',os.path.join(WORK,label+'-paste.png'))
   return value
  time.sleep(.1)
 raise RuntimeError('native GTK paste deadline')
def own_clipboard(kind):
 focus_fixture();guest('test ! -f '+fixture+'/source.json || mv '+fixture+'/source.json '+fixture+'/source-previous.json');native.key(RUN,['ctrl','alt','shift',{'text':'t','image':'i','files':'f'}[kind]])
 for _ in range(50):
  raw=guest('cat '+fixture+'/source.json 2>/dev/null')
  if raw:return json.loads(raw)
  time.sleep(.1)
 raise RuntimeError('foreign client did not receive copy shortcut')

def clipboard_flow():
 _,v,image=capture('region',(300,300,600,500));history=call('history.list',{'limit':50});record=next(w for w in history['records'] if w.get('local',{}).get('path')==v['path'])
 checks=[]
 for n in (1,2):
  if n==2:checks.append({'foreignOwner':own_clipboard('text'),'primary':primary()})
  copied=call('history.copyImage',{'id':record['id']});p=paste('3-image-'+str(n));actual=Image.open(os.path.join(WORK,'3-image-'+str(n)+'-paste.png')).convert('RGB');assert actual.size==image.size and differs(actual,image)==0
  checks.append({'copyImage':copied,'paste':p,'pixelDifference':differs(actual,image),'primary':primary()})
 for n in (1,2):
  if n==2:checks.append({'foreignOwner':own_clipboard('text'),'primary':primary()})
  op=call('text.recognize',{'source':'file','path':fixture+'/text.png','copy':True})['operationId']
  for _ in range(100):
   text=call('text.inspect',{'id':op})
   if text['state'] in ('completed','failed'):break
   time.sleep(.15)
  p=paste('3-text-'+str(n));assert p.get('text','').strip()=='putgd B acceptance text',p
  checks.append({'recognized':text['state'],'paste':p,'primary':primary()})
 for kind in ('text','image','files'):
  source=own_clipboard(kind);op,_=start('clipboard');v=wait(op);assert v['state']=='completed',v
  inspected=call('operation.inspect',{'id':op});assert len(inspected['items'])==(2 if kind=='files' else 1),inspected
  checks.append({'import':kind,'foreignSource':source,'operation':inspected,'primary':primary()})
 return True,{'checks':checks}

try:
 patch({'archive':{'keepUploads':True,'root':'/tmp/sweep-b-archive'},'preferences':{'notifications':False,'regionSelectionMode':'live'},'actions':{a:{'destination':'local','profileId':None} for a in ('region','window','desktop','clipboard','edit','record')}})
 call('ui.show',{'view':'settings'});time.sleep(.5);native.key(RUN,['alt','f4']);time.sleep(.5)
 fixture_pid=int(shell(('SWEEP_FIXTURE_FULLSCREEN=1 ' if desktop=='hyprland' else '')+'python3 /tmp/guest_fixture.py '+fixture+' > /tmp/sweep-b-gtk.log 2>&1 < /dev/null & echo $!\n').strip().splitlines()[-1]);time.sleep(3)
 focus_fixture();control(primarySet=True);primary()
 capabilities=call('capabilities');pathlib.Path(WORK,'capabilities.json').write_text(json.dumps(capabilities,indent=2))
 check('3-clipboard',clipboard_flow)
finally:
 finish_record()
 if active_editor:
  try:call('editor.cancel',{'id':active_editor})
  except Exception:pass
 if fixture_pid:
  pathlib.Path(WORK,'fixture-final.log').write_text(guest('cat /tmp/sweep-b-gtk.log'));pathlib.Path(WORK,'fixture-final-state.txt').write_text(guest('ls -l '+fixture+'; cat '+fixture+'/control-ack.json 2>/dev/null'));shell('kill -TERM '+str(fixture_pid)+'\n')
 call('ui.quit')
print('# %d failed'%failed[0],flush=True)
sys.exit(1 if failed[0] else 0)
