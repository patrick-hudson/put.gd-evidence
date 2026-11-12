from pathlib import Path
from PIL import Image
import numpy as np,json,sys
P=Path(sys.argv[1]);results={}
for f in P.rglob('capture.png'):
 if not (f.parent.name.startswith(('notice-','cap-visual','fallback-')) or P.name in ['sq3','sq4']):continue
 im=np.array(Image.open(f).convert('RGB')).astype('int16');h,w,_=im.shape
 if w<=960:continue
 mask=np.any(np.abs(im[:,960:w-1]-250)>12,axis=2);v={'rightMarginX':[960,w-1],'rowsChecked':h,'unexpectedPixels':int(mask.sum()),'exactBlankMargin':not bool(mask.any())};(f.parent/'blank-margin-verification.json').write_text(json.dumps(v,indent=2));results[str(f.relative_to(P))]=v
print(json.dumps(results))
