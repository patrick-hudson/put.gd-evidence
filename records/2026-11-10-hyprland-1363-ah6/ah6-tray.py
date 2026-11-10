import sys,json,time
from pathlib import Path
sys.argv=['checks','ah6','/home/patrick/work/put.gd/work/lab-bootstrap-omarchy/identity','hyprland']
exec(compile(Path('/tmp/p1363-gui.py').read_text().split('mode=sys.argv[4]')[0],'<gui>','exec'))
move(700,300);time.sleep(.5);move(1151,13);time.sleep(1.3);move(1124,13);time.sleep(.6)
guest(ENV+'python3 /tmp/wayland_pointer.py click 1124 13 --button right --extent 2304 800');time.sleep(1);photo('tray-open')
