import proton_accept as p
from pathlib import Path
import json,time
work=Path('pr').resolve(); original=Path.mkdir
Path.mkdir=lambda self,*a,**kw:None if self.is_dir() and (self.resolve()==work or self.resolve().is_relative_to(work/'profile')) else original(self,*a,**kw)
p.require_locks('k72','p1414-ec6-k72')
app=p.App('app',work)
(work/'resident.log').rename(work/'resident-before-reconcile.log')
report={'historyId':'2f12a198-cd73-4ca6-92b4-8bfd1e3e5bb8','actions':[]}
try:
 app.authorize_capture();app.start()
 caps=app.need('capabilities');report['capabilitiesInspected']=True
 def change(method):
  reply,error=app.call(method,{'id':report['historyId']});entry={'method':method,'error':error}
  if not error:
   oid=reply['shareOperationId'];entry['shareOperationId']=oid
   until=time.monotonic()+120
   while time.monotonic()<until:
    r,error=app.call('share.inspect',{'id':oid})
    if error or r.get('state')!='running':break
    time.sleep(.1)
   entry.update(state=(r or {}).get('state'),status=(r or {}).get('status'),error=error or (r or {}).get('error'))
  report['actions'].append(entry);return entry
 inspect=change('history.inspectLink')
 if inspect.get('status')=='shared':change('history.revokeLink')
 report['helpersGoneAfter']=p.helpers_gone(15)
 rows=app.need('history.list',{'limit':100,'offset':0}).get('records',[])
 report['remainingLinks']=sum(bool(x.get('linkAvailable')) for x in rows)
 report['targetStatus']=next((x.get('shareStatus') for x in rows if x.get('id')==report['historyId']),None)
finally:
 app.stop();app.remove_entries();report['helpersLeft']=p.helper_pids();(work/'sharing-reconciliation.json').write_text(json.dumps(report,indent=1));print(json.dumps(report))
