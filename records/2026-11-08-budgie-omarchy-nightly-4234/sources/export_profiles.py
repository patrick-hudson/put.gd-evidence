import subprocess,shlex,json,hashlib,tarfile,sys
from pathlib import Path,PurePosixPath
host,rid=sys.argv[1:];ip='192.168.68.'+('70' if host=='f44' else '69');base='/home/patrick/work/np1275/work/np/'+rid
opts=['-i','/home/patrick/.ssh/awskey_110724','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/'+host+'/known_hosts']
code='''import json,hashlib,tarfile
from pathlib import Path
out=Path(BASE);config=json.loads((out/'run-config.json').read_text());source=out/'profile-policy-original' if out.name=='r1' else Path(config['profiles'])
manifest=json.loads((out/'profile-sha256.json').read_text())
for name,digest in manifest.items():
 p=source/name;assert p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(source.resolve());assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
archive=out/'profiles-export.tgz'
if not archive.exists():
 with tarfile.open(archive,'x:gz') as t:
  for name in manifest:t.add(source/name,arcname=name,recursive=False)
print(json.dumps({'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files':manifest}))
'''.replace('BASE',repr(base))
proof=json.loads(subprocess.check_output(['ssh','-n',*opts,'patrick@'+ip,'python3 -c '+shlex.quote(code)],text=True))
local=Path('work/np1275/export')/rid;local.mkdir(mode=0o700,parents=True,exist_ok=True);archive=local/'profiles-export.tgz'
subprocess.run(['scp','-q',*opts,'patrick@'+ip+':'+base+'/profiles-export.tgz',str(archive)],check=True)
assert hashlib.sha256(archive.read_bytes()).hexdigest()==proof['sha256']
record=Path('work/np1275/evidence/2026-11-08-budgie-omarchy-nightly-4234');dest=record/'profiles'/rid
with tarfile.open(archive) as t:
 for m in t.getmembers():
  name=PurePosixPath(m.name);assert m.isfile() and not name.is_absolute() and '..' not in name.parts
  data=t.extractfile(m).read();assert hashlib.sha256(data).hexdigest()==proof['files'][m.name]
  p=dest/m.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
(dest/'export-proof.json').write_text(json.dumps(proof,indent=2));print('verified exact profile sources',host,rid)
