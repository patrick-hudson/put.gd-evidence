set -eu
cd "$HOME/work/s5202"
set -a; . ./session.env; set +a
export XDG_CONFIG_HOME=$HOME/work/s5202/c/config XDG_DATA_HOME=$HOME/work/s5202/c/data XDG_CACHE_HOME=$HOME/work/s5202/c/cache XDG_STATE_HOME=$HOME/work/s5202/c/state
for i in $(seq 1 10); do
 firefox --profile "$HOME/work/s5202/ff" https://en.wikipedia.org/wiki/Linux
 sleep 5
 python3 -c 'import random,time;time.sleep(random.uniform(0,1))'
 python3 trial.py --local-center --rel --cli "$HOME/work/s5202/bin/cli-b" --rect 470,200,980,720 --stop 780,956 --log "$HOME/work/s5202/c/helper.log" --vnc 5901 --start 2 --label "nightly-fixed-$i" >>c/tries-fixed.jsonl 2>>c/tries-fixed.err
done
