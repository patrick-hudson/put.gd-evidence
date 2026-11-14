#!/usr/bin/env python3
import hashlib,json,pathlib,shutil,sys
root=pathlib.Path('/home/patrick/work/sb1114'); name=sys.argv[1]; run=root/'work/lab-runs'/name; state=json.loads((run/'state.json').read_text()); out=run/'completion-evidence'; out.mkdir(mode=0o700,exist_ok=False)
for p in run.rglob('*'):
 if out in p.parents or not p.is_file() or p.is_symlink() or p.suffix not in ('.json','.jsonl','.txt','.log','.png','.mp4','.py','.sh','.xml'): continue
 rel=p.relative_to(run); dest=out/rel; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,dest)
for p in root.glob('vm-'+name+'*'):
 if p.is_file(): shutil.copy2(p,out/p.name)
if name.startswith('hn'): shutil.copy2(root/'baseline/SHA256SUMS',out/'published-nightly-SHA256SUMS.txt')
elif name=='ha1': shutil.copy2(run/'acceptance/build-identity.json',out/'baseline-build-info.json')
else: shutil.copy2(root/'artifacts/ubuntu26.04/build-info.json',out/'package-build-info.json')
completion={'run':str(run),'runId':state['id'],'completed':True,'outcome':sys.argv[2],'notes':'Completed acceptance attempt; harness failures retained'}
(out/'completion.json').write_text(json.dumps(completion,indent=2)+'\n')
manifest={'schemaVersion':1,'kind':'vm-overlay-cleanup-evidence',**completion,'files':{str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file()}}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'run':str(run),'files':len(manifest['files']),'bytes':sum(p.stat().st_size for p in out.rglob('*') if p.is_file())}))
