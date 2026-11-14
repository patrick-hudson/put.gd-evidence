set -eu
cd "$HOME/work/s5202"
. ./session.env
label=$1
for mode in fixed random steer; do
 for i in $(seq 1 10); do
  firefox --profile "$HOME/work/s5202/ff" https://en.wikipedia.org/wiki/Linux
  sleep 5
  python3 -c 'import random,time;time.sleep(random.uniform(0,1))'
  if test "$mode" = fixed; then delay=2; jitter=0; else delay=1; jitter=5; fi
  extra=""; if test "$mode" = steer; then extra=--steer; fi
  python3 trial.py $extra --native-center --rel --cli "$HOME/work/s5202/bin/cli-$label" --rect 470,200,980,720 --stop "$STOP" --log "$HOME/work/s5202/$label/helper.log" --vnc 5900 --start "$delay" --jitter "$jitter" --label "$label-$mode-$i" >> "$label/tries-$mode.jsonl" 2>> "$label/tries-$mode.err"
 done
done
