#!/bin/sh
# Omarchy guest: untouched captures, nightly and PR alternated (3 each), then the PR's tries.
cd $HOME/s
echo LANG=C.UTF-8 >> $HOME/session.env
set -a; . $HOME/session.env; set +a
out=$HOME/s/r; mkdir -p $out
NC=$HOME/s/nightly/squashfs-root/usr/bin/putgd-cli
PC=$HOME/s/pr/squashfs-root/usr/bin/putgd-cli
env3() { export XDG_CONFIG_HOME=$HOME/s/$1/config XDG_DATA_HOME=$HOME/s/$1/data XDG_CACHE_HOME=$HOME/s/$1/cache; }
start() { sh resident.sh start $1 $2 >> $out/campaign.log; sleep 10; for p in $(pgrep -x putgd-ui); do kill $p; done; sleep 2; }
stop() { sh resident.sh stop $1 >> $out/campaign.log; sleep 5; }
sh resident.sh stop nightly >> $out/campaign.log; sleep 5
(setsid nohup firefox --new-instance --profile $HOME/s/ff --kiosk https://en.wikipedia.org/wiki/Linux > $out/ff.log 2>&1 < /dev/null &)
sleep 25
for round in 1 2 3; do
  cat /proc/loadavg >> $out/load.txt
  env3 nightly; start nightly $HOME/s/nightly/squashfs-root/AppRun
  python3 untouched.py $NC 470,200,980,720 https://en.wikipedia.org/wiki/Linux $HOME/s/ff nightly-$round >> $out/untouched.jsonl 2>> $out/untouched.err
  stop nightly
  env3 pr; start pr $HOME/s/pr/squashfs-root/AppRun
  python3 untouched.py $PC 470,200,980,720 https://en.wikipedia.org/wiki/Linux $HOME/s/ff pr-$round >> $out/untouched.jsonl 2>> $out/untouched.err
  stop pr
done
cat /proc/loadavg >> $out/load.txt
env3 pr; start pr $HOME/s/pr/squashfs-root/AppRun
for mode in fixed random steer; do
  for i in 1 2 3 4 5 6 7 8 9 10; do
    firefox --profile $HOME/s/ff https://en.wikipedia.org/wiki/Linux > /dev/null 2>&1; sleep 6
    case $mode in fixed) args="--rel --native-center";; random) args="--rel --native-center --jitter 4";; steer) args="--rel --native-center --jitter 4 --steer";; esac
    python3 trial.py $args --cli $PC --rect 470,200,980,720 --stop 961,956 --log $HOME/s/pr/helper.log --label hypr-$mode-$i >> $out/tries-$mode.jsonl 2>> $out/tries.err
    sleep 2
  done
  cat /proc/loadavg >> $out/load.txt
done
stop pr
echo done > $out/campaign.done
