from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,shutil,numpy as np
P=Path('/home/patrick/work/s3a');W=960;H=24000;fp=next(Path('/usr/share/fonts').rglob('DejaVuSansMono.ttf'));font=ImageFont.truetype(str(fp),16)
for kind,prefix in [('counter','new-counter-'),('nonfixed','new-nonfixed-'),('nonfixed','new-nonfixed-v2-'),('late','new-late-')]:
 for i in range(2):
  out=P/(prefix+str(i))
  if not (out/'result.json').exists():continue
  log=[json.loads(x) for x in (P/(out.name+'-fixture.log')).read_text().splitlines() if x.startswith('{') and not json.loads(x).get('ready')]
  body=Image.new('RGB',(W,H),'white');d=ImageDraw.Draw(body)
  for y in range(0,H,24):d.text((16,y),f'Body row {y//24:04d} independent exact oracle',font=font,fill='black')
  if kind=='nonfixed':
   active=False;maximum=0
   for ev in log:
    pos=ev['pos']
    if pos==0:active=True;maximum=0
    if active and pos>maximum:
     maximum=pos;y=pos+552
     if y<H:d.rectangle((0,y,W-1,min(H-1,y+35)),fill='#806020');d.text((15,y+5),'Nonfixed counter '+str(ev['step']),font=font,fill='white')
  body.save(out/'generator-body.png')
  footer=None
  if kind in ['counter','late']:
   footer=Image.new('RGB',(W,36),'#806020');ImageDraw.Draw(footer).text((15,5),'Counter '+str(log[-1]['step']) if kind=='counter' else 'Late bottom banner',font=font,fill='white');footer.save(out/'generator-footer.png')
  top=None
  if kind=='late':
   top=Image.new('RGB',(W,36),'#205080');ImageDraw.Draw(top).text((15,5),'Late top bar',font=font,fill='white');top.save(out/'generator-header.png')
  ref=Image.new('RGB',(W,H+(36 if footer else 0)+(36 if top else 0)),'white');offset=36 if top else 0
  if top:ref.paste(top,(0,0))
  ref.paste(body,(0,offset))
  if footer:ref.paste(footer,(0,offset+H))
  ref.save(out/'generator-reference.png')
  cap=np.asarray(Image.open(out/'capture.png').convert('RGB'));ra=np.asarray(ref);nh=min(len(cap),len(ra));diff=np.any(cap[:nh]!=ra[:nh],axis=2)
  r=json.loads((out/'result.json').read_text());saved=out/'initial-oracle.json'
  if not saved.exists():shutil.copyfile(out/'result.json',saved)
  r['retainedOracle']={'method':'independent deterministic generator replay from recorded valueChanged pos/step events; no product pixels used to construct reference','fontSha256':hashlib.sha256(fp.read_bytes()).hexdigest(),'referenceSha256':hashlib.sha256((out/'generator-reference.png').read_bytes()).hexdigest(),'captureSha256':hashlib.sha256((out/'capture.png').read_bytes()).hexdigest(),'height':len(cap),'expectedHeight':len(ra),'mismatchPixels':int(diff.sum()),'firstBadRow':int(np.where(diff.any(axis=1))[0][0]) if diff.any() else None,'pixelExact':len(cap)==len(ra) and not bool(diff.any()),'fixtureLastPosition':log[-1]['pos'],'fixtureMaximumPosition':H+(36 if footer else 0)-600,'falseCompletion':r.get('capture',{}).get('endReason')=='end_of_content' and len(cap)!=len(ra)}
  if kind=='late':
   bodycap=cap[:-36];bd=np.any(bodycap!=np.asarray(body)[:len(bodycap)],axis=2);r['retainedOracle']['bodyPrefixMismatchPixels']=int(bd.sum());r['retainedOracle']['lateHeaderAtTop']=bool(np.array_equal(cap[:36],np.asarray(top)))
  (out/'result.json').write_text(json.dumps(r,indent=2));print(out.name,r['retainedOracle'],flush=True)
