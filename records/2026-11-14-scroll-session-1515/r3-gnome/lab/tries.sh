#!/bin/bash
# tries.sh LABEL N START JITTER : N tries of trial.py against the lab resident, Wikipedia opened afresh in the lab Firefox before each.
lab=$HOME/work/scroll-session/gnome
label=$1; n=$2; start=$3; jitter=$4
set -a; . "$lab/session.env"; set +a
export XDG_CONFIG_HOME=$lab/res/config XDG_DATA_HOME=$lab/res/data XDG_CACHE_HOME=$lab/res/cache
out=$lab/$label.jsonl
i=1
while [ "$i" -le "$n" ]; do
    firefox --new-instance --profile "$lab/ff-profile" "https://en.wikipedia.org/wiki/Linux" > /dev/null 2>&1 &
    ff=$!
    sleep 7
    python3 "$lab/trial.py" --rel --vnc 5901 --cli "$lab/../repo/build/dev/putgd-cli" --rect "$RECT" --stop auto --log "$lab/res/helper.log" --label "$label-$i" --start "$start" --jitter "$jitter" >> "$out" 2>> "$lab/$label.err"
    kill "$ff" 2>/dev/null; wait "$ff" 2>/dev/null
    sleep 3
    i=$((i + 1))
done
echo done > "$lab/$label.done"
