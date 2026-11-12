import json,numpy as np,hashlib
from pathlib import Path
from PIL import Image
import scroll_run
P=Path('/home/patrick/work/sa2')
for d in sorted(P.glob('editor-[0-9]')):
 if not (d/'capture.png').exists():continue
 im=np.asarray(Image.open(d/'capture.png').convert('RGB')).astype('int16');h,w,_=im.shape;y=np.arange(h);codes=np.array([scroll_run.pattern(*divmod(int(i),40)) for i in y],dtype='uint32');bad=0
 for c in range(15):
  a=64+c*55+2;b=min(64+(c+1)*55-2,860)
  if a>=b:continue
  want=np.where((codes>>(15-c))&1,16,250);bad+=int(np.count_nonzero(np.any(np.abs(im[:,a:b]-want[:,None,None])>12,axis=2)))
 mini=np.stack([30+(y*17)%190,40+(y*23)%180,50+(y*31)%170],axis=1);mask=np.any(im[:,860:]!=mini[:,None,:],axis=2);rows=np.flatnonzero(mask.any(axis=1));v={'mainColumnMismatchPixels':bad,'mainColumnExactFromTop':bad==0,'height':h,'minimapMismatchPixels':int(mask.sum()),'firstWrongMinimapRow':int(rows[0]) if len(rows) else None,'firstViewportMinimapExact':not mask[:600].any(),'wholeImageExactPrefix':bad==0 and not mask.any(),'sha256':hashlib.sha256((d/'capture.png').read_bytes()).hexdigest()};(d/'independent-editor-verification.json').write_text(json.dumps(v,indent=2));print(d.name,v)
