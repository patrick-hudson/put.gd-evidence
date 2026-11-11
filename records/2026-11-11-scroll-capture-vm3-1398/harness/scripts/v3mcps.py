import sys,time,json,shlex,subprocess,os
from pathlib import Path
B=Path('/home/patrick/work/svm1398');sys.path.insert(0,str(B/'repo/tools/lab'));import lab
k=sys.argv[1];r=B/'repo/work/lab-runs'/(k+'3');o=B/'v3evidence'/k
for i in range(1,6):
 n='mcp'+str(i);off=int(lab.guest_session(r,'stat -c %s /tmp/v3/helper.log').strip())
 p=subprocess.run([str(B/'repo/tools/mcp/.venv/bin/python'),str(B/'v3mcp.py'),k],env=dict(os.environ,VM_RUN=k),capture_output=True,text=True,timeout=300);(o/(n+'.console')).write_text(p.stdout+p.stderr)
 events=json.loads((B/('v3-'+k+'-mcp.json')).read_text());(o/(n+'-events.json')).write_text(json.dumps(events,indent=2));a=events[-1]['reply']['result']
 code="""import json,hashlib,shutil
from pathlib import Path
p=Path('/tmp/v3');d=p/'cases'/%r;d.mkdir();a=json.loads(%r);(d/'result.json').write_text(json.dumps({'capture':a},indent=2));(d/'helper.log').write_bytes((p/'helper.log').read_bytes()[%d:]);sha=a.get('result',{}).get('sha256')
if sha:
 f=next(f for f in (p/'archive').rglob('*.png') if hashlib.sha256(f.read_bytes()).hexdigest()==sha);shutil.copyfile(f,d/'capture.png')
"""%(n,json.dumps(a),off)
 lab.guest_session(r,'python3 -c '+shlex.quote(code));print(k,n,a.get('state'),a.get('endReason'),flush=True)
