import json,shutil,re,os,hashlib
from pathlib import Path
from PIL import Image
import numpy as np
import score as S
os.nice(10);Image.MAX_IMAGE_PIXELS=None
P=Path.home()/'work/sfa15';root=P/'scoring-m74';runs=root/'runs';derived=root/'derived';ex=root/'final-extras';rows=[];bar=[]
for d in sorted(runs.iterdir()):
 if d.name.startswith('chromium-') or d.name=='firefox-wiki-user-jump':
  rows.append(S.one(d));print(json.dumps(rows[-1]),flush=True)
for mode in ['user','auto']:
 src=runs/('firefox-wiki-'+mode+'-inside');d=derived/('firefox-inside-'+mode+'-page');d.mkdir(exist_ok=True);r=json.loads((src/'result.json').read_text());im=Image.open(src/'capture.png').convert('RGB');assert im.height==r['after']['docHeight']+158
 im.crop((0,118,im.width,im.height-40)).save(d/'capture.png')
 for n in ['reference.png','pinned.json']:shutil.copyfile(src/n,d/n)
 r['comparisonTransform']={'source':str(src),'topBrowserUi':118,'bottomPanel':40};r['rect']=[0,118,1920,922];(d/'result.json').write_text(json.dumps(r));rows.append(S.one(d));print(json.dumps(rows[-1]),flush=True)
 m=re.search(r'scroll: bar at (-?\d+),(-?\d+) (\d+)x(\d+) inside',(src/'helper.log').read_text());x,y,w,h=map(int,m.groups());a=np.asarray(im);dark=a[:,x:x+w].max(axis=2)<70;hits=[]
 for yy in range(a.shape[0]):
  edges=np.diff(np.r_[0,dark[yy].astype(np.int8),0]);starts=np.nonzero(edges==1)[0];ends=np.nonzero(edges==-1)[0]
  if len(starts) and max(ends-starts)>150:hits.append(yy)
 body=[yy for yy in hits if 118<=yy<im.height-40];bar.append({'mode':mode,'bar':[x,y,w,h],'allDarkRows':len(hits),'pageDarkRows':len(body),'hiddenCells':r['capture'].get('hiddenCells'),'hiddenRows':r['capture'].get('hiddenRows')});im.crop((0,im.height-700,im.width,im.height)).save(derived/('inside-'+mode+'-tail.png'))
for name,cap,ref in [('firefox-lostauto-final','lostauto','lostauto-reference.png'),('firefox-mixed','mixed','mixed-reference.png'),('firefox-user-recovered','user-recovered','mixed-reference.png')]:
 d=derived/name;d.mkdir(exist_ok=True)
 if cap=='lostauto':
  c=next(x['value'] for x in json.loads((ex/'lostauto-results.json').read_text()) if x['label']=='end');doc=json.loads((ex/'lostauto-reference-info.json').read_text())['after']
 else:
  meta=json.loads((ex/(cap+'-comparison-info.json')).read_text());c=meta['capture'];doc={'docHeight':24117,'w':1920}
 f=ex/(cap+'-capture.png');assert hashlib.sha256(f.read_bytes()).hexdigest()==c['result']['sha256'];shutil.copyfile(f,d/'capture.png');Image.open(ex/ref).crop((240,82,1680,82+c['height'])).save(d/'reference.png')
 pins=json.loads((runs/'firefox-wiki-auto/pinned.json').read_text())
 for sample in pins:
  out=[]
  for e in sample['elements']:
   x,y,w,h=e['rect'];x-=240;y-=82;x0=max(0,x);y0=max(0,y);x1=min(1440,x+w);y1=min(820,y+h)
   if x1>x0 and y1>y0:out.append(dict(e,rect=[x0,y0,x1-x0,y1-y0]))
  sample['elements']=out
 (d/'pinned.json').write_text(json.dumps(pins));(d/'result.json').write_text(json.dumps({'browser':'firefox','site':'wiki','mode':name,'capture':c,'after':doc,'seconds':c['elapsedMs']/1000,'rect':[240,200,1440,820],'comparisonTransform':{'referenceCrop':[240,82,1440,c['height']],'referenceSource':str(ex/ref),'pinnedSource':'earlier same desktop/viewport Wikipedia native DOM positions, translated and clipped to visible intersection'}}));rows.append(S.one(d));print(json.dumps(rows[-1]),flush=True)
report={'scores':rows,'bar':bar};(P/'scores-m74-final.json').write_text(json.dumps(report,indent=1));print(json.dumps(bar),flush=True)
