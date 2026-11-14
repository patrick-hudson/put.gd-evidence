set -eu
cd "$HOME/work/s5302"
set -a; . ./session.env; set +a
export PATH=$HOME/work/s5302/bin:$PATH LANG=C.UTF-8 XDG_CONFIG_HOME=$HOME/work/s5302/a/config XDG_DATA_HOME=$HOME/work/s5302/a/data XDG_CACHE_HOME=$HOME/work/s5302/a/cache XDG_STATE_HOME=$HOME/work/s5302/a/state
for i in $(seq 1 10); do
 firefox https://en.wikipedia.org/wiki/Linux
 sleep 5
 python3 -c 'import random,time;time.sleep(random.uniform(0,1))'
 python3 trial.py --native-center --rel --cli "$HOME/work/s5302/bin/cli-a" --rect 470,200,980,720 --stop 960,956 --log a/helper.log --start 1 --jitter 5 --label "a-random-$i" >>a/tries-random.jsonl 2>>a/tries-random.err
done
python3 pair-h.py pause >a/pair-driver.log 2>&1
