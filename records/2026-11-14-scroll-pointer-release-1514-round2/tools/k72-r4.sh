#!/bin/sh
lab=$HOME/work/scroll-1514-lab
cd "$lab"; set -a; . ./session.env; set +a
out=$lab/r4; mkdir -p $out
DC=$HOME/work/scroll-1514/build/dev/putgd-cli
export XDG_CONFIG_HOME=$lab/dev3-k72/config XDG_DATA_HOME=$lab/dev3-k72/data XDG_CACHE_HOME=$lab/dev3-k72/cache
sh resident.sh start dev3-k72 $HOME/work/scroll-1514/build/dev/putgd >> $out/campaign.log; sleep 8; for p in $(pgrep -u patrick -x putgd-ui); do kill $p; done
for i in 1 2 3 4 5 6 7 8 9 10; do
  firefox --profile $lab/ff https://en.wikipedia.org/wiki/Linux > /dev/null 2>&1; sleep 5
  python3 $lab/r3tools/trial.py --rel --jitter 4 --cli $DC --rect 470,200,980,720 --stop 961,956 --log $lab/dev3-k72/helper.log --label k72r4-random-$i >> $out/tries-random.jsonl 2>> $out/tries.err
  sleep 2
done
sh resident.sh stop dev3-k72 >> $out/campaign.log
echo done > $out/campaign.done
