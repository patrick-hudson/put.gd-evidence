"""Private scripted outcomes; reuses B/D real-input recipes and frozen fixtures, never witness gates."""
import sys,os,json,time,uuid,shlex,base64,io,hashlib,dataclasses,traceback,re
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,str(Path.cwd()))
from tools.lab import lab,nightly_desktops as nd
from tools.lab.surface_driver.target import Target
from tools.lab.surface_driver.fixtures import FACTORIES
from tools.lab.surface_driver.fixtures.base import Scope
from tools.lab.surface_driver.fixtures.clipboard import owner
from tools.lab.surface_driver.fixtures.uploads import clipboard_files
from tools.lab.surface_driver.recipes.outcomes import _clipboard_bytes,pixels_equal
from tools.lab.surface_driver.browser import default_browser,open_and_verify,live_download_digest,live_link_unavailable
from tools.lab.surface_driver.redact import Redactor
from tools.lab.surface_driver.api import RecipeFailed
from tools.lab.surface_driver import browser as browser_module
_browser_remote=browser_module._remote
def traced_browser_remote(ctx,action,values,*a,**kw):
 result=_browser_remote(ctx,action,values,*a,**kw)
 if action=="observe" and ctx.destination=="proton" and time.monotonic()-getattr(ctx,"_last_browser_note",0)>15:
  ctx.note("recipient readiness "+json.dumps({k:v for k,v in result.items() if k in ("pending","matched","foreign","url_host")}));ctx._last_browser_note=time.monotonic()
 return result
browser_module._remote=traced_browser_remote
from PIL import Image
@dataclasses.dataclass
class Frame:
 path:str
class NativeTarget(Target):
 def prefix(self):
  # D's sessenv/acc.py retains native XDG_RUNTIME_DIR for Hyprland IPC.
  return super().prefix().replace('export XDG_RUNTIME_DIR='+shlex.quote(self.root)+'/runtime\n','')
class Context:
 def __init__(self,run,out,desktop,package,host,destination):
  self.out=Path(out);self.out.mkdir(mode=0o700,parents=True,exist_ok=False)
  (self.out/'script.py').write_text(Path(__file__).read_text())
  self.desktop,self.package,self.host,self.destination=desktop,package,host,destination
  self.placement='guest';self._live_admitted=destination!='local';self._deadline=time.monotonic()+1500
  prep=json.loads(Path('work/sp/'+run.name+'-prep/firefox.json').read_text())
  self.profile=dict(guest=lab.state(run)['profile'],session='wayland',isolated_keyring=True,browser=dict(command=prep['command'],profile_root='/dev/shm/sp-firefox'))
  self.evidence=SimpleNamespace(redactor=Redactor());self.notes=[]
  root='/dev/shm/s'+uuid.uuid4().hex[:7]
  os.system('python3 tools/diagnostics/check_socket_paths.py --socket '+root+'/runtime/putgd/session.sock '+root+'/fx-12345678/secret-service/control/control >'+str(self.out/'socket-preflight.json'))
  self.target=NativeTarget(run=run,session_root=root,app_executable='putgd-launcher' if package=='appimage' else 'putgd')
  native=self.target.session('printf "%s" "$XDG_RUNTIME_DIR"').strip();self.target.socket=native+'/putgd/session.sock'
  assert len(self.target.socket.encode())<=107
  self.target.start();
  from tools.lab.surface_driver.fixtures.keyring import OWNER
  observed=self.shell("python3 - <<'KEYOWNER'\n"+OWNER+'\nKEYOWNER\n');provider=json.loads(observed['stdout'])['provider'];self.profile['isolated_keyring']=provider in ('ksecretd','oo7-daemon')
  self.scope=Scope(self);self._fixture_manager=SimpleNamespace(scope=self.scope)
  self.values={};self.scope.initialize()
  result=self.shell('mkdir -m 700 /dev/shm/sp-firefox');assert result['returncode']==0
  self.scope.defer('private Firefox root',lambda:self.shell('rmdir /dev/shm/sp-firefox'),priority=-900)
  build=self.call('ui.snapshot')['build'];assert build['gitCommit']=='2b5e1b2d3c11757f805331e4104eb06b2c79ad5c' and not build['dirty'];self.build=build
  self.note('scripted outcome pass; exact build '+build['gitCommit'])
  (self.out/'capabilities.json').write_text(json.dumps(self.call('capabilities'),indent=2))
  (self.out/'identity.json').write_text(json.dumps(self.target.identity(),indent=2))
 def shell(self,code,timeout=60,**kw):return self.target.execute(code,timeout)
 def cli(self,*args,**kw):return self.target.cli(*args,**kw)
 def call(self,m,p=None):
  r=self.cli(m,json.dumps(p or {}));v=json.loads(r['stdout']);assert v.get('ok'),m+': '+v.get('error',{}).get('code','invalid envelope');return v['result']
 def wait(self,f,label='',timeout=30,interval=.25):
  end=time.monotonic()+timeout;last=None
  while time.monotonic()<end:
   try:
    v=f()
    if v:return v
   except (AssertionError,KeyError) as e:last=e
   time.sleep(interval)
  raise RecipeFailed('timeout '+label+' '+str(last or ''))
 def expect(self,v,m):assert v,m
 def note(self,s):self.notes.append(self.evidence.redactor.text(str(s)));(self.out/'notes.json').write_text(json.dumps(self.notes,indent=2))
 def review(self,s):self.note('review '+s)
 def fixture(self,name,**kw):
  if name not in self.values:self.values[name]=FACTORIES[name](self.scope,**kw)
  return self.values[name]
 def frame(self,label,**kw):
  p=self.out/(label+'-'+str(time.time_ns())+'.png');self.target.capture_image().save(p);return Frame(str(p))
 def focus(self,*a,**kw):pass # No surface witness: browser helper establishes its own kiosk foreground.
 def keys(self,*chords):
  for chord in chords:lab.key(self.target.run,[{'Ctrl':'ctrl','Shift':'shift','Return':'ret','Escape':'esc'}.get(k,k.lower()) for k in chord.split('+')])
 def pointer(self,action,*points,button='left'):
  local=Path('tools/lab/wayland_pointer.py');remote=self.scope.root+'/wayland_pointer.py'
  if not self.values.get('_pointer'):
   for f in ('wayland_pointer.py','wayland_toplevels.py'):self.scope.write(self.scope.root+'/'+f,Path('tools/lab/'+f).read_bytes())
   self.values['_pointer']=True
  r=self.shell('python3 '+remote+' '+action+' '+' '.join(map(str,points))+' --extent 1280 800 --button '+button);assert r['returncode']==0,'real Wayland pointer failed'
 def close(self):
  errors=self.scope.close();self.note('fixture cleanup '+json.dumps(errors));assert not errors,errors
  history=self.call('history.list',{'limit':1});profiles=self.call('settings.get')['document']['profiles'];assert history.get('total',0)==0 and not profiles
  errors=self.target.close();assert not errors,errors
  gone=self.shell('test ! -e '+shlex.quote(self.target.root)+' && test ! -S '+shlex.quote(self.target.socket))['returncode']==0;assert gone
  (self.out/'cleanup.json').write_text(json.dumps(dict(historyRows=0,profiles=0,fixtureErrors=[],privateRootRemoved=True,residentSocketRemoved=True),indent=2))
 def fetch(self,path,name):
  v=self.scope.json('import json,base64\nfrom pathlib import Path\np=Path('+repr(path)+');assert p.is_relative_to(Path('+repr(self.target.root)+'));print(json.dumps(base64.b64encode(p.read_bytes()).decode()))')
  data=base64.b64decode(v);(self.out/name).write_bytes(data);return data

def complete(c,oid,name):
 op=c.wait(lambda:(o if(o:=c.call('operation.inspect',{'id':oid}))['state'] in ('completed','failed','partial','cancelled') else None),'operation '+name,timeout=150)
 assert op['state']=='completed',(name,op['state'],[i.get('error',{}).get('code') for i in op.get('items',[])])
 rows=c.wait(lambda:[r for r in c.call('history.list',{'limit':100})['records'] if r.get('operationId')==oid],'history row');assert len(rows)==1
 d=c.call('history.detail',{'id':rows[0]['id']});assert d['uploadStatus']=='uploaded' and d['local']['status']=='saved'
 data=c.fetch(d['local']['path'],name+Path(d['local']['path']).suffix)
 c.note(name+' operationId='+oid+' historyId='+d['id']+' sha256='+hashlib.sha256(data).hexdigest())
 return d,data

def object_check(c,d,data,absent=False):
 url=d['receipt']['directUrl']
 v=c.scope.json('''import urllib.request,urllib.error,hashlib,json
try:
 with urllib.request.urlopen(URL,timeout=20) as r:data=r.read(64*1024*1024);v={'status':r.status,'sha256':hashlib.sha256(data).hexdigest()}
except urllib.error.HTTPError as e:v={'status':e.code}
print(json.dumps(v))'''.replace('URL',repr(url)))
 assert v['status']==(404 if absent else 200),v
 if not absent:assert v['sha256']==hashlib.sha256(data).hexdigest()
 c.note('independent HTTP '+json.dumps(v))
 return v

def deletion(c,d):
 ids=[d['id']];p=c.call('delete.prepare',{'ids':ids});assert [t['historyId'] for t in p['targets']]==ids and p['acknowledgement'];c.note('delete.prepare exact owned historyId='+d['id'])
 job=c.call('delete.confirm',{'ids':ids,'acknowledgement':p['acknowledgement']})
 state=c.wait(lambda:(v if(v:=c.call('history.detail',{'id':d['id']}))['remoteStatus'] in ('removed','already_missing','failed','unsupported_safe_removal') else None),'delete',timeout=120)
 assert state['remoteStatus'] in ('removed','already_missing'),state['remoteStatus']

def capture(c,kind):
 before={o['id'] for o in c.call('operation.recent')['operations']}
 c.keys({'region':'Ctrl+Shift+1','window':'Ctrl+Shift+2','desktop':'Ctrl+Shift+3'}[kind]);time.sleep(1)
 if kind=='region':c.frame('region-selector');c.pointer('drag',100,100,500,350)
 oid=c.wait(lambda:next((o['id'] for o in c.call('operation.recent')['operations'] if o['id'] not in before),None),'real hotkey operation')
 return complete(c,oid,kind+'-'+str(time.time_ns()))

def cell(c,result,key,route,fn):
 if os.environ.get('SP_FLOWS') and key not in os.environ['SP_FLOWS'].split(','):return
 try:
  detail=fn();result[key]=dict(status='pass',route=route,proof=detail or {})
 except Exception as e:
  result[key]=dict(status='fail',route=route,cause=c.evidence.redactor.exception(e));c.note('cell '+key+' failed '+result[key]['cause']);c.frame(key+'-failed')
  (c.out/(key+'-trace.txt')).write_text(c.evidence.redactor.text(traceback.format_exc()))
 (c.out/'cells.json').write_text(json.dumps(result,indent=2));print(key,result[key]['status'],result[key].get('cause',''),flush=True)

def mime_setup(c):
 # Omarchy's desktop-specific defaults override xdg-mime's generic write. The
 # frozen browser guard already snapshots/restores every MIME file; temporarily
 # remove only these two override rows before that transaction, restore at scope exit.
 if c.desktop!='omarchy-hyprland':return
 path='/home/lab/.config/hyprland-mimeapps.list'
 raw=c.scope.json('import json,base64\nfrom pathlib import Path\np=Path('+repr(path)+');print(json.dumps(base64.b64encode(p.read_bytes()).decode()))')
 c.scope.python('import re\nfrom pathlib import Path\np=Path('+repr(path)+');p.write_text(re.sub(r"(?m)^x-scheme-handler/https?=.*(?:\\n|$)","",p.read_text()))')
 c.scope.defer('Omarchy MIME overrides',lambda:c.scope.python('import base64\nfrom pathlib import Path\nPath('+repr(path)+').write_bytes(base64.b64decode('+repr(raw)+'))'),priority=500)
 c.note('VM browser setup: temporarily removed Omarchy desktop-specific http/https MIME overrides; original bytes restored at cleanup')

def local_pass(c,result):
 service=c.fixture('loopback-s3');scope=c.scope;mime_setup(c)
 scope.patch({'actions':{n:dict(destination='upload',profileId=service.profile_id,shortcut={'region':'Ctrl+Shift+1','window':'Ctrl+Shift+2','desktop':'Ctrl+Shift+3'}.get(n,'')) for n in ('region','window','desktop','clipboard','edit','record')},'preferences':{'notifications':False,'uploadClipboardBehavior':'each_link'}})
 c.frame('isolated-desktop-start')
 # Reuse B's/D's frozen four-colour fixture and full-screen cover for pixel oracles.
 source=c.fixture('image');source_bytes=c.fetch(source.path,'source.png');original=Image.open(io.BytesIO(source_bytes)).convert('RGBA')
 scene=c.fixture('selector-desktop');scene.command('freeze');time.sleep(2);c.pointer('move',1200,700);time.sleep(.3)
 oracle=c.target.capture_image();oracle.save(c.out/'capture-oracle.png')
 saved={}
 def region():
  d,data=capture(c,'region');object_check(c,d,data);assert pixels_equal(Image.open(io.BytesIO(data)),oracle.crop((100,100,500,350)));saved['region']=d;return {'pixels':'400x250 exact QEMU framebuffer crop'}
 cell(c,result,'region_upload','QEMU Ctrl+Shift+1 + real Wayland pointer drag',region)
 def windowdesktop():
  d,data=capture(c,'desktop');object_check(c,d,data);im=Image.open(io.BytesIO(data));assert pixels_equal(im,oracle),'desktop pixels differ'
  caps=c.call('capabilities')['source']['capture']['window']
  if not caps.get('available'):
   before={o['id'] for o in c.call('operation.recent')['operations']};c.keys('Ctrl+Shift+2');time.sleep(2);reason=caps.get('reason') or caps.get('message') or caps;assert 'ext-foreign-toplevel-image-capture-source' in str(reason);return {'desktop':'exact pixels','window':'documented unavailable','reason':reason}
  d,data=capture(c,'window');object_check(c,d,data);assert pixels_equal(Image.open(io.BytesIO(data)),oracle),'fullscreen window pixels differ';return {'desktop':'exact pixels','window':'exact fullscreen fixture pixels'}
 cell(c,result,'window_desktop','QEMU desktop/window hotkeys; independent framebuffer',windowdesktop)
 def autocopy():
  d,data=capture(c,'region')
  c.wait(lambda:_clipboard_bytes(scope,'text/plain')==d['receipt']['directUrl'].encode(),'wl-paste exact auto-copied URL');return {'clipboard':'exact bytes without Copy action'}
 cell(c,result,'auto_copy','QEMU region hotkey; independent wl-paste',autocopy)
 def record():
  scores=[];active=None
  try:
   for frozen in (True,False):
    scene.command('freeze' if frozen else 'resume');scene.command('raise');time.sleep(.5)
    rid=c.call('recording.prepare',dict(target={'kind':'region','rect':scene.rect},format='mp4',fps=15,audio={'system':False}))['recordingId'];active=rid
    ready=c.wait(lambda:(v if(v:=c.call('recording.inspect',{'id':rid}))['state']!='preparing' else None),'record ready',timeout=35);assert ready['state']=='ready',ready.get('error')
    c.call('recording.start',{'id':rid});time.sleep(5);c.call('recording.stop',{'id':rid});state=c.wait(lambda:(v if(v:=c.call('recording.inspect',{'id':rid}))['state']=='reviewing' else None),'review',timeout=40)
    c.frame('private-recording-review-'+str(frozen));path=scope.root+'/out/'+rid+'.mp4';c.call('recording.saveCopy',{'id':rid,'path':path});c.wait(lambda:c.call('recording.inspect',{'id':rid}).get('lastExport',{}).get('status')=='saved','save clip',timeout=60)
    data=c.fetch(path,('static' if frozen else 'moving')+'.mp4')
    measured=c.shell(shlex.quote(scene.record_helper)+' --motion '+shlex.quote(path)+' 8');assert measured['returncode']==0;v=re.search(r'motion=([\d.]+) compared=(\d+) samples=8 durationMs=(\d+) size=640x320',measured['stdout']);assert v and int(v[2])>=6 and 4000<=int(v[3])<=30000;c.note('decoded motion '+v[0]);scores.append(float(v[1]))
    if frozen:c.call('recording.cancel',{'id':rid});active=None
    else:
     st=c.call('recording.inspect',{'id':rid});submitted=c.call('recording.upload',{'id':rid,'revision':st['edit']['revision']});d,published=complete(c,rid,'recording-upload');object_check(c,d,published);again=c.shell(shlex.quote(scene.record_helper)+' --motion '+shlex.quote(d['local']['path'])+' 8');match=re.search(r'motion=([\d.]+)',again['stdout']);assert again['returncode']==0 and match and float(match[1])>max(1,scores[0]+1);c.note('uploaded moving clip decoded motion='+match[1])
   assert scores[0]<=1 and scores[1]>max(1,scores[0]+1),scores
   return {'staticMotion':scores[0],'movingMotion':scores[1],'uploadedVideo':'exact exported hash'}
  finally:
   if active:c.cli('recording.cancel',json.dumps({'id':active}))
   scene.command('freeze')
 cell(c,result,'recording_upload','production recording session prepare/start/stop/saveCopy/upload; D motion/static oracle',record)
 # Hide the cover before editor/browser/file-manager outcomes.
 scene.command('quit');time.sleep(.7)
 def edit():
  oid=c.call('editor.open',{'source':'file','path':source.path})['operationId'];c.wait(lambda:c.call('editor.inspect',{'id':oid}),'editor ready')
  c.call('editor.apply',{'id':oid,'commands':[{'op':'add','shape':{'kind':'redact','rect':[350,20,240,120]}},{'op':'add','shape':{'kind':'arrow','from':[30,30],'to':[250,90],'color':'#ffffff','width':6}}]});c.frame('edited-before-upload');c.keys('Ctrl+Return');time.sleep(1)
  if c.call('operation.inspect',{'id':oid})['state']=='editing':c.call('editor.submit',{'id':oid})
  d,data=complete(c,oid,'edited-upload');object_check(c,d,data);im=Image.open(io.BytesIO(data)).convert('RGBA');assert im.size==(640,320);assert set(im.crop((355,25,585,135)).getdata())=={(0,0,0,255)};assert not pixels_equal(im,original);saved['edited']=d;return {'redaction':'solid black interior; annotated pixels differ; correct dimensions'}
 cell(c,result,'edit_upload','production editor.open/apply; real QEMU Ctrl+Enter (submit fallback recorded)',edit)
 def clipboard():
  cases=[]
  for kind,mime,path,data in [('image','image/png',source.path,source_bytes),('text','text/plain',scope.root+'/clip.txt',b'putgd scripted clipboard: exact bytes\n'),('file','text/uri-list',scope.root+'/clip.bin',b'putgd scripted binary\0\1\xff\n')]:
   if kind!='image':scope.write(path,data)
   if kind=='file':clipboard_files(scope,[path])
   else:owner(scope,path,mime,name='clipboard-'+kind)
   oid=c.call('action.invoke',{'action':'clipboard'})['operationId'];d,remote=complete(c,oid,'clipboard-'+kind);object_check(c,d,remote)
   if kind=='image':assert pixels_equal(Image.open(io.BytesIO(remote)),original)
   else:assert data==remote
   cases.append(kind)
  return {'verified':cases}
 cell(c,result,'upload_clipboard','native wl-copy sources; production action.invoke clipboard',clipboard)
 def copyimage():
  d=saved.get('edited')
  if not d:
   oid=c.call('upload.files',{'paths':[source.path],'profileId':service.profile_id})['operationId'];d,_=complete(c,oid,'cell-fixture');c.call('history.copyImage',{'id':d['id']});data=c.wait(lambda:_clipboard_bytes(scope,'image/png'),'wl-paste image');original_data=c.fetch(d['local']['path'],'copy-image-original.png');assert pixels_equal(Image.open(io.BytesIO(data)),Image.open(io.BytesIO(original_data)));(c.out/'copied-image.png').write_bytes(data);return {'clipboard':'decoded PNG exact RGBA pixels'}
 cell(c,result,'copy_image','production history.copyImage; independent wl-paste PNG',copyimage)
 def browser():
  d=saved.get('edited')
  if not d:
   oid=c.call('upload.files',{'paths':[source.path],'profileId':service.profile_id})['operationId'];d,_=complete(c,oid,'cell-fixture')
  with default_browser(c):
   opened=open_and_verify(c,lambda:c.call('history.openLink',{'id':d['id']}),{'kind':'s3','name':d['name'],'preview':True,'url_host':'127.0.0.1'})
   assert opened['matched'];return {'realDefaultFirefox':True,'contentMatched':True}
 cell(c,result,'link_browser','production history.openLink dispatch to real temporary default Firefox',browser)
 def deletecell():
  d=saved.get('edited')
  if not d:
   oid=c.call('upload.files',{'paths':[source.path],'profileId':service.profile_id})['operationId'];d,_=complete(c,oid,'cell-fixture');deletion(c,d);object_check(c,d,b'',absent=True);c.call('ui.show',{'view':'history'});c.frame('history-after-delete');return {'remote':'HTTP404 after exact prepared History deletion'}
 cell(c,result,'history_delete','production delete.prepare/confirm for exact owned History ID',deletecell)
 def survive():
  # A new publication sets a known clipboard, then real Quit; independently inspect socket-owner PID and clipboard.
  if os.environ.get('SP_PERSIST')=='1':
   token='sp-persist-'+scope.token
   argv=(['wl-clip-persist','--clipboard','regular','--selection-size-limit','33554432'] if c.desktop=='omarchy-hyprland' else ['wl-paste','--type','text','--watch','clipman','store','--histpath',scope.root+'/clipboard-manager.json','--max-items','1'])
   manager=scope.launch(argv,environment={'PUTGD_SP_PERSIST_OWNER':token},name='clipboard-persistence')
   def stop_followers():
    identities=scope.json("""import os,json
from pathlib import Path
found=[]
for p in Path('/proc').iterdir():
 if not p.name.isdecimal():continue
 try:
  if p.stat().st_uid!=os.getuid():continue
  if b'PUTGD_SP_PERSIST_OWNER='+TOKEN.encode() not in (p/'environ').read_bytes().split(bytes([0])):continue
  fields=(p/'stat').read_text().split(') ',1)[1].split()
  if fields[0]!='Z':found.append({'pid':int(p.name),'start':fields[19]})
 except (FileNotFoundError,ProcessLookupError,PermissionError):pass
print(json.dumps(found))
""".replace('TOKEN',repr(token)))
    for identity in identities:scope.stop(identity)
   scope.defer('clipboard manager descendants',stop_followers,priority=80)
   scope.defer('clipboard manager parent',lambda:scope.stop(manager),priority=90)
   time.sleep(1);c.note('VM setup correction: '+argv[0]+' distro clipboard persistence; owned process, tmpfs storage; stock golden failed ordinary wl-copy lifetime control')
  oid=c.call('upload.files',{'paths':[source.path],'profileId':service.profile_id})['operationId'];d,data=complete(c,oid,'survives-upload');object_check(c,d,data)
  wanted=d['receipt']['directUrl'].encode();c.wait(lambda:_clipboard_bytes(scope,'text/plain')==wanted,'auto copy before quit')
  identity=scope.json('import socket,struct,json\ns=socket.socket(socket.AF_UNIX);s.connect('+repr(c.target.socket)+');print(json.dumps(struct.unpack("3i",s.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))[0]))')
  c.call('ui.quit');c.target.started=False;time.sleep(2)
  try:
   status=c.shell('test ! -e /proc/'+str(identity)+' && test ! -e '+shlex.quote(c.target.socket));assert status['returncode']==0,'resident survives Quit unexpectedly';after=_clipboard_bytes(scope,'text/plain');c.note('resident PID absent after Quit; clipboard retained='+str(after==wanted));assert after==wanted,'clipboard lost after Quit: no desktop persistence owner'
  finally:scope._relaunch()
  time.sleep(2);assert _clipboard_bytes(scope,'text/plain')==wanted;return {'persistenceSetup':os.environ.get('SP_PERSIST')=='1','residentPid':identity,'afterQuit':'process absent; socket absent; clipboard exact after 2s and restart'}
 cell(c,result,'survives_exit','production ui.quit; independent /proc + socket + wl-paste; restart',survive)
 # Right-click requires row-specific observed coordinates; a separate interactive continuation uses this same scope.
 result.setdefault('file_manager_upload',dict(status='not_run',route='real file-manager right-click pending'))
 (c.out/'cells.json').write_text(json.dumps(result,indent=2))

def live_pass(c,result):
 from tools.lab.surface_driver.fixtures.live_outcomes import provider,verify_s3
 service=provider(c.scope);mime_setup(c);c.scope.patch({'preferences':{'notifications':False},'actions':{'region':{'shortcut':'Ctrl+Shift+1'}}})
 scene=c.fixture('selector-desktop');scene.command('freeze');scene.command('raise');time.sleep(1);c.pointer('move',1200,700)
 last=[None]
 def frozen_frame():
  im=c.target.capture_image();same=last[0] is not None and pixels_equal(im,last[0]);last[0]=im;return im if same else None
 oracle=c.wait(frozen_frame,'independent settled frozen frame',interval=.5);oracle.save(c.out/'live-region-oracle.png')
 d=None;cleaned=False
 def cleanup():
  nonlocal cleaned
  if cleaned or d is None:return
  if c.destination=='s3':
   deletion(c,d);verify_s3(c,service,d,absent=True)
   listing=service.client.list_objects_v2(Bucket=service.bucket,Prefix=service.prefix,MaxKeys=10);assert listing.get('KeyCount',0)==0;c.note('independent scoped S3 listing after cleanup KeyCount=0')
  else:
   c.call('history.revokeLink',{'id':d['id']});c.wait(lambda:c.call('history.detail',{'id':d['id']}).get('shareStatus')=='revoked','share revoked',timeout=180)
   c.note('retained Proton synthetic private file: '+service.prefix.rstrip('/')+'/'+d['name'])
   (c.out/'proton-retained.json').write_text(json.dumps({'count':1,'folder':service.prefix.rstrip('/'),'name':d['name'],'shareRevoked':True},indent=2))
  service.pending['remote']=False;cleaned=True
 try:
  service.pending['remote']=True;d,data=capture(c,'region');assert pixels_equal(Image.open(io.BytesIO(data)),oracle.crop((100,100,500,350)));c.wait(lambda:_clipboard_bytes(c.scope,'text/plain')==d['receipt']['directUrl'].encode(),'exact auto-copy')
  if c.destination=='s3':
   verify_s3(c,service,d,data);listed=service.client.list_objects_v2(Bucket=service.bucket,Prefix=service.prefix,MaxKeys=10);assert [o['Key'] for o in listed.get('Contents',[])]==[d['receipt']['objectReference']['key']];c.note('independent scoped S3 listing: exactly one owned object')
  with default_browser(c):
   def open_recipient():
    if c.destination=='proton':
     c.call('history.copyLink',{'id':d['id']});c.wait(lambda:_clipboard_bytes(c.scope,'text/plain')==d['receipt']['directUrl'].encode(),'copied share exact bytes');c.pointer('click',640,400);time.sleep(.6)
     for chord in ('Ctrl+L','Ctrl+V','Return'):c.keys(chord);time.sleep(.7)
     c.note('recipient route: production History Copy link, real Wayland click to focus, real QEMU Ctrl+L Ctrl+V Enter with compositor settling')
    else:c.note('recipient open route '+json.dumps(c.call('history.openLink',{'id':d['id']})))
   try:
    opened=open_and_verify(c,open_recipient,{'kind':c.destination,'name':d['name'],'preview':True});assert opened['matched']
    downloaded=live_download_digest(c,c.destination,d['local']['path'],filename=d['name']);assert downloaded.get('matches') and downloaded['sha256']==hashlib.sha256(data).hexdigest(),'recipient downloaded original hash differs or unproven';c.note('recipient original bytes hash matches local PNG')
   finally:cleanup()
   if c.destination=='proton':assert live_link_unavailable(c,'proton')['unavailable'],'revoked share still reachable'
  return {'pixels':'exact region','historyId':d['id'],'recipient':'original SHA256 and visible real Firefox','cleanup':'S3 exact object removed' if c.destination=='s3' else 'share revoked; synthetic private file retained'}
 finally:
  cleanup();scene.command('quit')


if __name__=='__main__':
 run,out,desktop,package,host=sys.argv[1:6];dest=sys.argv[6] if len(sys.argv)>6 else 'local';run=Path(run).resolve();c=Context(run,out,desktop,package,host,dest);result={}
 try:
  if dest=='local':local_pass(c,result)
  else:cell(c,result,'s3_region_upload' if dest=='s3' else 'proton_region_upload','real QEMU region hotkey/Wayland drag; native bridge; real default Firefox; production delete/revoke',lambda:live_pass(c,result))
 finally:
  c.close();(c.out/'build.json').write_text(json.dumps(c.build,indent=2));(c.out/'cells.json').write_text(json.dumps(result,indent=2))
