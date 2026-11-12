from pathlib import Path
import json,hashlib,shutil
P=Path('/home/patrick/work/s3a');O=P.parent/'scroll-accept3-guests-private';O.mkdir(mode=0o700,exist_ok=False);out=[]
for tag in ['budgie','neon','omarchy','kubuntu']:
 src=P/(tag+'-export');dst=O/tag;dst.mkdir(mode=0o700)
 for f in sorted(src.rglob('*')):
  assert not f.is_symlink(),f
  if not f.is_file():continue
  q=dst/f.relative_to(src);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,q);q.chmod(0o600);a=hashlib.file_digest(f.open('rb'),'sha256').hexdigest();b=hashlib.file_digest(q.open('rb'),'sha256').hexdigest();assert a==b;out.append({'source':str(f),'preserved':str(q),'sha256':a,'bytes':q.stat().st_size})
(O/'restore-index.json').write_text(json.dumps(out,indent=1));print({'preservedRoot':str(O),'files':len(out),'bytes':sum(x['bytes'] for x in out)},flush=True)
