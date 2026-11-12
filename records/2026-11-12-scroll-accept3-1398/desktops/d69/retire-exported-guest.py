from pathlib import Path
import sys,json,shutil
sys.path.insert(0,'/home/patrick/work/s3lab/tools/lab');import lab
lab.overlay_cleanup.ROOT=Path('/home/patrick/work/put.gd');P=Path('/home/patrick/work/s3a');tag,run=sys.argv[1:];r=Path('/home/patrick/work/put.gd/work/lab-runs')/run;e=P/(tag+'-export');state=json.loads((r/'state.json').read_text());proof=json.loads((e/'workstation-verified.json').read_text());receipt=json.loads((e/'export-receipt.json').read_text());assert lab.hash_file(e/'guest-evidence.tar.gz')==proof['sha256']==receipt['sha256']
for name in [tag+'-native-install.json',tag+'-appimage-install.json',tag+'-launch.json']:
 if (P/name).exists():shutil.copyfile(P/name,e/name)
completion={'run':str(r),'runId':state['id'],'completed':True,'outcome':'failed'};(e/'completion.json').write_text(json.dumps(completion,indent=2));m=e/'completion-manifest.json';m.write_text(json.dumps({'schemaVersion':1,'kind':'vm-overlay-cleanup-evidence',**completion,'files':{f.name:lab.hash_file(f) for f in e.iterdir() if f.is_file() and f.name not in ['completion-manifest.json','retirement.json']}},indent=2))
try:lab.ssh(r,'sync',timeout=15)
except Exception as ex:print('SYNC_ERROR',str(ex),flush=True)
stop=lab.reset(r);print('STOP',stop,flush=True);dry=lab.cleanup_overlay(r,evidence_manifest=m,dry_run=True,images_root=Path('/home/patrick/work/put.gd/work/lab-images'));print('DRY',dry,flush=True);actual=lab.cleanup_overlay(r,evidence_manifest=m,images_root=Path('/home/patrick/work/put.gd/work/lab-images'));(e/'retirement.json').write_text(json.dumps({'stop':stop,'dryRun':dry,'cleanup':actual},indent=2));print('RETIRED',actual,flush=True)
