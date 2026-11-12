import json,numpy as np,hashlib
from pathlib import Path
from PIL import Image
import scroll_run
P=Path('/home/lab/work/s3a');out={}
for d in [d for d in P.iterdir() if d.name.startswith(('firefox-probe-','firefox-valid'))]:
 if not (d/'capture.png').exists():continue
 n=d.name.split('-')[-2];im=np.asarray(Image.open(d/'capture.png').convert('RGB')).astype('int16');h,w,_=im.shape;bad=0;left=120 if n=='sidebar' else 0;top=40 if n=='sticky' else 80 if n=='shrink' else 0;bottom=40 if n=='sticky' else 0;body=im[top:h-bottom if bottom else h];heightok=len(body)==2400
 if heightok:
  codes=np.array([scroll_run.pattern(*divmod(y,40)) for y in range(2400)],dtype='uint32')
  for ci in range(16):
   a=left+64+ci*55+2;b=min(left+64+(ci+1)*55-2,w-(20 if n.startswith(('classic','overlay')) else 0))
   if a>=b:continue
   want=np.where((codes>>(15-ci))&1,16,250)
   if n=='blank':want[(np.arange(2400)>=800)&(np.arange(2400)<1400)|(np.arange(2400)>=1800)&(np.arange(2400)<2200)]=250
   bad+=int(np.count_nonzero(np.any(np.abs(body[:,a:b]-want[:,None,None])>12,axis=2)))
  if left:bad+=int(np.count_nonzero(np.any(im[:,:left]!=102,axis=2)))
  if top:
   band=im[:40];bad+=int(np.count_nonzero(np.any(np.abs(band-[32,80,128])>12,axis=2)))
   if top==80:bad+=int(np.count_nonzero(np.any(im[40:80]!=102,axis=2)))
  if bottom:bad+=int(np.count_nonzero(np.any(np.abs(im[-40:]-[128,96,32])>12,axis=2)))
 r={'method':'variant every scanline and full visible barcode cell interiors; fixed sidebar/header/footer colors','size':[w,h],'documentRows':len(body),'mismatchPixels':bad,'exact':heightok and bad==0,'sha256':hashlib.sha256((d/'capture.png').read_bytes()).hexdigest()}
 (d/'variant-verification.json').write_text(json.dumps(r,indent=2));out[d.name]=r
print(json.dumps(out))
