"""Bounded diagnostic: identify native comparison row mismatches; do not change acceptance scores."""
from pathlib import Path
import sys,json,re
import numpy as np
from PIL import Image
P=Path.home()/'work/sfa15/m74-supplement';sys.path.insert(0,str(P));import score as S
Image.MAX_IMAGE_PIXELS=None;rows=[]
for site in ['wiki','github','news']:
 d=P/'runs'/('firefox-'+site+'-user');r=json.loads((d/'result.json').read_text());x,y,w,h=r['rect'];im=Image.open(d/'capture.png').convert('RGB');a=np.asarray(im.crop((0,im.height-h,w,im.height)),dtype=np.int16);b=np.asarray(Image.open(d/'saving.png').convert('RGB').crop((x,y,x+w,y+h)),dtype=np.int16)
 ref=S.S.Reference.__new__(S.S.Reference);ref.pixels=b;ref.dx=0;ref.reachable=None;ref.rects=[];v=json.loads((d/'pre-done-viewport-info.json').read_text());top=v['y']+r['viewport']['rect'][1]-r['viewport']['info']['y']-y
 if top>0:ref.rects.append((0,0,w,top))
 for e in json.loads((d/'pre-done-pinned.json').read_text()):
  xx,yy,ww,hh=e['rect'];yy+=top;ref.rects.append((max(0,int(xx)-12),max(0,int(yy)-12),min(w,int(xx+ww+1)+12),min(h,int(yy+hh+1)+12)))
 text=(d/'helper.log').read_text();m=list(re.finditer(r'scroll: bar at (-?\d+),(-?\d+) (\d+)x(\d+)',text))[-1];bx,by,bw,bh=map(int,m.groups());ref.rects.append((bx-x-4,by-y-4,bx+bw-x+4,by+bh-y+4))
 raw=S.tolerant(ref,a);diff=np.abs(S.blur(a.mean(2))-S.blur(b.mean(2)));counts=(diff[:,24:w-44]>16).sum(1);largest=np.argsort(counts)[-8:][::-1]
 ref.rects.extend([(0,0,w,2),(0,h-2,w,h)]);edgeMasked=S.tolerant(ref,a)
 rows.append({'site':site,'region':r['rect'],'raw':raw,'diagnosticOnlyControlEdge2pxMasked':edgeMasked,'largestRows':[{'y':int(i),'pixelsDifferentOver16':int(counts[i])}for i in largest],'note':'Two-pixel edge mask is a diagnostic, not substituted into raw acceptance scores without verifying the observed control outline.'})
 width=min(1200,w);canvas=Image.new('RGB',(2*width,h));canvas.paste(Image.fromarray(a.astype('uint8')).crop((180,0,180+width,h)),(0,0));canvas.paste(Image.fromarray(b.astype('uint8')).crop((180,0,180+width,h)),(width,0));canvas.save(P/'analysis'/('native-Done-'+site+'-side.png'))
(P/'analysis/native-Done-edge-diagnostic.json').write_text(json.dumps(rows,indent=1));print(json.dumps(rows))

