import time,subprocess,sys
from pathlib import Path
p=Path('/home/patrick/work/sa2')
while not (p/'extra.done').exists():
 if (p/'extra.error').exists():raise RuntimeError('extra cases failed; preserve and inspect')
 time.sleep(3)
for n in ['user-row.py','notices.py']:
 subprocess.run(['python3',str(p/n),sys.argv[1]],check=True)
