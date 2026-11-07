from pathlib import Path
import subprocess,time
r=Path.home()/'work/f9t'
while Path('/proc/1855747').exists():time.sleep(2)
for args in [['history6.py','no','redo','history8'],['score.py','redo','still']]:
 with open(r/(args[0]+'.finish.log'),'w') as log:subprocess.run(['python3',str(r/args[0])]+args[1:],stdout=log,stderr=log)
