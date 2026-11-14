from pathlib import Path
import sys
from PIL import Image
sys.path.insert(0,str(Path.home()/'work/s52/tools/lab'));import lab
r=Path.home()/'work/s52/work/lab-runs'/sys.argv[1];p=Path.home()/'work/s1520'/sys.argv[2];raw=p.with_suffix('.ppm')
with lab.QMP(r/'qmp.sock') as q:q.execute('screendump',{'filename':str(raw)})
Image.open(raw).save(p);print(p)
