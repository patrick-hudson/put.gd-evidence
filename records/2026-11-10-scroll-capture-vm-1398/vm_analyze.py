import sys,json
from pathlib import Path
from types import SimpleNamespace
from PIL import Image
from scroll_run_vm import pattern,verify
p=Path(sys.argv[1]);summary=[]
for result in p.glob('*/result.json'):
 a=json.loads(result.read_text());out={'case':result.parent.name,'reportedPass':a.get('pass'),'capture':a.get('capture',{})};imfile=result.parent/'capture.png'
 if imfile.exists():
  im=Image.open(imfile).convert('RGB');w,h=im.size;cw=(w-76)//16
  got=[]
  for y in range(min(h,80)):
   bits=0
   for k in range(16):bits=(bits<<1)|(sum(im.getpixel((64+k*cw+cw//2,y)))<384)
   got.append(bits)
  offsets=[i for i in range(2400) if all(g==pattern((i+y)//40,(i+y)%40) for y,g in enumerate(got))]
  out['candidateStartPixels']=offsets
  if len(offsets)==1:
   args=SimpleNamespace(**a['arguments']);args.first_pixel=offsets[0];args.height=h;args.code_width=w
   out['prefixVerification']=verify(imfile,args)
 summary.append(out)
(p/'analysis.json').write_text(json.dumps(summary,indent=2));print(json.dumps([{k:v for k,v in x.items() if k!='capture'} for x in summary],indent=2))
