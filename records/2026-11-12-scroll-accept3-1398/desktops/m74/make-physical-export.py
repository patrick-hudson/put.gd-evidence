from pathlib import Path
import json,hashlib,tarfile,sys
P=Path('/home/patrick/work/s3a');host=sys.argv[1];out=P.parent/('scroll-accept3-'+host+'-private.tar.gz')
# Private cold archive. Include source and all test data; user autostart backups and baseline session environment stay private on host.
skip={'autostart-original-private','baseline-session-env.json'}
files=[p for p in sorted(P.rglob('*')) if p.is_file() and not p.is_symlink() and p.name not in skip and not any(v in ('debian13','budgie-export') for v in p.relative_to(P).parts) and p.suffix not in ('.deb','.rpm','.AppImage','.tar','.gz')]
index={str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files};manifest=P/('export-index-'+host+'.json');manifest.write_text(json.dumps(index,indent=1))
with tarfile.open(out,'w:gz') as t:
 for p in files+[manifest]:t.add(p,arcname=str(p.relative_to(P)),recursive=False)
r={'archive':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size,'files':len(files)};(P/('export-receipt-'+host+'.json')).write_text(json.dumps(r,indent=2));print(r,flush=True)
