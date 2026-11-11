import sys,time
from pathlib import Path
from PIL import Image
B=Path('/home/patrick/work/svm1398');sys.path.insert(0,str(B/'repo/tools/lab'));import lab
r=B/'repo/work/lab-runs/o3';o=B/'v3evidence/o'
for i in range(3):
 lab.pointer(r,1100,70,1280,800);time.sleep(.4);lab.pointer(r,1100,70,1280,800,True,button='right');time.sleep(.2);lab.pointer(r,1100,70,1280,800,False,button='right');time.sleep(.7);Image.open(lab.screenshot(r,'v3-notify-dismiss-'+str(i))['path']).save(o/('notify-dismiss-'+str(i)+'.png'))
