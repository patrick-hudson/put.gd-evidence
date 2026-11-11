import sys,json,shlex,time,subprocess
from pathlib import Path
B=Path('/home/patrick/work/svm1398');sys.path.insert(0,str(B/'repo/tools/lab'));import lab
for k,ident in [('n','8eca03bb-1166-46d1-a3f6-db5a3b3c050c'),('k','9fe5c5b5-8d55-4977-b84d-fb9fbbabf33d')]:
 r=B/'repo/work/lab-runs'/(k+'3');lab.put(r,B/'v3guest.py','/home/lab/v3guest.py')
 print(k,lab.guest_session(r,'python3 /home/lab/v3guest.py rpc scroll.cancel '+shlex.quote(json.dumps({'id':ident}))+' || true'))
 code="""import json
from pathlib import Path
p=Path('/tmp/v3/cases')
for d in list(p.iterdir()):
 if (d/'result.json').exists() and not d.name.startswith('harness'):
  a=json.loads((d/'result.json').read_text())
  if a.get('error') or (not a.get('capture',{}).get('state')):d.rename(d.with_name('harness-control-error-'+d.name))
"""
 print(lab.guest_session(r,'python3 -c '+shlex.quote(code)))
