set -eu
cd "$HOME/work/s5202"
systemctl --user show-environment | grep -E '^(DISPLAY|WAYLAND_DISPLAY|XDG_RUNTIME_DIR|DBUS_SESSION_BUS_ADDRESS|XDG_SESSION_TYPE|XDG_CURRENT_DESKTOP|XAUTHORITY)=' > session.env
set -a; . ./session.env; set +a
mkdir -m 700 -p c/config c/data c/cache c/state
python3 - <<'PY'
import os,subprocess,json
from pathlib import Path
l=Path.home()/'work/s5202';v={}
for s in ['putgd/session.sock','bus',os.environ['WAYLAND_DISPLAY'],'pipewire-0']:
 p=os.environ['XDG_RUNTIME_DIR']+'/'+s;v[p]=len(p.encode());assert len(p.encode())<=107
(l/'c/socket-paths.json').write_text(json.dumps(v,indent=2))
for key in ['enabled-extensions','disabled-extensions']:(l/'c'/('before-'+key+'.txt')).write_text(subprocess.check_output(['gsettings','get','org.gnome.shell',key],text=True))
PY
python3 mkconfig.py template.json c
export XDG_CONFIG_HOME=$HOME/work/s5202/c/config XDG_DATA_HOME=$HOME/work/s5202/c/data XDG_CACHE_HOME=$HOME/work/s5202/c/cache XDG_STATE_HOME=$HOME/work/s5202/c/state PUTGD_RECORD_DEBUG_LOG=$HOME/work/s5202/c/helper.log
setsid nohup putgd --background >c/resident.log 2>&1 </dev/null & echo $! >c/resident.pid
setsid nohup firefox --no-remote --profile "$HOME/work/s5202/ff" --kiosk https://en.wikipedia.org/wiki/Linux >c/firefox.log 2>&1 </dev/null & echo $! >c/firefox.pid
sleep 5
bin/cli-b diagnostics >c/diagnostics.json
gnome-extensions info putgd@put.gd >c/extension.txt
python3 rfbshot.py c/browser-ready.png --vnc 5901
