import sys,shlex,subprocess,hashlib,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'repo/tools/lab'));import lab
r=sys.argv[1];run=Path('/home/patrick/work/svm1398/repo/work/lab-runs')/r
script='''python3 - <<'INNER'
import tarfile,json,hashlib,os,subprocess
from pathlib import Path
p=Path.home()/'putgd-lab'; files=[]
for f in p.rglob('*'):
 if f.is_file() and ((f.parent.parent==p and f.name in ['result.json','capture.png','rpc.jsonl']) or (f.parent==p and f.suffix in ['.log'])):files.append(f)
with tarfile.open('/home/lab/vm-export.tar.gz','w:gz') as t:
 for f in files:t.add(f,arcname=str(f.relative_to(p)))
print(json.dumps({str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}))
INNER'''
(run/'export-hashes.json').write_text(lab.guest_session(run,script))
args=lab.ssh_args(run);args=args[:]; # use scp with production arguments translator
cmd=['scp','-i',str(run/'identity'),'-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(run/'known_hosts'),'-P',str(lab.state(run)['ssh_port']),'lab@127.0.0.1:/home/lab/vm-export.tar.gz',str(run/'export.tar.gz')]
subprocess.run(cmd,check=True)
print(r,hashlib.sha256((run/'export.tar.gz').read_bytes()).hexdigest())
