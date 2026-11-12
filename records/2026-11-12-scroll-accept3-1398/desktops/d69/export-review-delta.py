from pathlib import Path
import tarfile,sys,hashlib,json
P=Path('/home/patrick/work/s3a');host=sys.argv[1];fs=[f for f in P.glob('*-fixture.log') if f.is_file() and not f.is_symlink()]
for d in P.iterdir():
 if d.is_dir() and (d/'result.json').exists():fs += [f for f in d.glob('generator*.png') if f.is_file() and not f.is_symlink()]
a=P.parent/('scroll-accept3-'+host+'-review-delta.tar.gz')
with tarfile.open(a,'w:gz') as t:
 for f in fs:t.add(f,arcname=str(f.relative_to(P)),recursive=False)
r={'path':str(a),'sha256':hashlib.file_digest(a.open('rb'),'sha256').hexdigest(),'files':len(fs)};(P/('review-delta-'+host+'.json')).write_text(json.dumps(r,indent=2));print(r,flush=True)
