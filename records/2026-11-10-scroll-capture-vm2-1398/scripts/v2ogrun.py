import sys,time,json,shlex,concurrent.futures,subprocess
from pathlib import Path
from PIL import Image
sys.path.insert(0,'/home/patrick/work/svm1398/repo/tools/lab');import lab
base=Path('/home/patrick/work/svm1398');r=base/'repo/work/lab-runs/og';o=base/'v2evidence/g';o.mkdir(exist_ok=True)
def cmd(c):return lab.guest_session(r,c,timeout=300)
pkg=next((base/'v2artifacts/release-appimage').glob('*.AppImage'));(o/'install-receipt.json').write_text(json.dumps(lab.install(r,appimage=pkg),indent=2));print('g installed',flush=True)
for f,target in [('v2ogguest.py','v2guest.py'),('v2receiver.py','v2receiver.py'),('v2ruler.html','v2ruler.html')]:lab.put(r,base/f,'/home/lab/'+target)
print(cmd('python3 /home/lab/v2guest.py init'),flush=True)
(o/'scale-command.log').write_text(cmd('hyprctl eval '+shlex.quote('hl.monitor({ output = "Virtual-1", mode = "1280x800@74.99", position = "0x0", scale = 1.25 })')));time.sleep(3)
mon=json.loads(cmd('hyprctl monitors -j'));(o/'monitors-125.json').write_text(json.dumps(mon,indent=2));assert mon[0]['scale']==1.25,mon
print('g verified scale 1.25',flush=True)
pid=int(cmd('nohup chromium --ozone-platform=wayland --no-first-run --password-store=basic --user-data-dir=/home/lab/chromium-v2 --kiosk file:///home/lab/v2ruler.html > /tmp/v2/browser.log 2>&1 < /dev/null & echo $!').strip());(o/'browser.pid').write_text(str(pid));time.sleep(16);Image.open(lab.screenshot(r,'v2-g-browser-ready')['path']).save(o/'browser-ready.png');print('g BROWSER READY',flush=True)
