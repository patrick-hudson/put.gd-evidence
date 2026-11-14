set -eu
cd "$HOME/work/s5202"
set -a; . ./session.env; set +a
python3 - <<'PY'
from pathlib import Path
import os,signal,subprocess,json
l=Path.home()/'work/s5202';q='/usr/lib64/qt6/bin/qdbus'
r=subprocess.run([q,'org.kde.KWin','/Scripting','org.kde.kwin.Scripting.unloadScript','scroll1520r2-cursor'],capture_output=True,text=True,check=True)
v=subprocess.check_output([q,'org.kde.KWin','/Scripting','org.kde.kwin.Scripting.isScriptLoaded','scroll1520r2-cursor'],text=True).strip();assert v=='false'
for file,expected in [('cursor-service.pid',b'cursor-service.py')]:
 pid=int((l/file).read_text());p=Path('/proc')/str(pid)
 if p.exists():assert expected in (p/'cmdline').read_bytes();os.kill(pid,signal.SIGTERM)
rows=subprocess.check_output(['flatpak','ps','--columns=instance,pid,application'],text=True).strip().splitlines();assert len(rows)==1 and rows[0].split()[0]=='2581709389' and rows[0].split()[-1]=='org.mozilla.firefox';subprocess.run(['flatpak','kill','2581709389'],check=True)
assert not (Path.home()/'.config/kcminputrc').exists()
(l/'r12-witness.py').write_text((l/'terminal-witness.py').read_text().replace('terminal-received.txt','r12-received.txt'))
(l/'a/cleanup-settings.json').write_text(json.dumps({'cursorScriptLoaded':v,'originalInputConfigAbsent':True,'restoredInputConfigAbsent':True,'flatpakInstanceClosed':'2581709389'},indent=2))
PY
setsid nohup konsole --nofork -e python3 "$HOME/work/s5202/r12-witness.py" >a/r12-terminal.log 2>&1 </dev/null & echo $! >a/r12-terminal.pid
sleep 2
python3 rfbshot.py a/r12-open.png --vnc 5900
