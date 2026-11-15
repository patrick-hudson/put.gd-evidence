import json
from pathlib import Path
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
P=Path.home()/'work/sfa15';root=P/'scoring-f44';rows=[]
for mode,state in [('user','waiting'),('auto','autoScrolling')]:
 source=root/'extra/runs'/('firefox-wiki-'+mode+'-inside')/(state+'.png')
 native=np.asarray(Image.open(source).convert('RGB'))
 x0,x1,y0,y1=1760,1810,1032,1056
 control=float((native[y0:y1,x0:x1].max(axis=2)<80).mean())
 assert control>.8,(mode,control)
 a=np.asarray(Image.open(root/'runs'/('firefox-wiki-'+mode+'-inside')/'capture.png').convert('RGB'))
 perrow=(a[:,x0:x1].max(axis=2)<80).mean(axis=1)
 sums=np.r_[0,perrow.cumsum()];v=(sums[y1-y0:]-sums[:-(y1-y0)])/(y1-y0)
 matches=np.flatnonzero(v>.8).tolist()
 rows.append({'mode':mode,'nativeSource':str(source),'nativeDoneButtonCrop':[x0,y0,x1-x0,y1-y0],'nativeDarkCoverage':control,'scan':'Same fixed columns, every 24-row window of the full captured image; detects the dark Done button on GNOME white bar. Threshold dark RGB max<80, coverage>0.80. Also visually inspected the two last 800-row images.','capturedMaximumDarkCoverage':float(v.max()),'matchingRows':matches})
 assert not matches,rows[-1]
(P/'f44-gnome-white-bar-scan.json').write_text(json.dumps(rows,indent=1));print(json.dumps(rows))
