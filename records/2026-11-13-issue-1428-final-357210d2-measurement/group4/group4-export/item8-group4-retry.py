from pathlib import Path
import subprocess,json,os,time,socket,struct,signal,hashlib,threading,http.server,zipfile,io,sqlite3
from PIL import Image,ImageDraw,ImageFont
from text_proof import session_environment
r=Path.home()/'work/ocr-final-1428';w=Path.home()/'work/f14g4b';w.mkdir(mode=0o700);base,_=session_environment(['cinnamon']);base.pop('WAYLAND_DISPLAY',None);rt=Path('/tmp/f14gb1428');rt.mkdir(mode=0o700);runtime=rt/'r';runtime.mkdir(mode=0o700);sock=runtime/'putgd/session.sock';assert len(str(sock).encode())<=107
prefix=r/'ubuntu24-candidate/usr';env=base|dict(XDG_RUNTIME_DIR=str(runtime),XDG_CONFIG_HOME=str(w/'c'),XDG_DATA_HOME=str(w/'d'),XDG_STATE_HOME=str(w/'s'),XDG_CACHE_HOME=str(w/'k'));cli=str(prefix/'bin/putgd-cli');rows=[];app=None;viewer=None;server=None;monitor=None
(w/'socket-preflight.json').write_text(json.dumps({str(sock):len(str(sock).encode())}))
def raw(m,p={}):
 v=subprocess.run([cli,'--socket',str(sock),'--params-stdin',m],input=json.dumps(p),capture_output=True,text=True,env=env,timeout=40);return json.loads(v.stdout)
def call(m,p={}):
 v=raw(m,p)
 if not v.get('ok'):raise RuntimeError(v.get('error',{}).get('code','missing_reply'))
 return v['result']
def wait(f,sec=30):
 end=time.monotonic()+sec
 while time.monotonic()<end:
  v=f()
  if v:return v
  time.sleep(.05)
 raise RuntimeError('observation_deadline')
def editor_ready(op):
 v=raw('editor.inspect',{'id':op})
 if v.get('ok'):return v['result'] if v['result'].get('phase')=='editing' else None
 if v.get('error',{}).get('code')=='editor_starting':return None
 raise RuntimeError(v.get('error',{}).get('code','missing_reply'))
def terminal(op):return wait(lambda:(v if (v:=call('text.inspect',{'id':op}))['state'] in ['completed','failed','cancelled'] else None))
def recognize(path,copy=False):return call('text.recognize',{'source':'file','path':str(path),'copy':copy})['operationId']
def paste(primary=False):return subprocess.run(['xclip','-selection','primary' if primary else 'clipboard','-o'],env=base,capture_output=True,timeout=10).stdout
def clip(text,primary=False):
 p=subprocess.Popen(['xclip','-selection','primary' if primary else 'clipboard','-in','-loops','0'],env=base|{'PUTGD_TEXT_LAB_SESSION':'final1428'},stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);p.communicate(text.encode(),timeout=5)
def patch(p):return call('settings.patch',{'expectedRevision':call('settings.get')['metadata']['observedRevision'],'patch':p})
def record(name,status,**x):
 rows.append({'case':name,'status':status,**x});(w/'receipt.json').write_text(json.dumps({'candidate':'357210d2f1cb7b65f77166e34eb535d42e497fd0','rows':rows},indent=2));print(name,status,flush=True)
def case(name,f):
 try:f()
 except Exception as e:record(name,'not_run',reason=str(e) if isinstance(e,RuntimeError) else type(e).__name__)
def make(texts,name,size=(1920,1080),px=28):
 im=Image.new('RGB',size,'white');d=ImageDraw.Draw(im);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',px)
 for i,t in enumerate(texts):d.text((35,35+i*45),t,font=font,fill='black')
 p=w/(name+'.png');im.save(p);return p
canary='CANARYSILVER1428';p=make([canary,'PRIVATE MEASUREMENT ONLY','Grüße aus Köln — αβγ 1428'],'owned-screen-reference');unicode=r/'candidate-corpus/candidate-engine-additions/german/german-0.png'
try:
 app=subprocess.Popen([str(prefix/'bin/putgd'),'--background'],env=env,stdout=(w/'resident.log').open('x'),stderr=subprocess.STDOUT,start_new_session=True);wait(lambda:sock.exists());patch({'actions':{'edit':{'destination':'local','profileId':None}},'archive':{'root':str(w/'exports'),'keepUploads':True},'preferences':{'diagnostics':{'debugLogging':True}}});time.sleep(1)
 for task in Path('/proc',str(app.pid),'task').glob('*/children'):
  for child in map(int,task.read_text().split()):
   if Path('/proc',str(child),'comm').read_text().strip()=='putgd-ui':os.kill(child,signal.SIGTERM)
 time.sleep(.2);clip('SYNTHETIC PRIMARY 1428',True);primary=paste(True);assert primary==b'SYNTHETIC PRIMARY 1428'
 def privacy():
  global viewer,monitor
  before={}
  for x in Path('/tmp').rglob('*'):
   try:
    if x.is_file() and not x.is_symlink() and x.stat().st_uid==os.getuid():before[str(x)]=(x.stat().st_size,x.stat().st_mtime_ns)
   except OSError:pass
  viewer=subprocess.Popen(['feh','--fullscreen','--zoom','100','--title','putgd-item8-canary',str(p)],env=base,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(.8);win=subprocess.check_output(['xdotool','search','--pid',str(viewer.pid)],env=base,text=True).splitlines()[-1];g=subprocess.check_output(['xdotool','getwindowgeometry','--shell',win],env=base,text=True);assert 'WIDTH=1920' in g and 'HEIGHT=1080' in g
  monitor=subprocess.Popen(['dbus-monitor','--session',"type='method_call',interface='org.freedesktop.Notifications',member='Notify'"],env=base,stdout=subprocess.PIPE,stderr=subprocess.PIPE);time.sleep(.2);op=call('text.recognize',{'source':'monitor','copy':True})['operationId'];v=terminal(op);time.sleep(.5);monitor.terminate();notificationBytes,monitorError=monitor.communicate(timeout=5);notificationCalls=notificationBytes.count(b'member=Notify');notificationLeaks=canary.encode() in notificationBytes;record('privacy-notifications','met' if notificationCalls>0 and not notificationLeaks else ('missed' if notificationLeaks else 'not_run'),notificationCalls=notificationCalls,canaryInNotifications=notificationLeaks,monitorExit=monitor.returncode);assert v['state']=='completed' and canary in v.get('text','');viewer.terminate();viewer.wait();viewer=None
  diag=call('diagnostics.bundle',{'since':'1h','includeNames':False,'output':str(w/'diagnostics.zip'),'upload':False});hits=[];png=[];checked=0
  roots=[w/'c',w/'d',w/'s',w/'k',runtime];files=[w/'resident.log']+[x for root in roots for x in root.rglob('*') if x.is_file() and not x.is_symlink()]
  for x in Path('/tmp').rglob('*'):
   try:
    if x.is_file() and not x.is_symlink() and x.stat().st_uid==os.getuid() and before.get(str(x))!=(x.stat().st_size,x.stat().st_mtime_ns):files.append(x)
   except OSError:pass
  skipped=[]
  for x in set(files):
   try:
    if x.stat().st_size>32*1024*1024:skipped.append(str(x));continue
    b=x.read_bytes();checked+=1
    if canary.encode() in b:hits.append(str(x))
    if b'\x89PNG\r\n\x1a\n' in b:png.append(str(x))
   except OSError:skipped.append(str(x))
  with zipfile.ZipFile(w/'diagnostics.zip') as z:dh=[n for n in z.namelist() if canary.encode() in z.read(n)]
  hist=call('history.list',{'limit':100});recent=call('operation.recent');journalRead=subprocess.run(['journalctl','--user','--since','2 minutes ago','--output','cat','--no-pager'],capture_output=True);journal=journalRead.stdout;assert journalRead.returncode==0
  record('privacy-canary-files','met' if not hits and not png and not dh and not skipped and canary.encode() not in journal and op not in json.dumps(hist) and op not in json.dumps(recent) else 'missed',operationId=op,recognized=True,debugLogging=True,filesChecked=checked,canaryFiles=hits,pngSignatures=png,skipped=skipped,diagnosticHits=dh,journalCanary=canary.encode() in journal,historyContainsOperation=op in json.dumps(hist),recentContainsOperation=op in json.dumps(recent),notificationContent='separate privacy-notifications row, raw D-Bus traffic inspected only in memory')
 # admitted canary covered in final privacy runner
 def copy_cases():
  clip('SYNTHETIC USER COPY 1428');op=recognize(r/'gnome-4k-captures/gnome4k-monitor-light.png',True);time.sleep(.2);during=call('text.inspect',{'id':op})['state'];clip('SYNTHETIC USER COPY DURING JOB 1428');v=terminal(op);record('user-copy-during-recognition','met' if during not in ['completed','failed','cancelled'] and v['state']=='completed' and paste()==b'SYNTHETIC USER COPY DURING JOB 1428' and v.get('copyStatus')=='suppressed' else 'missed',stateBeforeUserCopy=during,copyStatus=v.get('copyStatus'))
  clip('SYNTHETIC COPY FALSE 1428');v=terminal(recognize(p,False));record('copy-false','met' if v['state']=='completed' and paste()==b'SYNTHETIC COPY FALSE 1428' else 'missed',copyStatus=v.get('copyStatus'))
  v=terminal(recognize(p,True));text=v.get('text','').encode();record('multi-line-unicode','met' if v['state']=='completed' and paste()==text and b'\n' in text and any(b>=128 for b in text) else 'missed',exactPaste=paste()==text,characterCount=v.get('characterCount'),textSha256=hashlib.sha256(text).hexdigest(),codes=len(v.get('codes',[])));record('PRIMARY-untouched','met' if paste(True)==primary else 'missed')
 case('clipboard',copy_cases)
 def cancelled():
  op=recognize(r/'synthetic-final/limit-24mp.png');helpers=[];until=time.monotonic()+5
  while not helpers and time.monotonic()<until:
   children=set()
   for t in Path('/proc',str(app.pid),'task').glob('*/children'):children.update(map(int,t.read_text().split()))
   for pid in children:
    try:
     if Path('/proc',str(pid),'comm').read_text().strip()=='putgd-ocr':helpers.append({'pid':pid,'startTicks':Path('/proc',str(pid),'stat').read_text().rsplit(') ',1)[1].split()[19]})
    except OSError:pass
   if not helpers:time.sleep(.05)
  assert helpers, 'no running helper observed'
  call('text.cancel',{'id':op});v=call('text.inspect',{'id':op});gone=bool(helpers) and all(not Path('/proc',str(x['pid'])).exists() for x in helpers);record('cooperative-text-cancel','met' if v['state']=='cancelled' and gone else 'missed',state=v['state'],operationId=op,helpers=helpers,helpersAndThreadsGone=gone)
 case('cooperative-text-cancel',cancelled)
 def editor():
  op=call('editor.open',{'source':'file','path':str(p)})['operationId'];wait(lambda:editor_ready(op));call('editor.recognize',{'id':op});v=call('editor.inspect',{'id':op});words=v['text']['words'];target=next(x for x in words if x['text']==canary);rect=target['rect'];old=v['text']['result']
  a=call('editor.apply',{'id':op,'commands':[{'op':'add','shape':{'kind':'redact','rect':rect}}]});sid=a['created'][0]
  def check(label):
   call('editor.recognize',{'id':op});t=call('editor.inspect',{'id':op})['text'];stale=raw('editor.selectText',{'id':op,'result':old,'all':True});oldCopy=raw('editor.copyText',{'id':op,'result':old,'all':True});copied=call('editor.copyText',{'id':op,'result':t['result'],'all':True});record(label,'met' if copied.get('copyStatus')=='copied' and oldCopy.get('error',{}).get('code')=='edit_stale' and b'PRIVATE' in paste() and not any(x['text']==canary for x in t['words']) and canary.encode() not in paste() and stale.get('error',{}).get('code')=='edit_stale' else 'missed',oldResultCode=stale.get('error',{}).get('code'),oldCopyCode=oldCopy.get('error',{}).get('code'),currentCopy=copied,wordCount=len(t['words']))
  check('editor-redact-added');call('editor.apply',{'id':op,'commands':[{'op':'update','shapeId':sid,'shape':{'rect':[1500,900,200,50]}}]});call('editor.recognize',{'id':op});assert any(x['text']==canary for x in call('editor.inspect',{'id':op})['text']['words']);old=call('editor.inspect',{'id':op})['text']['result'];call('editor.apply',{'id':op,'commands':[{'op':'update','shapeId':sid,'shape':{'rect':rect}}]});check('editor-redact-moved');call('editor.apply',{'id':op,'commands':[{'op':'undo'}]});call('editor.recognize',{'id':op});old=call('editor.inspect',{'id':op})['text']['result'];call('editor.apply',{'id':op,'commands':[{'op':'redo'}]});check('editor-redact-redo');data=paste();call('editor.cancel',{'id':op});time.sleep(.3);record('paste-after-editor-closes','met' if data and paste()==data else 'missed')
  op=call('editor.open',{'source':'file','path':str(r/'synthetic-final/limit-24mp.png')})['operationId'];wait(lambda:editor_ready(op));proc=subprocess.Popen([cli,'--socket',str(sock),'--params-stdin','editor.recognize'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,text=True);proc.stdin.write(json.dumps({'id':op}));proc.stdin.close();wait(lambda:call('editor.inspect',{'id':op}).get('text',{}).get('state')=='recognizing');call('editor.apply',{'id':op,'commands':[{'op':'add','shape':{'kind':'redact','rect':[10,10,500,100]}}]});proc.wait(timeout=30);answer=json.loads(proc.stdout.read());record('editor-late-revision','met' if answer.get('error',{}).get('code')=='edit_stale' else 'missed',error=answer.get('error',{}).get('code'));call('editor.cancel',{'id':op})
 # editor privacy covered by final privacy runner
 # Credential-free loopback custom HTTP destination: request pixels discarded in memory.
 class Handler(http.server.BaseHTTPRequestHandler):
  def log_message(self,*a):pass
  def do_POST(self):
   self.rfile.read(int(self.headers.get('Content-Length','0')));server.started.set();time.sleep(server.delay);b=json.dumps({'url':server.link}).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);server.delay=0;server.link='https://example.test/1428/short.png';server.started=threading.Event();threading.Thread(target=server.serve_forever,daemon=True).start()
 def upload_cases():
  settings={'accepts':['image','text','file'],'allowInsecureHttp':False,'arguments':[],'body':'multipart','connectTimeoutMs':10000,'data':'','dataSecret':False,'deletionUrl':'','errorMessage':'','fileFormName':'file','headers':[],'parameters':[],'requestMethod':'POST','requestTimeoutMs':60000,'requestUrl':'http://127.0.0.1:'+str(server.server_port)+'/upload','responseUrl':'{json:url}','secrets':[],'thumbnailUrl':''};patch({'profiles':[{'id':'item8-loopback','label':'Synthetic loopback receiver','provider':'custom-http','settings':settings,'credentials':{'mode':'session','reference':None}}],'preferences':{'uploadClipboardBehavior':'each_link'}})
  def uploaded():
   op=call('upload.files',{'paths':[str(p)],'profileId':'item8-loopback'})['operationId'];v=wait(lambda:(v if (v:=call('operation.inspect',{'id':op}))['state'] in ['completed','failed','partial'] else None),40);assert v['state']=='completed';return v['items'][0]['artifact']['id']
  server.delay=8;server.started.clear();op=call('upload.files',{'paths':[str(p)],'profileId':'item8-loopback'})['operationId'];assert server.started.wait(10);v=terminal(recognize(p,True));text=paste();wait(lambda:call('operation.inspect',{'id':op})['state']=='completed',20);record('pending-upload-link','met' if v['state']=='completed' and v.get('copyStatus')=='copied' and text==v.get('text','').encode() and text and paste()==text else 'missed',recognitionCopyStatus=v.get('copyStatus'),uploadCopyStatus=call('operation.inspect',{'id':op}).get('copyStatus'));items=call('history.list',{'limit':100})['records'];hid=items[0]['id'];call('history.copyLink',{'id':hid});record('later-explicit-copy','met' if paste()==server.link.encode() else 'missed');server.delay=0
 case('upload-and-show-qr',upload_cases)
 v=terminal(recognize(p,True));data=v.get('text','').encode();exactBefore=v['state']=='completed' and v.get('copyStatus')=='copied' and bool(data) and not v.get('codes') and paste()==data;app.terminate();app.wait(timeout=10);app=None;time.sleep(.3);record('paste-after-resident-quits','met' if exactBefore and data==paste() else 'missed',nonemptyBytes=len(data),independentPasteBefore=exactBefore,independentPasteAfter=paste()==data)
 # A no-code Unicode payload is independently pasted after the actual FUSE mount is gone.
 rt2=Path('/tmp/f14gc1428');rt2.mkdir(mode=0o700);runtime=rt2/'r';runtime.mkdir(mode=0o700);sock=runtime/'putgd/session.sock';assert len(str(sock).encode())<=107;env=base|dict(XDG_RUNTIME_DIR=str(runtime),XDG_CONFIG_HOME=str(w/'ac'),XDG_DATA_HOME=str(w/'ad'),XDG_STATE_HOME=str(w/'as'),XDG_CACHE_HOME=str(w/'ak'));image=r/'putgd-26.1113.4851-dev+g357210d2f1cb-x86_64.AppImage';app=subprocess.Popen([str(image),'--background'],env=env,stdout=(w/'appimage.log').open('x'),stderr=subprocess.STDOUT,start_new_session=True);wait(lambda:sock.exists());v=terminal(recognize(p,True));data=v.get('text','').encode()
 with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as peer:peer.connect(str(sock));pid,uid,_=struct.unpack('3i',peer.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
 assert uid==os.getuid();exe=os.readlink('/proc/'+str(pid)+'/exe');assert '/.mount_' in exe;mount=str(Path(exe).parents[2]);before=paste()==data and bool(data) and not v.get('codes');os.kill(pid,signal.SIGTERM);app.wait(timeout=10);app=None;time.sleep(.3);gone=mount not in Path('/proc/self/mountinfo').read_text();record('paste-after-AppImage-unmount','met' if before and gone and paste()==data else 'missed',independentPasteBefore=before,independentPasteAfter=paste()==data,mountGone=gone,PRIMARYUnchanged=paste(True)==primary,textBytes=len(data),textSha256=hashlib.sha256(data).hexdigest())

finally:
 if monitor and monitor.poll() is None:monitor.terminate();monitor.wait(timeout=5)
 if server:server.shutdown();server.server_close()
 if viewer and viewer.poll() is None:viewer.terminate();viewer.wait(timeout=5)
 if app and app.poll() is None:app.terminate();app.wait(timeout=10)
 (w/'closed.json').write_text(json.dumps({'closed':True,'scope':'owned primary app and covering viewer stopped; verify children and cleanup before lease release'}))
