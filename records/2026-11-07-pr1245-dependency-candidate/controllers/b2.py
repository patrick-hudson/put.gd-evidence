import os,sys,pathlib,subprocess,json,time,uuid,hashlib
sys.path.insert(0,str(pathlib.Path.home()/'nd'))
from tools.lab import provision_live_credentials as bridge
from tools.lab.surface_driver.fixtures.live_outcomes import key_set_two
os.umask(0o077)
p=pathlib.Path('/tmp/b21245');p.mkdir();runtime=p/'rt';runtime.mkdir()
app=pathlib.Path.home()/'c1245b/debian/app/usr';bin=app/'bin'
env=dict(os.environ,QT_QPA_PLATFORM='offscreen',XDG_RUNTIME_DIR=str(runtime),XDG_CONFIG_HOME=str(p/'config'),XDG_STATE_HOME=str(p/'state'),XDG_CACHE_HOME=str(p/'cache'),DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/1000/bus',LD_LIBRARY_PATH=str(app/'lib/x86_64-linux-gnu')+':'+str(app/'lib'))
socket=str(runtime/'putgd/session.sock');assert len(socket.encode())<=107
out=pathlib.Path.home()/'c1245b/b2';out.mkdir()
(out/'socket.json').write_text(json.dumps({'path':socket,'utf8Bytes':len(socket.encode())}))
log=(out/'resident.log').open('x');proc=subprocess.Popen([str(bin/'putgd'),'--background'],env=env,stdout=log,stderr=log)
(out/'pid.json').write_text(json.dumps({'pid':proc.pid,'app':str(bin/'putgd')}))
def cli(method,params={}):
 r=subprocess.run([str(bin/'putgd-cli'),'--socket',socket,method,json.dumps(params)],env=env,capture_output=True,text=True,timeout=150)
 try:d=json.loads(r.stdout)
 except:raise RuntimeError('cli_bad_reply_'+method)
 if not d.get('ok'):raise RuntimeError('cli_'+method+'_'+str((d.get('error') or {}).get('code')))
 return d['result']
def wait(method,params,done,seconds=600):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  d=cli(method,params)
  if done(d):return d
  time.sleep(1)
 raise RuntimeError('timeout_'+method)
reference='putgd-lab-'+str(uuid.uuid4());broker=str(pathlib.Path.home()/'putgd-lab/proton/bridge/putgd-lab-secret-bridge')
result={'kind':'real production resident multipart upload; offscreen, not desktop acceptance','bytes':1024*1024,'steps':[]}
def save(): (out/'result.json').write_text(json.dumps(result,indent=2))
try:
 for i in range(30):
  if pathlib.Path(socket).exists():break
  time.sleep(1)
 cli('capabilities')
 text=bridge.read_private_credentials(pathlib.Path.home()/'Documents/creds.txt')
 import re,urllib.request,base64
 def fields(text):
  return {re.sub('[^a-z]','',a.lower()):b.strip() for a,b in (line.split(':',1) for line in text.splitlines() if ':' in line)}
 prefix='acceptance/pr1245/'+uuid.uuid4().hex+'/'
 block=re.split(r'(?im)^Backblaze[^\n]*\n',text)[-1];block=re.split(r'(?im)^Cloudflare[^\n]*\n',block)[0];f=fields(block)
 keys=dict(accessKey=f['keyid'],secretKey=f['applicationkey'],sessionToken='')
 req=urllib.request.Request('https://api.backblazeb2.com/b2api/v3/b2_authorize_account',headers={'Authorization':'Basic '+base64.b64encode((keys['accessKey']+':'+keys['secretKey']).encode()).decode()})
 with urllib.request.urlopen(req,timeout=30) as response: auth=json.load(response)
 storage=auth['apiInfo']['storageApi'];allowed=storage.get('allowed',storage);buckets=allowed.get('buckets',[])
 if not buckets and allowed.get('bucketName'):buckets=[{'name':allowed['bucketName']}]
 if not buckets:
  req=urllib.request.Request(storage['apiUrl']+'/b2api/v3/b2_list_buckets',data=json.dumps({'accountId':auth['accountId']}).encode(),headers={'Authorization':auth['authorizationToken'],'Content-Type':'application/json'})
  with urllib.request.urlopen(req,timeout=30) as response:buckets=[{'name':b['bucketName']} for b in json.load(response)['buckets']]
 choices=[b['name'] for b in buckets];assert len(choices)==1,'ambiguous_authorized_bucket'
 bucket=choices[0]
 profile=dict(id='multipart1245',label='PR1245 B2 synthetic',provider='backblaze-b2',credentials={'mode':'keychain','reference':reference},settings=dict(apiUrl='https://api.backblazeb2.com',bucket=bucket,objectPrefix=prefix,linkMode='public',linkValidityDays=7,publicUrlBase=None,connectTimeoutMs=10000,requestTimeoutMs=600000))
 os.environ['DBUS_SESSION_BUS_ADDRESS']=env['DBUS_SESSION_BUS_ADDRESS']
 bridge.host_call(broker,'s3',dict(op='import',reference=reference,credentials=keys))
 result['credentialReference']=reference;save()
 d=cli('settings.get')
 cli('settings.patch',{'patch':{'profiles':[profile]},'expectedRevision':d['metadata']['acceptedRevision']})
 d=cli('settings.get');j=cli('setup.unlockCredentials',{'profileId':profile['id'],'expectedRevision':d['metadata']['acceptedRevision']})
 v=wait('setup.inspect',{'id':j['setupId']},lambda x:x['state']!='running');assert v['state']=='completed'
 payload=p/'multipart.bin';payload.write_bytes(b'putgd synthetic multipart 1245\n'*(result['bytes']//30)+b'x'*30)
 with payload.open('r+b') as f:f.truncate(result['bytes'])
 sha=hashlib.sha256(payload.read_bytes()).hexdigest();result['sha256']=sha
 
 for attempt in range(45):
  try:
   job=cli('upload.files',{'paths':[str(payload)],'profileId':profile['id']});break
  except RuntimeError as e:
   if str(e)!='cli_upload.files_initializing':raise
   time.sleep(2)
 else:raise RuntimeError('initializing_did_not_settle')
 result['operationId']=job['operationId'];save()
 op=wait('operation.inspect',{'id':job['operationId']},lambda x:x['state'] in ('completed','failed','partial','cancelled'))
 result['operation']=op;save();assert op['state']=='completed'
 records=cli('history.list',{'limit':50})['records'];rec=next(r for r in records if r.get('operationId')==job['operationId']);detail=cli('history.detail',{'id':rec['id']});result['history']=detail;save()
 import urllib.request
 url=detail['receipt']['directUrl']
 with urllib.request.urlopen(url,timeout=90) as response:
  h=hashlib.sha256();n=0
  while block:=response.read(1024*1024):h.update(block);n+=len(block)
 assert n==result['bytes'] and h.hexdigest()==sha
 result['downloadVerified']=True;save()
 ids=[rec['id']];prepared=cli('delete.prepare',{'ids':ids});result['deletePrepared']=prepared;save()
 deletion=cli('delete.confirm',{'ids':ids,'acknowledgement':prepared['acknowledgement']});result['deleteOperation']=deletion;save()
 final=wait('delete.inspect',{'id':deletion['deleteOperationId']},lambda x:x.get('state') in ('completed','failed','partial','cancelled'))
 result['deletion']=final;detail=cli('history.detail',{'id':rec['id']});assert detail['remoteStatus'] in ('removed','already_missing');result['status']='PASS';save()
except Exception as e:
 result['status']='FAIL';result['reason']=str(e) if isinstance(e,(RuntimeError,AssertionError)) else type(e).__name__;save()
finally:
 try:cli('ui.quit')
 except Exception:pass
 try:proc.wait(timeout=20)
 except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=10)
 # Keep credentials if publication cleanup is unconfirmed.
 if not result.get('operationId') or result.get('status')=='PASS':
  try:bridge.host_call(broker,'s3',dict(op='delete',reference=reference));result['credentialRemoved']=True;save()
  except Exception:result['credentialRemoved']=False;save()
print(json.dumps({'status':result['status'],'reason':result.get('reason')}))
