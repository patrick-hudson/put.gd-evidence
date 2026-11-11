from control import *
import hashlib,shlex
k=sys.argv[1];remote='/home/patrick/work/scn/ev/'+k+('cr2' if k=='k' else 'cn')
code="from pathlib import Path;import hashlib,json;p=Path(%r);m={str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in p.rglob('*') if f.is_file() and f.name not in ['all-sha256.json','workstation-verified-full.json']};(p/'all-sha256.json').write_text(json.dumps(m,indent=2))"%remote
ssh('d69','python3 -c '+shlex.quote(code),check=True)
opts=['-i','/home/patrick/.ssh/awskey_110724','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/d69/known_hosts']
subprocess.run(['scp','-r',*opts,'patrick@192.168.68.69:'+remote,str(BASE/'guests')],check=True)
p=BASE/'guests'/(k+('cr2' if k=='k' else 'cn'));m=json.loads((p/'all-sha256.json').read_text());assert all(hashlib.sha256((p/n).read_bytes()).hexdigest()==s for n,s in m.items());ack={'verified':True,'files':len(m),'manifestSha256':hashlib.sha256((p/'all-sha256.json').read_bytes()).hexdigest()};(p/'workstation-verified-full.json').write_text(json.dumps(ack,indent=2));put('d69',p/'workstation-verified-full.json',remote+'/workstation-verified-full.json');print(k,ack)
