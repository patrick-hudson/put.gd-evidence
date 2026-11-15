import accept as A
import os,json,time,subprocess,sys,threading,shutil,random
from pathlib import Path
P=A.P; L=A.L
sys.path.insert(0,str(P)); import sess as S
# Reset paths overridden by the historical harness import.
L.P=P;L.session_env=lambda:(A.E,A.DESKTOP);S.LAB=P
class Proc:
 def __init__(self,d):self.d=d
 def poll(self):return None if self.d.running() else 0
 def wait(self,timeout):
  t=time.time()
  while self.d.running():
   if time.time()-t>timeout:raise subprocess.TimeoutExpired('capture',timeout)
   time.sleep(.1)
 def terminate(self):A.rpc('scroll.cancel',{'id':self.d.sid})
class Stop:
 def __init__(self,d):self.d=d;self.sent=False
 def touch(self):
  if not self.sent and self.d.running():
   self.sent=True
   if hasattr(self.d,'before_done'):self.d.before_done()
   result=[]
   def stop_rpc():result.append(A.rpc('scroll.stop',{'id':self.d.sid}))
   t=threading.Thread(target=stop_rpc);t.start()
   for _ in range(60):
    if not t.is_alive():break
    v=A.rpc('scroll.inspect',{'id':self.d.sid})
    if v.get('state')=='finishing':
     try:S.desk(self.d.out/'saving.png')
     except Exception:pass
     break
    time.sleep(.01)
   t.join()
 def exists(self):return self.sent
class Driver:
 def __init__(self,rect,out,mode,env):
  self.began=time.time();self.out=out;self.stage=out/'stage';self.stage.mkdir();self.stop=Stop(self);self.lines=[];self.last={};self.end=None
  self.offset=(P/'helper.log').stat().st_size if (P/'helper.log').exists() else 0
  self.seen=set();params={'rect':rect,'maxHeight':60000}
  if os.environ.get('SFA_BASELINE')!='1':params['driver']='user' if mode=='user' else 'putgd'
  if mode=='user':
   point=[rect[0]+rect[2]-80,rect[1]+rect[3]-120]
   v=S.rfb.RFB(5900);v.pointer(*point);v.close();time.sleep(.2)
   (out/'pointer-setup.json').write_text(json.dumps({'method':'Initial absolute positioning in the browser right margin BEFORE scroll.prepare; no pointer event after prepare, only relative uinput wheel. Avoids delayed link hover popups.','point':point}))
  self.sid=A.rpc('scroll.prepare',params)['id']
  A.rpc('scroll.start',{'id':self.sid});self.p=Proc(self);self.lines=[json.dumps({'prepare':{'state':'capturing'}})]
 def capturing(self):return True
 def running(self):
  self.last=A.rpc('scroll.inspect',{'id':self.sid})
  activity=self.last.get('activity')
  if activity and activity not in self.seen:
   self.seen.add(activity)
   try:S.desk(self.out/(activity+'.png'))
   except Exception:pass
  if self.last.get('state') in ['done','failed','cancelled']:
   if not self.end:
    self.end=self.last;self.lines.append(json.dumps(dict(self.last,event='finished' if self.last['state']=='done' else 'failed',path='')))
    if self.last['state']=='done' and hasattr(A,'sync_artifact'):A.sync_artifact(self.sid)
    # Local archive is the admitted PNG; find only files under our private destination.
    
    for _ in range(100):
     images=sorted((P/'archive').rglob('*.png'),key=lambda x:x.stat().st_mtime)
     if images and images[-1].stat().st_mtime > self.began:break
     time.sleep(.1)
    if self.last['state']=='done' and images:
     self.lines[-1]=json.dumps(dict(self.last,event='finished',path=str(images[-1])))
    (self.out/'helper.log').write_bytes((P/'helper.log').read_bytes()[self.offset:])
   return False
  return True
 def events(self):
  self.running();return [json.loads(x) for x in self.lines]+[dict(self.last,event='progress',state=self.last.get('activity'))]
S.Driver=Driver
old_back=S.come_back
def come_back(d,out,rect,wheel):
 (out/'helper.log').write_bytes((P/'helper.log').read_bytes()[d.offset:])
 return old_back(d,out,rect,wheel)
S.come_back=come_back
# Save the browser's current viewport before the later full-page reference returns to top.
# The historical page recipe anchors through VNC after start. Move that setup
# before prepare, so every pointer movement during a capture is relative input.
import inspect
source=inspect.getsource(S.finish_run)
start=source.index('        if X11:')
end=source.index('        time.sleep(0.6)',start)
source=source[:start]+'        # Pointer anchored before prepare by Driver.\n'+source[end:]
exec(source,S.__dict__)
old_finish=S.finish_run
def finish_with_view(b,d,out,rect,mode,wheel,result,start,name):
 def before_done():
  import base64
  info=b.js(L.INFO)
  pinned=b.js("return [...document.querySelectorAll('*')].filter(e=>['sticky','fixed'].includes(getComputedStyle(e).position)).map(e=>{const q=e.getBoundingClientRect();return {rect:[q.x,q.y,q.width,q.height],what:(e.tagName+'.'+String(e.className||'')).slice(0,90)}}).filter(e=>e.rect[0]<innerWidth&&e.rect[1]<innerHeight&&e.rect[0]+e.rect[2]>0&&e.rect[1]+e.rect[3]>0)")
  if result['browser']=='firefox':
   obj=b.cmd('WebDriver:TakeScreenshot',{'id':None,'highlights':[],'full':False});data=obj.get('value',obj) if isinstance(obj,dict) else obj
  else:data=b.cmd('Page.captureScreenshot',{'format':'png','fromSurface':True,'captureBeyondViewport':False})['data']
  (out/'pre-done-viewport.png').write_bytes(base64.b64decode(data))
  (out/'pre-done-viewport-info.json').write_text(json.dumps(info,indent=1))
  (out/'pre-done-pinned.json').write_text(json.dumps(pinned,indent=1))
 d.before_done=before_done
 original_js=b.js;saved=False
 def js(script):
  nonlocal saved
  if not saved and 'after' in result and script.startswith('window.scrollTo'):
   saved=True
   try:
    import base64
    if result['browser']=='firefox':
     obj=b.cmd('WebDriver:TakeScreenshot',{'id':None,'highlights':[],'full':False});data=obj.get('value',obj) if isinstance(obj,dict) else obj
    else:data=b.cmd('Page.captureScreenshot',{'format':'png','fromSurface':True,'captureBeyondViewport':False})['data']
    (out/'done-viewport.png').write_bytes(base64.b64decode(data))
    (out/'done-viewport-info.json').write_text(json.dumps(result['after'],indent=1))
   except Exception as e:result['doneViewportError']=str(e)
  return original_js(script)
 b.js=js
 try:return old_finish(b,d,out,rect,mode,wheel,result,start,name)
 finally:b.js=original_js
S.finish_run=finish_with_view
if __name__=='__main__':
 kind,sites,modes=sys.argv[1],sys.argv[2].split(','),sys.argv[3].split(',')
 mouse=subprocess.Popen(['sudo','-n','python3',str(P/'umouse.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
 assert mouse.stdout.readline().startswith('ready')
 def wheel(x):mouse.stdin.write(x+'\n');mouse.stdin.flush()
 try:
  for site in sites:
   for mode in modes:
    profile=P/('profile-'+kind)
    if profile.exists():profile.rename(P/(profile.name+'-'+str(time.time_ns())))
    try:
     L.browser_start(kind)
     if kind=='chromium' and site=='python':
      b,_=L.connect();b.cmd('Emulation.setEmulatedMedia',{'features':[{'name':'prefers-color-scheme','value':'dark'}]});# Keep this session alive until the capture ends.
     S.run(kind,site,mode,wheel)
    finally:
     if (P/'browser.pid').exists():L.browser_stop()
 finally:
  wheel('q');mouse.wait(5)
