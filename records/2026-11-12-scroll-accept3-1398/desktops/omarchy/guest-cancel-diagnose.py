from pathlib import Path
from PIL import Image
import numpy as np,json
P=Path('/home/lab/work/s3a');out={}
for d in P.glob('cancel-*'):
 f=d/'screen-2s-later.png'
 if not f.exists():continue
 im=np.asarray(Image.open(f).convert('RGB')).astype('int16');mask=np.zeros(im.shape[:2],bool);mask[194:806,94:1066]=True;mask[200:800,100:1060]=False;mask[780:830,1040:1090]=False;bad=mask&np.any(np.abs(im-102)>12,axis=2);ys,xs=np.where(bad)
 if len(xs):
  v={'pixels':len(xs),'bbox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'colors':np.unique(im[bad],axis=0).tolist()};out[d.name]=v
  Image.open(f).crop((int(xs.min())-15,int(ys.min())-15,int(xs.max())+16,int(ys.max())+16)).save(d/'ring-difference-crop.png')
(P/'cancel-ring-diagnose.json').write_text(json.dumps(out,indent=2));print(out,flush=True)
