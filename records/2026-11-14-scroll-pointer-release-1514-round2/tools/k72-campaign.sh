#!/bin/sh
# k72: untouched captures (nightly, PR head) back to back, then the PR head's tries.
lab=$HOME/work/scroll-1514-lab
cd "$lab"
set -a; . ./session.env; set +a
out=$lab/r3; mkdir -p $out
NC=$lab/nightly/squashfs-root/usr/bin/putgd-cli
DC=$HOME/work/scroll-1514/build/dev/putgd-cli
env3() { export XDG_CONFIG_HOME=$lab/$1/config XDG_DATA_HOME=$lab/$1/data XDG_CACHE_HOME=$lab/$1/cache; }
start() { sh resident.sh start $1 $2 >> $out/campaign.log; sleep 8; for p in $(pgrep -u patrick -x putgd-ui); do kill $p; done; sleep 2; }
stop() { sh resident.sh stop $1 >> $out/campaign.log; sleep 4; }
uptime >> $out/load.txt
# untouched: nightly then PR, alternated, two each
for round in 1 2; do
  env3 nightly3-k72; start nightly3-k72 $lab/nightly/squashfs-root/AppRun
  python3 $lab/r3tools/untouched.py $NC 470,200,980,720 https://en.wikipedia.org/wiki/Linux $lab/ff nightly-$round >> $out/untouched.jsonl
  stop nightly3-k72
  env3 dev3-k72; start dev3-k72 $HOME/work/scroll-1514/build/dev/putgd
  python3 $lab/r3tools/untouched.py $DC 470,200,980,720 https://en.wikipedia.org/wiki/Linux $lab/ff pr-$round >> $out/untouched.jsonl
  stop dev3-k72
  uptime >> $out/load.txt
done
env3 dev3-k72; start dev3-k72 $HOME/work/scroll-1514/build/dev/putgd
for mode in fixed random vnc; do
  for i in 1 2 3 4 5 6 7 8 9 10; do
    firefox --profile $lab/ff https://en.wikipedia.org/wiki/Linux > /dev/null 2>&1; sleep 5
    case $mode in fixed) args="--rel";; random) args="--rel --jitter 4";; vnc) args="";; esac
    python3 $lab/r3tools/trial.py $args --cli $DC --rect 470,200,980,720 --stop 961,956 --log $lab/dev3-k72/helper.log --label k72-$mode-$i >> $out/tries-$mode.jsonl 2>> $out/tries.err
    sleep 2
  done
  uptime >> $out/load.txt
done
stop dev3-k72
echo done > $out/campaign.done
