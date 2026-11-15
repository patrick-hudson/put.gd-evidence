import json,re
from pathlib import Path
import numpy as np
from PIL import Image
import score as S
Image.MAX_IMAGE_PIXELS=None
P=Path.home()/'work/sfa15';rows=[]
for site in ['wiki','github','news']:
 d=P/'scoring-f44/runs'/f'firefox-{site}-user-doneproof2';r=json.loads((d/'result.json').read_text());v=json.loads((d/'pre-done-viewport-info.json').read_text());x,y,w,h=r['rect'];im=Image.open(d/'capture.png').convert('RGB');native=Image.open(d/'saving.png').convert('RGB');a=np.asarray(im.crop((0,im.height-h,w,im.height)),dtype=np.int16);ref=S.S.Reference.__new__(S.S.Reference);ref.pixels=np.asarray(native.crop((x,y,x+w,y+h)),dtype=np.int16);ref.dx=0;ref.reachable=None;ref.rects=[]
 # On this GNOME session Firefox reports workarea-relative Y; measured native
 # initial117 = reported85 +32px Shell panel. A later browser infobar adds45px.
 top=v['y']+32-y
 if top>0:ref.rects.append((0,0,w,top))
 for e in json.loads((d/'pre-done-pinned.json').read_text()):
  xx,yy,ww,hh=e['rect'];yy+=top;rx0=max(0,int(xx)-12);rx1=min(w,int(xx+ww+.999)+12);ry0=max(0,int(yy)-12);ry1=min(h,int(yy+hh+.999)+12)
  if rx1>rx0 and ry1>ry0:ref.rects.append((rx0,ry0,rx1,ry1))
 text=(d/'helper.log').read_text();bars=list(re.finditer(r'the Shell put the bar at (-?\d+),(-?\d+) (\d+)x(\d+)',text));assert bars
 bx,by,bw,bh=map(int,bars[-1].groups());ref.rects.append((bx-x-4,by-y-4,bx+bw-x+4,by+bh-y+4))
 bands=S.tolerant(ref,a);rows.append({'name':d.name,'nativeBandsEqualTotal':bands,'selectedRegion':r['rect'],'browserUiTopRows':top,'barExcludedFromComparison':[bx,by,bw,bh],'source':'saving.png: real native GNOME framebuffer during scroll.stop finishing, before its reply. Captured final screen compared directly to native pixels; no translation or later full-page snapshot. Current DOM fixed/sticky rectangles plus12px shadow and actual capture-bar bounds excluded.','rowsAtDone':r['capture']['rowsAtDone']})
(P/'f44-native-last-screen.json').write_text(json.dumps(rows,indent=1));print(json.dumps(rows))
