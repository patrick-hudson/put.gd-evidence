import time,subprocess,sys
from pathlib import Path
p=Path('/home/patrick/work/sr8')
while not (p/'campaign.done').exists():
 if (p/'campaign.error').exists():raise RuntimeError('regression failed; preserve and inspect')
 time.sleep(3)
subprocess.run(['python3',str(p/'review-extra.py'),sys.argv[1]],check=True)
