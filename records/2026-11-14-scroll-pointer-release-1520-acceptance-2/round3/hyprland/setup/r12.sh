set -eu
cd "$HOME/work/s5302"
systemctl --user show-environment | grep -E '^(DISPLAY|WAYLAND_DISPLAY|XDG_RUNTIME_DIR|DBUS_SESSION_BUS_ADDRESS|XDG_SESSION_TYPE|XDG_CURRENT_DESKTOP|XAUTHORITY)=' > session.env
set -a; . ./session.env; set +a
python3 - <<'PY'
from pathlib import Path
l=Path.home()/'work/s5302';(l/'r12-witness.py').write_text((l/'terminal-witness.py').read_text().replace('terminal-received.txt','r12-received.txt'))
PY
setsid nohup xterm -geometry 100x30+100+100 -e python3 "$HOME/work/s5302/r12-witness.py" > a/r12-terminal.log 2>&1 < /dev/null & echo $! > a/r12-terminal.pid
sleep 2
python3 rfbshot.py a/r12-open.png --vnc 5901
