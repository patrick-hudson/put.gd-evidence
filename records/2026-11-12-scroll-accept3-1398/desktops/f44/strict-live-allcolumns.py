from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
Image.MAX_IMAGE_PIXELS=300000000
P=Path('/home/patrick/work/s3a');summary=[]
for out in sorted((P/'runs').glob('accept3-*')):
 if not (out/'result.json').exists() or not (out/'capture.png').exists() or not (out/'reference.png').exists():continue
 ref=out/('reference-initial.png' if (out/'reference-initial.png').exists() else 'reference.png');cap=np.asarray(Image.open(out/'capture.png').convert('RGB'));r=np.asarray(Image.open(ref).convert('RGB'));H,W=cap.shape[:2];w=min(W,r.shape[1]);bands=[]
 for y in range(0,H,64):
  z=min(y+64,H)
  if z>len(r):bands.append({'rows':[y,z],'outsideReference':True});continue
  d=np.abs(cap[y:z,:w].astype('int16')-r[y:z,:w].astype('int16')).max(axis=2);bad=d>0;ys,xs=np.where(bad);bands.append({'rows':[y,z],'comparedPixels':int(d.size),'mismatchPixels':int(bad.sum()),'pixelsOver8':int((d>8).sum()),'pixelsOver32':int((d>32).sum()),'maxDelta':int(d.max()),'bbox':None if not len(xs) else [int(xs.min()),int(ys.min()+y),int(xs.max()+1),int(ys.max()+1+y)],'literalPixelExact':not bool(bad.any())})
 meta=json.loads((out/'result.json').read_text());b=meta.get('after',{});a=meta.get('afterReference',{});keys=['w','clientWidth','docHeight'];same={k:[b.get(k),a.get(k)] for k in keys if b.get(k)!=a.get(k)}
 v={'method':'Every RGB pixel, every 64-row band, all columns, zero offset; NO dynamic, antialiasing, fixed-sidebar, or UI-tail exclusions; all mismatches remain unresolved unless specifically explained in the report','reference':ref.name,'referenceSha256':hashlib.file_digest(ref.open('rb'),'sha256').hexdigest(),'captureSha256':hashlib.file_digest((out/'capture.png').open('rb'),'sha256').hexdigest(),'captureSize':[W,H],'referenceSize':[r.shape[1],r.shape[0]],'geometryChanges':same,'bands':bands,'literalExactBands':sum(x.get('literalPixelExact',False) for x in bands),'totalBands':len(bands)};(out/'strict-allcolumns.json').write_text(json.dumps(v,indent=1));item={'case':out.name,'exactBands':v['literalExactBands'],'totalBands':len(bands),'geometryChanges':same};summary.append(item);print(item,flush=True)
(P/'strict-allcolumns-summary.json').write_text(json.dumps(summary,indent=2))
