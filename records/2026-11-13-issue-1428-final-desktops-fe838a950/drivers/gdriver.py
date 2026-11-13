import subprocess,sys
from pathlib import Path
r=Path('/home/patrick/work/a1428/r/work/lab-runs/g2')
q=str(r/'qmp.sock');assert len(q.encode())<=107
args=['ssh','-p','22528','-i',str(r/'identity'),'-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(r/'known_hosts'),'-o','ExitOnForwardFailure=yes','-o','StreamLocalBindUnlink=yes','-R','/home/lab/a1428-qmp.sock:'+q,'-R','127.0.0.1:5989:127.0.0.1:5988','lab@127.0.0.1']
sys.exit(subprocess.run(args+sys.argv[1:]).returncode)
