import pass2 as p,fix6 as f,json,shutil
from PIL import Image
import numpy as np
for i in range(2):
 name='new-nonfixed-v2-'+str(i)
 r,o=f.with_fixture(name,['python3',str(p.P/'late_fixture-v2.py'),'nonfixed'],lambda:f.cap(name,maxh=30000))
 if (o/'capture.png').exists():
  shutil.copyfile(p.P/'nonfixed-generator.png',o/'generator-reference.png');im=np.asarray(Image.open(o/'capture.png').convert('RGB'));ref=np.asarray(Image.open(o/'generator-reference.png').convert('RGB'));h=len(im);n=min(h,len(ref));diff=np.any(im[:n]!=ref[:n],axis=2)
  r['oracle']={'height':h,'expectedHeight':24000,'mismatchPixels':int(diff.sum())+max(0,h-24000)*960,'firstBadRow':int(np.where(diff.any(axis=1))[0][0]) if diff.any() else None,'exactPrefix':h<=24000 and not bool(diff.any()),'falseCompletion':r.get('capture',{}).get('endReason')=='end_of_content' and h!=24000,'fixtureRevision':'small QImage patch updates; same generated content rule as v1'}
 f.save(r,o)
