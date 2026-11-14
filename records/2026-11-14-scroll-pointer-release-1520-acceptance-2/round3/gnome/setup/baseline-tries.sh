set -eu
cd "$HOME/work/s5302"
set -a; . ./session.env; set +a
export XDG_CONFIG_HOME=$HOME/work/s5302/b/config XDG_DATA_HOME=$HOME/work/s5302/b/data XDG_CACHE_HOME=$HOME/work/s5302/b/cache XDG_STATE_HOME=$HOME/work/s5302/b/state
for mode in fixed random; do
 for i in $(seq 1 10); do
  firefox --profile "$HOME/work/s5302/ff" https://en.wikipedia.org/wiki/Linux
  sleep 5
  python3 -c 'import random,time;time.sleep(random.uniform(0,1))'
  if test "$mode" = fixed; then delay=2; jitter=0; else delay=1; jitter=5; fi
  python3 trial.py --local-center --rel --cli "$HOME/work/s5302/bin/cli-b" --rect 470,200,980,720 --stop 780,956 --log "$HOME/work/s5302/b/helper.log" --vnc 5901 --start "$delay" --jitter "$jitter" --label "b-$mode-$i" >> "b/tries-$mode.jsonl" 2>> "b/tries-$mode.err"
 done
done
