import sys,time,json,shlex
from pathlib import Path
from PIL import Image
B=Path('/home/patrick/work/svm1398');sys.path.insert(0,str(B/'repo/tools/lab'));import lab
r=B/'repo/work/lab-runs/o3';o=B/'v3evidence/o'
def cmd(c):return lab.guest_session(r,c,timeout=300)
def shot(n):Image.open(lab.screenshot(r,'v3-'+n)['path']).save(o/(n+'.png'))
s=Path('/home/patrick/work/sf1398/qt_fixture.py').read_text();s=s.replace('w.showFullScreen();', '''from PyQt6.QtCore import QObject,QEvent
class WheelObserver(QObject):
    def eventFilter(self,obj,e):
        if e.type()==QEvent.Type.Wheel:print('WHEEL',e.angleDelta().x(),e.angleDelta().y(),e.pixelDelta().x(),e.pixelDelta().y(),int(e.phase().value),flush=True)
        return False
observer=WheelObserver();s.viewport().installEventFilter(observer)
w.showFullScreen();''');f=B/'v3events.py';f.write_text(s);lab.put(r,f,'/home/lab/v3events.py')
for n in ['wayland_pointer.py','wayland_toplevels.py']:lab.put(r,B/'repo/tools/lab'/n,'/home/lab/'+n)
pid=int(cmd('WAYLAND_DEBUG=client SC_Y=100 nohup python3 /home/lab/v3events.py --rows 600 --start 12000 > /tmp/v3/hypr-wheel.log 2>&1 < /dev/null & echo $!').strip());time.sleep(4);shot('wheel-before')
for i,notches in enumerate([-10,-10,-1,-1,1]):
 c='python3 /home/lab/wayland_pointer.py axis 500 300 '+str(notches)+' --extent 1280 800';(o/('wheel-command'+str(i)+'.log')).write_text(cmd(c));time.sleep(2);shot('wheel-after'+str(i))
(o/'hypr-wheel.log').write_text(cmd('cat /tmp/v3/hypr-wheel.log'));cmd('kill '+str(pid));print('Hyprland wheel probe complete',flush=True)
