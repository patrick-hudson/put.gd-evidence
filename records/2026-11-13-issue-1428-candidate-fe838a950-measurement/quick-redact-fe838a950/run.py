from pathlib import Path
import json,time,hashlib,collections
from PIL import Image,ImageDraw,ImageFont
from item8_campaign import Campaign
r=Path.home()/'work/ocr-corpus-1428';w=r/'candidate-editor-checks';c=Campaign(w);c.raw('editor.cancel',{'id':'6ec291b6-6b44-4be2-85a4-c11e46bf5ff3'});fixtures=r/'synthetic-final';extra=w/'fixtures';extra.mkdir(mode=0o700)
fontpath=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf');font=ImageFont.truetype(str(fontpath),20);im=Image.new('RGB',(900,180),'white');draw=ImageDraw.Draw(im);truth=[]
for cat,text,y in [('control','SYNTHETIC TEXT 1428',12),('email','hello@example.test',45)]:
 draw.text((12,y),text,font=font,fill='black');truth.append({'category':cat,'box':list(draw.textbbox((12,y),text,font=font)),'text_codepoints':list(map(ord,text))})
im.save(extra/'email-after-heading.png');(extra/'email-after-heading.truth.json').write_text(json.dumps({'words':truth,'font_pixels':20,'font_sha256':hashlib.sha256(fontpath.read_bytes()).hexdigest()},indent=2))
pages=sorted(fixtures.glob('redact-*.png'))+[fixtures/'clean-prose.png',fixtures/'clean-code.png',fixtures/'hashes.png',extra/'email-after-heading.png'];rows=[];exports=w/'quick-exports';exports.mkdir(mode=0o700)
def intersects(a,b):return a[0]<b[2] and a[2]>b[0] and a[1]<b[3] and a[3]>b[1]
for path in pages:
 row={'page':path.name,'sourceSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'status':'not_run'};op=None
 try:
  gt=json.loads(path.with_suffix('.truth.json').read_text())['words'];positive=[g for g in gt if g['category'] not in ['control','clean']];negative=[g for g in gt if g['category'] in ['control','clean']]
  op,state=c.open_editor(path);a=c.call('editor.apply',{'id':op,'commands':[{'op':'redactText','categories':['email','phone','ip','card','key']}]});state=c.call('editor.inspect',{'id':op});shapes=[s for s in state['shapes'] if s['kind']=='redact'];rects=[[s['rect'][0],s['rect'][1],s['rect'][0]+s['rect'][2],s['rect'][1]+s['rect'][3]] for s in shapes];out=exports/path.name;c.call('editor.saveCopy',{'id':op,'path':str(out)});flat=Image.open(out).convert('RGB');covered=[]
  for g in positive:
   crop=flat.crop(tuple(g['box']));covered.append(crop.getextrema()==((0,0),(0,0),(0,0)))
  extra_marks=sum(not any(intersects(rect,g['box']) for g in positive) or any(intersects(rect,g['box']) for g in negative) for rect in rects)
  row.update(status='measured',targetItems=len(positive),coveredItems=sum(covered),uncoveredItems=[i for i,v in enumerate(covered) if not v],redactMarks=len(shapes),extraMarks=extra_marks,apply=a,rects=rects,exportSha256=hashlib.sha256(out.read_bytes()).hexdigest(),allTargetBoxesOpaqueBlack=all(covered),negativePage=len(positive)==0,negativeAtMostOne=len(shapes)<=1 if not positive else None)
 except Exception as e:row['reason']=str(e)
 finally:
  if op:c.raw('editor.cancel',{'id':op})
 rows.append(row);(w/'quick-redact-pages.json').write_text(json.dumps({'candidate':'fe838a9502167672f3512e27c32c74cfcf6c84d1','scope':'offscreen real editor/core and exported pixels; native window pipeline covered separately','pages':rows},indent=2))
 print(path.name,row['status'],row.get('coveredItems'),row.get('extraMarks'),flush=True)
