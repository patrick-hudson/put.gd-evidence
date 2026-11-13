from pathlib import Path
import subprocess,json,os,time,socket,struct,signal,hashlib,datetime
from text_proof import session_environment,Input
from workload import call,validate_socket
r=Path.home()/'work/ocr-corpus-1428';root=Path.home()/'work/i8dp2';root.mkdir(mode=0o700);desktop,_=session_environment(['kwin_wayland','plasmashell']);desktop['WAYLAND_DISPLAY']=str(Path(desktop['XDG_RUNTIME_DIR'])/desktop['WAYLAND_DISPLAY']);assert len(desktop['WAYLAND_DISPLAY'].encode())<=107;desktop['QT_QPA_PLATFORM']='wayland';viewer=None;agent=None;realEntries=[];cli=str(r/'debian-candidate/usr/bin/putgd-cli');rt=Path('/tmp/i8dq1428');rt.mkdir(mode=0o700);inputSock=rt/'input.sock';assert len(str(inputSock).encode())<=107;agent=subprocess.Popen(['sudo','-n','python3',str(r/'host_input.py'),'serve','--socket',str(inputSock),'--user','patrick'],stdout=(root/'input.log').open('x'),stderr=subprocess.STDOUT,start_new_session=True)
def sync_cache():
 p=subprocess.run(['kbuildsycoca6','--noincremental'],env=desktop,capture_output=True,text=True,timeout=30);assert p.returncode==0;(root/'real-session-cache-refresh.log').open('a').write(p.stdout+p.stderr)
def entry(path,exe):
 path.parent.mkdir(parents=True,exist_ok=True);assert not path.exists();path.write_text('[Desktop Entry]\nType=Application\nName=put.gd item8 isolated permission\nExec="'+str(exe)+'"\nNoDisplay=true\nX-KDE-DBUS-Restricted-Interfaces=org.kde.KWin.ScreenShot2\n');path.chmod(0o600)
def waitfile(p,sec=20):
 end=time.monotonic()+sec
 while not p.exists() and time.monotonic()<end:time.sleep(.05)
 assert p.exists()
try:
 waitfile(inputSock);viewer=subprocess.Popen(['feh','--fullscreen','--zoom','100','--title','putgd-item8-dense-retry',str(r/'candidate-corpus/d69-captures/d69-terminal-dense-light-100.png')],env=desktop,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(.5)
 for index,kind in enumerate(['native','appimage']):
  assert datetime.datetime.now(datetime.timezone.utc).hour<12 or datetime.datetime.now(datetime.timezone.utc).minute<0,'stop before nightly desktop check';w=root/kind;w.mkdir(mode=0o700);runtime=rt/('r'+str(index));runtime.mkdir(mode=0o700);sock=runtime/'putgd/session.sock';assert len(str(sock).encode())<=107;env=desktop|dict(XDG_RUNTIME_DIR=str(runtime),XDG_CONFIG_HOME=str(w/'c'),XDG_DATA_HOME=str(w/'d'),XDG_STATE_HOME=str(w/'s'),XDG_CACHE_HOME=str(w/'k'),PYTHONPATH=str(Path.home()/'work/i8src'),PUTGD_TEXT_LAB_SESSION='item8-fe838-d69-retry');binary=r/'debian-candidate/usr/bin/putgd' if kind=='native' else r/'putgd-26.1113.4836-dev+gfe838a950216-x86_64.AppImage';app=None;pid=None;watch=None;real=Path.home()/'.local/share/applications'/('putgd-appimage-item8-'+kind+'-1428.desktop');local=w/'d/applications'/real.name
  try:
   if kind=='native':entry(local,binary);entry(real,binary);realEntries.append(real);sync_cache()
   app=subprocess.Popen([str(binary),'--background'],env=env,stdout=(w/'app.log').open('x'),stderr=subprocess.STDOUT,start_new_session=True);waitfile(sock)
   with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as peer:peer.connect(str(sock));pid,uid,_=struct.unpack('3i',peer.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
   assert uid==os.getuid();validate_socket(sock,pid);exe=Path(os.readlink('/proc/'+str(pid)+'/exe'))
   if kind=='appimage':assert '/.mount_' in str(exe);entry(real,exe);realEntries.append(real);sync_cache()
   # Only this owned UI can cover the fixture; close it, then raise the owned viewer.
   time.sleep(.5)
   for task in Path('/proc',str(pid),'task').glob('*/children'):
    for child in map(int,task.read_text().split()):
     if Path('/proc',str(child),'comm').read_text().strip()=='putgd-ui':os.kill(child,signal.SIGTERM)
   viewwin=subprocess.check_output(['xdotool','search','--pid',str(viewer.pid)],env=desktop,text=True).splitlines()[-1];subprocess.run(['xdotool','windowactivate','--sync',viewwin],env=desktop,check=True);time.sleep(.5);subprocess.run(['import','-window',viewwin,str(w/'owned-viewer.png')],env=desktop,check=True);state={'pid':pid,'exe':str(exe),'socket':str(sock),'cli':cli,'loadBefore':os.getloadavg(),'cpus':os.cpu_count(),'permissionMirror':str(real),'note':'Matching permission entry added only for this isolated executable; kbuildsycoca6 refreshed with actual desktop environment, separately from private app cache.'};(w/'state.json').write_text(json.dumps(state,indent=2));until=time.monotonic()+10
   while time.monotonic()<until:
    caps=call(cli,sock,'capabilities',{})
    if caps.get('text',{}).get('sources',{}).get('monitor',{}).get('available'):break
    time.sleep(.1)
   (w/'capabilities.json').write_text(json.dumps(caps,indent=2));probe=call(cli,sock,'text.recognize',{'source':'monitor','copy':False})['operationId'];end=time.monotonic()+30
   while time.monotonic()<end:
    v=call(cli,sock,'text.inspect',{'id':probe})
    if v['state'] in ['completed','failed','cancelled']:break
    time.sleep(.05)
   (w/'acquisition-probe.json').write_text(json.dumps({k:x for k,x in v.items() if k not in ['text','words','codes']},indent=2));print('ACQUISITION',kind,v['state'],v.get('error'),flush=True)
   if v['state']!='completed':continue
   events=w/'helper-events.jsonl';watch=subprocess.Popen(['sudo','-n','python3',str(r/'item8-helper-watch.py'),str(events)],stdout=(w/'observer.log').open('x'),stderr=subprocess.STDOUT,start_new_session=True);waitfile(events);driver=w/'select.py';driver.write_text('''#!/usr/bin/python3
import sys,json,time
from pathlib import Path
sys.path.insert(0,str(Path.home()/'work/ocr-corpus-1428'))
from workload import call
from text_proof import Input
w=Path(__file__).parent;s=json.loads((w/'state.json').read_text());end=time.monotonic()+10
while time.monotonic()<end:
 v=call(s['cli'],Path(s['socket']),'text.inspect',{'id':sys.argv[1]})
 if v['state']=='acquiring':break
 time.sleep(.05)
else:raise RuntimeError('selector not acquiring')
time.sleep(.5);i=Input('/tmp/i8dq1428/input.sock',1920,1080);i.drag((460,45),(1461,1035))
with (w/'selection-times.jsonl').open('a') as out:out.write(json.dumps({'id':sys.argv[1],'endNs':time.monotonic_ns()})+'\\n')
''');driver.chmod(0o700);p=subprocess.run(['python3',str(r/'workload.py'),'--cli',cli,'--pid',str(pid),'--socket',str(sock),'--region-driver',str(driver),'--helper-events',str(events),'--output',str(w/'workload.json')],env=env,capture_output=True,text=True);(w/'workload.log').write_text(p.stdout+p.stderr);print('WORKLOAD',kind,p.returncode,flush=True)
   def rss():
    return {line.split(':')[0]:int(line.split()[1]) for line in Path('/proc',str(pid),'smaps_rollup').read_text().splitlines() if line.startswith(('Rss:','Pss:'))}
   cache={'controlStart':rss()};time.sleep(60);cache['control60']=rss();op=call(cli,sock,'text.recognize',{'source':'file','path':str(r/'synthetic-codepoints/limit-24mp.png'),'copy':False})['operationId'];deadline=time.monotonic()+30
   while time.monotonic()<deadline:
    v=call(cli,sock,'text.inspect',{'id':op})
    if v['state'] in ['completed','failed','cancelled']:break
    time.sleep(.05)
   cache.update(operationId=op,state=v['state'],characterCount=v.get('characterCount'),truncated=v.get('truncated'));start=time.monotonic();time.sleep(60);cache['at60']=rss();cache['at60Elapsed']=time.monotonic()-start;time.sleep(max(0,120-(time.monotonic()-start)));cache['at120']=rss();cache['at120Elapsed']=time.monotonic()-start;cache['expiredAt120']=call(cli,sock,'text.inspect',{'id':op}).get('resultExpired');time.sleep(max(0,125-(time.monotonic()-start)));cache['expiredAt125']=call(cli,sock,'text.inspect',{'id':op}).get('resultExpired');(w/'cache.json').write_text(json.dumps(cache,indent=2));print('CACHE',kind,json.dumps(cache),flush=True);rows=[]
   for n in range(30):
    op=call(cli,sock,'text.recognize',{'source':'region','copy':True})['operationId'];subprocess.run([str(driver),op],env=env,check=True,timeout=20);end=json.loads((w/'selection-times.jsonl').read_text().splitlines()[-1])['endNs'];deadline=time.monotonic()+30
    while time.monotonic()<deadline:
     v=call(cli,sock,'text.inspect',{'id':op})
     if v['state'] in ['completed','failed','cancelled']:break
     time.sleep(.03)
    ack=time.monotonic_ns();paste=subprocess.run(['wl-paste','--no-newline'],env=desktop,capture_output=True,timeout=10);t=v.get('timings',{});measured=v['state']=='completed' and v.get('copyStatus')=='copied' and len(v.get('text',''))>7000 and not v.get('codes') and paste.returncode==0 and paste.stdout==v['text'].encode() and all(type(t.get(k))==int and t[k]>=0 for k in ['spawnMs','engineStartMs','recognizeMs','copyMs','totalMs']);rows.append({'operationId':op,'status':'measured' if measured else 'blocked','state':v['state'],'copyStatus':v.get('copyStatus'),'timings':t,'characterCount':v.get('characterCount'),'selectionToObservedAckMs':(ack-end)/1e6,'independentPasteMatches':paste.stdout==v.get('text','').encode()});(w/'region-latency.json').write_text(json.dumps({'complete':len(rows)==30 and all(x['status']=='measured' for x in rows),'rows':rows},indent=2))
   print('REGION30',kind,sorted(x['selectionToObservedAckMs'] for x in rows)[28],flush=True)
  except Exception as e:(w/'blocked.json').write_text(json.dumps({'reason':str(e)}));print('BLOCKED',kind,type(e).__name__,str(e),flush=True)
  finally:
   if pid and Path('/proc',str(pid)).exists():os.kill(pid,signal.SIGTERM)
   if app and app.poll() is None:app.wait(timeout=10)
   if watch:subprocess.run(['sudo','-n','kill','-TERM',str(watch.pid)],capture_output=True)
   if real in realEntries:real.unlink();realEntries.remove(real);sync_cache()
finally:
 if viewer and viewer.poll() is None:viewer.terminate();viewer.wait(timeout=5)
 if agent:subprocess.run(['sudo','-n','kill','-TERM',str(agent.pid)],capture_output=True)
 for p in realEntries:p.unlink()
 if realEntries:sync_cache()
 (root/'closed.json').write_text(json.dumps({'closed':True,'scope':'owned apps/input launchers and matching temporary host permission entries removed; verify before lease release'}))
