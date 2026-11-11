from pathlib import Path
import sys,json,numpy as np
from PIL import Image
D=Path.home()/'work/sfinal';B=Path.home()/'work/svm1398';ns={};exec((B/'v2analyze.py').read_text().split('out=json.loads')[0],ns)
k=sys.argv[1];p=D/'ev'/(k+'fin');out={}
for d in (p/'final/cases').iterdir():
 f=d/'capture.png'
 if not f.exists() or d.name.startswith(('gtk','qt','fraction')):continue
 a=np.asarray(Image.open(f).convert('RGB')).astype(np.int16);h,w,_=a.shape;v=ns['ruler'](f,None,first=None,codewidth=w)
 if 'firstPixel' not in v:out[d.name]=v;continue
 first=v['firstPixel'];cell=(w-76)//16;codes=ns['codes'][first:first+h];bad=0
 for c in range(16):
  want=np.where((codes>>(15-c))&1,16,250);bad+=int(np.count_nonzero(np.any(np.abs(a[:,64+c*cell:64+(c+1)*cell]-want[:,None,None])>12,axis=2)))
 bad+=int(np.count_nonzero(np.any(np.abs(a[:,64+16*cell:]-250)>12,axis=2)))
 out[d.name]={'mismatchPixels':bad,'firstPixel':first,'height':h}
(p/'pixel-verification.json').write_text(json.dumps(out,indent=2));print(k,{n:v for n,v in out.items() if v.get('mismatchPixels',1)})
