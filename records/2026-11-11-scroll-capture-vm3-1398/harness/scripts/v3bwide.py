from pathlib import Path
import numpy as np,json,re
from PIL import Image
p=Path('/home/patrick/work/svm1398/v3evidence/b');reference=np.asarray(Image.open(p/'qt1280-ready.png').convert('RGB'))[100:700,:1260];base=reference[:,:300];background=np.median(reference[:,300:],axis=1).astype(np.uint8)
out={}
for i in range(1,4):
 n='qt1280-'+str(i);d=p/'final/cases'/n;a=np.asarray(Image.open(d/'capture.png').convert('RGB'));bad=np.any(a[:,:300]!=base,axis=2);log=(d/'helper.log').read_text();out[n]={'matchesInitialTextPixels':not bad.any(),'changedPixelsInTextColumns':int(bad.sum()),'columns':[0,299],'backgroundMismatchPixels':int(np.any(a[:,300:]!=background[:,None,:],axis=2).sum()),'exactPrefix':not bad.any() and not np.any(a[:,300:]!=background[:,None,:]),'source':re.findall(r'scroll: source[^\n]*',log),'steps':[s for s in log.splitlines() if 'scroll step:' in s or 'scroll: ended' in s]};print(n,out[n])
(p/'qt-wide-prefix-verification.json').write_text(json.dumps(out,indent=2))
