import sys,time,subprocess
from pathlib import Path
r=Path.home()/'work/f9t';pid=int(sys.argv[1]);real=sys.argv[2];pat=sys.argv[3]
while Path('/proc/%d'%pid).exists():time.sleep(2)
for args in [['history3.py',real,pat,'history3'],['parity2.py',pat],['analyze2.py',pat,'still','av2']]+([['vaapi2.py']] if pat=='p6' else []):
 with open(r/(args[0]+'.log'),'w') as log:subprocess.run(['python3',str(r/args[0])]+args[1:],stdout=log,stderr=log)
