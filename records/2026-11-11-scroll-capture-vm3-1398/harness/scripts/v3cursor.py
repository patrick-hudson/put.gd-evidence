from pathlib import Path
import numpy as np,json
from PIL import Image
B=Path('/home/patrick/work/svm1398');ns={};exec((B/'v2analyze.py').read_text().split('out=json.loads')[0],ns)
f=B/'v3evidence/o/peek/clean01/capture.png';a=np.asarray(Image.open(f).convert('RGB')).astype(np.int16);h,w,_=a.shape;cell=(w-76)//16;bad=[]
for c in range(16):
 lo=64+c*cell;hi=lo+cell;want=np.where((ns['codes'][:h]>>(15-c))&1,16,250).astype(np.int16);ys,xs=np.nonzero(np.any(np.abs(a[:,lo:hi]-want[:,None,None])>12,axis=2));bad.extend(zip((xs+lo).tolist(),ys.tolist()))
ys,xs=np.nonzero(np.any(np.abs(a[:,64+16*cell:]-250)>12,axis=2));tail=list(zip((xs+64+16*cell).tolist(),ys.tolist()));out={'fullBarcodeMismatchPixels':len(bad),'rightTailMismatchPixels':len(tail),'barcodeFirst':bad[:20],'tailFirst':tail[:20]};(B/'v3evidence/o/cursor-verification.json').write_text(json.dumps(out,indent=2));print(out)
