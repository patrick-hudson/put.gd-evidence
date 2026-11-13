#!/usr/bin/env python3
"""Live B2 acceptance: credentials stay in memory on the builder."""
import base64,hashlib,json,os,pathlib,subprocess,sys,time,urllib.request,uuid
import b2_credentials
import record_acceptance as setup
r=setup.r

def flow(self):
 b=r.Build(*self.args.build[0].split('=',1),self.run); rows=[]; profile='sweep-b2-'+uuid.uuid4().hex[:10]; prefix='putgd-sweep-a/'+uuid.uuid4().hex+'/'; original=None; reference='putgd-lab-'+str(uuid.uuid4()); bridge_imported=False
 def row(name,**v): rows.append({'row':name,**v}); (self.run/'b2.json').write_text(json.dumps(rows,indent=2))
 def api(url,payload=None,token=None,basic=None):
  headers={'Authorization':('Basic '+basic) if basic else token,'Content-Type':'application/json'}
  req=urllib.request.Request(url,data=json.dumps(payload).encode() if payload is not None else None,headers=headers)
  with urllib.request.urlopen(req,timeout=45) as reply: return json.load(reply)
 def wait(op):
  observations=[]
  for _ in range(1200):
   v=self.cli(b,'operation.inspect',{'id':op}); observations.append({'state':v['state'],'progress':[x.get('uploadProgress') for x in v['items']]})
   if v['state'] in ('completed','failed','partial','cancelled'): return v,observations
   time.sleep(.1)
  raise RuntimeError('B2 operation deadline')
 def wait_setup(sid):
  for _ in range(1200):
   v=self.cli(b,'setup.inspect',{'id':sid})
   if v['state'] in ('completed','failed'): return v
   time.sleep(.1)
  raise RuntimeError('B2 setup deadline')
 def remove(record):
  selection=[record['id']]; preview=self.cli(b,'delete.prepare',{'ids':selection})
  assert [v['historyId'] for v in preview['targets']]==selection
  assert preview['targets'][0]['receipt']['directUrl']==record['receipt']['directUrl']
  row('delete-preview',displayName=record['name'],preview=preview)
  accepted=self.cli(b,'delete.confirm',{'ids':selection,'acknowledgement':preview['acknowledgement']})
  for _ in range(500):
   v=self.cli(b,'delete.inspect',{'id':accepted['deleteOperationId']})
   if v['state'] not in ('accepted','running'): return v
   time.sleep(.1)
  raise RuntimeError('B2 deletion deadline')
 try:
  key,secret,bucket=b2_credentials.read()
  authorization=api('https://api.backblazeb2.com/b2api/v3/b2_authorize_account',basic=base64.b64encode((key+':'+secret).encode()).decode())
  storage=authorization['apiInfo']['storageApi']; allowed=storage.get('allowed',storage); token=authorization['authorizationToken']; endpoint=storage['apiUrl']
  buckets=api(endpoint+'/b2api/v3/b2_list_buckets',{'accountId':authorization['accountId']},token=token)['buckets']
  eligible=[v for v in buckets if not bucket or v['bucketName']==bucket]
  if len(eligible)!=1: eligible=[v for v in eligible if 'put' in v['bucketName'].lower()]
  assert len(eligible)==1,'B2 test bucket is ambiguous'
  bucket=eligible[0]['bucketName']; bucket_id=eligible[0]['bucketId']; assert eligible[0]['bucketType']=='allPublic','B2 public readback needs a public test bucket'
  def listing():
   v=api(endpoint+'/b2api/v3/b2_list_file_versions',{'bucketId':bucket_id,'prefix':prefix,'maxFileCount':1000},token=token)
   return sorted((x['fileName'],x['fileId'],x['action'],x.get('contentSha1')) for x in v.get('files',[]))
  def unfinished():
   v=api(endpoint+'/b2api/v3/b2_list_unfinished_large_files',{'bucketId':bucket_id,'namePrefix':prefix,'maxFileCount':100},token=token); return [x['fileName'] for x in v.get('files',[]) if x['fileName'].startswith(prefix)]
  assert listing()==[] and unfinished()==[],'Fresh B2 prefix already exists'
  self.start_resident(b); time.sleep(3); self.stop_resident(b); self.open_cover(); self.start_resident(b)
  settings=self.cli(b,'settings.get'); original=settings['document']['profiles']
  destination={'id':profile,'label':'Sweep isolated B2 acceptance','provider':'backblaze-b2','settings':{'apiUrl':'https://api.backblazeb2.com','bucket':bucket,'objectPrefix':prefix,'linkMode':'public','linkValidityDays':7,'publicUrlBase':None,'connectTimeoutMs':10000,'requestTimeoutMs':60000},'credentials':{'mode':'keychain','reference':reference}}
  self.cli(b,'settings.patch',{'patch':{'profiles':original+[destination]},'expectedRevision':settings['metadata']['observedRevision']})
  settings=self.cli(b,'settings.get')
  sys.path.insert(0,str(pathlib.Path(__file__).parent/'tools/lab'))
  import provision_live_credentials as bridge
  # Documented QtKeychain bridge, secrets travel only over its private stdin pipe.
  oldenv=dict(os.environ); os.environ.update(self.env)
  try: bridge.host_call(str(pathlib.Path(__file__).parent/'lab-credential-bridge/putgd-lab-secret-bridge'),'s3',{'op':'import','reference':reference,'credentials':{'accessKey':key,'secretKey':secret,'sessionToken':''}})
  finally: os.environ.clear(); os.environ.update(oldenv)
  bridge_imported=True; row('credential-bridge-import',reference=reference,confirmed=True)
  key=secret=''
  unlocked=self.cli(b,'setup.unlockCredentials',{'profileId':profile,'expectedRevision':settings['metadata']['observedRevision']})
  assert wait_setup(unlocked['setupId'])['state']=='completed','B2 credential unlock refused'
  tested=self.cli(b,'setup.testDestination',{'profileId':profile,'expectedRevision':self.cli(b,'settings.get')['metadata']['observedRevision']})
  test=wait_setup(tested['setupId']); row('B1',passed=test['state']=='completed' and listing()==[],result=test,prefixEmptyAfterTest=listing()==[],unfinishedLargeFiles=unfinished())
  assert unfinished()==[],'B2 large test left an unfinished upload'
  assert test['state']=='completed',test
  completed=[]
  for name,body in [('control.txt',b'putgd B2 isolated unchanged control\n'),('payload.bin',bytes(range(256))*32768)]:
   path=self.run/name; path.write_bytes(body)
   op=self.cli(b,'upload.files',{'paths':[str(path)],'profileId':profile})['operationId']; result,progress=wait(op)
   assert result['state']=='completed',result
   seen=[p for obs in progress for p in obs['progress'] if p]
   assert all(p.get('bytesTransferred',0)>=0 and (p.get('bytesTotal') is None or p.get('bytesTransferred',0)<=p['bytesTotal']) for p in seen),'invalid B2 progress'
   row('progress-validation',observations=len(seen),valid=True)
   record=[v for v in self.cli(b,'history.list',{'limit':30})['records'] if v['operationId']==op][0]
   with urllib.request.urlopen(record['receipt']['directUrl'],timeout=30) as response: downloaded=response.read()
   assert hashlib.sha256(downloaded).digest()==hashlib.sha256(body).digest()
   completed.append(record)
   row('B2-'+name,passed=True,operation=result,progress=progress,sha256=hashlib.sha256(body).hexdigest(),readbackMatched=True)
   if name=='control.txt': control_listing=listing()
  self.cli(b,'ui.show',{'view':'history'}); time.sleep(1); self.desktop_frame(self.run/'frames/B2-uploaded.png')
  deleted=remove(completed[1]); after=listing(); row('B3',passed=all(v['status']=='removed' for v in deleted['items']) and after==control_listing,deletion=deleted,controlUnchanged=after==control_listing)
  cleanup=remove(completed[0]); row('B2-cleanup',deletion=cleanup,prefixEmpty=listing()==[])
 except Exception as e: row('driver-error',passed=False,errorType=type(e).__name__,error=str(e) if not isinstance(e,urllib.error.HTTPError) else 'HTTP '+str(e.code))
 finally:
  if original is not None:
   try:
    residue=listing()
    row('prefix-cleanup-preview',versions=residue)
    for filename,fileid,action,sha in residue:
     assert filename.startswith(prefix)
     api(endpoint+'/b2api/v3/b2_delete_file_version',{'fileName':filename,'fileId':fileid},token=token)
    row('prefix-cleanup-complete',empty=listing()==[])
   except Exception as e: row('prefix-cleanup',removed=False,errorType=type(e).__name__)
   try:
    s=self.cli(b,'settings.get'); self.cli(b,'settings.patch',{'patch':{'profiles':original},'expectedRevision':s['metadata']['observedRevision']}); row('profile-cleanup',removed=True)
   except Exception as e: row('profile-cleanup',removed=False,errorType=type(e).__name__)
  if bridge_imported:
   oldenv=dict(os.environ); os.environ.update(self.env)
   try:
    bridge.host_call(str(pathlib.Path(__file__).parent/'lab-credential-bridge/putgd-lab-secret-bridge'),'s3',{'op':'delete','reference':reference}); row('keyring-cleanup',reference=reference,removed=True)
   finally: os.environ.clear(); os.environ.update(oldenv)
  self.stop_resident(b); self.close_cover()
 return 0
r.Driver.main=flow
sys.exit(r.main())
