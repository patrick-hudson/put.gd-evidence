from pathlib import Path
import json,shutil,hashlib,os
r=Path.home()/'work/f9t';out=r/'export';out.mkdir(mode=0o700,exist_ok=True)
def clean(x):
 if isinstance(x,dict):return {k:clean(v) for k,v in x.items() if k not in ['credentials','png']}
 if isinstance(x,list):return [clean(v) for v in x]
 return x
def cp(p,rel):
 d=out/rel;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,d)
for p in r.iterdir():
 if p.is_dir() and p.name!='export':
  j=p/'results.json'
  if j.exists():
   dest=out/p.name/'results.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(clean(json.loads(j.read_text())),indent=1)+'\n')
  for f in (p/'frames').glob('*.png') if (p/'frames').exists() else []:cp(f,p.name+'/frames/'+f.name)
 if p.is_file() and (p.suffix=='.py' or p.suffix=='.json' or p.name=='identity.txt'):cp(p,p.name)
for p in (r/'vaapi2').glob('*.png') if (r/'vaapi2').exists() else []:cp(p,'vaapi2/'+p.name)
for f in ['record_run.py','cover_player.py','record_x13.py','cover_x11.py']:
 p=r/'tools/lab'/f
 if p.exists():cp(p,'drivers/'+f)
manifest={str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file()}
(out/'SHA256SUMS.json').write_text(json.dumps(manifest,indent=1)+'\n')
print(len(manifest),'files exported')
