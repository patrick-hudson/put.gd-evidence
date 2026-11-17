from pathlib import Path
import json,subprocess,sys,hashlib,time
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
import score
P=Path.cwd();summary=[]
for d in sorted((P/'runs').iterdir()):
 if not(d/'result.json').exists():continue
 r=json.loads((d/'result.json').read_text());c=r.get('capture')or{}
 if not(d/'capture.png').exists():continue
 assert hashlib.sha256((d/'capture.png').read_bytes()).hexdigest()==c['result']['sha256']
 h=Image.open(d/'capture.png').height
 if not(d/'where.log').exists():
  rows=list(range(300,h-64,2500))+[max(0,h-200)]
  with(d/'where.log').open('w')as f:subprocess.run([sys.executable,str(P/'where.py'),str(d),*map(str,rows)],stdout=f,stderr=subprocess.STDOUT,check=True)
 if not(d/'score.json').exists():(d/'score.json').write_text(json.dumps(score.one(d),indent=1))
 with(d/'unwritten.log').open('w')as f:subprocess.run([sys.executable,str(P/'unwritten.py'),str(d)],stdout=f,check=True)
 hashes={f.name:{'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size,'size':list(Image.open(f).size)}for f in d.glob('*.png')};(d/'image-hashes.json').write_text(json.dumps(hashes,indent=1))
 row=dict(name=d.name,score=json.loads((d/'score.json').read_text()),where=(d/'where.log').read_text(),unwritten=(d/'unwritten.log').read_text());summary.append(row);(P/'scoring-summary.json').write_text(json.dumps(summary,indent=1));print(json.dumps(row),flush=True)
