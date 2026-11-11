from pathlib import Path
import numpy as np,json
from PIL import Image
ns={};exec(Path('/home/patrick/work/svm1398/v2analyze.py').read_text().split('out=json.loads')[0],ns)
for k,n in [('n','plain-r3'),('k','mcp')]:
 p=Path('/home/patrick/work/svm1398/v2evidence')/k;f=p/'final/cases'/n/'capture.png';im=Image.open(f).convert('RGB');a=np.asarray(im);h,w,_=a.shape;cell=(w-76)//16;bad=[]
 for c in range(16):
  lo=int(64+(c+.12)*cell);hi=min(w,int(64+(c+.88)*cell));want=np.where((ns['codes'][:h]>>(15-c))&1,16,250).astype(np.int16);ys,xs=np.nonzero(np.any(np.abs(a[:,lo:hi,:].astype(np.int16)-want[:,None,None])>12,axis=2));bad.extend(zip((xs+lo).tolist(),ys.tolist()))
 if bad:
  x,y=bad[0];im.crop((max(0,x-100),max(0,y-100),min(w,x+350),min(h,y+200))).save(p/(n+'-unexpected-detail.png'))
  (p/(n+'-unexpected.json')).write_text(json.dumps({'count':len(bad),'bounds':[min(x for x,y in bad),min(y for x,y in bad),max(x for x,y in bad),max(y for x,y in bad)],'first':bad[:10]},indent=2))
  print(k,n,len(bad),[min(x for x,y in bad),min(y for x,y in bad),max(x for x,y in bad),max(y for x,y in bad)])
