from pathlib import Path
import inspect,json,numpy as np
from PIL import Image
import score
P=Path.cwd();src=inspect.getsource(score.tolerant).replace('equal = total = 0','equal = total = 0; badrows=[]').replace('equal += bad.sum() <= 0.01 * mask.sum()','equal += bad.sum() <= 0.01 * mask.sum()\n        if bad.sum() > 0.01 * mask.sum():badrows.append([lo,hi,round(float(bad.sum()/mask.sum()),4)])').replace('return [int(equal), int(total)]','return dict(equal=int(equal),total=int(total),badRows=badrows,horizontalShift=best)')
exec(src,score.__dict__)
for d in sorted((P/'runs').iterdir()):
 if d.name not in ['firefox-wiki-user-D-forced-2','chromium-github-user-Cchrome-1']:continue
 r=json.loads((d/'result.json').read_text());ref=score.S.Reference(d,r['rect'][3]);im=score.S.load_rgb(d/'capture.png');v=score.tolerant(ref,im);(d/'band-details.json').write_text(json.dumps(v,indent=1));print(d.name,v,flush=True)
