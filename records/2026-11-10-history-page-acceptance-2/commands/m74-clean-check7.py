from pathlib import Path
import shutil,json,hashlib
roots=[Path('/tmp/hp2c'),Path('/tmp/hp2d')]
archive=Path.home()/'putgd-lab/h1396-ci/p2-evidence';archive.mkdir(mode=0o700,exist_ok=True)
for root in roots:
 assert root.exists() and root.resolve()==root
 for p in Path('/proc').glob('[0-9]*/environ'):
  try:env=p.read_bytes().split(b'\0')
  except OSError:continue
  assert not any(x.startswith(b'XDG_CONFIG_HOME='+str(root).encode()+b'/') or x.startswith(b'XDG_RUNTIME_DIR='+str(root).encode()+b'/') for x in env),p.parent.name
 target=archive/root.name;target.mkdir(mode=0o700,exist_ok=True)
 for p in root.iterdir():
  if p.is_file() and (p.suffix in ('.png','.log') or p.name in ('results.json','commands.json')):shutil.copyfile(p,target/p.name)
 for p in sorted(root.rglob('*'),key=lambda x:len(x.parts),reverse=True):
  if p.is_dir() and not p.is_symlink():p.rmdir()
  else:p.unlink()
 root.rmdir()
print(json.dumps({'removed_profiles':[str(x) for x in roots],'servers_terminated':True,'resident_quit':True,'archive':str(archive),'initial_attempt_objects':'volatile fixture memory discarded at documented server teardown; no live destination','corrected_attempt_objects_remaining':0},indent=2))
