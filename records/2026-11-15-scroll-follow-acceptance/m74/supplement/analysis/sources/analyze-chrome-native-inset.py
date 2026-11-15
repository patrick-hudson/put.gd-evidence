"""Explicit measured Chrome viewport-inset transform; originals and raw scores retained."""
from pathlib import Path
import json,sys,shutil
from PIL import Image
P=Path(sys.argv[1])if len(sys.argv)>1 else Path.home()/'work/sfa15/aurora-supplement';sys.path.insert(0,str(P));import score as S
Image.MAX_IMAGE_PIXELS=None;rows=[]
for d in sorted((P/'runs').glob('chromium-*')):
 if not(d/'reference.png').exists():continue
 r=json.loads((d/'result.json').read_text());v=r['viewport'];x,y,w,h=r['rect'];reported=v['reportedRect'];top=y-reported[1];bottom=reported[1]+v['info']['h']-(y+h)
 assert top>=0 and bottom>=0,(d.name,top,bottom)
 out=P/'analysis'/('native-inset-'+d.name);out.mkdir(exist_ok=True);shutil.copyfile(d/'capture.png',out/'capture.png')
 im=Image.open(d/'reference.png');im.crop((0,top,im.width,im.height-bottom)).save(out/'reference.png')
 pins=json.loads((d/'pinned.json').read_text())
 for sample in pins:
  for e in sample['elements']:e['rect'][1]-=top
 (out/'pinned.json').write_text(json.dumps(pins))
 r['comparisonTransform']={'method':'Native selected region starts below reported browser viewport. Crop only the measured top/bottom inset from original full-page reference; no fitted vertical shift, no image scaling. Original capture and reference preserved.','nativeRegion':r['rect'],'browserReportedRect':reported,'initialLogicalHeight':v['info']['h'],'referenceTopCrop':top,'referenceBottomCrop':bottom}
 (out/'result.json').write_text(json.dumps(r));row=S.one(out);row['transform']=r['comparisonTransform'];rows.append(row);print(json.dumps(row),flush=True)
(P/'analysis/chrome-native-inset-scores.json').write_text(json.dumps(rows,indent=1))

