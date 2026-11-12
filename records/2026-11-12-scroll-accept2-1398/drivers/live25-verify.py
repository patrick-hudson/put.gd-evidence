from pathlib import Path
import json,hashlib,re,collections,numpy as np
from PIL import Image
P=Path('/home/patrick/work/sl25/live-site');summary=[]
for d in sorted(P.iterdir()):
 if not d.is_dir() or not (d/'capture.png').exists():continue
 r=json.loads((d/'result.json').read_text());cap=np.asarray(Image.open(d/'capture.png').convert('RGB'));ref=np.asarray(Image.open(d/'reference-before.png').convert('RGB'));h,w=cap.shape[:2];log=(d/'helper.log').read_text();top=re.findall(r'way to the top (\d+) steps, (\d+) ms, (.*)',log);r['wayUpSeconds']=int(top[-1][1])/1000 if top else 0;r['topReached']=('top proved' in top[-1][2]) if top else None;r['topReachedSource']='helper log' if top else 'not requested';r['capture'].setdefault('topReached',r['topReached']);r['referenceSize']=[ref.shape[1],ref.shape[0]]
 # Independent Firefox drawSnapshot and captured page: match static nonblank scanline strips without OCR.
 strips=[]
 for a,b in [(180,700),(800,1400)]:
  a=min(a,w);b=min(b,w);c=cap[:,a:b:4,:];f=ref[:,a:b:4,:];indexes=collections.defaultdict(list)
  for y,row in enumerate(f):
   if row.std()>12:indexes[hashlib.sha256(row.tobytes()).digest()].append(y)
  mapping=[]
  for y,row in enumerate(c):
   if row.std()<12:continue
   hits=indexes.get(hashlib.sha256(row.tobytes()).digest(),[])
   if len(hits)==1:mapping.append([y,hits[0]])
  offsets=collections.Counter(yy-y for y,yy in mapping);backwards=[(mapping[i-1],mapping[i]) for i in range(1,len(mapping)) if mapping[i][1]<mapping[i-1][1]-3];jumps=[]
  for i in range(1,len(mapping)):
   a0,b0=mapping[i-1];a1,b1=mapping[i]
   if a1-a0<40 and abs((b1-b0)-(a1-a0))>3:jumps.append([a0,b0,a1,b1])
  strips.append({'x':[a,b],'uniqueStaticMatchedScanlines':len(mapping),'captureRange':[mapping[0][0],mapping[-1][0]] if mapping else None,'referenceRange':[mapping[0][1],mapping[-1][1]] if mapping else None,'offsetHistogram':offsets.most_common(10),'backwardsMatches':backwards[:20],'localOffsetJumps':jumps[:20]})
 before=json.loads((d/'dom-before.json').read_text());ids=[]
 for x in before['anchors']:
  if x['id'] not in [v['id'] for v in ids]:ids.append(x)
 covered=[x for x in ids if x['y']<h];r['verification']={'method':'two independently rendered vertical scanline strips, exact RGB hash matches excluding uniform rows; no OCR','strips':strips,'documentCommentAnchors':len(ids),'commentAnchorsWithinCapturedDocumentPrefix':covered,'firstCommentY':ids[0]['y'] if ids else None,'loadedImagesBefore':before['loadingImages'],'documentHeightStable':r['domBeforeHeight']==r['domAfterHeight'],'limitation':'No pixel oracle for live content; row matching does not prove every pixel or hidden Load more content. Header classification supplemented by visual inspection.'}
 (d/'verification.json').write_text(json.dumps(r,indent=2));summary.append(r)
(P/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps([{'name':r['name'],'height':r['capture']['height'],'reason':r['capture']['endReason'],'wayUp':r['wayUpSeconds'],'topReached':r['topReached'],'strips':r['verification']['strips']} for r in summary]))
