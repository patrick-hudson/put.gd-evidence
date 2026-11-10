from pathlib import Path
import shutil,hashlib,json
r=Path('/tmp/c1364'); out=r/'packet';out.mkdir(exist_ok=False)
manifest={}
for p in list(r.rglob('*')):
 if not p.is_file() or p.is_symlink() or out in p.parents: continue
 rel=p.relative_to(r)
 if rel.parts[0] in ('pkg','lab'): continue
 manifest[str(rel)]={'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 if rel.name=='package.deb' or any(x in ('config','data','cache','state') for x in rel.parts): continue
 if rel.name=='marker.mkv' and rel.parts[0]!='a': continue
 dest=out/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
for name in ('record_run.py','virtual_mic.py','cover_player.py','rfb.py','summarize_run.py'):
 (out/'driver').mkdir(exist_ok=True);shutil.copy2(r/'lab'/name,out/'driver'/name)
(out/'host-source-manifest.json').write_text(json.dumps(manifest,indent=2))
print('packet',sum(p.stat().st_size for p in out.rglob('*') if p.is_file()))
