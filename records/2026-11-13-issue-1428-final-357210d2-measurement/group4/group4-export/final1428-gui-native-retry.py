from pathlib import Path
import subprocess,json,os,time,socket,struct,signal,threading,textwrap
from PIL import Image,ImageDraw,ImageFont
from text_proof import session_environment
from workload import call,validate_socket
r=Path.home()/'work/ocr-final-1428';root=Path.home()/'work/f1428gui-native-retry';root.mkdir(mode=0o700);desktop,_=session_environment(['cinnamon']);desktop.pop('WAYLAND_DISPLAY',None);cli=r/'ubuntu24-candidate/usr/bin/putgd-cli'
im=Image.new('RGB',(1000,240),'white');d=ImageDraw.Draw(im);paragraph='Text recognition runs only when requested. This short synthetic paragraph contains ordinary words and punctuation. The clipboard should preserve every line after the region is selected. Nothing here identifies a real person or account.'
for i,line in enumerate(textwrap.wrap(paragraph,78)):d.text((12,12+32*i),line,font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20),fill='black')
para=root/'paragraph.png';im.save(para);(root/'paragraph-source.json').write_text(json.dumps({'text':paragraph,'characters':len(paragraph),'fontPixels':20,'dimensions':[1000,240]}))
def quiet(w):
 def cpu():return list(map(int,Path('/proc/stat').read_text().splitlines()[0].split()[1:]))
 samples=[]
 for attempt in range(30):
  a=cpu();time.sleep(1);b=cpu();delta=sum(b)-sum(a);idle=(b[3]+b[4]-a[3]-a[4])/delta*100
  v={'load':os.getloadavg(),'cpus':os.cpu_count(),'oneSecondIdlePercent':idle};samples.append(v);(w/'quiet.json').write_text(json.dumps({'samples':samples,'quiet':idle>90}))
  if idle>90:return
 raise RuntimeError('host not quiet after30seconds')
for kind in ['native']:
 w=root/kind;w.mkdir(mode=0o700);rt=Path('/tmp/f1428retry'+('n' if kind=='native' else 'a'));rt.mkdir(mode=0o700);runtime=rt/'r';runtime.mkdir(mode=0o700);sock=runtime/'putgd/session.sock';assert len(str(sock).encode())<=107;env=desktop|dict(PUTGD_TEXT_LAB_SESSION='final1428-m74-g4',PYTHONPATH=str(Path.home()/'work/final1428src'),XDG_RUNTIME_DIR=str(runtime),XDG_CONFIG_HOME=str(w/'c'),XDG_DATA_HOME=str(w/'d'),XDG_STATE_HOME=str(w/'s'),XDG_CACHE_HOME=str(w/'k'));binary=r/'ubuntu24-candidate/usr/bin/putgd' if kind=='native' else next(r.glob('*.AppImage'));app=None;viewer=None;watch=None;stop=threading.Event()
 try:
  source=r/'candidate-corpus/m74-captures/m74-terminal-dense-light-100.png';viewer=subprocess.Popen(['feh','--fullscreen','--zoom','100',str(source)],env=desktop,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  deadline=time.monotonic()+8;win=None
  while time.monotonic()<deadline:
   q=subprocess.run(['xdotool','search','--pid',str(viewer.pid)],env=desktop,capture_output=True,text=True)
   if q.returncode==0 and q.stdout.splitlines():win=q.stdout.splitlines()[-1];break
   if viewer.poll() is not None:raise RuntimeError('owned source viewer exited')
   time.sleep(.1)
  assert win,'owned source viewer did not map'
  app=subprocess.Popen([str(binary),'--background'],env=env,stdout=(w/'app.log').open('x'),stderr=subprocess.STDOUT)
  end=time.monotonic()+20
  while not sock.exists() and time.monotonic()<end:time.sleep(.05)
  with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as peer:peer.connect(str(sock));pid,uid,_=struct.unpack('3i',peer.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
  assert uid==os.getuid();validate_socket(sock,pid);time.sleep(.5)
  for t in Path('/proc',str(pid),'task').glob('*/children'):
   for child in map(int,t.read_text().split()):
    if Path('/proc',str(child),'comm').read_text().strip()=='putgd-ui':os.kill(child,signal.SIGTERM)
  time.sleep(.5);subprocess.run(['xdotool','windowactivate','--sync',win],env=desktop,check=True);time.sleep(.5);subprocess.run(['import','-window',win,str(w/'owned-source.png')],env=desktop,check=True)
  state={'pid':pid,'cli':str(cli),'socket':str(sock),'selection':[460,45,1001,990],'socketBytes':len(str(sock).encode())};(w/'state.json').write_text(json.dumps(state));(w/'private-env.json').write_text(json.dumps(env))
  driver=w/'select.py';driver.write_text("""#!/usr/bin/python3
import json,subprocess,time,sys
from pathlib import Path
sys.path.insert(0,str(Path.home()/'work/ocr-final-1428'))
from workload import call
w=Path(__file__).parent;s=json.loads((w/'state.json').read_text());end=time.monotonic()+10
while time.monotonic()<end:
 v=call(s['cli'],Path(s['socket']),'text.inspect',{'id':sys.argv[1]})
 if v['state']=='acquiring':break
 if v['state'] in ['failed','cancelled']:raise RuntimeError('selection failed')
 time.sleep(.03)
else:raise RuntimeError('selector missing')
from Xlib import display,X,error
import os
d=display.Display();root=d.screen().root;atom=d.intern_atom('_NET_WM_PID');expected=(Path('/proc',str(s['pid']),'exe').resolve().parent/'putgd-capture').stat();deadline=time.monotonic()+10;found=False
while time.monotonic()<deadline and not found:
 for window in root.query_tree().children:
  try:
   attrs=window.get_attributes();g=window.get_geometry();prop=window.get_full_property(atom,X.AnyPropertyType)
   if not attrs.override_redirect or (g.width,g.height)!=(1920,1080) or not prop:continue
   owner=int(prop.value[0]);parts=Path('/proc',str(owner),'stat').read_text().rsplit(') ',1)[1].split()
   exe=Path('/proc',str(owner),'exe').stat()
   if owner==s['pid'] or int(parts[1])==s['pid'] and (exe.st_dev,exe.st_ino)==(expected.st_dev,expected.st_ino):found=True;break
  except (OSError,error.XError):pass
 if not found:time.sleep(.02)
assert found,'exact-owned selector did not map';time.sleep(.1);x,y,a,b=s['selection'];subprocess.run(['xdotool','mousemove','--sync',str(x),str(y),'mousedown','1'],check=True)
for n in range(1,11):subprocess.run(['xdotool','mousemove','--sync',str(x+a*n//10),str(y+b*n//10)],check=True);time.sleep(.015)
subprocess.run(['xdotool','mouseup','1'],check=True)
with (w/'selection-times.jsonl').open('a') as f:f.write(json.dumps({'id':sys.argv[1],'selectionEndNs':time.monotonic_ns()})+'\\n')
""");driver.chmod(0o700);raw=w/'helpers-raw.jsonl';events=w/'helpers.jsonl';events.touch()
  watch=subprocess.Popen(['sudo','-n','python3',str(r/'item8-helper-watch.py'),str(raw)],stdout=(w/'observer.log').open('x'),stderr=subprocess.STDOUT)
  def pump():
   seen=0
   while not stop.is_set():
    if raw.exists():
     lines=raw.read_text().splitlines()
     with events.open('a') as f:
      for line in lines[seen:]:
       v=json.loads(line)
       if v.get('event') in ['spawn','exit']:f.write(line+'\n')
       else:assert 'watching' in v and 'since' in v
     seen=len(lines)
    time.sleep(.02)
  thread=threading.Thread(target=pump);thread.start()
  quiet(w);p=subprocess.run(['python3',str(r/'workload.py'),'--cli',str(cli),'--pid',str(pid),'--socket',str(sock),'--region-driver',str(driver),'--helper-events',str(events),'--output',str(w/'workload.json')],env=env,capture_output=True,text=True);(w/'workload.log').write_text(p.stdout+p.stderr);print('WORKLOAD',kind,p.returncode,flush=True)
  for label,source,selection in [('dense',source,[460,45,1001,990]),('paragraph',para,[460,420,1000,240])]:
   if label=='paragraph':
    viewer.terminate();viewer.wait();viewer=subprocess.Popen(['feh','--fullscreen','--zoom','100',str(source)],env=desktop,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(.6)
   state['selection']=selection;(w/'state.json').write_text(json.dumps(state));quietdir=w/(label+'-conditions');quietdir.mkdir();quiet(quietdir);rows=[]
   for n in range(30):
    op=call(str(cli),sock,'text.recognize',{'source':'region','copy':True})['operationId'];subprocess.run([str(driver),op],env=env,check=True,timeout=20);start=json.loads((w/'selection-times.jsonl').read_text().splitlines()[-1])['selectionEndNs'];end=time.monotonic()+30
    while time.monotonic()<end:
     v=call(str(cli),sock,'text.inspect',{'id':op})
     if v['state'] in ['completed','failed','cancelled']:break
     time.sleep(.03)
    ack=time.monotonic_ns();paste=subprocess.run(['xclip','-selection','clipboard','-o'],env=desktop,capture_output=True,timeout=10);t=v.get('timings',{});measured=v['state']=='completed' and v.get('copyStatus')=='copied' and bool(v.get('text')) and paste.stdout==v['text'].encode() and all(type(t.get(k))==int for k in ['spawnMs','engineStartMs','recognizeMs','copyMs','totalMs']);rows.append({'operationId':op,'status':'recorded' if measured else 'blocked','characterCount':v.get('characterCount'),'timings':t,'selectionToObservedAckMs':(ack-start)/1e6,'independentPasteMatches':paste.stdout==v.get('text','').encode()});(w/(label+'-latency.json')).write_text(json.dumps({'rows':rows,'complete':len(rows)==30 and all(x['status']=='recorded' for x in rows)},indent=2))
   print('LATENCY',kind,label,sorted(x['selectionToObservedAckMs'] for x in rows)[28],flush=True)
  for theme in ['light','dark']:
   p=subprocess.run(['python3',str(r/'file_latency.py'),'--cli',str(cli),'--pid',str(pid),'--socket',str(sock),'--file',str(r/'gnome-4k-captures'/('gnome4k-monitor-'+theme+'.png')),'--runs','30','--output',str(w/('4k-'+theme+'.json'))],env=env,capture_output=True,text=True);(w/('4k-'+theme+'.log')).write_text(p.stdout+p.stderr);print('4K',kind,theme,p.returncode,flush=True)
 except Exception as e:(w/'blocked.json').write_text(json.dumps({'reason':str(e)}));print('BLOCKED',kind,str(e),flush=True)
 finally:
  if watch:subprocess.run(['sudo','-n','kill','-TERM',str(watch.pid)],capture_output=True);watch.wait(timeout=10)
  stop.set()
  if 'thread' in locals():thread.join(timeout=5)
  if app and app.poll() is None:
   if 'pid' in locals() and Path('/proc',str(pid)).exists():os.kill(pid,signal.SIGTERM)
   app.wait(timeout=10)
  if viewer and viewer.poll() is None:viewer.terminate();viewer.wait(timeout=5)
  (w/'closed.json').write_text(json.dumps({'closed':True}))
