import sys,json,subprocess,hashlib,tarfile,shutil
from pathlib import Path
host,run=sys.argv[1:];ip={'f44':'192.168.68.70','d69':'192.168.68.69'}[host];remote='/home/patrick/work/np1275/work/sp/';dest=Path('work/sp1275/export')/run;dest.mkdir(mode=0o700,parents=True,exist_ok=False)
scp=['scp','-i','/home/patrick/.ssh/awskey_110724','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/'+host+'/known_hosts']
for name in (run+'-evidence.tgz',run+'-export-ready.json'):subprocess.run([*scp,'patrick@'+ip+':'+remote+name,str(dest/name)],check=True)
ready=json.loads((dest/(run+'-export-ready.json')).read_text());archive=dest/(run+'-evidence.tgz');digest=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();assert digest(archive)==ready['archiveSha256']
extracted=dest/'files';extracted.mkdir()
with tarfile.open(archive) as tar:tar.extractall(extracted,filter='data')
assert {p.relative_to(extracted).as_posix() for p in extracted.rglob('*') if p.is_file()}==set(ready['files'])
assert all(digest(extracted/name)==value for name,value in ready['files'].items())
proof=dest/(run+'-workstation-verified.json');proof.write_text(json.dumps(dict(ready,verified=True),indent=2));proof.chmod(0o600)
subprocess.run([*scp,str(proof),'patrick@'+ip+':'+remote+proof.name],check=True);print('workstation export verified',run,len(ready['files']))
