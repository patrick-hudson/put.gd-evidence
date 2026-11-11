import sys,tarfile,shlex,time
from pathlib import Path
sys.path.insert(0,'/home/patrick/work/svm1398/repo/tools/lab');import lab
base=Path('/home/patrick/work/svm1398');k=sys.argv[1];r=base/'repo/work/lab-runs'/(k+'f');o=base/'v2evidence'/k
code="""from pathlib import Path
import tarfile
p=Path('/tmp/v2n')
with tarfile.open('/home/lab/v2-native2.tgz','w:gz') as t:
 for n in ['cases','archive','helper.log','resident.log','version.json','rpc.jsonl','capabilities.json','socket-preflight.json','fixture.log']:
  if (p/n).exists():t.add(p/n,arcname=n)
"""
print(lab.guest_session(r,'python3 -c '+shlex.quote(code)),flush=True);lab.get(r,'/home/lab/v2-native2.tgz',o/'native2.tgz');(o/'native').mkdir(exist_ok=True);tarfile.open(o/'native2.tgz').extractall(o/'native',filter='data')
lab.put(r,base/'v2start.py','/home/lab/v2start.py');print(lab.guest_session(r,'python3 /home/lab/v2start.py'),flush=True)
import subprocess
subprocess.run(['python3',str(base/'v2notice.py'),k],check=True)
