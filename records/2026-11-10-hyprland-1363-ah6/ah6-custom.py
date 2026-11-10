import sys,json,time
from pathlib import Path
sys.argv=['checks','ah6','/home/patrick/work/put.gd/work/lab-bootstrap-omarchy/identity','hyprland']
exec(compile(Path('/tmp/p1363-gui.py').read_text().split('mode=sys.argv[4]')[0],'<gui>','exec'))
mode=__import__('os').environ.get('CASE')
if mode=='monitor':
 move(1680,400);r=keyop(('ctrl','alt','m'),'key-monitor-correct');im=fetch(r['path']);im.save(E/'key-monitor-correct.png');assert im.size==(1024,768),r;print('real monitor shortcut PASS',flush=True)
elif mode=='cursor':exec(compile(Path('/tmp/p1363-ah6/ah6-cursor.py').read_text(),'<cursor>','exec'))
elif mode=='hide':
 cli('ui.hide');time.sleep(1)
elif mode=='config-hashes':
 print(guest('find /home/lab/.config/hypr -type f -exec sha256sum {} +'))
