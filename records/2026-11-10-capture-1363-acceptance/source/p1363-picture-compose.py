import sys,json
from pathlib import Path
from PIL import Image
E=Path(sys.argv[1]);name=sys.argv[2];spec=json.loads(Path(sys.argv[3]).read_text());rows=[];width=0;total_h=0;shapes=[]
for pan in spec['panels']:
 im=Image.open(E/pan['file']).convert('RGB');im=im.crop(tuple(pan['crop'])) if 'crop' in pan else im;rows.append((im,pan));width=max(width,im.width);total_h+=im.height+38
canvas=Image.new('RGB',(width,total_h),'#101114');y=0
for im,pan in rows:
 canvas.paste(im,(0,y+38));shapes.append({'kind':'text','at':[10,y+8],'text':pan['caption'],'color':'#ffffff','fontPixels':pan.get('captionPixels',18)})
 for shape in pan.get('shapes',[]):
  shape=json.loads(json.dumps(shape))
  if 'rect' in shape:shape['rect'][1]+=y+38
  if 'at' in shape:shape['at'][1]+=y+38
  for key in ['from','to']:
   if key in shape:shape[key][1]+=y+38
  shapes.append(shape)
 y+=im.height+38
canvas.save(E/(name+'-pre.png'));(E/(name+'-spec.json')).write_text(json.dumps(shapes))
