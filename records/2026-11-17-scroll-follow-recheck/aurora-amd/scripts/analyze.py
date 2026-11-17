from pathlib import Path
import json,subprocess,sys,hashlib
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
P=Path.cwd()
for d in sorted((P/'runs').iterdir()):
 if not(d/'capture.png').exists()or not(d/'reference.png').exists():continue
 height=Image.open(d/'capture.png').height
 rows=list(range(300,height-64,2500))+[max(0,height-200)]
 if not(d/'where.log').exists():
  with(d/'where.log').open('w')as f:subprocess.run([sys.executable,str(P/'where.py'),str(d),*map(str,rows)],stdout=f,stderr=subprocess.STDOUT,check=True)
 hashes={f.name:{'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size,'size':list(Image.open(f).size)}for f in d.glob('*.png')};(d/'image-hashes.json').write_text(json.dumps(hashes,indent=1))
 print(d.name,(d/'where.log').read_text(),flush=True)
