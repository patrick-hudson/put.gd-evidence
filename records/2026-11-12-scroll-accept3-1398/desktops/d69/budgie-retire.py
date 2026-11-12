from pathlib import Path
import sys,json,hashlib,shutil
sys.path.insert(0,'/home/patrick/work/s3lab/tools/lab');import lab
lab.overlay_cleanup.ROOT=Path('/home/patrick/work/put.gd');r=Path('/home/patrick/work/put.gd/work/lab-runs/s3b2');e=Path('/home/patrick/work/s3a/budgie-export');state=json.loads((r/'state.json').read_text())
proof=json.loads((e/'workstation-verified.json').read_text());archive=e/'guest-final-evidence.tar.gz';assert lab.hash_file(archive)==proof['sha256']=='2ea290d0cc90a2e77b7f97a6ea614f3bafe14ca829865f5f42ee0d4e6b1b7796'
for n in ['state.json','package.json','qmp-features.json']:
 if (r/n).exists():shutil.copyfile(r/n,e/n)
completion={'run':str(r),'runId':state['id'],'completed':True,'outcome':'failed'};(e/'completion.json').write_text(json.dumps(completion,indent=2))
files={p.name:lab.hash_file(p) for p in e.iterdir() if p.is_file() and p.name not in ['completion-manifest.json','retirement.json']}
manifest={'schemaVersion':1,'kind':'vm-overlay-cleanup-evidence',**completion,'files':files};m=e/'completion-manifest.json';m.write_text(json.dumps(manifest,indent=2))
try:print(lab.guest_session(r,'cd /home/lab/work/s3a && python3 -c "import pass2;pass2.rpc(\"ui.quit\")"; sync',timeout=30),flush=True)
except Exception as ex:print('guest quit',str(ex),flush=True)
stop=lab.reset(r);print('STOP',stop,flush=True)
dry=lab.cleanup_overlay(r,evidence_manifest=m,dry_run=True,images_root=Path('/home/patrick/work/put.gd/work/lab-images'));print('DRY',dry,flush=True)
actual=lab.cleanup_overlay(r,evidence_manifest=m,images_root=Path('/home/patrick/work/put.gd/work/lab-images'));(e/'retirement.json').write_text(json.dumps({'stop':stop,'dryRun':dry,'cleanup':actual},indent=2));print('RETIRED',actual,flush=True)
