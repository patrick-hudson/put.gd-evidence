"""Wide row search for actual missing content; runs on a builder after captures."""
import json,sys
from pathlib import Path
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
d=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(exist_ok=True)
a=np.asarray(Image.open(d/'capture.png').convert('L'),dtype=np.int16);b=np.asarray(Image.open(d/'reference.png').convert('L'),dtype=np.int16)
lo,hi=200,min(a.shape[1],b.shape[1])-250
cols=np.arange(lo,hi,32);rows=[]
for y in [1000,3000,5000,8000,10000,15000,20000,25000,30000,35000,a.shape[0]-200]:
 if y+64>a.shape[0]:continue
 stripe=a[y:y+64,cols];ys=np.arange(max(0,y-8500),min(b.shape[0]-64,y+8500),8)
 scores=np.empty(len(ys))
 for k in range(0,len(ys),128):
  z=ys[k:k+128];v=b[z[:,None,None]+np.arange(64)[None,:,None],cols[None,None,:]];scores[k:k+128]=np.abs(v-stripe).mean(axis=(1,2))
 candidates=set()
 for z in ys[np.argsort(scores)[:8]]:
  candidates.update(range(max(0,int(z)-9),min(b.shape[0]-64,int(z)+10)))
 best=min(candidates,key=lambda z:float(np.abs(a[y:y+64,lo:hi]-b[z:z+64,lo:hi]).mean()))
 diff=float(np.abs(a[y:y+64,lo:hi]-b[best:best+64,lo:hi]).mean());rows.append({'captureY':y,'referenceY':best,'offset':best-y,'meanGreyDifference':diff})
 if y in [3000,5000,8000,15000,30000]:
  ia=Image.open(d/'capture.png').convert('RGB');ib=Image.open(d/'reference.png').convert('RGB');w=min(1400,hi-lo);h=400
  canvas=Image.new('RGB',(2*w,h),'#eeeeee');canvas.paste(ia.crop((lo,max(0,y-100),lo+w,max(0,y-100)+h)),(0,0));canvas.paste(ib.crop((lo,max(0,best-100),lo+w,max(0,best-100)+h)),(w,0));canvas.save(out/f'seam-{y}-to-{best}.png')
(out/'wide-row-check.json').write_text(json.dumps({'run':str(d),'capturedHeight':a.shape[0],'referenceHeight':b.shape[0],'rows':rows,'method':'Unmodified capture beside browser reference. Search +/-8500 rows, sampled x every32 then full-width 64-row mean-grey refinement. No score threshold changed.'},indent=1));print(json.dumps(rows),flush=True)
