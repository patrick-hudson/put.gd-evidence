from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
P=Path('/home/lab/work/s3a');out={}
for d in sorted(P.glob('notice-*')):
 f=d/'capture.png'
 if not f.exists():continue
 im=np.asarray(Image.open(f).convert('RGB'));margin=im[:,944:];diff=np.any(margin!=250,axis=2);ys,xs=np.where(diff);timing=json.loads((d/'timing.json').read_text());notify=timing.get('observedNotify')
 v={'method':'Every RGB pixel in the fixture blank right margin x944..1899 must equal generator RGB250; actual putgd Notify call timestamp retained','mismatchPixels':int(diff.sum()),'bbox':None if not diff.any() else [int(xs.min()+944),int(ys.min()),int(xs.max()+945),int(ys.max()+1)],'notifyObserved':notify is not None,'observedDelayMs':None if not notify else round(1000*(timing['prepareCalled']-notify['time']),3),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
 (d/'notice-margin-verification.json').write_text(json.dumps(v,indent=2));out[d.name]=v
(P/'notice-margin-summary.json').write_text(json.dumps(out,indent=2));print(out,flush=True)
