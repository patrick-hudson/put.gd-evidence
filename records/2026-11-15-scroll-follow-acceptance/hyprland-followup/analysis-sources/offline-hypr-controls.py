"""Score retained native Hyprland control images using measured viewport origin."""
import sys,json,hashlib,shutil
from pathlib import Path
from PIL import Image
P=Path(sys.argv[1]);sys.path.insert(0,str(P));import score as S
Image.MAX_IMAGE_PIXELS=None;O=P/'analysis';O.mkdir(exist_ok=True);rows=[]
for prefix in ['mixed-focused','user-script-recovery','auto-script-recovery','auto-native-recovery','h2-auto-recovery','h2-valid-auto-recovery']:
 meta=P/(prefix+'-reference-info.json');events=P/(prefix+'-results.json')
 if not meta.exists()or not events.exists():continue
 m=json.loads(meta.read_text());ends=[x['value']for x in json.loads(events.read_text())if x['label']in['end','forced-end']and isinstance(x['value'],dict)and x['value'].get('state')=='done']
 if not ends:continue
 c=ends[-1];view=m['viewport']['rect'];rect=c.get('rect',m.get('rect',[240,200,1440,820]));rx,ry,w,h=rect;left=rx-view[0];top=ry-view[1];source=P/(prefix+'-capture.png')
 if not source.exists():
  want=c.get('sha256')or c.get('result',{}).get('sha256');index=json.loads((P/'native-export/native-restore-index.json').read_text())['files'];found=[P/'native-export'/n for n,v in index.items()if n.startswith('archive/')and v['sha256']==want];assert len(found)==1,(prefix,found);source=found[0];assert hashlib.sha256(source.read_bytes()).hexdigest()==want
 d=O/(prefix+'-native-origin');d.mkdir(exist_ok=True);shutil.copyfile(source,d/'capture.png');Image.open(P/(prefix+'-reference.png')).crop((left,top,left+w,top+c['height'])).save(d/'reference.png')
 pin=P/(prefix+'-pinned.json')
 if prefix=='mixed-focused'and pin.exists():
  pins=json.loads(pin.read_text())
  for sample in pins:
   for e in sample['elements']:e['rect'][0]+=view[0]
  pin_note='Same-run sampled DOM pins; correct the original zero-origin assumption by measured native X offset.'
 else:
  candidates=[P/'runs/firefox-wiki-auto-full-width/pinned.json',P/'runs/firefox-wiki-auto/pinned.json',P.parent/'guest-h/runs/firefox-wiki-auto-full-width/pinned.json'];pin=next(x for x in candidates if x.exists());pins=json.loads(pin.read_text())
  for sample in pins:
   a=[]
   for e in sample['elements']:
    x,y,ww,hh=e['rect'];x-=left;y-=top;x0=max(0,x);y0=max(0,y);x1=min(w,x+ww);y1=min(h,y+hh)
    if x1>x0 and y1>y0:a.append(dict(e,rect=[x0,y0,x1-x0,y1-y0]))
   sample['elements']=a
  pin_note='Borrowed static DOM pin geometry from the primary same-width Firefox Wikipedia run; not claimed contemporaneous. Unmasked score is also retained.'
 (d/'pinned.json').write_text(json.dumps(pins))
 r={'browser':'firefox','site':'wiki','mode':prefix,'capture':c,'after':m['after'],'seconds':c['elapsedMs']/1000,'rect':rect,'comparisonTransform':{'nativeInitialViewport':view,'referenceCrop':[left,top,w,c['height']],'pinSource':str(pin),'pinSourceSha256':hashlib.sha256(pin.read_bytes()).hexdigest(),'pinNote':pin_note,'sourceCaptureSha256':hashlib.sha256(source.read_bytes()).hexdigest()}};(d/'result.json').write_text(json.dumps(r));row=S.one(d);ref=S.S.Reference(d,h);ref.rects=[];row['unmaskedTolerant']=S.tolerant(ref,S.S.load_rgb(d/'capture.png'));row['pinNote']=pin_note;rows.append(row);print(json.dumps(row),flush=True)
(O/'control-image-scores-native-origin.json').write_text(json.dumps(rows,indent=1))
