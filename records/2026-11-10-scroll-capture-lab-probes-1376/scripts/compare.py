from PIL import Image
import numpy as np,json,sys
from pathlib import Path
p=Path(sys.argv[1]);a=np.array(Image.open(p/'before.png').convert('RGB'));b=np.array(Image.open(p/'after.png').convert('RGB'));best=[]
for dy in range(1,min(a.shape[0]-24,500)):
 d=np.abs(a[dy:].astype(np.int16)-b[:-dy].astype(np.int16));best.append((float(d.mean()),dy,int(d.max()),int(np.all(d==0,axis=(1,2)).sum())))
r={'shape':list(a.shape),'best':sorted(best)[:5]};print(json.dumps(r));(p/'comparison.json').write_text(json.dumps(r,indent=2)+'\n')
