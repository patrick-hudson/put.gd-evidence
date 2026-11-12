from pathlib import Path
from PIL import Image
import numpy as np,json
p=Path('/home/patrick/work/sl25/live-site');summary=json.loads((p/'summary.json').read_text())
for r in summary:
 d=p/r['name'];cap=np.array(Image.open(d/'capture.png').convert('RGB'),dtype='int16');ref=np.array(Image.open(d/'reference-before.png').convert('RGB'),dtype='int16')[:len(cap),:cap.shape[1]];mask=(np.abs(cap[:,0:300]-ref[:,0:300])>25).any(2).sum(1)>10;mask[:400]=False;ys=np.flatnonzero(mask);runs=[]
 for y in ys:
  if runs and y<=runs[-1][1]+2:runs[-1][1]=int(y)
  else:runs.append([int(y),int(y)])
 r['verification']['leftMarginNonDocumentBands']=runs;r['verification']['leftMarginMismatchPixels']=int(np.any(np.abs(cap[400:,0:300]-ref[400:,0:300])>25,2).sum());(d/'verification.json').write_text(json.dumps(r,indent=2));print(r['name'],runs)
(p/'summary.json').write_text(json.dumps(summary,indent=2))
