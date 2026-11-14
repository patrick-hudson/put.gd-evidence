set -eu
cd "$HOME/work/s5202"
set -a; . ./session.env; set +a
python3 - <<'PY'
from pathlib import Path
from trial import cli
import json,os,signal
l=Path.home()/'work/s5202';a=l/'a';v=cli(str(l/'bin/cli-a'),'scroll.stop',{'id':(a/'terminal-session-id').read_text()});(a/'terminal-stop.json').write_text(json.dumps(v,indent=2));print(v['result']['endReason']);cli(str(l/'bin/cli-a'),'ui.quit',{})
for file,expected in [('a/terminal.pid',b'xterm'),('a/firefox.pid',b'firefox')]:
 pid=int((l/file).read_text());p=Path('/proc')/str(pid)
 if p.exists():
  assert expected in (p/'cmdline').read_bytes();os.kill(pid,signal.SIGTERM)
PY
python3 - <<'PY'
from pathlib import Path
import subprocess
l=Path.home()/'work/s5202'
for key,file in [('enabled-extensions','enabled-before.txt'),('disabled-extensions','disabled-before.txt')]:subprocess.run(['gsettings','set','org.gnome.shell',key,(l/file).read_text().strip()],check=True)
subprocess.run(['gsettings','set','org.gnome.desktop.peripherals.mouse','accel-profile',(l/'accel-before.txt').read_text().strip()],check=True)
PY
sudo -n rpm -e --test putgd
sudo -n rpm -e putgd
sudo -n systemctl restart gdm
