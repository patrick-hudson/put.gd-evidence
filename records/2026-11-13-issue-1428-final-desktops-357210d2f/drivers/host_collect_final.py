from pathlib import Path
import json,tarfile,hashlib,os,sys
r=Path(sys.argv[1]);assert r.parent==Path('/tmp') and r.name.startswith('tp-') and r.stat().st_uid==os.getuid();d=json.loads((r/'receipt.json').read_text());assert d.get('desktop','').endswith('-8a') or (d.get('desktop','').endswith('-final3572') and d.get('build',{}).get('gitCommit')=='357210d2f1cb7b65f77166e34eb535d42e497fd0')
o=Path.home()/'work/b1428'/sys.argv[2];assert not o.exists()
with tarfile.open(o,'w') as t:
 for f in r.rglob('*'):
  if f.is_file() and not f.is_symlink() and f.suffix in ('.json','.jsonl','.png','.txt'):t.add(f,arcname=str(f.relative_to('/tmp')),recursive=False)
print(json.dumps({'path':str(o),'sha256':hashlib.sha256(o.read_bytes()).hexdigest(),'desktop':d['desktop']}))
