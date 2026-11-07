#!/bin/bash
# usage: runpair.sh TAG APPDIR BLOCK [extra m1187 args...] — absent then enabled
set -u
cd ~/work/i1187
tag=$1; app=$2; blk=$3; shift 3
for mode in absent enabled; do
  n="$tag-$mode-b$blk"
  timeout 420 dbus-run-session -- python3 -I tools/m1187.py "$n" "$app" "out/$n" "$mode" --secs 240 "$@" > "out/$n.log" 2>&1
done
echo done > "out/$tag-b$blk.done"
