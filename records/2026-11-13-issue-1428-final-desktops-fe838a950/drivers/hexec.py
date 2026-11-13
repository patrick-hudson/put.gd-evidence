import subprocess,sys
from pathlib import Path
r=Path('/home/patrick/work/a1428/r/work/lab-runs/h1')
a=['-i',str(r/'identity'),'-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(r/'known_hosts')]
if sys.argv[1]=='--copy': c=['scp','-P','22530']+a+sys.argv[2:-1]+['lab@127.0.0.1:'+sys.argv[-1]]
elif sys.argv[1]=='--get':c=['scp','-P','22530']+a+['lab@127.0.0.1:'+sys.argv[2],sys.argv[3]]
else:c=['ssh','-p','22530']+a+['lab@127.0.0.1']+sys.argv[1:]
sys.exit(subprocess.run(c).returncode)
