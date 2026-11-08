"""Export, then guarded retirement only after a verified workstation copy."""
import argparse,json,hashlib,sys,tarfile,shutil
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tools.lab import lab,nightly_desktops as n
from tools.lab.surface_driver.collect import collect
p=argparse.ArgumentParser();p.add_argument('phase',choices=('export','retire'));p.add_argument('--run',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--export-receipt',type=Path);a=p.parse_args()
run=a.run.resolve();out=a.out.resolve();info=lab.state(run)
if a.phase=='export':
 lab.verify_owned_guest(run)
 attempts=sorted(p.parent for p in out.glob('*/receipt.json'))
 archive=out/'attachments.tgz'
 if attempts:
  collect(attempts,archive)
  with tarfile.open(archive) as stream:
   for member in stream.getmembers():
    if member.isfile():
     assert hashlib.sha256(stream.extractfile(member).read()).hexdigest()==n.digest(out/member.name)
 for name in ('state.json','package.json','qmp-features.json'):
  if (run/name).exists():shutil.copy2(run/name,out/('vm-'+name))
 result=json.loads((out/'result.json').read_text())
 completion=dict(schemaVersion=1,kind='vm-overlay-cleanup-evidence',run=str(run),runId=info['id'],completed=True,outcome='passed' if all(v['status']=='green' for v in result['cells'].values()) else 'failed')
 n.save(out/'completion.json',completion)
 files={name:n.digest(out/name) for name in ('completion.json','result.json','vm-state.json','vm-package.json','vm-qmp-features.json','attachments.tgz','run-config.json','profile-sha256.json','driver.py','driver-original.py') if (out/name).exists()}
 n.save(out/'completion-manifest.json',dict(completion,files=files))
 n.save(out/'export-ready.json',dict(run=str(run),runId=info['id'],files=dict(files,**{'completion-manifest.json':n.digest(out/'completion-manifest.json')})))
 print('export ready',info['id'])
else:
 proof=json.loads(n.private_file(a.export_receipt).read_text());ready=json.loads((out/'export-ready.json').read_text())
 assert proof['runId']==info['id'] and proof['verified'] is True and proof['files']==ready['files']
 assert all(n.digest(out/name)==digest for name,digest in proof['files'].items())
 lab.reset(run)
 images=Path(info['golden']).parents[1]
 n.save(out/'retirement-dry-run.json',lab.cleanup_overlay(run,evidence_manifest=out/'completion-manifest.json',images_root=images,dry_run=True))
 n.save(out/'retirement.json',lab.cleanup_overlay(run,evidence_manifest=out/'completion-manifest.json',images_root=images))
 print('retired',info['id'])
