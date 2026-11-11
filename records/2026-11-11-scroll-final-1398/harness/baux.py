from pathlib import Path
import sys,shlex,json,time,subprocess
from PIL import Image
B=Path.home()/'work/svm1398';D=Path.home()/'work/sfinal';sys.path.insert(0,str(B/'repo/tools/lab'));import lab
r=B/'repo/work/lab-runs/bfin2';o=D/'ev/bfin2';o.mkdir(parents=True,exist_ok=True)
def cmd(c):return lab.guest_session(r,c,timeout=180)
def shot(n):Image.open(lab.screenshot(r,'baux-'+n)['path']).save(o/(n+'.png'))
(o/'notification-server.txt').write_text(cmd('busctl --user status org.freedesktop.Notifications; ps -u lab -o pid,comm,args | grep -E "notif|budgie|swaync|mako" || true'))
pid=cmd('nohup env SC_Y=100 python3 /home/lab/v3ruler.py --rows 600 > /tmp/v3/cap-banner-fixture.log 2>&1 < /dev/null & echo $!').strip();time.sleep(3)
(o/'cap.console').write_text(cmd('python3 /home/lab/v3guest.py case cap 100,100,960,600'));shot('cap-fullscreen');cmd('kill '+pid);time.sleep(1);shot('cap-after-fixture-close');time.sleep(2);shot('cap-after-fixture-close-3s')
(o/'notification-server-after.txt').write_text(cmd('busctl --user status org.freedesktop.Notifications; find /tmp/v3/state -name "*.jsonl" -type f -print'))
code="""from pathlib import Path
import json
p=Path('/tmp/v3');out=[]
for f in (p/'state').rglob('*.jsonl'):
 for l in f.read_text().splitlines():
  if 'notif' in l.lower():out.append(l)
print('\n'.join(out))
"""
(o/'notification-log.jsonl').write_text(cmd('python3 -c '+shlex.quote(code)))
print('BANNER CHECK EXPORTED')
