"""Compare both actual admitted images with the native cursor's opaque foreground."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
P=Path('/home/patrick/work/sfa15/guest-h2');B=Path('/home/patrick/work/sfa15/guest-h2-baseline');O=P/'analysis';O.mkdir(exist_ok=True)
control=Image.open(P/'arrow-native-control.png').convert('RGB');a=np.asarray(control.crop((1836,957,1861,986)));bm=a.max(2)<60;wm=a.min(2)>245;assert bm.sum()>15 and wm.sum()>8,(bm.sum(),wm.sum());Image.fromarray(a).save(O/'arrow-native-control-template.png')
black=list(zip(*np.where(bm)));white=list(zip(*np.where(wm)))
def scan(f,label):
 im=Image.open(f).convert('RGB');a=np.asarray(im);dark=a.max(2)<80;light=a.min(2)>225;h=a.shape[0]-bm.shape[0]+1;w=a.shape[1]-bm.shape[1]+1;hit=np.ones((h,w),bool)
 for points,kind in [(black,False),(white,True)]:
  for j in np.linspace(0,len(points)-1,min(10,len(points)),dtype=int):
   y,x=points[j];hit&=(light if kind else dark)[y:y+h,x:x+w]
 ys,xs=np.where(hit);matches=[]
 for y,x in zip(ys,xs):
  d=dark[y:y+bm.shape[0],x:x+bm.shape[1]][bm].mean();l=light[y:y+wm.shape[0],x:x+wm.shape[1]][wm].mean()
  if d>=.97 and l>=.97:
   matches.append({'x':int(x),'y':int(y),'blackShare':float(d),'whiteShare':float(l)})
   im.crop((int(x),int(y),int(x)+25,int(y)+29)).resize((200,232),Image.Resampling.NEAREST).save(O/(label+'-arrow-'+str(len(matches))+'.png'))
 return {'label':label,'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'size':list(im.size),'matches':matches}
rows=[scan(P/'arrow-native-control.png','native-control'),scan(P/'arrow-controlled-capture.png','candidate')]
assert any(m['x']==1836 and m['y']==957 for m in rows[0]['matches']),rows[0]
if(B/'arrow-controlled-capture.png').exists():
 rows.append(scan(B/'arrow-native-control.png','nightly-native-control'));assert any(m['x']==1836 and m['y']==957 for m in rows[-1]['matches'])
 rows.append(scan(B/'arrow-controlled-capture.png','nightly'))
out={'method':'All full-image origins. Native positive-control cursor on magenta at actual compositor pointer1840,960. Isolate black core/opaque white outline; sparse prefilter then >=97% of every foreground pixel in each class. Both builds use real relative initial anchor1840,960 inside full region before prepare, no external pointer movement during capture. No cursor shape was generated or substituted. This checks the observed arrow shape, not all possible cursors.','blackPixels':int(bm.sum()),'whitePixels':int(wm.sum()),'rows':rows};(O/'arrow-controlled-comparison.json').write_text(json.dumps(out,indent=1));print(json.dumps(out),flush=True)
