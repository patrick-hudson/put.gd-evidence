from pathlib import Path
import sys,shlex
sys.path.insert(0,'/home/patrick/work/s3lab/tools/lab');import lab
lab.overlay_cleanup.ROOT=Path('/home/patrick/work/put.gd');run=Path('/home/patrick/work/put.gd/work/lab-runs/s3b2');P=Path('/home/patrick/work/s3a')
for n in ['timer-case.py','timer-oracle-steady.py','switch-oracle.py','v2-cases.py','late_fixture-v2.py','warning-proof.py','warning_fixture.py','payload-proof.py']:lab.put(run,Path('/home/patrick/work/s3guest-b')/n,'/home/lab/work/s3a/'+n)
for args in [['timer-case.py'],['warning-proof.py','b'],['v2-cases.py']]:
 name='final-'+args[0];cmd='cd /home/lab/work/s3a && set +e; python3 '+shlex.join(args)+' > /home/lab/work/s3a/'+name+'.console 2>&1; code=$?; cat /home/lab/work/s3a/'+name+'.console; echo HARNESS_EXIT:$code'
 print('START',args,flush=True);data=lab.guest_session(run,cmd,timeout=1000);(P/('budgie-'+name+'.console')).write_text(data);print(data[-1800:],flush=True)
