from pathlib import Path
import tarfile,json,hashlib,sys
P=Path('/home/patrick/work/s3a');tag=sys.argv[1];out=P.parent/('scroll-accept3-'+tag+'-review.tar.gz'); files=[]
for f in P.iterdir():
 if f.is_file() and not f.is_symlink() and (f.suffix in ['.py','.html'] or f.name in ['identity.json','capabilities.json','controls7.json','controls7-repeat.json','payload-proof.json','notice-margin-summary.json','live-completeness.json','live-verification-summary.json','live-initial-verification-summary.json','cleanup.json','hotkey-restoration.json','c17.json','c18.json'] or f.name.endswith('.console')):files.append(f)
for d in P.iterdir():
 if not d.is_dir() or d.is_symlink():continue
 if (d/'result.json').exists() or d.name in ['c16','c17','c18']:
  for f in d.iterdir():
   if f.is_file() and not f.is_symlink() and (f.suffix in ['.json','.log','.txt'] or f.name in ['capture.png','reference-generator.png','reference-top.png','reference-footer.png','cap-warning-visible.png','failure-history.png']):files.append(f)
for d in (P/'runs').glob('accept3-*'):
 if not d.is_dir():continue
 for f in d.iterdir():
  if f.is_file() and not f.is_symlink() and f.suffix in ['.json','.png','.log','.txt']:files.append(f)
index={str(f.relative_to(P)):hashlib.file_digest(f.open('rb'),'sha256').hexdigest() for f in files}
with tarfile.open(out,'w:gz') as t:
 for f in sorted(set(files)):t.add(f,arcname=str(f.relative_to(P)),recursive=False)
r={'path':str(out),'sha256':hashlib.file_digest(out.open('rb'),'sha256').hexdigest(),'bytes':out.stat().st_size,'files':index};(P/('review-export-'+tag+'.json')).write_text(json.dumps(r,indent=2));out.chmod(0o600);print({k:v for k,v in r.items() if k!='files'},flush=True)
