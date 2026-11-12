import proton_accept as p
import json
from pathlib import Path
p.require_locks('k72','p1414-r4-k72-diag')
w=Path('diag');w.mkdir(mode=0o700)
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
finally:
 a.stop();print('helper gone',p.helpers_gone(15))
