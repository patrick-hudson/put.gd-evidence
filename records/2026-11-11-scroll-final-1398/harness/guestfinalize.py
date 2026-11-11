from pathlib import Path
import sys,shlex,json,re
B=Path.home()/'work/svm1398';D=Path.home()/'work/sfinal';sys.path.insert(0,str(B/'repo/tools/lab'));import lab
k=sys.argv[1];r=B/'repo/work/lab-runs'/(k+'fin');o=D/'ev'/(k+'fin')
code="""import json
from pathlib import Path
p=Path('/tmp/v3');d=json.loads((p/'cases/cancel/result.json').read_text());i=d['id'];h=d['history'];print(json.dumps({'id':i,'state':d['capture']['state'],'matchingHistory':[v for v in h.get('records',[]) if v.get('id')==i or v.get('operationId')==i],'stagingFiles':[str(f) for f in (p/'data').rglob('*') if f.is_file() and i in str(f)]},indent=2))
"""
(o/'cancel-invariants.json').write_text(lab.guest_session(r,'python3 -c '+shlex.quote(code)))
s=lab.guest_session(r,'cat /tmp/v3/stop-top-1.log');pos=re.findall(r'position (\d+)',s);(o/'stop-top-position.json').write_text(json.dumps({'fixtureFinalPosition':int(pos[-1]) if pos else 12000}))
code=Path('/home/patrick/work/pfin/receiptverify.py').read_text().replace('/home/patrick/work/pfin','/tmp/v3').replace("['cap-final','cap-warning','stop-middle-final','mcp','user']","['cap','postcap','stop-mid','mcp1','user']").replace("f=P/name/'capture.png'","f=P/'cases'/name/'capture.png'")
(o/'loopback-output.log').write_text(lab.guest_session(r,'python3 -c '+shlex.quote(code)));lab.get(r,'/tmp/v3/loopback-verification.json',o/'loopback-verification.json')
print(k,'finalized')
