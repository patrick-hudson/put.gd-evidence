import sys,subprocess,json,tarfile,hashlib
from pathlib import Path
from vm_remote import SSH,BASE
p=Path(__file__).parent
for r in ['o','b','n','k']:
 d=p/(r+'-final');d.mkdir(exist_ok=True)
 for name in ['export.tar.gz','export-hashes.json','state.json','final-identity.json']:
  args=['scp']+SSH[1:-1]+['patrick@192.168.68.69:'+BASE+'/work/lab-runs/'+r+'/'+name,str(d/name)]
  subprocess.run(args,check=True)
 for name in [r+'-mcp.json',r+'-mcp-harness-failed.json']:
  subprocess.run(['scp']+SSH[1:-1]+['patrick@192.168.68.69:/home/patrick/work/svm1398/'+name,str(d/name)],check=True)
 with tarfile.open(d/'export.tar.gz') as t:t.extractall(d/'results',filter='data')
 hashes=json.loads((d/'export-hashes.json').read_text())
 assert all(hashlib.sha256((d/'results'/name).read_bytes()).hexdigest()==sha for name,sha in hashes.items())
 print(r,'verified',len(hashes),'files')
