import sys,json,hashlib,shutil,subprocess
from pathlib import Path
S=Path.home()/'work/kq/src';sys.path.insert(0,str(S));from tools.lab import lab
for n in sys.argv[1:]:
 r=S/'work/lab-runs'/n;o=Path.home()/'work/kq/evidence'/n;state=lab.state(r)
 shutil.copy2(r/'state.json',o/'state-final.json')
 for f in (Path.home()/'work/kq').glob(n+'*.log'):shutil.copy2(f,o/f.name)
 completed=dict(run=str(r),runId=state['id'],completed=True,outcome='passed');(o/'completion.json').write_text(json.dumps(completed,indent=2))
 manifest=dict(schemaVersion=1,kind='vm-overlay-cleanup-evidence',**completed,files={str(p.relative_to(o)):hashlib.sha256(p.read_bytes()).hexdigest() for p in o.rglob('*') if p.is_file() and p.name!='cleanup-manifest.json'})
 m=o/'cleanup-manifest.json';m.write_text(json.dumps(manifest,indent=2));print(lab.reset(r),flush=True)
 for dry in [True,False]:
  result=lab.cleanup_overlay(r,evidence_manifest=m,dry_run=dry,images_root=Path.home()/'work/put.gd/work/lab-images');(o/('cleanup-preview.json' if dry else 'cleanup-result.json')).write_text(json.dumps(result,indent=2));print(result,flush=True)
 shutil.copy2(r/'overlay-cleanup.json',o/'overlay-cleanup.json')
 print('retired',n,flush=True)
