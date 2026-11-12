import subprocess as s,pathlib,tarfile
b=pathlib.Path('/tmp/kr61');out=b/'2026-11-12-proton-k72-revoke-reliability'
ssh=['ssh','-i','/home/patrick/.ssh/awskey_110724','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','-o','ConnectTimeout=15','-o','UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/k72/known_hosts','patrick@192.168.68.72']
with (b/'logs.tar').open('wb') as f:s.run(ssh+['cd ~/work/kr61 && tar -cf - p*/profile/state/putgd/logs/*.jsonl'],stdout=f,check=True)
with tarfile.open(b/'logs.tar') as t:
 for m in t:
  (out/m.name.split('/')[0]/'app.jsonl').write_bytes(t.extractfile(m).read())
for name in ['2026-11-12T08-12-29Z-proton-release.json','2026-11-12T08-12-30Z-release.json']:
 (out/name).write_bytes(s.check_output(ssh+['cat ~/putgd-lab/locks/history/'+name]))
