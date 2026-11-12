from pathlib import Path
import json,numpy as np
from PIL import Image
P=Path('/home/lab/work/s3a');out={}
for d in P.glob('cancel-*'):
 f=d/'screen-2s-later.png'
 if not f.exists():continue
 a=np.asarray(Image.open(f).convert('RGB')).astype('int16');mask=np.zeros(a.shape[:2],bool);mask[194:806,94:1066]=True;mask[200:800,100:1060]=False;mask[780:830,1040:1090]=False;b=(np.abs(a-102)>12).any(axis=2)&mask;y,x=np.where(b);v={'raw':json.loads((d/'ui-verification.json').read_text()),'ringDifferenceBounds':None if not len(x) else [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)],'pointerExclusionPendingVisualReview':bool(len(x))};(d/'pointer-audit.json').write_text(json.dumps(v,indent=2));out[d.name]=v
 if len(x):Image.open(f).crop((60,370,125,445)).resize((520,600)).save(P/'cancel-cursor-review.png')
(P/'cancel-pointer-audit.json').write_text(json.dumps(out,indent=2));print(out,flush=True)
