from pathlib import Path
import tarfile,hashlib
l=Path.home()/'work/s5302';dst=l/'evidence.tgz'
with tarfile.open(dst,'w:gz') as t:
 for label in ['a','b']:
  d=l/label
  if not d.exists():continue
  for p in sorted(d.iterdir()):
   if p.is_file() and p.suffix in ['.json','.jsonl','.log','.png','.txt','.err','.pid']:t.add(p,arcname=str(p.relative_to(l)),recursive=False)
  for p in sorted((d/'out').rglob('*.png')):t.add(p,arcname=str(p.relative_to(l)),recursive=False)
 for p in l.iterdir():
  if p.is_file() and (p.suffix in ['.py','.sh'] or p.name.endswith('-before.txt') or p.name in ['cursor-query.txt','cursor-probe.log','page.html']):t.add(p,arcname='setup/'+p.name,recursive=False)
print(hashlib.sha256(dst.read_bytes()).hexdigest(),dst.stat().st_size)
