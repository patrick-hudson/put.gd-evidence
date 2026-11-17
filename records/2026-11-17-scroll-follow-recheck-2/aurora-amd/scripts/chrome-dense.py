from pathlib import Path
from PIL import Image
import numpy as np,json
Image.MAX_IMAGE_PIXELS=None
P=Path.cwd();D=P/'runs/chromium-github-user-Cchrome-1';a=np.asarray(Image.open(D/'capture.png').convert('L'),dtype=np.float32);b=np.asarray(Image.open(D/'reference.png').convert('L'),dtype=np.float32);rows=[]
for r in range(17500,33501,100):
 band=a[r:r+64,400:1240:4];costs=[float(np.abs(b[r+s:r+s+64,400:1240:4]-band).mean())for s in range(-75,76)];i=int(np.argmin(costs));rows.append(dict(row=r,shift=i-75,difference=costs[i]))
(D/'dense-align.json').write_text(json.dumps(rows,indent=1));last=None
for row in rows:
 if row['shift']!=last:print(row,flush=True);last=row['shift']
lines=(D/'helper.log').read_text().splitlines();ix=[i for i,l in enumerate(lines)if 'scroll track:'in l and 'placed offset'in l][-1];(D/'loss-helper-excerpt.log').write_text('\n'.join(lines[max(0,ix-6):ix+40])+'\n');print('\n'.join(lines[max(0,ix-2):ix+17]))
white=(a[:,20:1900]>=248).mean(1)>.999;start=len(a)
while start and white[start-1]:start-=1
print('white-tail',start,len(a)-start)
