from pathlib import Path
import json,hashlib,sys
from PIL import Image,ImageChops
l=Path(sys.argv[1]) if len(sys.argv)>1 else Path.home()/'work/s1520/a'
files={}
for p in sorted((l/'out').rglob('*.png')): files.setdefault(hashlib.sha256(p.read_bytes()).hexdigest(),[]).append(p)
r={}
byop={}
if (l/'cancel.json').exists():
 for row in json.load(open(l/'cancel.json')).get('before',{}).get('records',[]):
  if row.get('local',{}).get('path'): byop[row.get('operationId')]=l/'out/images'/Path(row['local']['path']).name
for mode in ['pointer','api']:
 a=json.load(open(l/(mode+'-plain.json')));b=json.load(open(l/(mode+'-resumed.json')))
 aa=files.get(a.get('result',{}).get('sha256'),[]);bb=files.get(b.get('result',{}).get('sha256'),[])
 pa=aa[-2 if mode=='api' and len(aa)>1 else 0] if aa else None;pb=bb[-1 if mode=='api' else 1 if len(bb)>1 else 0] if bb else None
 pa=byop.get(a.get('id'),pa);pb=byop.get(b.get('id'),pb)
 v={'plainHeight':a.get('height'),'resumedHeight':b.get('height'),'plainEnd':a.get('endReason'),'resumedEnd':b.get('endReason'),'plainFile':str(pa),'resumedFile':str(pb),'missing':not(pa and pb)}
 if pa and pb:
  x=Image.open(pa).convert('RGB');y=Image.open(pb).convert('RGB');v['sizeEqual']=x.size==y.size
  v['different64RowBands']=[row//64 for row in range(0,min(x.height,y.height),64) if ImageChops.difference(x.crop((0,row,x.width,min(row+64,x.height))),y.crop((0,row,y.width,min(row+64,y.height)))).getbbox()]
 r[mode]=v
json.dump(r,open(l/'band-comparison.json','w'),indent=2);print(json.dumps(r))
