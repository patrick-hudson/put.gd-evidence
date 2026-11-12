import live7 as l,json,traceback,struct
from pathlib import Path
from PIL import Image
import numpy as np
P=l.P;summary=[]
for out in sorted((P/'runs').glob('accept3-*')):
 if not (out/'capture.png').exists() or not (out/'reference.png').exists():continue
 try:
  for n in ['capture.png','reference.png']:
   b=(out/n).read_bytes()[:24];w,h=struct.unpack('>II',b[16:24]);assert 0<w<=5120 and 0<h<=150000 and w*h<=300000000,(n,w,h)
  l.verify(out);v=json.loads((out/'verification.json').read_text());Image.MAX_IMAGE_PIXELS=300000000
  cap=np.asarray(Image.open(out/'capture.png').convert('RGB'));ref=np.asarray(Image.open(out/'reference.png').convert('RGB'));H,W=cap.shape[:2];width=min(W,ref.shape[1]);cols=np.ones(width,bool)
  for e in v['excluded']:
   if 'x' in e and 'y' not in e:cols[e['x'][0]:e['x'][1]]=False
  dy=0;bands=[]
  for y0 in range(0,H,64):
   y1=min(H,y0+64)
   for sy,shift in v['shiftChanges']:
    if sy<=y0:dy=shift
   mask=np.broadcast_to(cols,(y1-y0,width)).copy()
   for e in v['excluded']:
    if 'y' in e:
     a,b=max(e['y'][0]-y0,0),min(e['y'][1]-y0,y1-y0)
     if a<b:
      x=e.get('x',[0,width]);mask[a:b,x[0]:x[1]]=False
   if y0+dy<0 or y1+dy>len(ref):bands.append({'rows':[y0,y1],'referenceOffset':dy,'outsideReference':True});continue
   delta=np.abs(cap[y0:y1,:width].astype('int16')-ref[y0+dy:y1+dy,:width].astype('int16')).max(axis=2);valid=int(mask.sum());diff=int(np.count_nonzero((delta>0)&mask))
   bands.append({'rows':[y0,y1],'referenceOffset':dy,'comparedPixels':valid,'mismatchPixels':diff,'pixelsOver8':int(np.count_nonzero((delta>8)&mask)),'pixelsOver32':int(np.count_nonzero((delta>32)&mask)),'maxDelta':int(delta[mask].max()) if valid else 0,'literalPixelExact':diff==0})
  result={'rule':'literal RGB comparison at the reference offsets located independently by equal-row hashes; same explicit column/band exclusions as verification.json; nonzero mismatches are not automatically waived','bands':bands,'literalExactBands':sum(x.get('literalPixelExact',False) for x in bands),'totalBands':len(bands),'referenceShiftChanges':v['shiftChanges']};(out/'pixel-bands.json').write_text(json.dumps(result,indent=2));item={'case':out.name,'bands':len(bands),'literalExact':result['literalExactBands'],'coarseBad':v['badBands'],'shiftChanges':v['shiftChanges']};summary.append(item);print(json.dumps(item),flush=True)
 except Exception:
  err=traceback.format_exc();(out/'verification-error.txt').write_text(err);summary.append({'case':out.name,'error':err});print('VERIFY-ERROR',out.name,err[-500:],flush=True)
(P/'live-verification-summary.json').write_text(json.dumps(summary,indent=2))
