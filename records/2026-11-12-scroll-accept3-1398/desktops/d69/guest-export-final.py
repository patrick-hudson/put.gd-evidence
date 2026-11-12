from pathlib import Path
import json,hashlib,tarfile,os
P=Path('/home/lab/work/s3a');out=P.parent/'s3-budgie-final-evidence.tar.gz'
files=[p for p in sorted(P.rglob('*')) if p.is_file() and not p.is_symlink()]
idx={str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files};(P/'export-index.json').write_text(json.dumps(idx,indent=1))
with tarfile.open(out,'w:gz') as t:
 for p in files+[P/'export-index.json']:t.add(p,arcname=str(p.relative_to(P)),recursive=False)
print(json.dumps({'archive':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'size':out.stat().st_size,'files':len(files)}),flush=True)
