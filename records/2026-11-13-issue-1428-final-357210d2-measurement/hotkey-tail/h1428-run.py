from pathlib import Path
import subprocess,json,os,time,socket,struct,signal,hashlib,math
from text_proof import session_environment
from workload import call
r=Path.home()/'work/ocr-final-1428';root=Path.home()/'work/h1428-tail3';root.mkdir(mode=0o700);desktop,_=session_environment(['cinnamon']);desktop.pop('WAYLAND_DISPLAY',None);baseline=r/'nightly-head-baseline/usr';candidate=r/'ubuntu24-candidate/usr';source=r/'candidate-corpus/m74-captures/m74-browser-local-light-100.png';probe=Path.home()/'work/final1428src/build/release/putgd-bench-capture';rows=[]
def quiet(out):
 samples=[]
 for _ in range(30):
  a=list(map(int,Path('/proc/stat').read_text().splitlines()[0].split()[1:]));time.sleep(1);b=list(map(int,Path('/proc/stat').read_text().splitlines()[0].split()[1:]));idle=100*((b[3]+b[4])-(a[3]+a[4]))/(sum(b)-sum(a));samples.append({'load':os.getloadavg(),'cpus':os.cpu_count(),'idlePercent':idle});(out/'quiet.json').write_text(json.dumps(samples))
  if idle>90:return
 raise RuntimeError('host did not become quiet')
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
schedule=[('warm',b,i) for i,b in enumerate(['A','B']*3)]+[('quiet',b,i) for i,b in enumerate(['A','B']*30)]
index=[]
for condition,build,number in schedule:
 label=f'{condition}-{number:02}-{build}';prefix=baseline if build=='A' else candidate;w=root/label;w.mkdir(mode=0o700);rt=Path('/tmp/h1428c-'+condition[0]+str(number));rt.mkdir(mode=0o700);sock=rt/'putgd/session.sock';assert len(str(sock).encode())<=107
 env=desktop|dict(XDG_RUNTIME_DIR=str(rt),XDG_CONFIG_HOME=str(w/'c'),XDG_DATA_HOME=str(w/'d'),XDG_STATE_HOME=str(w/'s'),XDG_CACHE_HOME=str(w/'k'));cli=str(prefix/'bin/putgd-cli');app=None
 try:
  app=subprocess.Popen([str(prefix/'bin/putgd'),'--background'],env=env,stdout=(w/'resident.log').open('x'),stderr=subprocess.STDOUT,start_new_session=True);deadline=time.monotonic()+20
  while not sock.exists() and time.monotonic()<deadline:time.sleep(.05)
  with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as peer:peer.connect(str(sock));pid,uid,_=struct.unpack('3i',peer.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
  assert uid==os.getuid() and pid==app.pid
  settings=call(cli,sock,'settings.get',{});call(cli,sock,'settings.patch',{'expectedRevision':settings['metadata']['observedRevision'],'patch':{'actions':{'region':{'destination':'local','profileId':None,'shortcut':'Ctrl+Shift+F12'}},'archive':{'root':str(w/'exports'),'keepUploads':True},'preferences':{'notifications':False,'launchAtLogin':False,'diagnostics':{'debugLogging':True}}}});time.sleep(1)
  for child in uis(pid):os.kill(child,signal.SIGTERM)
  time.sleep(.5);quiet(w)
  files={}
  for line in Path('/proc',str(pid),'maps').read_text().splitlines():
   parts=line.split(None,5)
   if len(parts)!=6 or not parts[5].startswith('/'):continue
   path=parts[5];lo,hi=parts[0].split('-');entry=files.setdefault(path,{'mappedBytes':0,'fileBytes':Path(path).stat().st_size});entry['mappedBytes']+=int(hi,16)-int(lo,16)
  (w/'identity.json').write_text(json.dumps({'build':build,'condition':condition,'block':number,'residentPid':pid,'socketBytes':len(str(sock).encode()),'version':json.loads(subprocess.check_output([cli,'--version-json'],text=True)),'files':files,'binarySha256':hashlib.sha256((prefix/'bin/putgd').read_bytes()).hexdigest(),'captureSha256':hashlib.sha256((prefix/'bin/putgd-capture').read_bytes()).hexdigest()},indent=2))
  cfg={'samples':60 if condition=='warm' else 1,'warmups':5,'spacingSeconds':3 if condition=='warm' else .2,'quietSeconds':40 if condition=='quiet' else 0}
  p=subprocess.run(['python3',str(r/'h1428-witness.py'),str(pid),str(prefix/'bin/putgd-capture'),str(w/'witness'),json.dumps(cfg)],env=env,capture_output=True,text=True,timeout=600);(w/'witness.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
  v=json.loads((w/'witness/receipt.json').read_text());assert v['complete'];index.append({'condition':condition,'build':build,'block':number,'receipt':str(w/'witness/receipt.json'),'count':len(v['rows'])});(root/'index.json').write_text(json.dumps(index,indent=2));print(label,'complete',len(v['rows']),flush=True)
 finally:
  if app and app.poll() is None:app.terminate();app.wait(timeout=10)
(root/'complete.json').write_text(json.dumps({'complete':True,'blocks':len(index)}))
