from pathlib import Path
import json,hashlib,shutil,sys
r=Path.home()/'work/r9b';o=r/'public';o.mkdir(exist_ok=True,mode=0o700)
for p in r.glob('*.py'):shutil.copy2(p,o/p.name)
for d in r.iterdir():
 if d.is_dir() and (d/'results.json').exists():
  dst=o/d.name;dst.mkdir(exist_ok=True)
  for f in d.glob('*.json'):shutil.copy2(f,dst/f.name)
  if (d/'frames').exists():
   for f in (d/'frames').glob('*.png'):
    (dst/'frames').mkdir(exist_ok=True);shutil.copy2(f,dst/'frames'/f.name)
  for f in (d/'logs').glob('df-*'):
   shutil.copy2(f,dst/f.name)
for p in list(r.glob('*.json'))+list(r.glob('*.txt'))+list(r.glob('*.log')):shutil.copy2(p,o/p.name)
(o/'SHA256SUMS.json').write_text(json.dumps({str(p.relative_to(o)):hashlib.sha256(p.read_bytes()).hexdigest() for p in o.rglob('*') if p.is_file()},indent=1)+'\n')
