import subprocess,sys,json,traceback
from pathlib import Path
P=Path('/home/patrick/work/s3a');h=sys.argv[1]
for args in [['startcancel.py',h],['browsercases.py'],['capmore.py'],['notices.py',h],['newcases.py','f']]:
 with (P/(args[0]+'.console')).open('w') as log:
  r=subprocess.run(['python3',str(P/args[0]),*args[1:]],stdout=log,stderr=subprocess.STDOUT)
 print(args,r.returncode,flush=True)
subprocess.run(['python3',str(P/'verify-cancel-ui.py')])
