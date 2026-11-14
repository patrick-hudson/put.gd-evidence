from pathlib import Path
import tarfile,json,hashlib
l=Path.home()/'work/s1520';dst=l/'b-evidence.tgz'
with tarfile.open(dst,'w:gz') as t:
 for label in ['a','b']:
  d=l/label
  for p in sorted(d.iterdir()):
   if p.is_file() and p.suffix in ['.json','.jsonl','.log','.png','.txt','.err','.pid']:t.add(p,arcname=str(p.relative_to(l)),recursive=False)
  for p in sorted((d/'out').rglob('*.png')):t.add(p,arcname=str(p.relative_to(l)),recursive=False)
print(hashlib.sha256(dst.read_bytes()).hexdigest(),dst.stat().st_size)
