import os,sys,json,time,subprocess,struct,hashlib
from pathlib import Path
from trial import cli,Rfb
LAB=Path.home()/'work/s1520'; label=sys.argv[1];mode=sys.argv[2];d=LAB/label
for k,v in dict(XDG_CONFIG_HOME=d/'config',XDG_DATA_HOME=d/'data',XDG_CACHE_HOME=d/'cache',XDG_STATE_HOME=d/'state').items():os.environ[k]=str(v)
C=os.environ.get('CLI','/usr/bin/putgd-cli');port=int(os.environ.get('VNC','5901'));r=None
if 'Budgie' in os.environ.get('XDG_CURRENT_DESKTOP',''):
 from geometry import output
 r=output()
else:r=Rfb(port)
local_pointer=None
if (os.environ.get('LOCAL_UI')=='1' or any(x in os.environ.get('XDG_CURRENT_DESKTOP','') for x in ['Hyprland','Budgie'])) and mode in ['pointer','stoptop','large']:
 from localinput import Pointer
 local_pointer=Pointer(r);r=local_pointer
def call(m,p={}):
 v=cli(C,m,p)
 with open(d/'calls.jsonl','a') as f:f.write(json.dumps({'t':time.monotonic(),'method':m,'reply':v})+'\n')
 if not v.get('ok'):raise RuntimeError(v)
 return v['result']
def shot(n):
 if 'Budgie' in os.environ.get('XDG_CURRENT_DESKTOP',''):
  seq=time.time_ns();req=LAB/'shot-request.json';tmp=req.with_suffix('.tmp');tmp.write_text(json.dumps({'seq':seq,'label':label,'name':n}));tmp.replace(req)
  for _ in range(200):
   if (LAB/('shot-'+str(seq)+'.done')).exists():return
   time.sleep(.05)
  print('SCREENSHOT FAILED: '+n,flush=True);return
 r=subprocess.run(['python3',str(LAB/'rfbshot.py'),str(d/(n+'.png')),'--vnc',str(port)])
 if r.returncode: print('SCREENSHOT FAILED: '+n,flush=True)
def key(k):
 for state in [1,0]:r.sock.sendall(struct.pack('>BBHI',4,state,0,k));time.sleep(.05)
def page(local=False,end=False):
 url='file://'+str(LAB/'page.html')+('#mid' if end else '') if local else 'https://en.wikipedia.org/wiki/Linux'
 subprocess.run(['firefox','--profile',str(LAB/'ff'),url],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 time.sleep(5)
def start(rect=[470,200,980,720]):
 s=call('scroll.prepare',{'rect':rect,'maxHeight':60000})['id'];call('scroll.start',{'id':s});return s
def wait(s):
 for _ in range(800):
  v=call('scroll.inspect',{'id':s})
  if v.get('state') in ['done','failed','cancelled']:return v
  time.sleep(.3)
 raise RuntimeError('capture did not end')
def click(x,y):
 r.pointer(x,y,1);time.sleep(.06);r.pointer(x,y)
def move(x,y):r.pointer(x,y);time.sleep(1)
def output(n,v):
 json.dump(v,open(d/(n+'.json'),'w'),indent=2)
 print(n,json.dumps(v),flush=True)
if mode=='live':
 for i in range(2):
  page();s=start();time.sleep(5);shot('live-'+str(i)+'-running');output('live-'+str(i),wait(s))
elif mode in ['api','pointer']:
 page(True);plain=wait(start());output(mode+'-plain',plain)
 page(True);s=start();time.sleep(6)
 if mode=='api':call('scroll.pause',{'id':s})
 else:move(960,540)
 time.sleep(1);v=call('scroll.inspect',{'id':s});output(mode+'-paused',v);shot(mode+'-paused')
 off=(d/'helper.log').stat().st_size;time.sleep(2)
 text=(d/'helper.log').read_bytes()[off:].decode();output(mode+'-quiet',{'injectionLines':[l for l in text.splitlines() if 'scroll inject:' in l]})
 if mode=='api':call('scroll.resume',{'id':s})
 else:
  x,y=map(int,os.environ['RESUME'].split(','));move(x,y);click(x,y)
 output(mode+'-resumed',wait(s))
elif mode=='cancel':
 page(True);before=call('history.list',{'limit':100});files=sorted(str(p) for p in (d/'out').rglob('*') if p.is_file());s=start();time.sleep(4);call('scroll.pause',{'id':s});call('scroll.cancel',{'id':s});time.sleep(1)
 output('cancel',{'session':call('scroll.inspect',{'id':s}),'before':before,'after':call('history.list',{'limit':100}),'filesBefore':files,'filesAfter':sorted(str(p) for p in (d/'out').rglob('*') if p.is_file())})
elif mode=='stoptop':
 page(True,True);s=start();time.sleep(.8);shot('top-running') if 'Budgie' in os.environ.get('XDG_CURRENT_DESKTOP','') else subprocess.Popen(['python3',str(LAB/'rfbshot.py'),str(d/'top-running.png'),'--vnc',str(port)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);move(960,540);shot('top-paused');x,y=map(int,os.environ.get('STOP','960,956').split(','));click(x,y);output('stoptop',wait(s))
elif mode=='large':
 page();s=start([700,30,1200,1030]);time.sleep(2);shot('large-running');move(960,540);shot('large-paused');output('large-paused',call('scroll.inspect',{'id':s}));call('scroll.cancel',{'id':s})

if local_pointer: local_pointer.close()
