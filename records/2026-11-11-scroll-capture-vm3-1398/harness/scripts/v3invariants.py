import sys,json,shlex
from pathlib import Path
B=Path('/home/patrick/work/svm1398');sys.path.insert(0,str(B/'repo/tools/lab'));import lab
for k in sys.argv[1]:
 r=B/'repo/work/lab-runs'/(k+'3');o=B/'v3evidence'/k
 code="""import json
from pathlib import Path
p=Path('/tmp/v3');d=json.loads((p/'cases/cancel/result.json').read_text());i=d['id'];h=d['history'];out={'id':i,'state':d['capture']['state'],'matchingHistory':[v for v in h.get('records',[]) if v.get('id')==i or v.get('operationId')==i],'stagingMatches':[str(f.relative_to(p)) for f in (p/'data').rglob('*') if i in str(f)]};print(json.dumps(out,indent=2))
"""
 (o/'cancel-invariants.json').write_text(lab.guest_session(r,'python3 -c '+shlex.quote(code)))
