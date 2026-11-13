from pathlib import Path
import tarfile,json,hashlib
r=Path('/tmp/tp-hozfzxjt');assert (r/'workload.json').exists();p=Path.home()/'work/b1428';p.mkdir(mode=0o700,parents=True,exist_ok=True);src=Path.home()/'.local/share/putgd';dst=p/'data-tp-hozfzxjt-retained';assert src.exists() and not dst.exists();src.rename(dst)
out=Path('/home/lab/b1428/receipts-recovered.tar');assert not out.exists()
with tarfile.open(out,'w') as t:
 for f in r.rglob('*'):
  if f.is_file() and not f.is_symlink() and f.suffix in ('.json','.jsonl','.txt','.png'):t.add(f,arcname=str(f.relative_to('/tmp')),recursive=False)
print(json.dumps({'file':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'retained':str(dst),'reason':'Original driver completed measurements but receipt serialization followed a rename whose parent was absent; raw root and stdout preserved instead.'}))
