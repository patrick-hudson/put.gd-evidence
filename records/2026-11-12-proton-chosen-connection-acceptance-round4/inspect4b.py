import proton_accept as p
import json
from pathlib import Path
p.require_locks('k72','p1414-r4-k72-inspect')
w=Path('diag2');w.mkdir(mode=0o700)
a=p.App('app',w)
for env in [a.environment,a.cli_environment]:
 for n in ['config','data','state']:env['XDG_'+n.upper()+'_HOME']=str(Path('pr/profile',n).resolve())
try:
 a.start()
 rows=a.need('history.list',{'limit':100,'offset':0})['records']
 safe=[{k:r.get(k) for k in ['id','linkAvailable','shareStatus','phase','remoteStatus']} for r in rows]
 (w/'history-status.json').write_text(json.dumps(safe,indent=2))
 print('history rows',len(safe),'available',sum(bool(r['linkAvailable']) for r in safe))
 from collections import Counter
 print('shareStatus',dict(Counter(r['shareStatus'] for r in safe)))
 import round3,time
 inspected=[]
 for row in rows:
  if row.get('shareStatus')!='unknown':continue
  entry={'historyId':row['id'],'beforeError':round3.clean(row.get('error'))}
  reply,error=a.call('history.inspectLink',{'id':row['id']});entry['requestError']=round3.clean(error)
  if not error:
   end=time.monotonic()+120
   while time.monotonic()<end:
    result,error=a.call('share.inspect',{'id':reply['shareOperationId']})
    if error or result.get('state') not in ('accepted','running'):break
    time.sleep(.1)
   entry.update(result=round3.clean(result),error=round3.clean(error))
  inspected.append(entry)
 (w/'inspections.json').write_text(json.dumps(inspected,indent=2))
 print('read-only inspections',[(x['historyId'],(x.get('result') or {}).get('status')) for x in inspected])
finally:
 a.stop();print('helper gone',p.helpers_gone(15))
