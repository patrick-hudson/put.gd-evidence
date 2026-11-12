from pathlib import Path
import json,re,numpy as np,hashlib
from PIL import Image
import scroll_run
P=Path('/home/patrick/work/sa2');d=P/'timer-resize';r=json.loads((d/'result.json').read_text());im=np.asarray(Image.open(d/'capture.png').convert('RGB')).astype('int16');H,W,_=im.shape
steps=re.findall(r'scroll step:.*fixed (\d+)/(\d+)',(d/'helper.log').read_text());top,bottom=map(int,steps[-1]);body=im[top:H-bottom];bad=0
shot=np.asarray(Image.open(sorted(d.glob('screen-*.png'))[-1]).convert('RGB')).astype('int16')[200:800,100:1060]
rightStart=761 if np.any(shot[top:600-bottom,760]!=102) else 760
for ci in range(13):
 codes=np.array([scroll_run.pattern(*divmod(y,40)) for y in range(24000)],dtype='uint32');want=np.where((codes>>(15-ci))&1,16,250)
 bad+=int(np.count_nonzero(np.any(np.abs(body[:24000,64+ci*55+2:min(64+(ci+1)*55-2,rightStart)]-want[:,None,None])>12,axis=2)))
shot=np.asarray(Image.open(sorted(d.glob('screen-*.png'))[-1]).convert('RGB')).astype('int16')[200:800,100:1060]
fixedbad=int(np.count_nonzero(np.any(im[:top]!=shot[:top],axis=2)))+int(np.count_nonzero(np.any(im[-bottom:]!=shot[-bottom:],axis=2)))
rightbad=int(np.count_nonzero(np.any(body[:,rightStart:]!=102,axis=2)))
v={'method':'final steady fixed bands; every visible full barcode cell; exact fixed-band equality to final live frame; right gray','rightBackgroundStartsAt':rightStart,'top':top,'bottom':bottom,'documentRows':len(body),'badCellPixels':bad,'fixedBandMismatchPixels':fixedbad,'rightBackgroundMismatchPixels':rightbad,'exact':len(body)==24000 and bad==0 and fixedbad==0 and rightbad==0}
(d/'independent-layout-verification.json').write_text(json.dumps(v,indent=2));print(v)
