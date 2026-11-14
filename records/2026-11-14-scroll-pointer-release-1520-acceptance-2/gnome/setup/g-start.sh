set -eu
cd "$HOME/work/s5202"
systemctl --user show-environment | grep -E '^(DISPLAY|WAYLAND_DISPLAY|XDG_RUNTIME_DIR|DBUS_SESSION_BUS_ADDRESS|XDG_SESSION_TYPE|XDG_CURRENT_DESKTOP|XAUTHORITY)=' > session.env
set -a; . ./session.env; set +a
python3 - <<'PY'
import os
for p in [os.environ['XDG_RUNTIME_DIR']+'/putgd/session.sock',os.environ['XDG_RUNTIME_DIR']+'/bus']:
 print(p,len(p.encode()));assert len(p.encode())<=107
PY
mkdir -m 700 -p bin b/config b/data b/cache b/state ff
printf '#!/bin/sh\nexec /usr/bin/putgd-cli "$@"\n' > bin/cli-b
chmod 700 bin/cli-b
python3 mkconfig.py template.json b
export XDG_CONFIG_HOME=$HOME/work/s5202/b/config XDG_DATA_HOME=$HOME/work/s5202/b/data XDG_CACHE_HOME=$HOME/work/s5202/b/cache XDG_STATE_HOME=$HOME/work/s5202/b/state PUTGD_RECORD_DEBUG_LOG=$HOME/work/s5202/b/helper.log
setsid nohup putgd --background > b/resident.log 2>&1 < /dev/null & echo $! > b/resident.pid
setsid nohup firefox --no-remote --profile "$HOME/work/s5202/ff" --kiosk https://en.wikipedia.org/wiki/Linux > b/firefox.log 2>&1 < /dev/null & echo $! > b/firefox.pid
sleep 4
python3 - <<'PY'
from trial import Rfb
import struct,time
r=Rfb(5901)
for s in [1,0]:r.sock.sendall(struct.pack('>BBHI',4,s,0,0xff1b));time.sleep(.1)
PY
bin/cli-b diagnostics > b/diagnostics.json
gnome-extensions info putgd@put.gd > b/extension.txt
gdbus call --session -d org.gnome.Shell -o /org/gnome/Shell -m org.gnome.Shell.Eval 'JSON.stringify(global.get_pointer())' > cursor-query.txt
python3 rfbshot.py b/browser-ready.png --vnc 5901
