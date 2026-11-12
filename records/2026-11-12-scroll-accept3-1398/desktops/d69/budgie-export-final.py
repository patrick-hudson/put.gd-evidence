from pathlib import Path
import sys,json,shlex
sys.path.insert(0,'/home/patrick/work/s3lab/tools/lab');import lab
lab.overlay_cleanup.ROOT=Path('/home/patrick/work/put.gd');r=Path('/home/patrick/work/put.gd/work/lab-runs/s3b2');P=Path('/home/patrick/work/s3a')
for src,dest in [('guest-late-fixture-current.py','late_fixture.py'),('guest-late-ruler-v3.py','late-ruler-v3.py'),('guest-replay-all-late.py','replay-all-late.py'),('guest-export-final.py','export-evidence.py')]:lab.put(r,P/src,'/home/lab/work/s3a/'+dest)
print(lab.guest_session(r,'cd /home/lab/work/s3a && python3 late-ruler-v3.py && python3 replay-all-late.py && python3 export-evidence.py',timeout=1500),flush=True)
e=P/'budgie-export';e.mkdir(exist_ok=True)
lab.get(r,'/home/lab/work/s3-budgie-evidence.tar.gz',e/'guest-final-evidence.tar.gz',timeout=300)
print('EXPORTED',flush=True)
