set -eu
cd "$HOME/work/s5302"
python3 guest-prep.py >prep-nightly-restart.log
set -a; . ./session.env; set +a
export PATH=$PWD/bin:$PATH LANG=C.UTF-8
export XDG_CONFIG_HOME=$PWD/b/config XDG_DATA_HOME=$PWD/b/data XDG_CACHE_HOME=$PWD/b/cache XDG_STATE_HOME=$PWD/b/state PUTGD_RECORD_DEBUG_LOG=$PWD/b/helper.log
nohup ./squashfs-root/AppRun --background >b/restart-resident.log 2>&1 </dev/null & echo $! >b/restart-resident.pid
sleep 3
bin/cli-b diagnostics >b/restart-diagnostics.json
firefox https://en.wikipedia.org/wiki/Linux
sleep 6
python3 - <<'PY'
from pathlib import Path
from trial import cli
import json
l=Path.home()/'work/s5302';s=cli(str(l/'bin/cli-b'),'scroll.prepare',{'rect':[470,200,980,720]})['result']['id'];(l/'b/bar-probe-id.txt').write_text(s);print(cli(str(l/'bin/cli-b'),'scroll.start',{'id':s}))
PY
