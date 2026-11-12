from pathlib import Path
import sys,json
sys.path.insert(0,'/home/patrick/work/s3lab/tools/lab');import lab
r=Path('/home/patrick/work/put.gd/work/lab-runs/s3h');P=Path('/home/patrick/work/s3a')
lab.put(r,P/'omarchy-stop-attempt.py','/home/lab/omarchy-stop-attempt.py');print(lab.ssh(r,'python3 /home/lab/omarchy-stop-attempt.py',timeout=40),flush=True)
lab.put(r,P/'guest-omarchy-drivers-v2.tar','/home/lab/work/guest-drivers-v2.tar');print(lab.ssh(r,'umask 077; mkdir /home/lab/work/s3a; tar -xf /home/lab/work/guest-drivers-v2.tar -C /home/lab/work/s3a',timeout=30),flush=True)
print(lab.guest_session(r,'cd /home/lab/work/s3a && python3 -c "import pass2; pass2.setup()"',timeout=90),flush=True)
print(lab.guest_session(r,'cd /home/lab/work/s3a && python3 guest-native-suite.py',timeout=7200),flush=True)
