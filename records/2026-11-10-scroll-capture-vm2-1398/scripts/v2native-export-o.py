import sys,shlex,tarfile
from pathlib import Path
sys.path.insert(0,'/home/patrick/work/svm1398/repo/tools/lab');import lab
base=Path('/home/patrick/work/svm1398');r=base/'repo/work/lab-runs/of';o=base/'v2evidence/o'
code="""from pathlib import Path
import tarfile
p=Path('/tmp/v2n')
with tarfile.open('/home/lab/v2-native-failed.tgz','w:gz') as t:
 for n in ['cases','archive','helper.log','resident.log','version.json','rpc.jsonl','capabilities.json','socket-preflight.json']:
  if (p/n).exists():t.add(p/n,arcname=n)
"""
lab.guest_session(r,'python3 -c '+shlex.quote(code));lab.get(r,'/home/lab/v2-native-failed.tgz',o/'native-failed.tgz');(o/'native').mkdir(exist_ok=True);tarfile.open(o/'native-failed.tgz').extractall(o/'native',filter='data')
