from pathlib import Path
import json
P=Path('/home/lab/work/s3a')
for d in sorted(P.glob('new-*')):
 f=d/'result.json'
 if d.is_dir() and f.exists():
  v=json.loads(f.read_text());print(json.dumps({'case':d.name,'state':v.get('capture',{}).get('state'),'end':v.get('capture',{}).get('endReason'),'height':v.get('capture',{}).get('height'),'oracle':v.get('oracle'),'error':v.get('error')}))
