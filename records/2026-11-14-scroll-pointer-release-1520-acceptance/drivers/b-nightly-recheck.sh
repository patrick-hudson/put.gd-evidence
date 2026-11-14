set -eu
cd "$HOME/work/s1520"
set -a; . ./session.env; set +a
python3 - <<'INNER'
from pathlib import Path
import os,signal
l=Path.home()/'work/s1520';pid=int((l/'a/terminal.pid').read_text());p=Path('/proc')/str(pid)
if p.exists():
 assert b'xterm' in (p/'cmdline').read_bytes();os.kill(pid,signal.SIGTERM)
INNER
bin/cli-a ui.quit > a/quit-before-recheck.json
sleep 2
export XDG_CONFIG_HOME=$HOME/work/s1520/b/config XDG_DATA_HOME=$HOME/work/s1520/b/data XDG_CACHE_HOME=$HOME/work/s1520/b/cache XDG_STATE_HOME=$HOME/work/s1520/b/state PUTGD_RECORD_DEBUG_LOG=$HOME/work/s1520/b/helper.log
setsid nohup ./squashfs-root/AppRun --background > b/resident-recheck.log 2>&1 < /dev/null & echo $! > b/resident-recheck.pid
sleep 2
bin/cli-b diagnostics > b/recheck-diagnostics.json
firefox --profile "$HOME/work/s1520/ff" https://en.wikipedia.org/wiki/Linux
sleep 5
python3 trial.py --local-center --rel --cli "$HOME/work/s1520/bin/cli-b" --rect 470,200,980,720 --stop 780,956 --log "$HOME/work/s1520/b/helper.log" --start 5.401 --label b-random6-recheck > b/failure-rechecks.jsonl 2> b/failure-rechecks.err
bin/cli-b ui.quit > b/quit.json
