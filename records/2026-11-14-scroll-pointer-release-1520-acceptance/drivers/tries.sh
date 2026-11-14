#!/bin/sh
# tries.sh LABEL CLI RECT STOP N [URL]: N tries of trial.py, the page opened afresh before each.
lab=$HOME/work/s1520
label=$1; cli=$2; rect=$3; stop=$4; n=$5; url=${6:-https://en.wikipedia.org/wiki/Linux}
set -a; . "$lab/session.env"; set +a
export XDG_CONFIG_HOME=$lab/$label/config XDG_DATA_HOME=$lab/$label/data XDG_CACHE_HOME=$lab/$label/cache
out=$lab/$label/tries${TRIAL_SUFFIX:-}.jsonl
i=1
while [ "$i" -le "$n" ]; do
    if [ -n "${FIREFOX_PROFILE:-}" ]; then firefox --profile "$FIREFOX_PROFILE" "$url" > /dev/null 2>&1; sleep 5; fi
    python3 "$lab/trial.py" ${TRIAL_ARGS:-} --cli "$cli" --rect "$rect" --stop "$stop" --log "$lab/$label/helper.log" --label "$label-$i" >> "$out" 2>> "$lab/$label/tries.err"
    sleep 3
    i=$((i + 1))
done
echo done >> "$out.done"
