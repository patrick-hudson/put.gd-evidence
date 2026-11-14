import os,subprocess,shlex,json
from pathlib import Path
l=Path.home()/'work/s5202'
pid=subprocess.check_output(['pgrep','-x','quickshell'],text=True).split()[0]
e=dict(x.split('=',1) for x in Path(f'/proc/{pid}/environ').read_bytes().decode().split('\0') if '=' in x)
keep=['DISPLAY','WAYLAND_DISPLAY','XDG_RUNTIME_DIR','DBUS_SESSION_BUS_ADDRESS','XDG_SESSION_TYPE','XDG_CURRENT_DESKTOP','HYPRLAND_INSTANCE_SIGNATURE','OMARCHY_PATH']
(l/'session.env').write_text(''.join(k+'='+shlex.quote(e[k])+'\n' for k in keep if k in e));os.environ.update(e)
print(subprocess.run(['hyprctl','eval','hl.monitor({ output = "Virtual-1", mode = "1920x1080@60", position = "0x0", scale = 1 })'],capture_output=True,text=True).stdout)
for f in (Path.home()/'.config/hypr').glob('*input*'):
 print(f, f.read_text()[:6000])
(l/'bin').mkdir(exist_ok=True)
(l/'bin/firefox').write_text('#!/usr/bin/python3\nimport subprocess,sys\np=subprocess.Popen(["chromium","--user-data-dir=/home/lab/work/s5202/chromium","--no-first-run","--no-default-browser-check","--kiosk",sys.argv[-1]],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)\n')
(l/'bin/firefox').chmod(0o700)
for x in ['config','data','cache','state','run']:(l/'b'/x).mkdir(parents=True,exist_ok=True,mode=0o700)
for p in [l/'b/run/putgd/session.sock',Path('/run/user/1000/putgd/session.sock')]:print('socket',p,len(str(p).encode()));assert len(str(p).encode())<=107
