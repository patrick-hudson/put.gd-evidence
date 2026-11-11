from control import *
import shutil
src=BASE.parent/'final/m74/raw';out=BASE/'native-tools';out.mkdir(exist_ok=True)
for f in src.glob('*.py'):
 text=f.read_text().replace('/home/patrick/work/pfin','/home/patrick/work/pcn')
 (out/f.name).write_text(text)
f=out/'text_fixture.py';t=f.read_text().replace('w.showFullScreen(); print', 'w.showFullScreen();\n    from PyQt6.QtCore import QTimer\n    QTimer.singleShot(1000, lambda: w.verticalScrollBar().setValue(w.verticalScrollBar().maximum()))\n    print').replace('w.fullscreen(); w.present(); print', 'w.fullscreen(); w.present();\n    GLib.timeout_add(1000, lambda: (s.get_vadjustment().set_value(s.get_vadjustment().get_upper()), False)[1])\n    print');f.write_text(t)
for h in IPS:
 ssh(h,'mkdir -m 700 /home/patrick/work/pcn',check=True)
 for f in out.glob('*.py'):put(h,f,'/home/patrick/work/pcn/'+f.name)
 ssh(h,'cp /home/patrick/work/pfin/ruler.html /home/patrick/work/pcn/ruler.html',check=True)
