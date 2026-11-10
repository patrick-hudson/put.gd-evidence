import os,stat,sys,json
from pathlib import Path
root=Path(sys.argv[1]);assert str(root) in ('/tmp/h396k','/tmp/h396m')
assert root.is_dir() and not root.is_symlink() and root.stat().st_uid==os.getuid()
assert not (root/'runtime/putgd/session.sock').exists()
for name in ('pid','pid2'):
 if (root/name).exists():
  pid=int((root/name).read_text())
  assert not Path('/proc/'+str(pid)).exists(), 'Resident still alive'
paths=list(root.rglob('*'))
for p in paths:
 assert p.lstat().st_uid==os.getuid(), 'Unexpected owner'
for p in sorted(paths,key=lambda p:len(p.parts),reverse=True):
 if p.is_dir() and not p.is_symlink():p.rmdir()
 else:p.unlink()
root.rmdir();print(json.dumps({'removedPrivateRoot':str(root),'residentPidsGone':True,'filesRemoved':len(paths)}))
