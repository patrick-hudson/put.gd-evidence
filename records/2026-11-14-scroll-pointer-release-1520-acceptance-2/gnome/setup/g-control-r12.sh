set -eu
cd "$HOME/work/s5202"
systemctl --user show-environment | grep -E '^(DISPLAY|WAYLAND_DISPLAY|XDG_RUNTIME_DIR|DBUS_SESSION_BUS_ADDRESS|XDG_SESSION_TYPE|XDG_CURRENT_DESKTOP|XAUTHORITY)=' > session.env
set -a; . ./session.env; set +a
python3 - <<'PY'
from pathlib import Path
l=Path.home()/'work/s5202';(l/'r12-control-witness.py').write_text((l/'terminal-witness.py').read_text().replace('a/terminal-received.txt','c/r12-received.txt'))
PY
setsid nohup xterm -geometry 100x30+100+100 -e python3 "$HOME/work/s5202/r12-control-witness.py" >c/r12-terminal.log 2>&1 </dev/null & echo $! >c/r12-terminal.pid
sleep 2
python3 - <<'PY'
from trial import Rfb
import struct,time
r=Rfb(5901)
for s in [1,0]:r.sock.sendall(struct.pack('>BBHI',4,s,0,0xff1b));time.sleep(.1)
PY
python3 rfbshot.py c/r12-open.png --vnc 5901
