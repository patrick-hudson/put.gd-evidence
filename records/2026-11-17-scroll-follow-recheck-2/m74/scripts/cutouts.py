from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
import numpy as np
Image.MAX_IMAGE_PIXELS=None
P=Path.cwd();out=[]
def scan(d,prior=False):
 a=Image.open(d/'capture.png').convert('RGB');b=Image.open(d/'reference.png').convert('RGB');aa=np.asarray(a);bb=np.asarray(b);h=min(a.height,b.height)
 if prior:ranges=[(300,2400)]
 else:
  details=json.loads((d/'band-details.json').read_text());rows=details['badRows'];ranges=[]
  for lo,hi,_ in rows:
   if lo>=2500:continue
   if ranges and lo<=ranges[-1][1]:ranges[-1]=(ranges[-1][0],hi)
   else:ranges.append((lo,hi))
 boxes=[]
 for y0,y1 in ranges:
  ar=aa[y0:y1,:1900];br=bb[y0:y1,:1900];mask=(ar.min(2)>248)&(br.min(2)<220)
  # Group nearby missing ink on an 8-pixel grid; report exact pixel bounds afterwards.
  gh=(mask.shape[0]+7)//8;gw=(mask.shape[1]+7)//8;grid=np.zeros((gh,gw),bool)
  yy,xx=np.where(mask);grid[yy//8,xx//8]=True;seen=set()
  for gy,gx in zip(*np.where(grid)):
   if (gy,gx)in seen:continue
   todo=[(gy,gx)];seen.add((gy,gx));cells=[]
   while todo:
    cy,cx=todo.pop();cells.append((cy,cx))
    for ny,nx in [(cy-1,cx),(cy+1,cx),(cy,cx-1),(cy,cx+1)]:
     if 0<=ny<gh and 0<=nx<gw and grid[ny,nx]and(ny,nx)not in seen:seen.add((ny,nx));todo.append((ny,nx))
   l=min(x for y,x in cells)*8;t=min(y for y,x in cells)*8;rr=min(mask.shape[1],(max(x for y,x in cells)+1)*8);bt=min(mask.shape[0],(max(y for y,x in cells)+1)*8)
   sub=mask[t:bt,l:rr];count=int(sub.sum())
   if count<120 or rr-l<16 or bt-t<4:continue
   ys,xs=np.where(sub);box=[l+int(xs.min()),y0+t+int(ys.min()),l+int(xs.max())+1,y0+t+int(ys.max())+1]
   boxes.append(dict(box=box,boundingPixels=(box[2]-box[0])*(box[3]-box[1]),whiteMissingInkPixels=count))
 if boxes:
  target=P/'prior-cutouts'if prior else d;target.mkdir(exist_ok=True)
  for i,row in enumerate(boxes):
   l,t,rr,bt=row['box'];bounds=(max(0,l-16),max(0,t-16),min(a.width,rr+16),min(h,bt+16));ca=a.crop(bounds);cb=b.crop(bounds);pic=Image.new('RGB',(ca.width*2+12,ca.height+22),'white');pic.paste(ca,(0,22));pic.paste(cb,(ca.width+12,22));draw=ImageDraw.Draw(pic);draw.text((0,0),'capture '+str(row['box']),fill='red');draw.text((ca.width+12,0),'reference',fill='red');name='cutout-candidate-'+str(i+1)+'.png';pic.save(target/name);row['picture']=name
 (P/'prior-cutouts'if prior else d).mkdir(exist_ok=True)
 (P/'prior-cutouts'/'candidates.json'if prior else d/'cutout-candidates.json').write_text(json.dumps(boxes,indent=1,default=int));print(d.name,boxes,flush=True)
for d in sorted((P/'runs').iterdir()):
 if 'github'in d.name and(d/'band-details.json').exists():scan(d)
prior=Path.home()/'work/sfr17/runs/firefox-github-user-A1-3';assert hashlib.sha256((prior/'capture.png').read_bytes()).hexdigest()=='2986ec87858480e380b0d8650fdc3a40a335957d17e8e792c9e8207df2341038';scan(prior,True)
(P/'prior-cutouts/identity.json').write_text(json.dumps({'recordCommit':'f19043f6b932103d2a29f8fac10ac6164cf674e0','run':str(prior),'captureSha256':'2986ec87858480e380b0d8650fdc3a40a335957d17e8e792c9e8207df2341038'},indent=1))
