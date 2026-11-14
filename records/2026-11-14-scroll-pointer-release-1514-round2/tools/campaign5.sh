#!/bin/sh
# A/B on one build: the watch on and off, alternated, three untouched captures each.
cd $HOME/s
set -a; . $HOME/session.env; set +a
out=$HOME/s/r5; mkdir -p $out
PC=$HOME/s/pr5/squashfs-root/usr/bin/putgd-cli
for round in 1 2 3; do
  for w in 1 0; do
    lbl=pr5w$w
    export XDG_CONFIG_HOME=$HOME/s/$lbl/config XDG_DATA_HOME=$HOME/s/$lbl/data XDG_CACHE_HOME=$HOME/s/$lbl/cache
    PUTGD_SCROLL_WATCH=$w sh resident.sh start $lbl $HOME/s/pr5/squashfs-root/AppRun >> $out/campaign.log; sleep 10; for p in $(pgrep -x putgd-ui); do kill $p; done; sleep 2
    cat /proc/loadavg >> $out/load.txt
    python3 untouched.py $PC 470,200,980,720 https://en.wikipedia.org/wiki/Linux $HOME/s/ff watch$w-$round >> $out/untouched.jsonl 2>> $out/untouched.err
    sh resident.sh stop $lbl >> $out/campaign.log; sleep 15
  done
done
echo done > $out/campaign.done
