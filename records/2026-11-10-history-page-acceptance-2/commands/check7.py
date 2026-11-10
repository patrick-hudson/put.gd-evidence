from session_base import *
import urllib.request,contextlib
import pyatspi,probe
root=Path('/tmp/hp2c');root.mkdir(mode=0o700)
native,_=session_environment();os.environ.update(native)
base=Path.home()/'putgd-lab/h1396-ci'
@contextlib.contextmanager
def clipboard(label):
 d=root/('clip-'+label);d.mkdir(mode=0o700)
 p=subprocess.Popen(['python3',str(base/'p2-clipboard.py'),str(d)],env=native,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 identity=json.loads(p.stdout.readline());ready=json.loads(p.stdout.readline());assert ready.get('ready'),ready
 print(json.dumps({'clipboard_before':label,'metadata':ready,'pid':identity['identity']['pid']}),flush=True)
 try:yield
 finally:
  p.stdin.close();p.wait(timeout=10);assert p.returncode==0;assert (d/'clipboard-state').read_text()=='restored';print('clipboard restored after '+label,flush=True)
env=native.copy()
for key,sub in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_STATE_HOME','state'),('XDG_CACHE_HOME','cache'),('XDG_RUNTIME_DIR','runtime')]:
 (root/sub).mkdir(mode=0o700);env[key]=str(root/sub)
(root/'files').mkdir(mode=0o700);(root/'config/putgd').mkdir(mode=0o700);DOC['archive']['root']=str(root/'files');(root/'config/putgd/config.json').write_text(json.dumps(DOC))
assert len(str(root/'runtime/putgd/session.sock').encode())<=107
env.update(QT_LINUX_ACCESSIBILITY_ALWAYS_ON='1',QT_ACCESSIBILITY='1')
resident=None;server=None;ids=[];links=[];names=[];results={};log=[]
def call(m,p={}):
 q=subprocess.run(['putgd-cli',m,json.dumps(p)],env=env,capture_output=True,text=True,timeout=40);v=json.loads(q.stdout)
 # Deletion references stay in memory; keep only safe readbacks for history and prepare.
 safe=v
 if m=='history.list':
  safe={'ok':v.get('ok'),'result':{'records':[{k:r.get(k) for k in ('id','operationId','name')} for r in v.get('result',{}).get('records',[])]}}
 if m in ('history.detail','delete.prepare','delete.inspect','delete.confirm','operation.inspect'):
  z=v.get('result',{});safe={'ok':v.get('ok'),'error':v.get('error'),'result':{k:z[k] for k in ('id','state','remoteStatus','uploadStatus','localStatus','name') if k in z}}
 log.append({'method':m,'params':{k:v for k,v in p.items() if k!='acknowledgement'},'reply':safe});(root/'commands.json').write_text(json.dumps(log,indent=2));assert v['ok'],v.get('error');return v['result']
def st():
 for _ in range(80):
  s=call('ui.history',{'action':'inspect'})
  if not s.get('busy') and not s.get('page',{}).get('loading'):return s
  time.sleep(.1)
 raise RuntimeError('history busy')
def act(a,**kw):
 r=call('ui.history',dict(action=a,**kw));st();return r

def window():
 os.environ.update(env)
 ws=probe.x11_windows({'title':'put.gd','owned':True});assert len(ws)==1 and ws[0]['states']['active'];w=ws[0];assert Path('/proc/'+str(w['pid'])+'/exe').resolve().name=='putgd-ui';return w

def shot(n,dialog=False):
 if dialog:
  w=probe.x11_windows({'title':'Delete from destination','owned':True});assert len(w)==1;w=w[0];assert Path('/proc/'+str(w['pid'])+'/exe').resolve().name=='putgd-ui'
 else:w=window()
 subprocess.run(['import','-window',w['window_id'],str(root/(n+'.png'))],env=env,check=True)
 print('saved owned app XID',n,w['window_id'],flush=True)
def click_name(name):
 window();nodes=[]
 def walk(n):
  if n.name==name and n.getState().contains(pyatspi.STATE_SHOWING):nodes.append(n)
  for c in n:walk(c)
 for a in pyatspi.Registry.getDesktop(0):
  if Path('/proc/'+str(a.get_process_id())+'/exe').resolve().name=='putgd-ui':walk(a)
 assert len(nodes)==1,(name,len(nodes));r=nodes[0].queryComponent().getExtents(pyatspi.DESKTOP_COORDS)
 subprocess.run(['xdotool','mousemove',str(r.x+r.width//2),str(r.y+r.height//2),'click','1'],env=env,check=True)
def cliptext():return subprocess.check_output(['xclip','-selection','clipboard','-o'],env=native).decode()
def control(path,value=None):
 req=urllib.request.Request(endpoint+path,data=json.dumps(value).encode() if value is not None else None,headers={'Content-Type':'application/json'});return json.load(urllib.request.urlopen(req,timeout=5))
try:
 server=subprocess.Popen(['python3',str(base/'p2-http-server.py')],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True);port=int(server.stdout.readline());endpoint='http://127.0.0.1:'+str(port);control('/__reset',{'auth':'none'})
 with clipboard('resident-start'):
  with (root/'app.log').open('w') as f:resident=subprocess.Popen(['putgd','--background'],env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=f,start_new_session=True)
  for _ in range(100):
   if (root/'runtime/putgd/session.sock').exists():break
   time.sleep(.1)
 call('diagnostics');call('capabilities');cur=call('settings.get')
 uploader={'Name':'Synthetic token-free loopback','RequestMethod':'POST','RequestURL':endpoint+'/upload/json','Body':'MultipartFormData','FileFormName':'file','URL':'{json:files[0].url}','DeletionURL':'{json:files[0].delete}'}
 (root/'loopback.sxcu').write_text(json.dumps(uploader))
 imported=call('settings.importUploader',{'path':str(root/'loopback.sxcu'),'expectedRevision':cur['metadata']['observedRevision'],'profileId':'history-p2-loopback','credentialMode':'session'})
 pid=imported['profileId'];cur=call('settings.get');call('settings.patch',{'expectedRevision':cur['metadata']['observedRevision'],'patch':{'actions':{'edit':{'destination':'upload','profileId':pid,'shortcut':''}}}})
 from PIL import Image
 for i in range(3):
  name='Synthetic-check7-%d.png'%(i+1);path=root/name;Image.new('RGB',(64,64),(30+i*30,100,190)).save(path)
  oid=call('editor.open',{'source':'file','path':str(path)})['operationId'];time.sleep(.3)
  with clipboard('submit-'+str(i)):
   call('editor.submit',{'id':oid})
   for _ in range(100):
    op=call('operation.inspect',{'id':oid})
    if op['state'] in ('completed','failed','partial'):break
    time.sleep(.1)
   assert op['state']=='completed'
  rows=call('history.list',{'limit':20})['records'];row=next(r for r in rows if r.get('operationId')==oid);detail=call('history.detail',{'id':row['id']});ids.append(row['id']);names.append(detail['name']);links.append(detail['receipt']['directUrl'])
 call('ui.show',{'view':'history'});st();act('closeDetails');act('select',ids=ids);s=st();assert s['selectedRows']==3 and len(s['eligibleLinkIds'])==3 and len(s['deletableIds'])==3;shot('07-three-selected');results['three-selected']=True;results['selection-note']=s.get('selectionSummary')
 with clipboard('copy-method'):
  act('copySelectedLinks');time.sleep(.3);actual=cliptext().splitlines();assert len(actual)==3 and set(actual)==set(links);results['copy-method']=True
 with clipboard('copy-button'):
  click_name('Copy 3 links');time.sleep(.3);actual=cliptext().splitlines();assert len(actual)==3 and set(actual)==set(links);results['copy-button']=True
 act('deleteSelected');s=st();assert s['deletionConfirmationOpen'];
 def dialog_names(n):
  found=[n.name] if n.name in names else []
  for c in n:found+=dialog_names(c)
  return found
 actual=[]
 for a in pyatspi.Registry.getDesktop(0):
  if Path('/proc/'+str(a.get_process_id())+'/exe').resolve().name=='putgd-ui':actual+=dialog_names(a)
 assert set(actual)==set(names),(actual,names);shot('07-confirmation',dialog=True);results['exact-confirmation-names']=names
 act('cancelConfirmation');assert not st()['deletionConfirmationOpen'];assert all(call('history.detail',{'id':i})['remoteStatus']=='present' for i in ids);results['cancel-keeps-all-present']=True
 act('select',ids=ids[:2]);assert st()['selectedRows']==2;shot('07-two-selected');act('select',ids=ids);assert st()['selectedRows']==3;results['selection-count-updates']=True
except Exception as e:results['stopped']=repr(e);print('ERROR',repr(e),flush=True)
finally:
 try:
  if (root/'runtime/putgd/session.sock').exists():
   try:act('cancelConfirmation')
   except Exception:pass
   # Single-item deletion only: review exact IDs/effect before each confirmation.
   for hid in ids:
    d=call('history.detail',{'id':hid})
    if d.get('remoteStatus')!='present':continue
    prepared=call('delete.prepare',{'ids':[hid]});assert [t['historyId'] for t in prepared['targets']]==[hid];assert len(prepared['targets'])==1
    print('single-item cleanup prepared',hid,prepared['targets'][0].get('effect'),flush=True)
    job=call('delete.confirm',{'ids':[hid],'acknowledgement':prepared['acknowledgement']})
    did=job.get('deleteOperationId') or job.get('id');assert did,job
    for _ in range(100):
     ds=call('delete.inspect',{'id':did})
     if ds['state'] not in ('running','queued','pending'):break
     time.sleep(.1)
    assert call('history.detail',{'id':hid})['remoteStatus']=='removed'
   state=control('/__state');results['remaining_objects']=sum(not x.get('deleted') for x in state['files'].values());assert results['remaining_objects']==0
   call('ui.quit');resident.wait(timeout=15)
 except Exception as e:results['cleanup_error']=repr(e)
 try:
  if (root/'runtime/putgd/session.sock').exists():call('ui.quit')
  if resident:resident.wait(timeout=15)
 except Exception as e:results['quit_error']=repr(e)
 if server:server.terminate();server.wait(timeout=10)
 (root/'results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results),flush=True)
