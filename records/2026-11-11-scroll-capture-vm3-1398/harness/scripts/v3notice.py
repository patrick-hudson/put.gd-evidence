import sys,json,time,subprocess,shlex,threading
from pathlib import Path
from PIL import Image
B=Path('/home/patrick/work/svm1398');sys.path.insert(0,str(B/'repo/tools/lab'));import lab
r=B/'repo/work/lab-runs/o3';o=B/'v3evidence/o'
def cmd(c):return lab.guest_session(r,c,timeout=300)
def shot(n):Image.open(lab.screenshot(r,'v3-'+n)['path']).save(o/(n+'.png'))
lab.put(r,B/'v3guest.py','/home/lab/v3guest.py')
# Dismiss pre-existing diagnostic toasts before the controlled local-route test.
subprocess.run(['python3',str(B/'v3dismiss-o.py')],check=True)
monitor=int(cmd('nohup dbus-monitor --session '+shlex.quote("interface='org.freedesktop.Notifications'")+' > /tmp/v3/notification-bus.log 2>&1 < /dev/null & echo $!').strip())
print(cmd('python3 /home/lab/v3guest.py patch '+shlex.quote(json.dumps({'actions':{'scroll':{'destination':'local'}}}))),flush=True)
pid=int(cmd('nohup chromium --no-first-run --password-store=basic --user-data-dir=/tmp/v3/chromium --kiosk file:///home/lab/v3ruler.html > /tmp/v3/notice-browser.log 2>&1 < /dev/null & echo $!').strip());time.sleep(16);shot('notice-local-ready')
for n in ['cap-local','postcap-local']:
 print(n,'START',flush=True)
 t=threading.Thread(target=lambda: [(time.sleep(.8),shot(n+'-during'+str(i))) for i in range(8)]);t.start()
 (o/(n+'.console')).write_text(cmd('python3 /home/lab/v3guest.py case '+n+' 0,0,1280,800'));t.join();shot(n+'-end');print(n,'END',flush=True)
cmd('kill '+str(pid)+' || true');cmd('python3 /home/lab/v3guest.py patch '+shlex.quote(json.dumps({'actions':{'scroll':{'destination':'upload','profileId':'scroll-local'}}})))

cmd('kill '+str(monitor)+' || true')
(o/'notification-bus.log').write_text(cmd('cat /tmp/v3/notification-bus.log'))
