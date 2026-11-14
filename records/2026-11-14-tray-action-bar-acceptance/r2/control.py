import sys,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from tools.lab.surface_driver.target import Target
from tools.lab.rfb import RFB
class Control:
 def __init__(self,host,root,port=None):
  self.host=host;self.root=root;self.out=ROOT/'work/ta1532/r2'/host;self.out.mkdir(parents=True,exist_ok=True)
  self.t=Target(host_profile=str(ROOT/'work/ta1532'/f'{host}.json'),session_root=root,placement='native');self.t.require_lock(host,'ta1532-r2');self.port=port or self.t.physical.config['vnc_port']
 def call(self,method,params=None):
  r=self.t.cli(method,json.dumps(params or {}));v=json.loads(r['stdout']);self.log({'method':method,'params':params or {},'reply':v})
  if not v['ok']:raise RuntimeError(str(v['error']))
  return v['result']
 def patch(self,patch):
  return self.call('settings.patch',{'patch':patch,'expectedRevision':self.call('settings.get')['metadata']['acceptedRevision']})
 def shell(self,script):return self.t.execute(script)
 def session(self,script):return self.t.session(script)
 def log(self,v):
  with (self.out/'trace.jsonl').open('a') as f:f.write(json.dumps(v)+'\n')
 def frame(self,name):
  self.t.heartbeat(force=True);r=RFB(self.port)
  try:
   from PIL import Image
   w,h,p=r.frame();Image.frombytes('RGB',(w,h),p,'raw','BGRX').save(self.out/(name+'.png'))
  finally:r.close()
  self.log({'frame':name,'time':time.time()})
 def input(self,fn):
  self.t.heartbeat(force=True);r=RFB(self.port)
  try:fn(r)
  finally:r.close()
 def click(self,x,y,button='left'):
  def go(r):
   r.pointer(x,y);time.sleep(.08);r.pointer_button(x,y,button,True);time.sleep(.08);r.pointer_button(x,y,button,False)
  self.input(go);self.log({'click':[x,y,button]});time.sleep(.3)
 def key(self,*keys):self.input(lambda r:r.key(*keys));time.sleep(.2)
 def hover(self,x,y):self.input(lambda r:r.pointer(x,y));time.sleep(.4)
def receiver_mode(value):
 from tools.lab.physical_host import PhysicalHost
 x=PhysicalHost(json.loads((ROOT/'work/ta1532/k72.json').read_text()))
 x.ssh(x.run,"python3 - <<'MODE'\nfrom pathlib import Path\nPath('/tmp/ta2-http/control.json').write_text("+repr(json.dumps(value))+ ")\nMODE\n")

class GuestControl(Control):
 def __init__(self,run,name,port=5988):
  from tools.lab.physical_host import PhysicalHost
  self.host=name;self.root='/home/lab/putgd-lab';self.run='/home/patrick/work/ta1532-src/work/lab-runs/'+run;self.port=port;self.out=ROOT/'work/ta1532/r2'/name;self.out.mkdir(parents=True,exist_ok=True);self.physical=PhysicalHost(json.loads((ROOT/'work/ta1532/f44.json').read_text()))
 def remote(self,code,timeout=60):
  return self.physical.ssh(self.physical.run,"cd ~/work/ta1532-src\npython3 - <<'GUEST'\nfrom tools.lab import lab\nfrom pathlib import Path\nimport json\nr=Path("+repr(self.run)+")\n"+code+"\nGUEST\n",timeout=timeout)
 def call(self,method,params=None):
  result=json.loads(self.remote('print(json.dumps(lab.cli(r,'+repr(method)+','+repr(params or {})+')))'));self.log({'method':method,'params':params or {},'result':result});return result
 def patch(self,patch):return self.call('settings.patch',{'patch':patch,'expectedRevision':self.call('settings.get')['metadata']['acceptedRevision']})
 def shell(self,script):return self.remote('print(lab.guest_session(r,'+repr(script)+'))')
 def session(self,script):return self.shell(script)
 def frame(self,name):
  time.sleep(.5);r=RFB(self.port)
  try:
   from PIL import Image
   w,h,p=r.frame();Image.frombytes('RGB',(w,h),p,'raw','BGRX').save(self.out/(name+'.png'))
  finally:r.close()
  self.log({'frame':name,'time':time.time()})
 def input(self,fn):
  r=RFB(self.port)
  try:fn(r)
  finally:r.close()
