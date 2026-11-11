import json,sys,numpy as np,hashlib
from pathlib import Path
from PIL import Image
import scroll_run
P=Path('/home/patrick/work/sr8');out={}
for d in P.iterdir():
 f=d/'capture.png'
 if not d.is_dir() or not f.is_file() or d.name.startswith(('qtfull','qtnarrow','gtkfull','gtknarrow','harness')):continue
 a=json.loads((d/'result.json').read_text());scale=a.get('scale',1)
 if scale!=1:continue
 im=np.asarray(Image.open(f).convert('RGB')).astype(np.int16);h,w,_=im.shape
 first=a.get('viewportFirstPixelCandidates',[1200 if d.name=='half-off' else 0])[0];head=40 if d.name=='sticky' else 0;foot=head
 y=np.arange(h-head-foot)+first;codes=np.array([scroll_run.pattern(*divmod(int(i),40)) for i in y],dtype=np.uint32);bad=0
 for c in range(16):
  want=np.where((codes>>(15-c))&1,16,250);part=im[head:h-foot if foot else h,64+c*55:64+(c+1)*55];bad+=int(np.count_nonzero(np.any(np.abs(part-want[:,None,None])>12,axis=2)))
 tail=im[head:h-foot if foot else h,944:];bad+=int(np.count_nonzero(np.any(np.abs(tail-250)>12,axis=2)))
 out[d.name]={'fullCellAndRightMarginMismatchPixels':bad,'rowsChecked':len(y),'firstPixel':first,'pngSha256':hashlib.sha256(f.read_bytes()).hexdigest()}
(P/'pixel-verification.json').write_text(json.dumps(out,indent=2));print(json.dumps({n:v for n,v in out.items() if v['fullCellAndRightMarginMismatchPixels']}))
