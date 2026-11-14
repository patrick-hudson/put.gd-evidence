set -eu
cd "$HOME/work/s5202"
. ./session.env
python3 - <<'PY'
from pathlib import Path
from trial import cli
import json,os,signal
l=Path.home()/'work/s5202'
for mode in ['fixed','random','steer']:
 v=[json.loads(x) for x in (l/'b'/('tries-'+mode+'.jsonl')).read_text().splitlines()];assert len(v)==10
assert json.loads((l/'b/escape.json').read_text())['savedFiles']
r=cli(str(l/'bin/cli-b'),'ui.quit',{});assert r['ok'];(l/'b/quit-final.json').write_text(json.dumps(r,indent=2))
pid=int((l/'firefox.pid').read_text());p=Path('/proc')/str(pid)
if p.exists():assert str(l/'ff').encode() in (p/'cmdline').read_bytes();os.kill(pid,signal.SIGTERM)
PY
sudo -n apt-get --no-auto-remove remove -y putgd >install-remove.log 2>&1
python3 - <<'PY'
from pathlib import Path
import json,hashlib,subprocess
l=Path.home()/'work/s5202';before=json.loads((l/'before-state.json').read_text());p=Path('/etc/apt/sources.list.d/putgd.sources');assert before['aptSourceExists'] and p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==before['aptSourceSha256']
(l/'r12-witness.py').write_text((l/'terminal-witness.py').read_text().replace('a/terminal-received.txt','a/r12-received.txt'))
PY
setsid nohup xterm -geometry 100x30+100+100 -e python3 "$HOME/work/s5202/r12-witness.py" >a/r12-terminal.log 2>&1 </dev/null & echo $! >a/r12-terminal.pid
sleep 2
python3 rfbshot.py a/r12-open.png --vnc 5900
