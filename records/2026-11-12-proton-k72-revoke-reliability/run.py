import proton_accept as p
import json,time,os,signal,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone

def utc():return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00','Z')
def clean(v):
 if isinstance(v,dict):return {k:clean(x) for k,x in v.items() if k.lower() not in ('directurl','url','link','receipt','options') and not k.startswith('_')}
 if isinstance(v,list):return [clean(x) for x in v]
 return v

def action(a,method,hid,index):
 start=utc();one=time.monotonic()
 reply,error=a.call(method,{'id':hid})
 state={}
 if not error:
  deadline=time.monotonic()+120
  while time.monotonic()<deadline:
   state,error=a.call('share.inspect',{'id':reply['shareOperationId']},timeout=20)
   if error or (state or {}).get('state')!='running':break
   time.sleep(.1)
 return dict(index=index,historyId=hid,startUtc=start,seconds=round(time.monotonic()-one,3),status=(state or {}).get('status',''),errorCode=((error or (state or {}).get('error')) or {}).get('code',''),request=clean(reply),result=clean(state))

def no_processes():
 found=[]
 for d in Path('/proc').iterdir():
  if not d.name.isdigit():continue
  try:
   if d.stat().st_uid==os.getuid() and (d/'comm').read_text().strip().startswith('putgd'):found.append(int(d.name))
  except OSError:pass
 return found

p.require_locks('k72','kr61')
base=Path.cwd()
for num,build in enumerate(['pr','nightly']*3,1):
 if datetime.now(timezone.utc).hour>=11:raise SystemExit('Time safety stop before noon')
 p.require_locks('k72','kr61');assert not no_processes(),no_processes()
 w=base/f'p{num}';w.mkdir(mode=0o700)
 a=p.App(base/build,w)
 # Explicit PID only shutdown, no process-group or pattern signal.
 def stop():
  a.call('ui.quit',timeout=15)
  if a.process:
   try:a.process.wait(timeout=30)
   except subprocess.TimeoutExpired:
    os.kill(a.process.pid,signal.SIGTERM);a.process.wait(timeout=15)
 report={'pass':num,'build':build,'startedUtc':utc(),'uploads':[],'revocations':[],'cleanup':[]}
 def save():(w/'results.json').write_text(json.dumps(report,indent=2)+'\n')
 try:
  a.start();report['appPid']=a.process.pid
  report['version']=json.loads(subprocess.run([str(a.launcher),'--version-json'],env=a.environment,capture_output=True,text=True).stdout)
  report['folder']=p.configure(a)
  payload=w/'payloads';payload.mkdir(mode=0o700)
  for i in range(1,32):
   path=(payload/f'kr61-p{num}-{i:02d}.bin').resolve();path.write_bytes(os.urandom(65536))
   invoked=time.monotonic();reply,error=a.call('upload.files',{'paths':[str(path)],'profileId':p.PROFILE_ID})
   outcome={'error':error,'state':'refused'} if error else p.follow(a,reply['operationId'],invoked)
   outcome['helperGoneAfter']=p.helpers_gone(15)
   report['uploads'].append(clean(outcome));save()
   print('pass',num,'upload',i,outcome.get('state'),flush=True)
  report['shared']=sum(x.get('shareStatus')=='shared' for u in report['uploads'] for x in u.get('items',[]))
  ids={x['historyId'] for u in report['uploads'] for x in u.get('items',[])}
  rows=a.need('history.list',{'limit':100,'offset':0}).get('records',[])
  assert all(r['id'] in ids for r in rows),'Unexpected history rows'
  # Same history.list order, linkAvailable filter, revoke request and poll loop as revoke-all.
  for row in rows:
   if not row.get('linkAvailable'):continue
   hid=row.get('id') or row.get('historyId')
   result=action(a,'history.revokeLink',hid,len(report['revocations'])+1)
   report['revocations'].append(result);save()
   print('pass',num,'revoke',result['index'],result['status'],result['errorCode'],flush=True)
  for row in report['revocations']:
   if row['status']=='revoked':continue
   inspection=action(a,'history.inspectLink',row['historyId'],row['index'])
   retry=action(a,'history.revokeLink',row['historyId'],row['index'])
   report['cleanup'].append({'inspection':inspection,'retry':retry});save()
   if retry['status']!='revoked':raise RuntimeError('Link did not revoke; stop')
  report['revokedFirst']=sum(r['status']=='revoked' for r in report['revocations'])
  assert report['shared']==31 and len(report['revocations'])==31,'Incomplete pass'
 finally:
  stop();report['helpersGoneAfter']=p.helpers_gone(15);report['endedUtc']=utc();report['processesLeft']=no_processes();save()
 assert not report['processesLeft'],report['processesLeft']
 print('PASS COMPLETE',num,report['shared'],report['revokedFirst'],flush=True)
 if num<6:time.sleep(21)
