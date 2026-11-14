set -eu
cd "$HOME/work/s1520"
set -a; . ./session.env; set +a
if test -S "$XDG_RUNTIME_DIR/putgd/session.sock"; then bin/cli-a ui.quit > a/quit.json; fi
sleep 2
python3 - <<'PY'
from pathlib import Path
import os,signal,hashlib
l=Path.home()/'work/s1520';pid=int((l/'a/terminal.pid').read_text());proc=Path('/proc')/str(pid)
if proc.exists():
 assert b'xterm' in (proc/'cmdline').read_bytes();os.kill(pid,signal.SIGTERM)
p=Path.home()/'.config/budgie-desktop/labwc/rc.xml';p.write_bytes((l/'rc-before.xml').read_bytes());print('config restored',hashlib.sha256(p.read_bytes()).hexdigest())
s=(l/'terminal-witness.py').read_text().replace('terminal-received.txt','r12-received.txt');(l/'r12-witness.py').write_text(s)
PY
XDG_RUNTIME_DIR=/run/user/1000 labwc --reconfigure
nohup xterm -geometry 100x30+100+100 -e python3 "$HOME/work/s1520/r12-witness.py" > a/r12-terminal.log 2>&1 < /dev/null & echo $! > a/r12-terminal.pid
