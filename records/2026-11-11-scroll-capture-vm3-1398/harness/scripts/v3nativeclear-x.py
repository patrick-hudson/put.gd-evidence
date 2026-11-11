import sys,time
from pathlib import Path
from PIL import Image
B=Path('/home/patrick/work/svm1398');sys.path.insert(0,str(B/'repo/tools/lab'));import lab
r=B/'repo/work/lab-runs/o3';o=B/'v3evidence/o'
for n in ['wayland_pointer.py','wayland_toplevels.py']:lab.put(r,B/'repo/tools/lab'/n,'/home/lab/'+n)
print(lab.guest_session(r,'python3 /home/lab/wayland_pointer.py click 1254 54 --extent 1280 800 --button left'))
time.sleep(2);Image.open(lab.screenshot(r,'v3-native-dismiss-x')['path']).save(o/'native-dismiss-x.png')
