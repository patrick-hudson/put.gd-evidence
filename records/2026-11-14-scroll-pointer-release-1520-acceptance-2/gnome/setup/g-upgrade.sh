set -eu
cd "$HOME/work/s5202"
set -a; . ./session.env; set +a
bin/cli-b ui.quit > b/quit.json
python3 - <<'PY'
from pathlib import Path
import os,signal
p=int((Path.home()/'work/s5202/b/firefox.pid').read_text());q=Path('/proc')/str(p)
if q.exists():
 assert b'firefox' in (q/'cmdline').read_bytes();os.kill(p,signal.SIGTERM)
PY
sudo -n rpm -U --test after.rpm
sudo -n rpm -Uvh after.rpm
sudo -n systemctl restart gdm
