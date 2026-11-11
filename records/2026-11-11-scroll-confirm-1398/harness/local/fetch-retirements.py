from control import *
import shlex,hashlib
opts=['-i','/home/patrick/.ssh/awskey_110724','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile=/home/patrick/work/put.gd/work/remote-builders/d69/known_hosts']
for run,ev in [('ocn','ocn'),('bcn','bcn'),('ncn','ncn'),('kcr2','kcr2'),('kcn','kcn-bootfail')]:
 dest=BASE/'guests'/ev;files={}
 for n in ['completion.json','retirement-summary.md','cleanup-manifest.json','cleanup-dry-run.json','cleanup-result.json']:files[n]='/home/patrick/work/scn/ev/'+ev+'/'+n
 files['overlay-cleanup.json']='/home/patrick/work/svm1398/repo/work/lab-runs/'+run+'/overlay-cleanup.json'
 code='from pathlib import Path;import json,hashlib;files='+repr(files)+';print(json.dumps({n:hashlib.sha256(Path(p).read_bytes()).hexdigest() for n,p in files.items()}))'
 m=json.loads(ssh('d69','python3 -c '+shlex.quote(code),check=True,capture_output=True,text=True).stdout)
 for n,remote in files.items():subprocess.run(['scp',*opts,'patrick@192.168.68.69:'+remote,str(dest/n)],check=True);assert hashlib.sha256((dest/n).read_bytes()).hexdigest()==m[n]
 (dest/'retirement-export-verified.json').write_text(json.dumps(m,indent=2));print(run,'retirement verified')
