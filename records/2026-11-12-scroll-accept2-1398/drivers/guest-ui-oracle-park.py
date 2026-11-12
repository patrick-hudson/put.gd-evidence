from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,re
import sys
P=Path(sys.argv[1]);out={}
for d in P.glob('cancel-*'):
 f=d/'screen-2s-later.png'
 if not f.exists():continue
 im=np.asarray(Image.open(f).convert('RGB')).astype('int16');mask=np.zeros(im.shape[:2],bool);mask[194:806,94:1066]=True;mask[200:800,100:1060]=False;mask[780:830,1040:1090]=False;park=re.findall(r'away (-?\d+),(-?\d+)',(d/'helper.log').read_text());rawRing=int(np.count_nonzero(np.any(np.abs(im[mask]-102)>12,axis=1)));cursor=None
 if park:
  ax,ay=map(int,park[-1]);cursor=[100+ax,200+ay];cx,cy=cursor;mask[max(0,cy-2):cy+34,max(0,cx-2):cx+26]=False
 ring=int(np.count_nonzero(np.any(np.abs(im[mask]-102)>12,axis=1)));bottom=int(np.count_nonzero(np.any(np.abs(im[807:880,100:660]-102)>12,axis=2)));top=int(np.count_nonzero(np.any(np.abs(im[120:194,100:660]-102)>12,axis=2)));v={'rawRingMismatchPixels':rawRing,'excludedCursorParkPoint':cursor,'ringMismatchPixels':ring,'bottomBarMismatchPixels':bottom,'topBarMismatchPixels':top,'noRingOrBar':ring==0 and bottom==0 and top==0,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()};(d/'ui-verification.json').write_text(json.dumps(v,indent=2));out[d.name]=v
(P/'cancel-ui-verification.json').write_text(json.dumps(out,indent=2));print({n:v for n,v in out.items() if not v['noRingOrBar']});print('checked',len(out))
