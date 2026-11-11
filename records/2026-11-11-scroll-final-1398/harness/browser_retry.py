from pathlib import Path
import sys,json,shlex,time,subprocess
from PIL import Image
B=Path.home()/'work/svm1398';D=Path.home()/'work/sfinal';sys.path.insert(0,str(B/'repo/tools/lab'));import lab
k=sys.argv[1];r=B/'repo/work/lab-runs'/(k+'fin');o=D/'ev'/(k+'fin')
def cmd(c):return lab.guest_session(r,c,timeout=300)
def shot(n):Image.open(lab.screenshot(r,'retry-'+n)['path']).save(o/(n+'.png'))
code="""from pathlib import Path
p=Path('/tmp/v3/cases')
for d in list(p.iterdir()):
 if d.name.startswith(('rapid','burst')):d.rename(d.with_name('harness-firefox-consent-'+d.name))
"""
cmd('python3 -c '+shlex.quote(code))
for f in list(o.iterdir()):
 if f.name.startswith(('rapid','burst','browser-ready')) and f.is_file():f.rename(f.with_name('harness-firefox-consent-'+f.name))
pid=cmd('nohup firefox --no-remote --profile /home/lab/v3firefox --kiosk file:///home/lab/v3ruler.html > /tmp/v3/browser-retry.log 2>&1 < /dev/null & echo $!').strip();time.sleep(14);shot('browser-consent-before')
lab.pointer(r,640,327,1280,800);time.sleep(.2);lab.pointer(r,640,327,1280,800,True);time.sleep(.2);lab.pointer(r,640,327,1280,800,False);time.sleep(4);shot('browser-consent-dismissed')
try:
 for n in [f'rapid{i:02}' for i in range(1,6)]+[f'burst{i:02}' for i in range(1,4)]:
  (o/(n+'.console')).write_text(cmd('python3 /home/lab/v3guest.py case '+n+' 0,0,1280,800'));shot(n+'-end');print(n,'DONE',flush=True)
finally:cmd('kill '+pid+' || true')
(o/'browser-retry.done').write_text('done')
