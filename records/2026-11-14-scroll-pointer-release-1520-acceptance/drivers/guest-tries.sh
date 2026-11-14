#!/bin/sh
set -eu
cd "$HOME/work/s1520"
label=$1; stop=$2; port=${3:-5900}; delay=${4:-2}; jitter=${5:-0}; suffix=${6:-fixed}
set -a; . ./session.env; set +a
export PATH=$HOME/work/s1520/bin:$PATH
export XDG_CONFIG_HOME=$HOME/work/s1520/$label/config XDG_DATA_HOME=$HOME/work/s1520/$label/data XDG_CACHE_HOME=$HOME/work/s1520/$label/cache XDG_STATE_HOME=$HOME/work/s1520/$label/state
for i in $(seq 1 10); do
 firefox --profile "$HOME/work/s1520/ff" https://en.wikipedia.org/wiki/Linux
 sleep 5
 python3 -c 'import time,random;time.sleep(random.uniform(0,1))'
 python3 trial.py --cli "$HOME/work/s1520/bin/cli-$label" --rect 470,200,980,720 --stop "$stop" --log "$HOME/work/s1520/$label/helper.log" --vnc "$port" --rel --start "$delay" --jitter "$jitter" --label "$label-$suffix-$i" >> "$label/tries-$suffix.jsonl" 2>> "$label/tries-$suffix.err"
 sleep 1
done
