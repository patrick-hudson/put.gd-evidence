set -eu
cd "$HOME/work/s5302"
set -a; . ./session.env; set +a
export PATH=$PWD/bin:$PATH LANG=C.UTF-8
bin/cli-b ui.quit >b/quit.json
python3 - <<'PY'
from pathlib import Path
import subprocess,json,signal,os
l=Path.home()/'work/s5302';cs=json.loads(subprocess.check_output(['hyprctl','clients','-j'],text=True));owned=[c for c in cs if c['class']=='chromium'];assert len(owned)==1,owned
pid=owned[0]['pid'];cmd=Path(f'/proc/{pid}/cmdline').read_bytes();assert b'chromium' in cmd and b'/home/lab/work/s5302/chromium' in cmd;os.kill(pid,signal.SIGTERM)
PY
hyprctl reload >b/input-restore.log
sleep 1
python3 - <<'PY'
from pathlib import Path
import subprocess
l=Path.home()/'work/s5302';(l/'a/terminal-received.txt').rename(l/'a/r12-first-resident-received-retained.txt')
p=subprocess.Popen(['foot','-e','python3',str(l/'terminal-witness.py')],start_new_session=True,stdout=open(l/'b/r12-terminal.log','w'),stderr=subprocess.STDOUT);(l/'b/r12-terminal.pid').write_text(str(p.pid))
PY
sleep 1
python3 input-click-h.py 600 400 >b/r12-click.json
sudo -n python3 "$PWD/keyboard.py"
sleep 1
cp a/terminal-received.txt b/r12-received.txt
