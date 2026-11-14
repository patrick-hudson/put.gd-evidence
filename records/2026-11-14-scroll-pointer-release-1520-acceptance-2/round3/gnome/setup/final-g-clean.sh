set -eu
cd "$HOME/work/s5302"
set -a; . ./session.env; set +a
bin/cli-b ui.quit >b/quit.json
python3 - <<'PY'
from pathlib import Path
import os,signal,subprocess
l=Path.home()/'work/s5302';pid=int((l/'b/firefox.pid').read_text());p=Path('/proc')/str(pid)
if p.exists():assert b'firefox' in (p/'cmdline').read_bytes();os.kill(pid,signal.SIGTERM)
for key,file in [('enabled-extensions','enabled-before.txt'),('disabled-extensions','disabled-before.txt')]:subprocess.run(['gsettings','set','org.gnome.shell',key,(l/file).read_text().strip()],check=True)
subprocess.run(['gsettings','set','org.gnome.desktop.peripherals.mouse','accel-profile',(l/'accel-before.txt').read_text().strip()],check=True)
PY
sudo -n rpm -e --test putgd
sudo -n rpm -e putgd
sudo -n systemctl restart gdm
