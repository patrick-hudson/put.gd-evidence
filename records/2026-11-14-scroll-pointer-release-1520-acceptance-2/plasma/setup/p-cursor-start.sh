set -eu
cd "$HOME/work/s5202"
set -a; . ./session.env; set +a
export PATH=$HOME/work/s5202/bin:$PATH
nohup python3 cursor-service.py > cursor-service.log 2>&1 < /dev/null & echo $! > cursor-service.pid
sleep .3
python3 - <<'PY'
import subprocess,json,time
from pathlib import Path
q='/usr/lib64/qt6/bin/qdbus';l=Path.home()/'work/s5202';name='scroll1520r2-cursor'
assert subprocess.check_output([q,'org.kde.KWin','/Scripting','org.kde.kwin.Scripting.isScriptLoaded',name],text=True).strip()=='false'
sid=subprocess.check_output([q,'org.kde.KWin','/Scripting','org.kde.kwin.Scripting.loadScript',str(l/'kwin-cursor.js'),name],text=True).strip();assert sid.isdigit();(l/'cursor-script-id').write_text(sid)
paths=subprocess.check_output([q,'org.kde.KWin'],text=True).splitlines();paths=[p.strip() for p in paths if p.strip().endswith('/Script'+sid) or p.strip()=='/'+sid];assert len(paths)==1,paths;path=paths[0];(l/'cursor-script-path').write_text(path);print(sid,path)
subprocess.run([q,'org.kde.KWin',path,'org.kde.kwin.Script.run'],check=True);time.sleep(.5)
from trial import cursorpos
v=cursorpos();print('native cursor',v);(l/'cursor-initial.json').write_text(json.dumps(v))
PY
