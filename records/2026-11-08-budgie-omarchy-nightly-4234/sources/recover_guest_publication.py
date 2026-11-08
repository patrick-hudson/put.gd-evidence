"""Guest-side cleanup of one exact retained synthetic publication; no secret output."""
import json,os,re,stat,subprocess,sys,time
from pathlib import Path
p=json.loads(Path(sys.argv[1]).read_text());root=Path(p['root'])
assert root.parent==Path('/dev/shm') and re.fullmatch('n[0-9a-f]{8}',root.name)
s=root.lstat();assert root.resolve()==root and stat.S_ISDIR(s.st_mode) and s.st_uid==os.getuid() and stat.S_IMODE(s.st_mode)==0o700
fx=list(root.glob('fx-*'));assert len(fx)==1
fx=fx[0];owner=fx/'owner';st=owner.lstat();assert stat.S_ISREG(st.st_mode) and st.st_uid==os.getuid() and owner.read_text()[:8]==fx.name[3:]
assert (fx/'data/putgd/history.sqlite').is_file()
env=dict(os.environ, XDG_CONFIG_HOME=str(root/'config'),XDG_DATA_HOME=str(fx/'data'),XDG_STATE_HOME=str(root/'state'),XDG_CACHE_HOME=str(root/'cache'),XDG_RUNTIME_DIR=str(root/'runtime'),PUTGD_RECORD_KEEP_WORKING=str(fx/'working'))
assert len(str(root/'runtime/putgd/session.sock').encode())<=107
log=(root/'recovery.log').open('ab')
app=subprocess.Popen(['putgd','--background'],env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
def call(method,params=None):
 r=subprocess.run(['putgd-cli',method,json.dumps(params or {})],env=env,capture_output=True,text=True,timeout=180)
 try:v=json.loads(r.stdout)
 except ValueError:raise RuntimeError('cleanup CLI invalid response: '+method) from None
 if not v.get('ok'):
  code=v.get('error',{}).get('code','unknown');assert re.fullmatch('[a-z0-9_]+',code)
  raise RuntimeError('cleanup CLI '+method+': '+code)
 return v['result']
def wait(fn):
 end=time.monotonic()+180
 while True:
  if v:=fn():return v
  assert time.monotonic()<end,'cleanup operation deadline'
  time.sleep(.2)
for _ in range(100):
 try:call('capabilities');break
 except RuntimeError:time.sleep(.2)
else:raise RuntimeError('cleanup resident did not start')
try:
 settings=call('settings.get');assert settings['metadata']['path']==str(root/'config/putgd/config.json')
 profiles=settings['document']['profiles'];assert len(profiles)==1 and profiles[0]['id']=='tier1-live'
 reference=profiles[0]['credentials']['reference'];assert reference==p['reference']
 records=call('history.list',{'limit':100})['records'];assert [r['id'] for r in records]==p['historyIds']
 hid=p['historyIds'][0];d=call('history.detail',{'id':hid});dest=d['receipt']['destination']
 assert d['uploadStatus']=='uploaded' and dest['profileId']=='tier1-live' and dest['credentials']['reference']==reference
 proof=dict(root=str(root),historyId=hid,operationId=d['operationId'],provider=p['provider'],profileId='tier1-live')
 if p['provider']=='s3':
  assert dest['providerId']=='s3' and dest['settings']['bucket']=='put.gd'
  prefix=dest['settings']['objectPrefix'];assert re.fullmatch('acceptance/tier1-live/[0-9a-f]{32}/',prefix)
  key=d['receipt']['objectReference']['key'];assert key.startswith(prefix)
  proof.update(bucket='put.gd',objectPath=key,prefix=prefix)
  if d.get('remoteStatus') not in ('removed','already_missing'):
   setup=call('setup.unlockCredentials',{'profileId':'tier1-live','expectedRevision':settings['metadata']['observedRevision']})
   done=wait(lambda:(v if (v:=call('setup.inspect',{'id':setup['setupId']}))['state']!='running' else None));assert done['state']=='completed'
   plan=call('delete.prepare',{'ids':[hid]})
   assert [t['historyId'] for t in plan['targets']]==[hid] and plan['targets'][0]['receipt']['objectReference']['key']==key
   assert plan['localCopiesPreserved'] is True and plan['acknowledgement']
   proof['preparedEffect']=plan['targets'][0]['effect']
   # Persist the exact reviewed ID/effect before acknowledging it.
   Path(p['proof']).write_text(json.dumps(dict(proof,prepared=True),indent=2))
   deleted=call('delete.confirm',{'ids':[hid],'acknowledgement':plan['acknowledgement']})
   proof['deleteOperationId']=deleted['deleteOperationId']
   wait(lambda:(v if (v:=call('delete.inspect',{'id':deleted['deleteOperationId']}))['state'] in ('completed','partial','failed','cancelled') else None))
  d=wait(lambda:(v if (v:=call('history.detail',{'id':hid})).get('remoteStatus') in ('removed','already_missing','failed','unknown','changed','version_retained','hidden_version_retained') else None));assert d['remoteStatus'] in ('removed','already_missing') and not d['linkAvailable']
  proof['remoteStatus']=d['remoteStatus']
 else:
  assert dest['providerId']=='proton-drive'
  proof['folder']=dest['settings']['folderName'];assert re.fullmatch('putgd-tier1-[0-9a-f]{32}',proof['folder'])
  if d.get('shareStatus')!='revoked':
   shared=call('history.revokeLink',{'id':hid});proof['shareOperationId']=shared['shareOperationId']
   wait(lambda:(v if (v:=call('share.inspect',{'id':shared['shareOperationId']}))['state'] in ('completed','failed','cancelled') else None))
  d=wait(lambda:(v if (v:=call('history.detail',{'id':hid})).get('shareStatus') in ('revoked','failed','unknown','changed') else None));assert d['shareStatus']=='revoked' and not d['linkAvailable']
  proof.update(shareStatus='revoked',retainedSyntheticFiles=1)
 call('history.clear');call('cache.clear');assert call('history.list',{'limit':1}).get('total',0)==0
 current=call('settings.get')
 actions={k:dict(destination='local',profileId=None,publicationMode='default') for k in current['document']['actions']}
 call('settings.patch',{'expectedRevision':current['metadata']['observedRevision'],'patch':{'profiles':[],'actions':actions}})
 assert call('settings.get')['document']['profiles']==[]
 proof.update(historyCleared=True,profilesCleared=True)
 Path(p['proof']).write_text(json.dumps(proof,indent=2))
 print(json.dumps(proof))
finally:
 try:call('ui.quit')
 finally:
  app.wait(timeout=20);log.close()
