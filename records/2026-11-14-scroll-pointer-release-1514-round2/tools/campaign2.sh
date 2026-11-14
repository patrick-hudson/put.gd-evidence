#!/bin/sh
cd $HOME/s
set -a; . $HOME/session.env; set +a
out=$HOME/s/r2; mkdir -p $out
PC=$HOME/s/pr2/squashfs-root/usr/bin/putgd-cli
export XDG_CONFIG_HOME=$HOME/s/pr2/config XDG_DATA_HOME=$HOME/s/pr2/data XDG_CACHE_HOME=$HOME/s/pr2/cache
sh resident.sh start pr2 $HOME/s/pr2/squashfs-root/AppRun >> $out/campaign.log; sleep 10; for p in $(pgrep -x putgd-ui); do kill $p; done; sleep 2
cat /proc/loadavg >> $out/load.txt
python3 untouched.py $PC 470,200,980,720 https://en.wikipedia.org/wiki/Linux $HOME/s/ff pr2-1 >> $out/untouched.jsonl 2>> $out/untouched.err
for mode in fixed random steer; do
  for i in 1 2 3 4 5 6 7 8 9 10; do
    firefox --profile $HOME/s/ff https://en.wikipedia.org/wiki/Linux > /dev/null 2>&1; sleep 6
    case $mode in fixed) args="--rel --native-center";; random) args="--rel --native-center --jitter 4";; steer) args="--rel --native-center --jitter 4 --steer";; esac
    python3 trial.py $args --cli $PC --rect 470,200,980,720 --stop 961,956 --log $HOME/s/pr2/helper.log --label hypr2-$mode-$i >> $out/tries-$mode.jsonl 2>> $out/tries.err
    sleep 2
  done
  cat /proc/loadavg >> $out/load.txt
done
sh resident.sh stop pr2 >> $out/campaign.log
echo done > $out/campaign.done
