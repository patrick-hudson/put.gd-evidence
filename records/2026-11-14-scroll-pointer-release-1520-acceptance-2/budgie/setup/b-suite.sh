set -eu
cd "$HOME/work/s5202"
set -a; . ./session.env; set +a
export LANG=C.UTF-8
for label in "${1:-b}"; do
 export XDG_CONFIG_HOME=$HOME/work/s5202/$label/config XDG_DATA_HOME=$HOME/work/s5202/$label/data XDG_CACHE_HOME=$HOME/work/s5202/$label/cache XDG_STATE_HOME=$HOME/work/s5202/$label/state
 for i in 1 2 3; do
  uptime >> "$label/load.txt"
  python3 untouched.py "$HOME/work/s5202/bin/cli-$label" 470,200,980,720 https://en.wikipedia.org/wiki/Linux "$HOME/work/s5202/ff" "$label-$i" >> "$label/s1.jsonl" 2>> "$label/s1.err"
 done
done
if test "${1:-b}" = b; then exit 0; fi
for mode in fixed random; do
 for i in $(seq 1 10); do
  firefox --profile "$HOME/work/s5202/ff" https://en.wikipedia.org/wiki/Linux
  sleep 5
  python3 -c 'import random,time;time.sleep(random.uniform(0,1))'
  if test "$mode" = fixed; then delay=2; jitter=0; else delay=1; jitter=5; fi
  python3 trial.py --local-center --rel --cli "$HOME/work/s5202/bin/cli-a" --rect 470,200,980,720 --stop 960,956 --log "$HOME/work/s5202/a/helper.log" --vnc 5900 --start "$delay" --jitter "$jitter" --label "a-$mode-$i" >> "a/tries-$mode.jsonl" 2>> "a/tries-$mode.err"
 done
done
