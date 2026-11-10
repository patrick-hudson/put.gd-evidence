import os,sys,json,time,subprocess,hashlib,threading,shutil,re
from pathlib import Path
import record_run,rfb
P=Path('/home/patrick/work/p21398')
def rpc(m,p={}):
 e=json.loads((P/'env.json').read_text()); r=subprocess.run(['putgd-cli','--socket',str(P/'r/putgd/session.sock'),m,json.dumps(p)],env=e,text=True,capture_output=True,timeout=70)
 o=json.loads(r.stdout)
 with open(P/'rpc.jsonl','a') as f:f.write(json.dumps({'time':time.time(),'method':m,'params':p,'reply':o})+'\n')
 assert o['ok'],o
 return o['result']
def setup():
 e,desktop=record_run.session_environment()
 for n in ['c','d','s','cache','r','archive']:(P/n).mkdir(mode=0o700,exist_ok=False)
 for k,n in [('CONFIG','c'),('DATA','d'),('STATE','s'),('CACHE','cache'),('RUNTIME','r')]:e['XDG_'+k+('_DIR' if k=='RUNTIME' else '_HOME')]=str(P/n)
 e.update(PIPEWIRE_RUNTIME_DIR='/run/user/1000',PULSE_SERVER='unix:/run/user/1000/pulse/native',PUTGD_RECORD_DEBUG_LOG=str(P/'helper.log'),SC_Y='200')
 (P/'env.json').write_text(json.dumps(e));os.chmod(P/'env.json',0o600)
 assert len(str(P/'r/putgd/session.sock').encode())<=107
 ident={'desktop':desktop,'build':json.loads(subprocess.check_output(['putgd-cli','--version-json'])),'packageSha256':hashlib.sha256(next(P.glob('*.deb')).read_bytes()).hexdigest() if list(P.glob('*.deb')) else hashlib.sha256(next(P.glob('*.rpm')).read_bytes()).hexdigest()}
 for cmd in ['uname -a','loginctl list-sessions','cat /sys/class/tty/tty0/active','sudo -n fgconsole','uptime','df -h /tmp','df -i /tmp','loginctl show-session 2','dpkg-query -W kwin-wayland plasma-workspace','rpm -q gnome-shell mutter']:
  ident[cmd]=subprocess.run(cmd,shell=True,text=True,capture_output=True).stdout
 (P/'identity.json').write_text(json.dumps(ident,indent=2))
 q=subprocess.Popen(['putgd','--background'],env=e,stdout=open(P/'resident.log','w'),stderr=subprocess.STDOUT,start_new_session=True);(P/'resident.pid').write_text(str(q.pid))
 for i in range(100):
  if (P/'r/putgd/session.sock').exists():break
  time.sleep(.1)
 s=rpc('settings.get');d=s['document'];d['preferences']['notifications']=False;d['archive'].update(keepUploads=True,root=str(P/'archive'));rpc('settings.save',{'document':d,'expectedRevision':s['metadata']['observedRevision']})
 (P/'capabilities.json').write_text(json.dumps(rpc('scroll.capabilities'),indent=2));time.sleep(2)
 # Close only this isolated resident's dashboard by its owned PID, without killing it.
 owned=[]
 for proc in Path('/proc').iterdir():
  if not proc.name.isdigit():continue
  try:
   if (proc/'comm').read_text().strip()=='putgd-ui' and ('XDG_CONFIG_HOME='+str(P/'c')).encode() in (proc/'environ').read_bytes().split(b'\0'):owned.append(int(proc.name))
  except (FileNotFoundError,PermissionError,ProcessLookupError):pass
 if desktop=='plasmashell' and owned:
  js=P/'close-ui.js';js.write_text('for (const w of workspace.stackingOrder) { if ('+json.dumps(owned)+'.includes(w.pid)) w.closeWindow(); }')
  real=dict(os.environ,XDG_RUNTIME_DIR='/run/user/1000',DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/1000/bus')
  name='physical2-close-ui';i=subprocess.check_output(['qdbus6','org.kde.KWin','/Scripting','org.kde.kwin.Scripting.loadScript',str(js),name],env=real,text=True).strip()
  subprocess.run(['qdbus6','org.kde.KWin','/Scripting/Script'+i,'org.kde.kwin.Script.run'],env=real,capture_output=True);time.sleep(.5)
  subprocess.run(['qdbus6','org.kde.KWin','/Scripting','org.kde.kwin.Scripting.unloadScript',name],env=real,capture_output=True)
 time.sleep(2)

def capture(name,rows=60,maxh=None,scale=1,text=False,stop=None,immediate=False):
 out=P/name;out.mkdir();log=P/'helper.log';offset=log.stat().st_size if log.exists() else 0
 result={'name':name,'rows':rows,'scale':scale,'maxHeight':maxh,'packageSha256':json.loads((P/'identity.json').read_text())['packageSha256']}
 e=json.loads((P/'env.json').read_text());done=threading.Event()
 def frames():
  try:
   v=rfb.RFB(5901 if os.uname().nodename=='fedora' else 5900)
   for i in range(200):
    if done.is_set():break
    v.screenshot(out/('screen-%03d.png'%i));done.wait(1)
   v.sock.close()
  except Exception as ex:(out/'visual-error.txt').write_text(str(ex))
 th=None
 try:
  rect=([0,0,960,1080] if name.startswith('firefox') else [100,200,960,600]) if not text else [0,0,600 if 'narrow' in name else 1900,1080]
  args={'rect':rect}
  if maxh:args['maxHeight']=maxh
  v=rpc('scroll.prepare',args);ident=v['id'];result['id']=ident
  while v['state']!='ready':time.sleep(.1);v=rpc('scroll.inspect',{'id':ident})
  if not immediate:time.sleep(.8)
  th=threading.Thread(target=frames);th.start();rpc('scroll.start',{'id':ident});start=time.monotonic();stopped=False
  while True:
   v=rpc('scroll.inspect',{'id':ident})
   if v['state'] in ['done','failed','cancelled']:break
   if stop is not None and not stopped and time.monotonic()-start>=stop:result['stateAtStop']=v;rpc('scroll.stop',{'id':ident});stopped=True
   if time.monotonic()-start>250:raise TimeoutError('capture')
   time.sleep(.15)
  result['capture']=v
  sha=v.get('result',{}).get('sha256')
  found=None
  for i in range(80):
   for f in (P/'archive').rglob('*.png'):
    if hashlib.sha256(f.read_bytes()).hexdigest()==sha:found=f;break
   if found or not sha:break
   time.sleep(.2)
  if found:
   shutil.copyfile(found,out/'capture.png')
   if text:
    import verify_text
    result['verification']=verify_text.verify(str(out/'capture.png'),1500)
    result['verification']['ok']=result['verification']['ok'] and result['verification']['lines']==1500 and len(result['verification']['pitch'])==1
   elif scale!=1:
    import verify_scaled
    result['verification']=verify_scaled.verify(str(out/'capture.png'),scale,rows)
   else:
    import scroll_run,argparse
    expected=min(rows*40,maxh or 30000)
    if stop is not None:expected=v['height']
    a=argparse.Namespace(scale=1,height=expected,rows=rows,first_pixel=0,header=0,footer=0,code_width=960,format='fixture',scrollbar=0)
    if stop is not None:
     from PIL import Image
     im=Image.open(out/'capture.png').convert('RGB');decoded=[]
     for yy in range(min(40,im.height)):
      b=0
      for cc in range(16):b=b<<1 | (sum(im.getpixel((64+cc*55+27,yy)))<384)
      decoded.append(b)
     candidates=[]
     for first in range(rows*40-im.height+1):
      if all(decoded[yy]==scroll_run.pattern(*divmod(first+yy,40)) for yy in range(len(decoded))):candidates.append(first)
     result['viewportFirstPixelCandidates']=candidates
     if len(candidates)==1:a.first_pixel=candidates[0]
    result['verification']=scroll_run.verify(out/'capture.png',a)
  expected=min(rows*40,maxh or 30000)
  result['falseEnd']=v.get('endReason')=='end_of_content' and not text and v.get('height')!=round(rows*40*scale)
  result['pass']=v.get('endReason')==('stopped' if stop is not None else 'height_cap' if (maxh or 30000)<rows*40 else 'end_of_content') and result.get('verification',{}).get('ok',result.get('verification',{}).get('pass',False))
 except Exception as ex:
  result.update(error=str(ex),pass_=False)
  try:rpc('scroll.cancel',{'id':ident})
  except Exception:pass
 finally:
  done.set()
  if th:th.join(15)
  txt=log.read_bytes()[offset:].decode(errors='replace') if log.exists() else ''
  (out/'helper.log').write_text(txt);result['sourceLines']=re.findall(r'scroll: source fresh .*',txt)
  (out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='capture'}),flush=True)
 if result.get('falseEnd'):(P/'STOP-FALSE-END').write_text(name);raise RuntimeError('FALSE END OF CONTENT: '+name)
 return result
def batch(kind,n):
 e=json.loads((P/'env.json').read_text());cmd=['python3',str(P/'qt_fixture.py')];rows=60;maxh=None;sc=1;text=False
 if kind=='long':rows=600;maxh=40000;cmd+=['--rows','600']
 if kind=='cap':rows=1000;cmd+=['--rows','1000']
 if kind=='scaled':sc=1.25
 if kind in ['gtk','qttext','gtknarrow','qtnarrow','gtkfull','qtfull','gtknarrowfull','qtnarrowfull']:cmd=['python3',str(P/'text_fixture.py'),'gtk' if kind.startswith('gtk') else 'qt'];text=True;maxh=60000
 if kind=='firefox':
  (P/'ffprofile').mkdir(exist_ok=True);cmd=['firefox','--no-remote','--profile',str(P/'ffprofile'),'--kiosk',(P/'ruler.html').as_uri()]
 f=subprocess.Popen(cmd,env=e,stdout=open(P/(kind+'-fixture.log'),'w'),stderr=subprocess.STDOUT,start_new_session=True);(P/'fixture.pid').write_text(str(f.pid))
 try:
  time.sleep(14 if kind=='firefox' else 3)
  for i in range(n):capture(kind+'-%02d'%i,rows,maxh,sc,text,immediate=kind=='race')
 finally:
  f.terminate();f.wait(10)
if __name__=='__main__':
 if sys.argv[1]=='setup':setup()
 elif sys.argv[1]=='batch':batch(sys.argv[2],int(sys.argv[3]))
