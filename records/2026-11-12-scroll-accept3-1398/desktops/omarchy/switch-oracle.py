from pathlib import Path
from PIL import Image
import numpy as np,json,sys,hashlib
P=Path(sys.argv[1]);out={}
def bits(r,l):
 if l<2:return 65535
 if l<30:return r
 x=(r*2654435761+l*40503+0x9e3779b9)&0xffffffff;x^=x>>15;x=x*0x2c1b3c6d&0xffffffff;x^=x>>12;x=x*0x297a2d39&0xffffffff;x^=x>>15;b=x&65535;return b if b not in (0,65535) else 0x5a5a^l
for d in P.glob('switch*'):
 f=d/'capture.png'
 if not f.exists():continue
 im=np.array(Image.open(f).convert('RGB')).astype('int16');h,w,_=im.shape;signature=[sum((im[y,64+c*55+27].sum()<384)<<(15-c) for c in range(12,16)) for y in range(40)];candidates=[n for n in range(24001-h) if all((bits(*divmod(n+y,40))&15)==b for y,b in enumerate(signature))];bad=0
 if len(candidates)==1:
  first=candidates[0];codes=np.array([bits(*divmod(first+y,40)) for y in range(h)],dtype='uint32')
  for c in range(11,16):
   lo=max(64+c*55+2,720);hi=64+(c+1)*55-2
   if hi<=lo:continue
   want=np.where((codes>>(15-c))&1,16,250);bad+=int(np.count_nonzero(np.any(np.abs(im[:,lo:hi]-want[:,None,None])>12,2)))
  bad+=int(np.count_nonzero(np.any(np.abs(im[:,:720]-102)>12,2)));bad+=int(np.count_nonzero(np.any(np.abs(im[:,944:]-250)>12,2)))
 v={'method':'fixed left720px; unique40scanline barcode signature on scrolling right; all visible cell interiors on every scanline','firstPixelCandidates':candidates,'height':h,'mismatchPixels':bad,'exactViewport':len(candidates)==1 and bad==0,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()};(d/'switch-verification.json').write_text(json.dumps(v,indent=2));out[d.name]=v
print(json.dumps(out))
