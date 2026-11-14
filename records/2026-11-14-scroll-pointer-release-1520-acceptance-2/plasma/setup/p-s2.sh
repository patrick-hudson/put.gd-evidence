set -eu
cd "$HOME/work/s5202"
set -a; . ./session.env; set +a
export PATH=$HOME/work/s5202/bin:$PATH
export XDG_CONFIG_HOME=$HOME/work/s5202/a/config XDG_DATA_HOME=$HOME/work/s5202/a/data XDG_CACHE_HOME=$HOME/work/s5202/a/cache XDG_STATE_HOME=$HOME/work/s5202/a/state
for mode in fixed random steer; do
 for i in $(seq 1 10); do
  firefox --profile "$HOME/work/s5202/ff" https://en.wikipedia.org/wiki/Linux
  sleep 5
  python3 -c 'import random,time;time.sleep(random.uniform(0,1))'
  if test "$mode" = fixed; then delay=2; jitter=0; else delay=1; jitter=5; fi
  extra=""; if test "$mode" = steer; then extra=--steer; fi
  python3 trial.py $extra --local-center --rel --cli "$HOME/work/s5202/bin/cli-a" --rect 470,200,980,720 --stop 960,956 --log "$HOME/work/s5202/a/helper.log" --vnc 5900 --start "$delay" --jitter "$jitter" --label "a-$mode-$i" >> "a/tries-$mode.jsonl" 2>> "a/tries-$mode.err"
 done
done
