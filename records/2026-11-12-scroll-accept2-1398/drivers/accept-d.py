import time,subprocess,sys
from pathlib import Path
p=Path('/home/patrick/work/sa2')
while not (p/'probes.done').exists():time.sleep(2)
for name in ['user-row.py','notices.py']:
 r=subprocess.run(['python3',str(p/name),sys.argv[1]],stdout=open(p/(name+'.console'),'w'),stderr=subprocess.STDOUT)
(p/'presentation.done').write_text('done')
