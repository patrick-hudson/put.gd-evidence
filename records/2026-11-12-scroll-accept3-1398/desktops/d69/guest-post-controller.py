from pathlib import Path
import sys,time,json
sys.path.insert(0,'/home/patrick/work/s3lab/tools/lab');import lab
P=Path('/home/patrick/work/s3a');r=Path('/home/patrick/work/put.gd/work/lab-runs')/sys.argv[1]
while lab.ssh(r,'if [ -f /home/lab/work/s3a/suite.done ]; then echo done; else echo wait; fi',timeout=15).strip()!='done':time.sleep(15)
for n in ['gtk-capfit-fixture.py','guest-capfit.py','notice-margin-oracle.py','browser-retry-after-tou.py']:
 lab.put(r,P/n,'/home/lab/work/s3a/'+n)
if sys.argv[1] in ['s3n','s3h']:print(lab.guest_session(r,'cd /home/lab/work/s3a && python3 browser-retry-after-tou.py',timeout=1800),flush=True)
cmd='cd /home/lab/work/s3a && set +e; python3 guest-capfit.py > capfit.console 2>&1; code=$?; cat capfit.console; echo CAPFIT_EXIT:$code; python3 notice-margin-oracle.py; touch post.done'
print(lab.guest_session(r,cmd,timeout=900),flush=True)
