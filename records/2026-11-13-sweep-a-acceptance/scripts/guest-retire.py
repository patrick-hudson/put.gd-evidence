#!/usr/bin/env python3
"""Retire one completed campaign's owned VM through lab.py.
Runs on the QEMU host after exported evidence has been verified.
"""
import hashlib,json,pathlib,subprocess,sys
root=pathlib.Path('/home/patrick/work/sa1113')
run=root/'work/lab-runs'/sys.argv[1]
evidence=run/'completion-evidence'
assert sys.argv[2] in ('passed','failed')
state=json.loads((run/'state.json').read_text())
evidence.mkdir(mode=0o700,exist_ok=False)
for source in ('state.json','install.json'):
 if (run/source).is_file(): (evidence/source).write_bytes((run/source).read_bytes())
completion={'run':str(run),'runId':state['id'],'completed':True,'outcome':sys.argv[2]}
(evidence/'completion.json').write_text(json.dumps(completion,indent=2)+'\n')
manifest={'schemaVersion':1,'kind':'vm-overlay-cleanup-evidence',**completion,'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in evidence.iterdir() if p.is_file()}}
(evidence/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
lab=[sys.executable,str(root/'tools/lab/lab.py')]
subprocess.run(lab+['reset','--run',str(run)],check=True)
for extra in (['--dry-run'],[]):
 subprocess.run(lab+['cleanup','--run',str(run),'--images-root','/home/patrick/work/put.gd/work/lab-images','--evidence-manifest',str(evidence/'manifest.json')]+extra,check=True)
