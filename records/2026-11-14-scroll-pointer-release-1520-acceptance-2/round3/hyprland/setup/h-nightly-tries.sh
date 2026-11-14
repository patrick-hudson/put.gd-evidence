set -eu
cd "$HOME/work/s5302"
set -a; . ./session.env; set +a
export PATH=$PWD/bin:$PATH LANG=C.UTF-8
export XDG_CONFIG_HOME=$PWD/b/config XDG_DATA_HOME=$PWD/b/data XDG_CACHE_HOME=$PWD/b/cache XDG_STATE_HOME=$PWD/b/state
python3 - <<'PY'
from trial import cli
from pathlib import Path
l=Path.home()/'work/s5302';print(cli(str(l/'bin/cli-b'),'scroll.cancel',{'id':(l/'b/bar-probe-id.txt').read_text()}))
PY
for i in $(seq 0 10); do
 firefox https://en.wikipedia.org/wiki/Linux
 sleep 5
 python3 -c 'import random,time;time.sleep(random.uniform(0,1))'
 if test "$i" = 0; then delay=1.709; jitter=0; label=b-random8-recheck; out=b/failure-recheck.jsonl; else delay=1; jitter=5; label=b-random-$i; out=b/tries-random.jsonl; fi
 python3 trial.py --native-center --rel --cli "$PWD/bin/cli-b" --rect 470,200,980,720 --stop 780,956 --log b/helper.log --start "$delay" --jitter "$jitter" --label "$label" >>"$out" 2>>b/tries-random.err
done
