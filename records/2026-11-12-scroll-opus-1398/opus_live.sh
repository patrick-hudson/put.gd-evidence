#!/bin/bash
# Live cells. $1 host. Chromium must be installed for the cr cells.
set -u
H=$1; L=$HOME/work/sopus/l; export SF7=$L
cd $HOME/work/sopus/s
[ "$H" = d69 ] && export ACCEPT3_MAX_HEIGHT=30000
echo "== resident $(date -u +%T)"; python3 live7.py resident start > $L/resident-start.txt 2>&1 || exit 1
if [ "$H" = m74 ]; then CR="pr:top"; FF="mdn:top wiki:half"; else CR="pr:top"; FF="wiki:top"; fi
for kind in chromium firefox; do
  [ $kind = chromium ] && cells=$CR || cells=$FF
  echo "== $kind $(date -u +%T)"; python3 live7.py browser start $kind || continue
  for c in $cells; do for i in 0 1; do
    s=${c%%:*}; m=${c##*:}; echo "-- $kind $s $m $i $(date -u +%T)"
    python3 live7.py run $s $m opus-${kind:0:2}-$s-$m-$i 2>&1 | tail -4
  done; done
  python3 live7.py browser stop
done
python3 live7.py resident stop
echo "== live done $(date -u +%T)"; touch $L/live.done
