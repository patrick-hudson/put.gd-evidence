import fix6 as f, pass2 as p,json
from PIL import Image
import numpy as np
import sys
for kind in (sys.argv[1:] or ['a','b','c','f']):
 for i in range(2):
  name='new-'+kind+'-'+str(i)
  def capture():
   r,o=f.cap(name,maxh=30000);c=r.get('capture',{});png=o/'capture.png';v={}
   if png.exists():
    im=np.asarray(Image.open(png).convert('RGB'));ref=np.asarray(Image.open(p.P/(kind+'-generator.png')).convert('RGB'));h=im.shape[0];diff=np.any(im!=ref[:h],axis=2);v={'pixelExact':not bool(diff.any()),'mismatchPixels':int(diff.sum()),'height':h,'expectedHeight':24000,'firstBadRow':int(np.where(diff.any(axis=1))[0][0]) if diff.any() else None}
   r['oracle']=v;r['wrongAdmitted']=bool(v and not v['pixelExact']);r['falseEnd']=c.get('endReason')=='end_of_content' and c.get('height')!=24000;r['pass']=bool(v.get('pixelExact') and not r['falseEnd'] and (c.get('endReason')=='end_of_content' or kind=='c' and c.get('truncated')));f.save(r,o)
  f.with_fixture(name,['python3',str(p.P/'adversarial.py'),kind],capture)
