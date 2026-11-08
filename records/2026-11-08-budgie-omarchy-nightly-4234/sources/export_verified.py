import json,subprocess,hashlib,sys,shlex
from pathlib import Path
host,rid=sys.argv[1:];ip='192.168.68.'+('70' if host=='f44' else '69');base='/home/patrick/work/np1275/work/np/'+rid
opts=['-i','/home/patrick/.ssh/awskey_110724','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/'+host+'/known_hosts']
local=Path('work/np1275/export')/rid;local.mkdir(mode=0o700,parents=True,exist_ok=True)
ready=json.loads(subprocess.check_output(['ssh','-n',*opts,'patrick@'+ip,'cat '+shlex.quote(base+'/export-ready.json')],text=True))
for name,want in ready['files'].items():
 target=local/name
 if not target.exists():subprocess.run(['scp','-q',*opts,'patrick@'+ip+':'+base+'/'+name,str(target)],check=True)
 assert hashlib.sha256(target.read_bytes()).hexdigest()==want
(local/'export-ready.json').write_text(json.dumps(ready,indent=2))
proof=dict(runId=ready['runId'],verified=True,files=ready['files']);p=local/'workstation-export-verified.json';p.write_text(json.dumps(proof,indent=2));p.chmod(0o600)
subprocess.run(['scp','-q',*opts,str(p),'patrick@'+ip+':'+base+'/workstation-export-verified.json'],check=True)
print('Verified workstation export',rid,ready['runId'])
