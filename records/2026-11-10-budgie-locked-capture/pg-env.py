import os,sys,subprocess
from pathlib import Path
e=os.environ.copy()
for p in Path('/proc').iterdir():
 try:
  if (p/'comm').read_text().strip() in ('quickshell','budgie-panel'):
   env=dict(x.split('=',1) for x in (p/'environ').read_text().split('\0') if '=' in x)
   for k in ('WAYLAND_DISPLAY','HYPRLAND_INSTANCE_SIGNATURE','OMARCHY_PATH','XDG_RUNTIME_DIR','DBUS_SESSION_BUS_ADDRESS','XDG_CURRENT_DESKTOP','XDG_SESSION_TYPE','QT_QPA_PLATFORM'):
    if k in env:e[k]=env[k]
   break
 except (OSError,UnicodeError):pass
os.execvpe('bash',['bash','-c',sys.argv[1]],e)
