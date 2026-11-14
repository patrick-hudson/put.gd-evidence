set -eu
cd "$HOME/work/s5202"
. ./session.env
python3 input-click.py 450 300 >a/terminal-click.json
sudo -n python3 keyboard.py
sleep .3
python3 - <<'PY'
from pathlib import Path
from trial import cli
import json
l=Path.home()/'work/s5202';a=l/'a';w=(a/'terminal-received.txt').read_text().strip();assert w=='abc',w;off=int((a/'terminal-offset.txt').read_text());text=(a/'helper.log').read_bytes()[off:].decode();(a/'terminal-quiet.log').write_text(text);v={'witness':w,'injectionLines':[s for s in text.splitlines() if 'scroll inject:' in s]};assert not v['injectionLines'];(a/'terminal-input.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
PY
python3 rfbshot.py a/terminal-typed.png --vnc 5900
python3 - <<'PY'
from pathlib import Path
from trial import cli
import json,os,signal
l=Path.home()/'work/s5202';a=l/'a';v=cli(str(l/'bin/cli-a'),'scroll.stop',{'id':(a/'terminal-session-id').read_text()});(a/'terminal-stop.json').write_text(json.dumps(v,indent=2));assert v['ok']
pid=int((a/'terminal.pid').read_text());p=Path('/proc')/str(pid)
if p.exists():assert b'xterm' in (p/'cmdline').read_bytes() and b'terminal-witness.py' in (p/'cmdline').read_bytes();os.kill(pid,signal.SIGTERM)
PY
python3 esc-check.py a >a/escape-driver.log 2>&1
