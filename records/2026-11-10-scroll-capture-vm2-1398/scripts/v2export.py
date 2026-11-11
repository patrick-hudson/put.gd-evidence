import sys,json,shlex,tarfile,hashlib
from pathlib import Path
sys.path.insert(0,'/home/patrick/work/svm1398/repo/tools/lab');import lab
base=Path('/home/patrick/work/svm1398');k=sys.argv[1];r=base/'repo/work/lab-runs'/('og' if k=='g' else k+'f');o=base/'v2evidence'/k
# Materialize the PNG returned by the agent-only MCP operation by its descriptor SHA.
m=base/('v2-'+k+'-mcp.json')
if m.exists():
 events=json.loads(m.read_text());capture=events[-1]['reply']['result'];sha=capture.get('result',{}).get('sha256')
 if sha:
  code="""import json,hashlib,shutil
from pathlib import Path
p=Path('/tmp/v2');d=p/'cases/mcp';d.mkdir(exist_ok=True)
capture=json.loads(%r);sha=capture['result']['sha256']
f=next(f for f in (p/'archive').rglob('*.png') if hashlib.sha256(f.read_bytes()).hexdigest()==sha)
shutil.copyfile(f,d/'capture.png');(d/'result.json').write_text(json.dumps({'capture':capture},indent=2))
""" % json.dumps(capture)
  lab.guest_session(r,'python3 -c '+shlex.quote(code));(o/'mcp-events.json').write_text(json.dumps(events,indent=2))
script="""python3 - <<'INNER'
import tarfile,hashlib,json
from pathlib import Path
p=Path('/tmp/v2');files=[]
for name in ['cases','archive','received','harness-no-hypr']:
 if (p/name).exists():files += [f for f in (p/name).rglob('*') if f.is_file()]
for name in ['helper.log','resident.log','resident-restart.log','rpc.jsonl','version.json','capabilities.json','socket-preflight.json','hypr-socket-preflight.json','gtk.log','qt.log','browser.log','browser-retry.log','browser-home-retry.log','fraction.log']:
 if (p/name).is_file():files.append(p/name)
with tarfile.open('/home/lab/v2-final.tgz','w:gz') as t:
 for f in files:t.add(f,arcname=str(f.relative_to(p)))
print(json.dumps({str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}))
INNER"""
(o/'final-hashes.json').write_text(lab.guest_session(r,script,timeout=180));lab.get(r,'/home/lab/v2-final.tgz',o/'final.tgz',timeout=180)
(o/'final').mkdir(exist_ok=True);tarfile.open(o/'final.tgz').extractall(o/'final',filter='data')
hashes=json.loads((o/'final-hashes.json').read_text())
assert all(hashlib.sha256((o/'final'/n).read_bytes()).hexdigest()==v for n,v in hashes.items())
(o/'export-verified.json').write_text(json.dumps({'files':len(hashes),'verified':True,'archiveSha256':hashlib.sha256((o/'final.tgz').read_bytes()).hexdigest()},indent=2))
(o/'state.json').write_text((r/'state.json').read_text())
print(k,'EXPORTED VERIFIED',len(hashes),flush=True)
