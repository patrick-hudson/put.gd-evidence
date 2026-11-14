set -eu
cd "$HOME/work/s5202"
. ./session.env
python3 input-click.py 450 300 >a/r12-click.json
sudo -n python3 keyboard.py
sleep .3
python3 rfbshot.py a/r12-typed.png --vnc 5900
python3 - <<'PY'
from pathlib import Path
from trial import cursorpos
import os,signal,json,subprocess,time,hashlib
l=Path.home()/'work/s5202';a=l/'a';w=(a/'r12-received.txt').read_text().strip();assert w=='abc';pid=int((a/'r12-terminal.pid').read_text());p=Path('/proc')/str(pid);assert b'xterm' in (p/'cmdline').read_bytes() and b'r12-witness.py' in (p/'cmdline').read_bytes();os.kill(pid,signal.SIGTERM);time.sleep(.5)
before=json.loads((l/'before-state.json').read_text());initial=dict(x.split('=',1) for x in before['pointer'].splitlines());subprocess.run(['xdotool','mousemove','--sync',initial['X'],initial['Y']],check=True);devices=[p.read_text().strip() for p in Path('/sys/class/input').glob('event*/device/name')];test=[s for s in devices if 'putgd-lab' in s or 'scroll-1520' in s];assert not test
status=subprocess.run(['dpkg-query','-W','-f=${db:Status-Abbrev} ${Version}\n','putgd'],capture_output=True,text=True).stdout;assert status.startswith('rc '),status
source=Path('/etc/apt/sources.list.d/putgd.sources');sha=hashlib.sha256(source.read_bytes()).hexdigest();assert sha==before['aptSourceSha256']
v={'witness':w,'testInputDevices':test,'pointerRestoredToAcquirePosition':cursorpos(),'packageStatusAfter':status,'aptSourceSha256Before':before['aptSourceSha256'],'aptSourceSha256After':sha,'xinputAfter':subprocess.check_output(['xinput','--list','--long'],text=True),'aSessionSocketExists':(l/'a/run/putgd/session.sock').exists(),'bSessionSocketExists':(l/'b/run/putgd/session.sock').exists()};v['xinputListMatchesBefore']=v['xinputAfter']==before['xinput'];assert v['xinputListMatchesBefore'];assert not v['aSessionSocketExists'] and not v['bSessionSocketExists'];(a/'cleanup.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
PY
python3 rfbshot.py a/r12-clean.png --vnc 5900
