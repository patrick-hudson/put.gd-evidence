import json
from pathlib import Path
import numpy as np
from PIL import Image
import score as S
Image.MAX_IMAGE_PIXELS=None
P=Path.home()/'work/sfa15';out=[]
for site in ['github','news']:
 d=P/'scoring-f44/runs'/f'firefox-{site}-user-doneproof2'
 v=np.asarray(Image.open(d/'pre-done-viewport.png').convert('RGB'),dtype=np.int16);im=Image.open(d/'capture.png');h=v.shape[0];a=np.asarray(im.crop((0,im.height-h,im.width,im.height)),dtype=np.int16)
 x0,x1=150,1700;y0,y1=200,min(h-150,700);aa=S.blur(a.mean(axis=2));bb=S.blur(v.mean(axis=2))
 choices=[(float(np.abs(aa[y0:y1,x0:x1]-bb[y0+dy:y1+dy,x0+dx:x1+dx]).mean()),dx,dy)for dx in range(-4,5)for dy in range(-4,5)]
 choices.sort();best,dx,dy=choices[0]
 ref=S.S.Reference.__new__(S.S.Reference);ref.pixels=np.roll(np.roll(v,-dy,axis=0),-dx,axis=1);ref.rects=[(0,0,v.shape[1],5),(0,h-5,v.shape[1],h)];ref.dx=0;ref.reachable=None
 for e in json.loads((d/'pre-done-pinned.json').read_text()):
  x,y,w,eh=e['rect'];x0=max(0,int(x)-12);x1=min(v.shape[1],int(x+w+.999)+12);y0=max(0,int(y)-12);y1=min(h,int(y+eh+.999)+12)
  if x1>x0 and y1>y0:ref.rects.append((x0,y0,x1,y1))
 bands=S.tolerant(ref,a)
 out.append({'site':site,'bestGreyBlurOffsets':choices[:5],'zeroOffsetMeanDifference':next(x[0]for x in choices if x[1:]==(0,0)),'alignedBandsEqualTotal':bands,'referenceAlignment':[dx,dy],'method':'One constant translation of current browser reference, chosen from +/-4px over central content. No local warping or changing the capture. Same visible fixed/sticky rectangles and 12px scorer shadow; ignore5edge rows affected by translation. Raw unaligned scores retained in pre-done-f44-final.json.'})
(P/'f44-pre-done-offset-analysis.json').write_text(json.dumps(out,indent=1));print(json.dumps(out))
