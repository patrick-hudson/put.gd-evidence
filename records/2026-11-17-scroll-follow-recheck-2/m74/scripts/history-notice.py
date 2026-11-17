import accept as A,json,time
from pathlib import Path
from find_history import find_operation
P=A.P
found=[]
for d in (P/'runs').iterdir():
 if not(d/'result.json').exists():continue
 r=json.loads((d/'result.json').read_text());c=r.get('capture')or{}
 if c.get('foundAgain',0)>0:found.append((d,c))
assert found,'No foundAgain>0 run; force D before this check'
d,c=next(((d,c)for d,c in found if c.get('endReason')=='done'),found[0])
r=find_operation(A,c['id']);(P/'history-note.json').write_text(json.dumps({'run':d.name,'inspect':json.loads((d/'scroll-inspect.json').read_text()),'historyRecord':r},indent=1))
A.rpc('ui.show',{'view':'history'});time.sleep(2)
A.rpc('ui.history',{'action':'select','ids':[r['id']]});A.rpc('ui.history',{'action':'openDetails'});time.sleep(1)
(P/'history-ui.json').write_text(json.dumps(A.rpc('ui.history',{'action':'inspect'}),indent=1))
import rfb
v=rfb.RFB(5900);v.screenshot(P/'history-note.png');v.close()
print(json.dumps({'run':d.name,'foundAgain':c['foundAgain'],'note':c.get('note'),'history':r},indent=1))
