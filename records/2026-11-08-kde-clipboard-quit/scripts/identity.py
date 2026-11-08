import sys,json
from pathlib import Path
S=Path.home()/'work/kq/src';sys.path.insert(0,str(S));from tools.lab import lab
for n in ['n1','k1']:
 r=S/'work/lab-runs'/n;o=Path.home()/'work/kq/evidence'/n
 text=lab.guest_session(r,'cat /etc/os-release; dpkg-query -W plasma-workspace kwin-wayland kwin-x11 2>/dev/null || true; echo session=$XDG_SESSION_TYPE; pgrep -ax kwin_wayland || true; pgrep -ax kwin_x11 || true; cat ~/.config/klipperrc 2>/dev/null || true')
 (o/'desktop-identity.txt').write_text(text)
 try:(o/'current-running-identity.json').write_text(json.dumps(lab.verify_running_app(r),indent=2))
 except Exception as e:print(n,str(e))
 print(n,text,flush=True)
