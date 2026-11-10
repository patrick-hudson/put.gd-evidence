from PIL import Image
from pathlib import Path
import sys,json
sys.path.insert(0,'/tmp/sp1398');from scroll_run import pattern
p=Path('/tmp/sp1398/qt-fractional-y200');im=Image.open(p/'capture.png').convert('RGB');s=1.25;errors=[]
if im.size!=(1200,3000):errors.append('dimensions '+str(im.size))
# Qt rounds scaled one-pixel rectangle boundaries. Check complete barcode words
# on every physical scanline against an offset no greater than one physical pixel,
# and independently require row indices 0..59 at their expected centre positions.
def code(y):
 b=0
 for c in range(16):
  x=int((64+(c+.5)*55)*s);rgb=im.getpixel((x,y))
  if max(rgb)-min(rgb)>12:errors.append('non-ruler colour at %d,%d'%(x,y))
  b=b<<1 | (sum(rgb)<384)
 return b
for row in range(60):
 y=round((row*40+15)*s)
 if y>=im.height or code(y)!=row:errors.append('row centre '+str(row))
for y in range(im.height):
 got=code(y);accepted=False
 for shift in (-1,0,1):
  pos=max(0,int((y+shift)/s));row,l=divmod(pos,40)
  if got==pattern(row,l):accepted=True;break
 if not accepted:errors.append('scanline beyond 1 physical pixel tolerance '+str(y))
 if len(errors)>30:break
out={'pass':not errors,'scale':s,'size':list(im.size),'rows':60,'tolerancePhysicalPixels':1,'errors':errors}
(p/'fractional-verification.json').write_text(json.dumps(out,indent=2));print(out)
