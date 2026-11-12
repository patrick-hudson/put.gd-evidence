from pathlib import Path
from PIL import Image
import json,numpy as np
P=Path('/home/lab/work/s3a');d=P/'new-nonfixed-v2-0'
a=Image.open(d/'capture.png').convert('RGB');b=Image.open(d/'generator-reference.png').convert('RGB');o=Image.new('RGB',(1920,900));o.paste(a.crop((0,500,960,1400)),(0,0));o.paste(b.crop((0,500,960,1400)),(960,0));o.save(P/'nonfixed-join.png')
d=P/'timer-resize';a=np.asarray(Image.open(d/'capture.png').convert('RGB'));shots=[]
for f in sorted(d.glob('screen-*.png')):
 b=np.asarray(Image.open(f).convert('RGB'))[200:800,100:1060];diff=np.any(a!=b,axis=2);shots.append({'screen':f.name,'mismatchPixels':int(diff.sum()),'bbox':None if not diff.any() else [int(np.where(diff)[1].min()),int(np.where(diff)[0].min()),int(np.where(diff)[1].max()),int(np.where(diff)[0].max())]})
(d/'viewport-verification.json').write_text(json.dumps({'method':'all RGB pixels against real console viewport screenshots','comparisons':shots},indent=2));print(shots)
