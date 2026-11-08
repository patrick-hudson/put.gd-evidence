import sys,json,hashlib,shutil,tarfile,subprocess
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tools.lab import lab,nightly_desktops as n
phase,rid=sys.argv[1:3];run=Path('work/lab-runs')/rid;run=run.resolve();base=Path('work/sp').resolve();out=base/(rid+'-export');archive=base/(rid+'-evidence.tgz');info=lab.state(run)
if phase=='export':
 out.mkdir(mode=0o700)
 # Only this row's private files, never a VM key/disk or another worker.
 for p in sorted(base.glob(rid+'-*')):
  if p in (out,archive) or p.is_symlink():continue
  if p.is_dir():shutil.copytree(p,out/'attempts'/p.name)
  elif p.is_file():
   (out/'logs').mkdir(exist_ok=True);shutil.copy2(p,out/'logs'/p.name)
 for name in ('state.json','package.json','qmp-features.json'):
  if (run/name).exists():shutil.copy2(run/name,out/('vm-'+name))
 # Retain non-secret bridge/lending receipts for this exact run only.
 receipts=Path.home()/'putgd-lab/proton/receipts'
 for directory in receipts.glob('*-'+rid):
  assert directory.is_dir() and not directory.is_symlink()
  for p in directory.glob('*.json'):
   d=out/'proton-lending'/directory.name;d.mkdir(parents=True,exist_ok=True);shutil.copy2(p,d/p.name)
 private_roots=lab.ssh(run,"find /dev/shm -maxdepth 1 -type d -name 's???????' -printf '%p\\n'").strip();assert not private_roots,'owned application roots retained'
 native=lab.guest_session(run,'test ! -S "$XDG_RUNTIME_DIR/putgd/session.sock" && echo gone').strip();assert native=='gone'
 # No put.gd worker remains; ordinary desktop processes are preserved.
 proc=lab.ssh(run,"ps -u $(id -u) -o comm= | python3 -c 'import sys,json;print(json.dumps([p.strip() for p in sys.stdin if p.strip().startswith(\"putgd\")]))'").strip();assert json.loads(proc)==[],proc
 n.save(out/'guest-cleanup.json',dict(privateApplicationRoots=[],residentSocketRemoved=True,putgdProcesses=[]))
 cells={k:dict(status='not_run') for k in n.FLOWS}
 for p in sorted(base.glob(rid+'-*/cells.json'),key=lambda p:p.stat().st_mtime_ns):
  for k,v in json.loads(p.read_text()).items():
   if v['status']!='not_run' or cells[k]['status']=='not_run':cells[k]=v
 n.save(out/'scripted-result.json',dict(kind='scripted-outcome-pass',tag='v26.1108.4234-nightly',source='2b5e1b2d3c11757f805331e4104eb06b2c79ad5c',cells=cells))
 completion=dict(schemaVersion=1,kind='vm-overlay-cleanup-evidence',run=str(run),runId=info['id'],completed=True,outcome='passed' if all(v['status']=='pass' for v in cells.values()) else 'failed')
 n.save(out/'completion.json',completion)
 files={p.relative_to(out).as_posix():n.digest(p) for p in sorted(out.rglob('*')) if p.is_file()}
 n.save(out/'completion-manifest.json',dict(completion,files=files))
 with tarfile.open(archive,'w:gz') as tar:
  for p in sorted(out.rglob('*')):
   if p.is_file():tar.add(p,arcname=p.relative_to(out).as_posix(),recursive=False)
 n.save(base/(rid+'-export-ready.json'),dict(run=str(run),runId=info['id'],archiveSha256=n.digest(archive),files={**files,'completion-manifest.json':n.digest(out/'completion-manifest.json')}))
 print('export ready',rid,n.digest(archive))
else:
 proof=json.loads((base/(rid+'-workstation-verified.json')).read_text());ready=json.loads((base/(rid+'-export-ready.json')).read_text());assert proof==dict(ready,verified=True)
 assert all(n.digest(out/name)==digest for name,digest in ready['files'].items())
 lab.reset(run);images=Path(info['golden']).parents[1]
 n.save(out/'retirement-dry-run.json',lab.cleanup_overlay(run,evidence_manifest=out/'completion-manifest.json',images_root=images,dry_run=True))
 n.save(out/'retirement.json',lab.cleanup_overlay(run,evidence_manifest=out/'completion-manifest.json',images_root=images))
 print('guarded-retired',rid)
