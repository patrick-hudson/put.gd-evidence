import json,re,sys
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from PIL import Image
import score as S
Image.MAX_IMAGE_PIXELS=None
root=Path(sys.argv[1]);out=[]
for d in sorted(root.iterdir()):
 if not (d/'result.json').exists():continue
 r=json.loads((d/'result.json').read_text());c=r.get('capture') or {}
 if r.get('mode')!='user' or 'inside' in d.name or c.get('endReason')!='done':continue
 if not (d/'pre-done-viewport.png').exists():out.append({'name':d.name,'missingPreDoneViewport':True,'note':'Post-Done screenshots may contain hover popups appearing after capture finished and do not establish a row8 failure.'});continue
 view=np.asarray(Image.open(d/'pre-done-viewport.png').convert('RGB'),dtype=np.int16)
 im=Image.open(d/'capture.png').convert('RGB');h=min(r['rect'][3],view.shape[0],im.height)
 image=np.asarray(im.crop((0,im.height-h,im.width,im.height)),dtype=np.int16)
 # This matrix uses the full measured browser viewport. The final h rows of the
 # saved image must match that current viewport, outside its fixed/sticky boxes.
 assert image.shape[1]==view.shape[1],(d,image.shape,view.shape)
 ref=S.S.Reference.__new__(S.S.Reference);ref.pixels=view[-h:];ref.rects=[]
 pins=[{'elements':json.loads((d/'pre-done-pinned.json').read_text())}]
 for sample in pins:
  for e in sample['elements']:
   x,y,w,eh=e['rect'];x0=max(0,int(x)-12);x1=min(view.shape[1],int(x+w+.999)+12);y0=max(0,int(y)-12);y1=min(h,int(y+eh+.999)+12)
   if x1>x0 and y1>y0:ref.rects.append((x0,y0,x1,y1))
 ref.dx=0;ref.reachable=None
 bands=S.tolerant(ref,image)
 info=json.loads((d/'pre-done-viewport-info.json').read_text());text=(d/'helper.log').read_text()
 out.append({'name':d.name,'bandsEqualTotal':bands,'lastRows':h,'viewportAtDone':info,'rowsAtDone':c.get('rowsAtDone'),'freshFrameBeforeFinish':'scroll fresh frame:' in text,'doneFreshRowsLogged':bool(re.search(r"Done.s fresh frame added \d+ rows",text)),'method':'Compare final saved h rows with browser current viewport screenshot taken immediately BEFORE scroll.stop; original tolerant bands, current visible fixed/sticky DOM rectangles clipped to viewport plus scorer 12px shadow. No later full-page reference used.'})
print(json.dumps(out,indent=1))
