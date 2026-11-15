import sys,json,hashlib,shutil
from pathlib import Path
from PIL import Image
P=Path(sys.argv[1]);sys.path.insert(0,str(P));import score as S
Image.MAX_IMAGE_PIXELS=None
O=P/'analysis';out=[]
for prefix in ['mixed-focused','user-script-recovery','auto-script-recovery','auto-native-recovery']:
 meta=P/(prefix+'-reference-info.json');events=P/(prefix+'-results.json')
 if not meta.exists()or not events.exists():continue
 m=json.loads(meta.read_text());c=next((x['value']for x in json.loads(events.read_text())if x['label']=='end'),None)
 if not c or c.get('state')!='done':continue
 source=P/(prefix+'-capture.png')
 if not source.exists():
  want=c.get('sha256')or c.get('result',{}).get('sha256');matches=[]
  for f in (P/'native-export/archive').rglob('*.png'):
   if hashlib.sha256(f.read_bytes()).hexdigest()==want:matches.append(f)
  assert len(matches)==1,(prefix,want,len(matches));source=matches[0]
  (O/(prefix+'-offline-artifact-proof.json')).write_text(json.dumps({'operationId':c['id'],'sourceNativeArchivePath':str(source),'sha256':want,'sourceArchiveVerifiedBeforeRetirement':True,'matchedTerminalResultSha256':True},indent=1))
 view=m['viewport']['rect'];top=200-view[1];d=O/prefix;d.mkdir(exist_ok=True);shutil.copyfile(source,d/'capture.png');Image.open(P/(prefix+'-reference.png')).crop((240,top,1680,top+c['height'])).save(d/'reference.png')
 if prefix=='mixed-focused':shutil.copyfile(P/(prefix+'-pinned.json'),d/'pinned.json')
 else:
  pins=json.loads((P/'runs/firefox-wiki-auto/pinned.json').read_text())
  for sample in pins:
   elems=[]
   for e in sample['elements']:
    x,y,w,h=e['rect'];x-=240;y-=top;x0=max(0,x);y0=max(0,y);x1=min(1440,x+w);y1=min(820,y+h)
    if x1>x0 and y1>y0:elems.append(dict(e,rect=[x0,y0,x1-x0,y1-y0]))
   sample['elements']=elems
  (d/'pinned.json').write_text(json.dumps(pins))
 after=m.get('after')or{'docHeight':Image.open(P/(prefix+'-reference.png')).height}
 r={'browser':'firefox','site':'wiki','mode':prefix,'capture':c,'after':after,'seconds':c['elapsedMs']/1000,'rect':[240,200,1440,820],'comparisonTransform':{'referenceCrop':[240,top,1440,c['height']],'nativeInitialViewport':view,'sourceReference':str(P/(prefix+'-reference.png')),'pinSource':'Same-run sampled visible rectangles'if prefix=='mixed-focused'else'Main auto-run visible fixed/sticky DOM rectangles transformed to selected region; not a contemporaneous mask.'}}
 (d/'result.json').write_text(json.dumps(r));out.append(S.one(d));print(json.dumps(out[-1]),flush=True)
(O/'control-image-scores.json').write_text(json.dumps(out,indent=1))
