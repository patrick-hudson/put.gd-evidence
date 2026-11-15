"""Scan real Hyprland outputs for its actual black/white native arrow."""
from pathlib import Path
import json,numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
P=Path('/home/patrick/work/sfa15/guest-h');out=P/'analysis/arrow-scan';out.mkdir(exist_ok=True)
control=Image.open(P/'cleanup-desktop.png').convert('RGB');template=np.asarray(control.crop((24,84,49,113)));bm=template.max(2)<60;wm=template.min(2)>245
assert bm.sum()>15 and wm.sum()>8,(bm.sum(),wm.sum());Image.fromarray(template).save(out/'native-arrow-control.png')
black=list(zip(*np.where(bm)));white=list(zip(*np.where(wm)));features=[(black,False),(white,True)]
def scan(path):
 im=Image.open(path).convert('RGB');a=np.asarray(im);dark=a.max(2)<80;light=a.min(2)>225;h=a.shape[0]-template.shape[0]+1;w=a.shape[1]-template.shape[1]+1;hit=np.ones((h,w),bool)
 for pts,kind in features:
  for j in np.linspace(0,len(pts)-1,min(10,len(pts)),dtype=int):
   y,x=pts[j];hit&=(light if kind else dark)[y:y+h,x:x+w]
 ys,xs=np.where(hit);matches=[]
 for y,x in zip(ys,xs):
  d=dark[y:y+bm.shape[0],x:x+bm.shape[1]][bm].mean();l=light[y:y+wm.shape[0],x:x+wm.shape[1]][wm].mean()
  if d>=.97 and l>=.97:matches.append({'x':int(x),'y':int(y),'blackShare':float(d),'whiteShare':float(l)})
 return {'path':str(path),'size':list(im.size),'prefilterCandidates':len(ys),'matches':matches}
rows=[scan(P/'cleanup-desktop.png')];assert any(r['x']==24 and r['y']==84 for r in rows[0]['matches']),rows[0]
for d in sorted((P/'runs').iterdir()):
 if '-auto'not in d.name:continue
 f=d/'capture.png'
 if not f.exists()and(d/'recovered-terminal-result.json').exists():f=Path(json.loads((d/'recovered-terminal-result.json').read_text())['verifiedArtifact'])
 if f.exists():rows.append(scan(f));print(d.name,len(rows[-1]['matches']),flush=True)
o={'method':'Every pixel origin in each full auto image. Actual native arrow from cleanup framebuffer, on purple background; black core and opaque white outline isolated by colour. Ten sparse points per class prefilter, then >=97% of every foreground mask pixel. Native control must detect its arrow at the original coordinates. This checks this observed arrow shape; it does not claim all cursor shapes are absent.','templateBlackPixels':int(bm.sum()),'templateWhitePixels':int(wm.sum()),'rows':rows}
(out/'results.json').write_text(json.dumps(o,indent=1));print(json.dumps({'controlMatches':len(rows[0]['matches']),'autoImages':len(rows)-1,'autoMatches':sum(len(r['matches'])for r in rows[1:])}),flush=True)
