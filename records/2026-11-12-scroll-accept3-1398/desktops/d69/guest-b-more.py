from pathlib import Path
import sys,subprocess,json,shlex
sys.path.insert(0,'/home/patrick/work/s3lab/tools/lab');import lab
lab.overlay_cleanup.ROOT=Path('/home/patrick/work/put.gd');run=Path('/home/patrick/work/put.gd/work/lab-runs/s3b2');out=Path('/home/patrick/work/s3a')
for args in [['more-a.py'],['next-native.py','b'],['newcases.py','a','b','c'],['latecases.py'],['minimap-repeat.py','minimap']]:
 cmd='cd /home/lab/work/s3a && python3 '+shlex.join(args);print('START',args,flush=True)
 try:
  data=lab.guest_session(run,cmd,timeout=1800);(out/('budgie-'+args[0]+'.console')).write_text(data);print('END',args,data[-1500:],flush=True)
 except Exception as ex:
  (out/('budgie-'+args[0]+'.error')).write_text(str(ex));print('ERROR',args,str(ex),flush=True)
print('guest batches done',flush=True)
