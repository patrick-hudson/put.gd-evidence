import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'repo/tools/lab'));import lab
r=Path('/home/patrick/work/svm1398/repo/work/lab-runs')/sys.argv[1]
info=lab.state(r);completion={'run':str(r),'runId':info['id'],'completed':True,'outcome':'failed'}
e=r/'retirement-evidence';e.mkdir(exist_ok=True);(e/'completion.json').write_text(json.dumps(completion));
for name in ['export.tar.gz','export-hashes.json','state.json']:
 (e/name).write_bytes((r/name).read_bytes())
manifest={'schemaVersion':1,'kind':'vm-overlay-cleanup-evidence',**completion,'files':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in e.iterdir() if f.name!='manifest.json'}}
(e/'manifest.json').write_text(json.dumps(manifest));print(lab.reset(r))
import subprocess
cmd=['python3','tools/lab/lab.py','cleanup','--run',str(r),'--images-root','/home/patrick/work/put.gd/work/lab-images','--evidence-manifest',str(e/'manifest.json')]
subprocess.run(cmd+['--dry-run'],cwd='/home/patrick/work/svm1398/repo',check=True);subprocess.run(cmd,cwd='/home/patrick/work/svm1398/repo',check=True)
