from pathlib import Path
import os,json,shutil,hashlib
roots=['hp2f','hp2g','hp2h','hp2j','hp2l','hp2n','hp2q','hp2s','hp2w','hp2y','hp2z','hp3a']
archive=Path.home()/'putgd-lab/h1396-ci/p2-evidence';archive.mkdir(mode=0o700,exist_ok=True)
# No process may retain one of these private profiles.
found=[]
for p in Path('/proc').glob('[0-9]*/environ'):
 try:data=p.read_bytes().split(b'\0')
 except OSError:continue
 if any(any(x.startswith(k+b'=/tmp/'+r.encode()+b'/') for k in (b'XDG_CONFIG_HOME',b'XDG_RUNTIME_DIR')) for r in roots for x in data):found.append(p.parent.name)
assert not found,found
for name in roots:
 root=Path('/tmp')/name
 if not root.exists():continue
 target=archive/name;target.mkdir(mode=0o700,exist_ok=True)
 for p in root.iterdir():
  if p.is_file() and p.suffix in ('.json','.log','.png') and p.name!='synthetic.png':shutil.copyfile(p,target/p.name)
 # Exact owned profile files, bottom-up; no recursive shell removal.
 for p in sorted(root.rglob('*'),key=lambda p:len(p.parts),reverse=True):
  if p.is_dir() and not p.is_symlink():p.rmdir()
  else:p.unlink()
 root.rmdir()
print(json.dumps({'private_profiles_removed':roots,'processes_remaining':found,'archive':str(archive),'unverified_crops_kept_on_host_only':['hp2h'],'packages_installed':[]},indent=2))
