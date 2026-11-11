# Pixel templates for fixture's four known decimal digits, no OCR dependency.
import numpy as np,json,sys
from PIL import Image
from pathlib import Path
def verify(path):
 a=np.asarray(Image.open(path).convert('L')).astype('int16');m=np.abs(a[:,:180]-np.median(a[:,:180]))>60
 rows=m.any(1);edges=np.diff(np.r_[False,rows,False].astype(int));bands=list(zip(np.where(edges==1)[0],np.where(edges==-1)[0]));whole=[m[y:z] for y,z in bands]
 if len(whole)!=1500 or len({x.shape for x in whole})!=1:return {'pass':False,'reason':'bands or shapes','bands':len(whole)}
 slots=[]
 for factor in (1000,100,10,1):
  samples=[whole[d*factor] for d in range(2 if factor==1000 else 10)]
  changed=np.logical_or.reduce([x!=samples[0] for x in samples]).any(0)
  cols=np.where(changed)[0];lo,hi=int(cols[0]),int(cols[-1])+1
  slots.append((lo,hi,[x[:,lo:hi] for x in samples]))
 slots=[(lo,min(hi,slots[n+1][0] if n<3 else lo+(lo-slots[n-1][0])),samples) for n,(lo,hi,samples) in enumerate(slots)]
 slots=[(lo,hi,[x[:,:hi-lo] for x in samples]) for lo,hi,samples in slots]
 bad=[]
 for i,x in enumerate(whole):
  for n,d in enumerate(f'{i:04d}'):
   lo,hi,templates=slots[n]
   if not np.array_equal(x[:,lo:hi],templates[int(d)]):bad.append([i,n]);break
 advance=[(x[0],x[1]) for x in slots]
 return {'pass':not bad,'bands':len(whole),'digitAdvance':advance,'badCount':len(bad),'firstBad':bad[:12],'method':'four known decimal glyphs compared pixel-for-pixel on every line band, edge bands included'}
if __name__=='__main__':
 p=Path('/home/patrick/work/p31398')
 for f in sorted(p.glob('*full-*/capture.png')):
  r=verify(f);(f.parent/'order-verification.json').write_text(json.dumps(r,indent=2));print(f.parent.name,r)
