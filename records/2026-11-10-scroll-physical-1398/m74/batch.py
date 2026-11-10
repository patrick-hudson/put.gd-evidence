import subprocess,json,sys
from pathlib import Path
p=Path('/tmp/sp1398')
for mode in sys.argv[1:]:
 subprocess.run(['python3',str(p/'campaign.py'),mode],timeout=300)
 f=p/mode/'result.json'
 if f.exists():
  o=json.loads(f.read_text());print(mode,o.get('pass'),o.get('error'),o.get('verification'),flush=True)
