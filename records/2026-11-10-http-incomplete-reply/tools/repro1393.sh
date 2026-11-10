#!/bin/sh
# #1393: run one case of the scripted-receiver suite many times under CPU contention and
# keep the log and the worker's diagnostic lines of every failing run.
# usage: repro1393.sh RUNS HOGS OUTDIR [test function] [time scale]
B=$HOME/work/i1393/build/dev
OUT=$3
CASE=${4:-aReplyCutOffAfterItsStatusLineIsUnknown}
SCALE=${5:-3}
mkdir -p "$OUT" || exit 2
pids=""
i=0
while [ $i -lt "$2" ]; do
  python3 -c 'while True: pass' &
  pids="$pids $!"
  i=$((i+1))
done
# Only the busy loops this script started, by PID.
trap 'kill $pids 2>/dev/null' EXIT INT TERM
n=0; failed=0
start=$(date +%s)
while [ $n -lt "$1" ]; do
  n=$((n+1))
  PUTGD_HTTP_DIAG=$OUT/diag-$n.txt PUTGD_TEST_TIME_SCALE=$SCALE "$B/test_http_uploader" $CASE > "$OUT/run-$n.log" 2>&1
  if [ $? -ne 0 ]; then
    failed=$((failed+1))
    echo "run $n FAILED (load $(cut -d' ' -f1 /proc/loadavg))"
    grep -A3 "FAIL!" "$OUT/run-$n.log" | cut -c1-260 | head -8
    cat "$OUT/diag-$n.txt" 2>/dev/null
  else
    rm -f "$OUT/run-$n.log" "$OUT/diag-$n.txt"
  fi
done
echo "case=$CASE runs=$n failed=$failed hogs=$2 scale=$SCALE seconds=$(( $(date +%s) - start )) load=$(cut -d' ' -f1-3 /proc/loadavg)"
