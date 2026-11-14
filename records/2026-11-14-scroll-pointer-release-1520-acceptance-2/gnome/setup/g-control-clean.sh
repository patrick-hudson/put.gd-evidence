set -eu
cd "$HOME/work/s5202"
set -a; . ./session.env; set +a
python3 - <<'PY'
from pathlib import Path
from trial import cli
import json,os,signal,subprocess
l=Path.home()/'work/s5202';c=l/'c';v=[json.loads(x) for x in (c/'tries-fixed.jsonl').read_text().splitlines()];assert len(v)==10
r=cli(str(l/'bin/cli-b'),'ui.quit',{});assert r['ok'];(c/'quit.json').write_text(json.dumps(r))
pid=int((c/'firefox.pid').read_text());p=Path('/proc')/str(pid)
if p.exists():assert b'firefox' in (p/'cmdline').read_bytes();os.kill(pid,signal.SIGTERM)
for key in ['enabled-extensions','disabled-extensions']:subprocess.run(['gsettings','set','org.gnome.shell',key,(c/('before-'+key+'.txt')).read_text().strip()],check=True)
subprocess.run(['gsettings','set','org.gnome.desktop.peripherals.mouse','accel-profile',(l/'accel-before.txt').read_text().strip()],check=True)
PY
sudo -n rpm -e --test putgd
sudo -n rpm -e putgd
sudo -n systemctl restart gdm
