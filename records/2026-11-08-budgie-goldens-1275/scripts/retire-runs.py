from pathlib import Path
import hashlib,json,shutil,sys,datetime
root=Path('/home/patrick/work/putgd-a1275');sys.path.insert(0,str(root/'tools/lab'));import lab,overlay_cleanup
export=root/'evidence/2026-11-08-budgie-goldens-1275'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
index={str(p.relative_to(export)):sha(p) for p in sorted(export.rglob('*')) if p.is_file()}
(export/'export-index.json').write_text(json.dumps(index,indent=2)+'\n')
for n in ['a1','a2','a3','a4']:
 r=root/'work/lab-runs'/n;state=lab.state(r);d=r/'completion';d.mkdir(mode=0o700)
 record={'schemaVersion':1,'kind':'vm-overlay-cleanup-evidence','run':str(r),'runId':state['id'],'completed':True,'outcome':'failed' if n=='a3' else 'passed','scope':'step-1 real-session compatibility probes; Magpie shortcut test negative on a3; not new adapter certification','exportDirectory':str(export),'timestampUtc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 (d/'completion.json').write_text(json.dumps(record,indent=2)+'\n');shutil.copy2(export/'export-index.json',d/'export-index.json');shutil.copy2(export/'private-archive-index.json',d/'private-archive-index.json')
 record['files']={f.name:sha(f) for f in d.iterdir() if f.is_file()};(d/'manifest.json').write_text(json.dumps(record,indent=2)+'\n')
 result=overlay_cleanup.cleanup(r,evidence_manifest=d/'manifest.json',images_root=Path('/home/patrick/work/put.gd/work/lab-images'))
 print(n,json.dumps(result),flush=True)
