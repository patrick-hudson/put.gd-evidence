from pathlib import Path
import sys,shlex
sys.path.insert(0,'/home/patrick/work/s3lab/tools/lab');import lab
lab.overlay_cleanup.ROOT=Path('/home/patrick/work/put.gd');run=Path('/home/patrick/work/put.gd/work/lab-runs/s3b2');P=Path('/home/patrick/work/s3a')
for args in [['newcases.py','a','b','c','f'],['latecases.py'],['timer-oracle-steady.py'],['switch-oracle.py','/home/lab/work/s3a']]:
 name='retry-'+args[0];command='cd /home/lab/work/s3a && python3 '+shlex.join(args)+' > '+name+'.console 2>&1; status=$?; cat '+name+'.console; echo HARNESS_EXIT:$status'
 print('START',args,flush=True);data=lab.guest_session(run,command,timeout=1800);(P/('budgie-'+name+'.console')).write_text(data);print(data[-1800:],flush=True)
