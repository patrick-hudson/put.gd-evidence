from pathlib import Path
import subprocess,json,os,time,socket,struct,signal,hashlib,math
from text_proof import session_environment
from workload import call
r=Path.home()/'work/ocr-corpus-1428';root=Path.home()/'work/i8ab2';root.mkdir(mode=0o700);desktop,_=session_environment(['cinnamon']);desktop.pop('WAYLAND_DISPLAY',None);baseline=r/'nightly-head-baseline/usr';candidate=r/'ubuntu24-candidate/usr';source=r/'candidate-corpus/m74-captures/m74-browser-local-light-100.png';probe=Path.home()/'work/i8src/build/release/putgd-bench-capture';rows=[]
def children(pid):
 out=set()
 for p in (Path('/proc')/str(pid)/'task').glob('*/children'):
  try:out.update(map(int,p.read_text().split()))
  except OSError:pass
 return out
def uis(pid):
 result=[]
 for p in children(pid):
  try:
   if Path('/proc',str(p),'comm').read_text().strip()=='putgd-ui':result.append(p)
  except OSError:pass
 return result
def windows(pid,env):
 p=subprocess.run(['xdotool','search','--onlyvisible','--pid',str(pid)],env=env,capture_output=True,text=True);result=[]
 for win in p.stdout.split():
  q=subprocess.run(['xdotool','getwindowgeometry','--shell',win],env=env,capture_output=True,text=True)
  try:
   g=dict(line.split('=',1) for line in q.stdout.splitlines());
   if int(g.get('WIDTH','0'))>=400 and int(g.get('HEIGHT','0'))>=200:result.append(win)
  except (ValueError,KeyError):pass
 return result
def names(pid):return sorted({f[5].rsplit('/',1)[-1] for line in Path('/proc',str(pid),'maps').read_text().splitlines() if len(f:=line.split(None,5))==6 and f[5].startswith('/')})
for index,(label,prefix) in enumerate([('baseline',baseline),('candidate',candidate)]):
 w=root/label;w.mkdir(mode=0o700);rt=Path('/tmp/i8ac'+str(index)+'1428');rt.mkdir(mode=0o700);runtime=rt/'r';runtime.mkdir(mode=0o700);sock=runtime/'putgd/session.sock';assert len(str(sock).encode())<=107;env=desktop|dict(XDG_RUNTIME_DIR=str(runtime),XDG_CONFIG_HOME=str(w/'c'),XDG_DATA_HOME=str(w/'d'),XDG_STATE_HOME=str(w/'s'),XDG_CACHE_HOME=str(w/'k'));cli=str(prefix/'bin/putgd-cli');app=subprocess.Popen([str(prefix/'bin/putgd'),'--background'],env=env,stdout=(w/'resident.log').open('x'),stderr=subprocess.STDOUT,start_new_session=True)
 try:
  end=time.monotonic()+20
  while not sock.exists() and time.monotonic()<end:time.sleep(.05)
  with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as peer:peer.connect(str(sock));pid,uid,_=struct.unpack('3i',peer.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
  assert uid==os.getuid();state={'candidate':json.loads(subprocess.check_output([cli,'--version-json'],text=True)),'residentPid':pid,'socketBytes':len(str(sock).encode()),'loadBefore':os.getloadavg(),'cpus':os.cpu_count(),'scope':'physical Cinnamon X11; public shown/phaseediting acknowledgement followed by independent owned visible-window witness; CLI/poll overhead included','binaries':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [prefix/'bin/putgd',prefix/'bin/putgd-ui',prefix/'bin/putgd-capture',probe]}};(w/'identity.json').write_text(json.dumps(state,indent=2));s=call(cli,sock,'settings.get',{});call(cli,sock,'settings.patch',{'expectedRevision':s['metadata']['observedRevision'],'patch':{'actions':{'region':{'destination':'local','profileId':None,'shortcut':'Ctrl+Shift+F12'},'edit':{'destination':'local','profileId':None}},'archive':{'root':str(w/'exports'),'keepUploads':True},'preferences':{'notifications':False,'launchAtLogin':False}}});time.sleep(1)
  initial=uis(pid)
  for child in initial:os.kill(child,signal.SIGTERM)
  time.sleep(.5);state['closedOwnedOnboardingUiPids']=initial;(w/'identity.json').write_text(json.dumps(state,indent=2))
  for view in ['main','edit-image']:
   for i in range(10):
    before=set(uis(pid))
    for child in before:os.kill(child,signal.SIGTERM)
    deadline=time.monotonic()+5
    while uis(pid) and time.monotonic()<deadline:time.sleep(.05)
    assert not uis(pid), 'previous UI still alive';start=time.monotonic_ns()
    if view=='main':answer=call(cli,sock,'ui.show',{'view':'activity'});op=None
    else:
     op=call(cli,sock,'editor.open',{'source':'file','path':str(source)})['operationId'];end=time.monotonic()+15
     while time.monotonic()<end:
      response=subprocess.run([cli,'--socket',str(sock),'--params-stdin','editor.inspect'],input=json.dumps({'id':op}),env=env,capture_output=True,text=True,timeout=20);response=json.loads(response.stdout)
      if not response.get('ok'):
       if response.get('error',{}).get('code')=='editor_starting':time.sleep(.01);continue
       raise RuntimeError(response.get('error',{}).get('code','missing_reply'))
      answer=response['result']
      if answer.get('phase')=='editing':break
      time.sleep(.01)
     assert answer.get('phase')=='editing'
    ack=time.monotonic_ns();deadline=time.monotonic()+5;pids=[];visible=[]
    while time.monotonic()<deadline:
     pids=uis(pid)
     if len(pids)==1:visible=windows(pids[0],env)
     if visible:break
     time.sleep(.01)
    assert len(pids)==1 and visible, 'owned meaningful window did not map';p=pids[0];elapsed=(time.monotonic_ns()-start)/1e6;args=Path('/proc',str(p),'cmdline').read_bytes().split(b'\0');assert (b'--edit-image' in args)==(view=='edit-image');row={'version':label,'view':view,'index':i,'ackMs':(ack-start)/1e6,'ownedMappedMs':elapsed,'uiPid':p,'windows':visible,'mappedNames':names(p)};rows.append(row);(root/'ui-startup.json').write_text(json.dumps(rows,indent=2))
    if i==0:subprocess.run(['import','-window',visible[0],str(w/(view+'-owned-window.png'))],env=env,check=True)
    if op:call(cli,sock,'editor.cancel',{'id':op})
    else:
     for win in visible:subprocess.run(['wmctrl','-ic',hex(int(win))],env=env,capture_output=True)
    end=time.monotonic()+3
    while Path('/proc',str(p)).exists() and time.monotonic()<end:time.sleep(.05)
    if Path('/proc',str(p)).exists():os.kill(p,signal.SIGTERM);time.sleep(.3)
   print('UI',label,view,'p95',max(x['ownedMappedMs'] for x in rows if x['version']==label and x['view']==view),flush=True)
  caps=call(cli,sock,'capabilities',{});(w/'capabilities.json').write_text(json.dumps(caps,indent=2));p=subprocess.run([str(probe),'--resident-pid',str(pid),'--capture-helper',str(prefix/'bin/putgd-capture'),'--live-outline','--output',str(w/'hotkey.json')],env=env,stdout=(w/'probe.log').open('x'),stderr=subprocess.STDOUT,timeout=240);print('HOTKEY',label,p.returncode,flush=True)
 except Exception as e:
  import traceback
  (w/'blocked.json').write_text(json.dumps({'reason':str(e) if isinstance(e,(RuntimeError,AssertionError)) else type(e).__name__,'stack':[{'function':f.name,'line':f.lineno} for f in traceback.extract_tb(e.__traceback__)]}));print('BLOCKED',label,type(e).__name__,str(e),flush=True)
 finally:
  app.terminate();app.wait(timeout=10)
(root/'closed.json').write_text(json.dumps({'closed':True,'frozenProbeSha256':hashlib.sha256(probe.read_bytes()).hexdigest(),'note':'The frozen C++ probe was run unchanged, five warmups and30samples. Its route-free-settings-incompatible Python setup wrapper was not modified or used.'}))
