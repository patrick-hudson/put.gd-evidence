import sys,json,time
from pathlib import Path
S=Path.home()/'work/kq/src';sys.path.insert(0,str(S));from tools.lab import lab
r=S/'work/lab-runs/n1';o=Path.home()/'work/kq/evidence/n1'
lab.guest_session(r,'export PATH=$HOME/putgd-lab/bin:$PATH\n(setsid -f putgd-launcher --background > ~/verify.log 2>&1 </dev/null); true');time.sleep(5)
(o/'current-running-identity.json').write_text(json.dumps(lab.verify_running_app(r),indent=2));print((o/'current-running-identity.json').read_text());print(lab.guest_session(r,'export PATH=$HOME/putgd-lab/bin:$PATH\nputgd-cli ui.quit; sleep 2; pgrep -ax putgd || true; pgrep -ax putgd-clipboard || true'))
