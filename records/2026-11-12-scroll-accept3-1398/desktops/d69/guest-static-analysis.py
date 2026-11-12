from pathlib import Path
import tarfile,json,io,hashlib
from PIL import Image
import numpy as np
P=Path('/home/patrick/work/s3a')
for tag in ['neon','omarchy']:
 out=P/(tag+'-export');f=out/'guest-evidence.tar.gz'
 with tarfile.open(f) as t:
  r=json.load(t.extractfile('timer-resize/result.json'));a=np.asarray(Image.open(t.extractfile('timer-resize/capture.png')).convert('RGB'));H,W=a.shape[:2];rect=r['capture']['rect'];v=[]
  if H<=rect[3]:
   for n in t.getnames():
    if n.startswith('timer-resize/screen-') and n.endswith('.png'):
     im=np.asarray(Image.open(t.extractfile(n)).convert('RGB'));x,y,w,h=rect;b=im[y:y+h,x:x+w][:H];v.append({'frame':n,'mismatchPixels':int(np.count_nonzero(np.any(a!=b,axis=2)))})
   (out/'timer-viewport-verification.json').write_text(json.dumps({'method':'Every RGB pixel against the same selected rectangle in independently retained real QEMU console frames; exact prefix only, not proof of a complete document','captureHeight':H,'frames':v,'exactFrameFound':any(x['mismatchPixels']==0 for x in v)},indent=2));print(tag,v,flush=True)
