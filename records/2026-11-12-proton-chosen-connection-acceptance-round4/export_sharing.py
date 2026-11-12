import sqlite3,json
from pathlib import Path
p=Path.home()/'work/p4a/pr/profile/data/putgd/history.sqlite'
c=sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True)
rows=[]
for (raw,) in c.execute('select data from sharing_operations'):
 d=json.loads(raw);rows.append({k:d.get(k) for k in ['id','historyId','action','state','status','error','progress']})
# Export no receipts, links, protected input or destination metadata.
print(json.dumps(rows,indent=2))
