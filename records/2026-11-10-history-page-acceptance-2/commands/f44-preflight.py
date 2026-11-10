import os,subprocess,json,sys,runpy
from pathlib import Path
root=Path('/tmp/hp2f');root.mkdir(mode=0o700)
pid=subprocess.check_output(['pgrep','-u',str(os.getuid()),'-x','gnome-shell'],text=True).split()[0]
env=dict(x.split('=',1) for x in Path('/proc/'+pid+'/environ').read_text().split('\0') if '=' in x)
env.update(HOME=str(Path.home()),PATH='/usr/bin:/bin',XDG_RUNTIME_DIR='/run/user/1000',QT_QPA_PLATFORM='xcb')
shown=subprocess.check_output(['systemctl','--user','show-environment'],text=True)
for l in shown.splitlines():
 k,_,v=l.partition('=')
 if k in ('DISPLAY','XAUTHORITY','DBUS_SESSION_BUS_ADDRESS','WAYLAND_DISPLAY'):env[k]=v
p=subprocess.Popen(['python3',str(Path.home()/'putgd-lab/h1396-ci/p2-clipboard.py'),str(root)],env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
try:
 print(p.stdout.readline(),flush=True);r=p.stdout.readline();print(r,flush=True)
 if not json.loads(r).get('ready'):raise RuntimeError('clipboard preservation blocked; no resident launched')
 (root/'clipboard-preflight-pass').touch()
finally:
 p.stdin.close();p.wait(timeout=10);print('keeper exit',p.returncode,flush=True)
