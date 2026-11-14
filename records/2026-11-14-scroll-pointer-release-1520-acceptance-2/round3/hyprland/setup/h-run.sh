set -eu
cd "$HOME/work/s5302"
set -a; . ./session.env; set +a
export PATH=$HOME/work/s5302/bin:$PATH LANG=C.UTF-8
for label in b a; do
 if test "$label" = a; then sh switch-after.sh >switch-after.log 2>&1; fi
 export XDG_CONFIG_HOME=$HOME/work/s5302/$label/config XDG_DATA_HOME=$HOME/work/s5302/$label/data XDG_CACHE_HOME=$HOME/work/s5302/$label/cache XDG_STATE_HOME=$HOME/work/s5302/$label/state
 bin/cli-$label diagnostics >$label/diagnostics.json
 python3 - "$label" <<'PY'
from pathlib import Path
import json,sys
l=Path.home()/'work/s5302';v=json.loads((l/sys.argv[1]/'diagnostics.json').read_text())['result']['build'];(l/sys.argv[1]/'build.json').write_text(json.dumps(v,indent=2));print(v)
PY
 uptime >"$label/load.txt"
 python3 untouched.py "$HOME/work/s5302/bin/cli-$label" 470,200,980,720 https://en.wikipedia.org/wiki/Linux "$HOME/work/s5302/chromium" "$label-1" >"$label/s1.jsonl" 2>"$label/s1.err"
done
for i in $(seq 1 10); do
 firefox https://en.wikipedia.org/wiki/Linux
 sleep 5
 python3 -c 'import random,time;time.sleep(random.uniform(0,1))'
 python3 trial.py --native-center --rel --cli "$HOME/work/s5302/bin/cli-a" --rect 470,200,980,720 --stop 960,956 --log a/helper.log --start 1 --jitter 5 --label "a-random-$i" >>a/tries-random.jsonl 2>>a/tries-random.err
done
python3 pair-h.py pause >a/pair-driver.log 2>&1
