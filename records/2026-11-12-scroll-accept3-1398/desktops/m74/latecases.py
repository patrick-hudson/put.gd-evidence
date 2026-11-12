import pass2 as p,fix6 as f,json
from PIL import Image
import numpy as np
for kind in ['counter','nonfixed','late']:
 for i in range(2):
  name='new-'+kind+'-'+str(i)
  r,o=f.with_fixture(name,['python3',str(p.P/'late_fixture.py'),kind],lambda:f.cap(name,maxh=30000))
  if not (o/'capture.png').exists():
   r['oracle']={'imageAbsent':True};f.save(r,o);continue
  im=np.asarray(Image.open(o/'capture.png').convert('RGB'));ref=np.asarray(Image.open(p.P/(kind+'-generator.png')).convert('RGB'));h=len(im)
  if kind in ['late','counter']:
   footer=np.asarray(Image.open(p.P/(kind+'-footer.png')).convert('RGB'));ref=np.concatenate([ref,footer])
  if kind=='late':ref=np.concatenate([np.asarray(Image.open(p.P/(kind+'-top.png')).convert('RGB')),ref])
  nh=min(h,len(ref));diff=np.any(im[:nh]!=ref[:nh],axis=2);r['oracle']={'height':h,'expectedHeight':len(ref),'pixelExact':h==len(ref) and not diff.any(),'mismatchPixels':int(diff.sum()),'firstBadRow':int(np.where(diff.any(axis=1))[0][0]) if diff.any() else None};r['contract']='late bar once at top, banner once at bottom, body exact' if kind=='late' else 'generator body exact; counter footer once at bottom' if kind=='counter' else 'body with monotonic bottom-8%-only repaints, exact against final generator';f.save(r,o)
