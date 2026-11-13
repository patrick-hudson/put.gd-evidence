from pathlib import Path
import subprocess,json,os,time,socket,struct,signal,hashlib,threading,http.server,zipfile,io,sqlite3
from PIL import Image,ImageDraw,ImageFont
from text_proof import session_environment
r=Path.home()/'work/ocr-corpus-1428';w=Path.home()/'work/i8g4d';w.mkdir(mode=0o700);base,_=session_environment(['cinnamon']);base.pop('WAYLAND_DISPLAY',None);rt=Path('/tmp/i8gf1428');rt.mkdir(mode=0o700);runtime=rt/'r';runtime.mkdir(mode=0o700);sock=runtime/'putgd/session.sock';assert len(str(sock).encode())<=107
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
def recognize_editor(op):
 call('editor.recognize',{'id':op})
 v=wait(lambda:(v if (v:=call('editor.inspect',{'id':op})).get('text',{}).get('state') in ['completed','failed','cancelled'] else None))
 if v['text']['state']!='completed':raise RuntimeError('editor recognition did not complete')
 return v['text']
def terminal(op):return wait(lambda:(v if (v:=call('text.inspect',{'id':op}))['state'] in ['completed','failed','cancelled'] else None))
def recognize(path,copy=False):return call('text.recognize',{'source':'file','path':str(path),'copy':copy})['operationId']
def paste(primary=False):return subprocess.run(['xclip','-selection','primary' if primary else 'clipboard','-o'],env=base,capture_output=True,timeout=10).stdout
def clip(text,primary=False):
 p=subprocess.Popen(['xclip','-selection','primary' if primary else 'clipboard','-in','-loops','0'],env=base,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);p.communicate(text.encode(),timeout=5)
def patch(p):return call('settings.patch',{'expectedRevision':call('settings.get')['metadata']['observedRevision'],'patch':p})
def record(name,status,**x):
 rows.append({'case':name,'status':status,**x});(w/'receipt.json').write_text(json.dumps({'candidate':'fe838a9502167672f3512e27c32c74cfcf6c84d1','rows':rows},indent=2));print(name,status,flush=True)
def case(name,f):
 try:f()
 except Exception as e:
  import traceback
  record(name,'not_run',reason=str(e) if isinstance(e,RuntimeError) else type(e).__name__,stack=[{'function':f.name,'line':f.lineno} for f in traceback.extract_tb(e.__traceback__)])
def make(texts,name,size=(1920,1080),px=28):
 im=Image.new('RGB',size,'white');d=ImageDraw.Draw(im);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',px)
 for i,t in enumerate(texts):d.text((35,35+i*45),t,font=font,fill='black')
 p=w/(name+'.png');im.save(p);return p
canary='SUNFLOWER';p=make(['SYNTHETIC PRIVACY CHECK','PRIVATE '+canary+' MEASUREMENT ONLY','Grüße aus Köln — αβγ 1428'],'owned-screen-reference');unicode=r/'candidate-corpus/candidate-engine-additions/german/german-0.png'
try:
 app=subprocess.Popen([str(prefix/'bin/putgd'),'--background'],env=env,stdout=(w/'resident.log').open('x'),stderr=subprocess.STDOUT,start_new_session=True);wait(lambda:sock.exists());patch({'actions':{'edit':{'destination':'local','profileId':None}},'archive':{'root':str(w/'exports'),'keepUploads':True},'preferences':{'diagnostics':{'debugLogging':True}}});time.sleep(1)
 for task in Path('/proc',str(app.pid),'task').glob('*/children'):
  for child in map(int,task.read_text().split()):
   if Path('/proc',str(child),'comm').read_text().strip()=='putgd-ui':os.kill(child,signal.SIGTERM)
 time.sleep(.2);primary=paste(True)
 def privacy():
  global viewer,monitor
  before={}
  for x in Path('/tmp').rglob('*'):
   try:
    if x.is_file() and not x.is_symlink() and x.stat().st_uid==os.getuid():before[str(x)]=(x.stat().st_size,x.stat().st_mtime_ns)
   except OSError:pass
  viewer=subprocess.Popen(['feh','--fullscreen','--zoom','100','--title','putgd-item8-canary',str(p)],env=base,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(.8);win=subprocess.check_output(['xdotool','search','--pid',str(viewer.pid)],env=base,text=True).splitlines()[-1];g=subprocess.check_output(['xdotool','getwindowgeometry','--shell',win],env=base,text=True);assert 'WIDTH=1920' in g and 'HEIGHT=1080' in g
  monitor=subprocess.Popen(['dbus-monitor','--session',"type='method_call',interface='org.freedesktop.Notifications',member='Notify'"],env=base,stdout=subprocess.PIPE,stderr=subprocess.PIPE);time.sleep(.2);op=call('text.recognize',{'source':'monitor','copy':True})['operationId'];v=terminal(op);record('privacy-source-admitted','met' if v['state']=='completed' and canary in v.get('text','') else 'not_run',state=v['state'],canaryRecognized=canary in v.get('text',''),characterCount=v.get('characterCount'));time.sleep(.5);monitor.terminate();notificationBytes,monitorError=monitor.communicate(timeout=5);notificationCalls=notificationBytes.count(b'member=Notify');notificationLeaks=canary.encode() in notificationBytes;record('privacy-notifications','met' if notificationCalls>0 and not notificationLeaks else ('missed' if notificationLeaks else 'not_run'),notificationCalls=notificationCalls,canaryInNotifications=notificationLeaks,monitorExit=monitor.returncode);assert v['state']=='completed' and canary in v.get('text','');viewer.terminate();viewer.wait();viewer=None
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
  hist=call('history.list',{'limit':100});recent=call('operation.recent');journalRead=subprocess.run(['sudo','-n','journalctl','_UID='+str(os.getuid()),'--since','2 minutes ago','--output','cat','--no-pager'],capture_output=True);journal=journalRead.stdout;record('privacy-system-journal','met' if journalRead.returncode==0 and canary.encode() not in journal else ('missed' if canary.encode() in journal else 'not_run'),queryExit=journalRead.returncode,canaryFound=canary.encode() in journal)
  record('privacy-canary-files','met' if not hits and not png and not dh and not skipped and canary.encode() not in journal and op not in json.dumps(hist) and op not in json.dumps(recent) else 'missed',operationId=op,recognized=True,debugLogging=True,filesChecked=checked,canaryFiles=hits,pngSignatures=png,skipped=skipped,diagnosticHits=dh,journalCanary=canary.encode() in journal,historyContainsOperation=op in json.dumps(hist),recentContainsOperation=op in json.dumps(recent),notificationContent='separate privacy-notifications row, raw D-Bus traffic inspected only in memory')
 case('privacy-canary-files',privacy)
 def copy_cases():
  clip('SYNTHETIC USER COPY 1428');op=recognize(r/'gnome-4k-captures/gnome4k-monitor-light.png',True);time.sleep(.2);during=call('text.inspect',{'id':op})['state'];clip('SYNTHETIC USER COPY DURING JOB 1428');v=terminal(op);record('user-copy-during-recognition','met' if during not in ['completed','failed','cancelled'] and v['state']=='completed' and paste()==b'SYNTHETIC USER COPY DURING JOB 1428' and v.get('copyStatus')=='suppressed' else 'missed',stateBeforeUserCopy=during,copyStatus=v.get('copyStatus'))
  clip('SYNTHETIC COPY FALSE 1428');v=terminal(recognize(p,False));record('copy-false','met' if v['state']=='completed' and paste()==b'SYNTHETIC COPY FALSE 1428' else 'missed',copyStatus=v.get('copyStatus'))
  v=terminal(recognize(p,True));text=v.get('text','').encode();record('multi-line-unicode','met' if v['state']=='completed' and paste()==text and b'\n' in text and any(b>=128 for b in text) else 'missed',exactPaste=paste()==text,characterCount=v.get('characterCount'),textSha256=hashlib.sha256(text).hexdigest(),codes=len(v.get('codes',[])));record('PRIMARY-untouched','met' if paste(True)==primary else 'missed')
 # Previously measured clipboard cases retained in i8g4b.
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
 # Previously measured cooperative cancellation retained in i8g4b.
 def editor():
  op=call('editor.open',{'source':'file','path':str(p)})['operationId'];wait(lambda:editor_ready(op));recognize_editor(op);v=call('editor.inspect',{'id':op});words=v['text']['words'];target=next(x for x in words if x['text']==canary);rect=target['rect'];old=v['text']['result']
  a=call('editor.apply',{'id':op,'commands':[{'op':'add','shape':{'kind':'redact','rect':rect}}]});sid=a['created'][0]
  def check(label):
   recognize_editor(op);t=call('editor.inspect',{'id':op})['text'];stale=raw('editor.selectText',{'id':op,'result':old,'all':True});oldCopy=raw('editor.copyText',{'id':op,'result':old,'all':True});copied=call('editor.copyText',{'id':op,'result':t['result'],'all':True});record(label,'met' if copied.get('copyStatus')=='copied' and oldCopy.get('error',{}).get('code')=='edit_stale' and b'PRIVATE' in paste() and not any(x['text']==canary for x in t['words']) and canary.encode() not in paste() and stale.get('error',{}).get('code')=='edit_stale' else 'missed',oldResultCode=stale.get('error',{}).get('code'),oldCopyCode=oldCopy.get('error',{}).get('code'),currentCopy=copied,wordCount=len(t['words']))
  check('editor-redact-added');call('editor.apply',{'id':op,'commands':[{'op':'update','shapeId':sid,'shape':{'rect':[1500,900,200,50]}}]});recognize_editor(op);assert any(x['text']==canary for x in call('editor.inspect',{'id':op})['text']['words']);old=call('editor.inspect',{'id':op})['text']['result'];call('editor.apply',{'id':op,'commands':[{'op':'update','shapeId':sid,'shape':{'rect':rect}}]});check('editor-redact-moved');call('editor.apply',{'id':op,'commands':[{'op':'undo'}]});recognize_editor(op);old=call('editor.inspect',{'id':op})['text']['result'];call('editor.apply',{'id':op,'commands':[{'op':'redo'}]});check('editor-redact-redo');data=paste();call('editor.cancel',{'id':op});time.sleep(.3);record('paste-after-editor-closes','met' if data and paste()==data else 'missed')
  record('editor-forced-late-delivery','not_run',reason='editor.recognize is asynchronous and returns immediately; no external switch exists to force an obsolete result to arrive after the revision changes. Live word/revision exclusion measured separately; no late-packet pass inferred from cancellation.')
 case('editor-privacy',editor)
 v=terminal(recognize(p,True));data=v.get('text','').encode();exactBefore=v['state']=='completed' and v.get('copyStatus')=='copied' and bool(data) and not v.get('codes') and paste()==data;app.terminate();app.wait(timeout=10);app=None;time.sleep(.3);record('paste-after-resident-quits','met' if exactBefore and data==paste() else 'missed',nonemptyBytes=len(data),independentPasteBefore=exactBefore,independentPasteAfter=paste()==data)

finally:
 if monitor and monitor.poll() is None:monitor.terminate();monitor.wait(timeout=5)
 if server:server.shutdown();server.server_close()
 if viewer and viewer.poll() is None:viewer.terminate();viewer.wait(timeout=5)
 if app and app.poll() is None:app.terminate();app.wait(timeout=10)
 (w/'closed.json').write_text(json.dumps({'closed':True,'scope':'owned primary app and covering viewer stopped; verify children and cleanup before lease release'}))
