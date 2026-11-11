from pathlib import Path
import numpy as np,json,sys
from PIL import Image
mode=sys.argv[1];p=Path.home()/'work/pfin' if mode=='native' else Path.home()/'work/sfinal/ev';out={}
roots=[p] if mode=='native' else [p/(k+'fin')/'final/cases' for k in 'obnk']
for root in roots:
 for d in root.iterdir():
  if not d.is_dir() or not d.name.startswith(('qtfull','qtnarrow','gtkfull','gtknarrow','qt1280','qt600','gtk1280','gtk600')):continue
  f=d/'capture.png'
  if not f.exists():continue
  a=np.asarray(Image.open(f).convert('RGB')).astype(np.int16);h,w,_=a.shape;part=a[:,max(int(w*.8),420):];bg=np.median(part.reshape(-1,3),axis=0);bad=int(np.count_nonzero(np.any(np.abs(part-bg)>12,axis=2)))
  out[str(d.relative_to(p))]={'width':w,'height':h,'background':bg.tolist(),'rightBackgroundMismatchPixels':bad,'columnsFrom':max(int(w*.8),420)}
f=p/'text-background-verification.json';f.write_text(json.dumps(out,indent=2));print(mode,'checked',len(out),'bad', {n:v for n,v in out.items() if v['rightBackgroundMismatchPixels']})
