import sys,json,time
from pathlib import Path
S=Path.home()/'work/kq/src';sys.path.insert(0,str(S));from tools.lab import lab
r=S/'work/lab-runs/k1';o=Path.home()/'work/kq/evidence/k1';lab.ssh(r,"cat /etc/sddm.conf > ~/kq-sddm-before.conf; printf '[Autologin]\\nUser=lab\\nSession=plasmax11\\nRelogin=true\\n[General]\\nDisplayServer=x11\\n' > ~/kq-sddm.conf\nsudo -n apt-get -y --reinstall -o DPkg::Pre-Invoke::='cp /home/lab/kq-sddm.conf /etc/sddm.conf' install xclip > ~/kq-switch.log 2>&1\nsync",timeout=200)
old=json.loads((r/'state.json').read_text());(o/'state-wayland.json').write_text(json.dumps(old,indent=2))
p=lab.load_profile('kde-wayland');p.update(name='kde-x11-probe',session='x11',qt_platform='xcb');(S/'tools/lab/profiles/kde-x11-probe.yaml').write_text(json.dumps(p))
old['profile']='kde-x11-probe';(r/'state.json').write_text(json.dumps(old,indent=2))
q=lab.QMP(r/'qmp.sock');q.execute('system_reset');q.close();print('rebooted to X11 configuration',flush=True)
