import native_acceptance as n,json,sqlite3,uuid
from datetime import datetime,timedelta,timezone
from pathlib import Path
root=Path('/tmp/h396k');assert not (root/'runtime/putgd/session.sock').exists()
db=root/'data/putgd/history.sqlite'
print(json.dumps(n.grow_database(db,236)))
with sqlite3.connect(db) as c:
 c.row_factory=sqlite3.Row
 rows=list(c.execute('select * from history order by created desc'))
 for i,row in enumerate(rows):
  d=json.loads(row['data']);created=(datetime(2026,11,10,18,tzinfo=timezone.utc)-timedelta(days=i//80,seconds=i%80)).isoformat(timespec='milliseconds').replace('+00:00','Z')
  d.update(created=created,name='Synthetic-history-%03d.png'%i)
  if i%17==0:d.update(uploadStatus='failed',error={'code':'synthetic_failure','message':'Synthetic upload failure','details':{}})
  c.execute('update history set created=?,name=?,upload_status=?,data=? where id=?',(created,d['name'],d['uploadStatus'],json.dumps(d).encode(),row['id']))
  op=json.loads(c.execute('select data from operations where id=?',(row['operation_id'],)).fetchone()[0]);op['created']=created
  c.execute('update operations set data=? where id=?',(json.dumps(op).encode(),row['operation_id']))
 print('Synthetic fixture: 236 image rows, three days, 14 failed rows; local destination only; no links or remote objects.')
